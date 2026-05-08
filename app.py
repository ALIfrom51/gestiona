import MySQLdb
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import json
import os
from datetime import datetime, timedelta
import jwt
import hashlib

app = Flask(__name__)
CORS(app)

@app.route('/')
def serve_frontend():
    return send_from_directory('.', 'index.html')

# Config
JWT_SECRET = 'your-secret-key-change-in-production'
JWT_ALGORITHM = 'HS256'

# MySQL Config
db_config = {
    'host': os.getenv('MYSQL_HOST', 'db-1'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'root'),
    'database': os.getenv('MYSQL_DATABASE', 'internship_db'),
    'use_pure': True
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as err:
        print(f"Error: {err}")
        return None

# ==================== HELPERS ====================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_token(user_id, role, username):
    payload = {
        'user_id': user_id,
        'role': role,
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_auth_header():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    return auth_header.split(' ')[1]

def check_auth():
    token = get_auth_header()
    if not token:
        return None, None
    
    user = verify_token(token)
    if not user:
        return None, None
    
    return user, user.get('role')

def require_role(*roles):
    def decorator(f):
        def wrapper(*args, **kwargs):
            user, role = check_auth()
            if not user or role not in roles:
                return jsonify({'error': 'Unauthorized'}), 403
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

# ==================== AUTH ====================

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM USERS WHERE USERNAME = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if user['PASSWORD'] != password:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        token = create_token(user['IDUSER'], user['ROLE'], user['USERNAME'])
        
        return jsonify({
            'token': token,
            'user': {
                'id': user['IDUSER'],
                'username': user['USERNAME'],
                'role': user['ROLE'],
                'firstname': user['FIRSTNAME'],
                'lastname': user['LASTNAME']
            }
        }), 200
    except Exception as err:
        return jsonify({'error': str(err)}), 500

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    user, role = check_auth()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT IDUSER, USERNAME, ROLE, FIRSTNAME, LASTNAME, EMAIL FROM USERS WHERE IDUSER = %s", (user['user_id'],))
        current_user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return jsonify(current_user), 200
    except Exception as err:
        return jsonify({'error': str(err)}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    return jsonify({'message': 'Logged out'}), 200

# ==================== STAGIAIRE ====================

@app.route('/api/stagiaires', methods=['GET'])
@require_role('ADMIN', 'RH', 'ENCADRANT')
def get_stagiaires():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.*, rh.NOMRH, rh.PRENOMRH, e.NOMENCADRANT, e.PRENOMENCADRANT
            FROM STAGIAIRE s
            LEFT JOIN RH rh ON s.IDRH = rh.IDRH
            LEFT JOIN ENCADRANT e ON s.IDENCADRANT = e.IDENCADRANT
        """)
        stagiaires = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(stagiaires), 200
    except Exception as err:
        return jsonify({'error': str(err)}), 500

@app.route('/api/stagiaires/<int:numero>', methods=['GET'])
@require_role('ADMIN', 'RH', 'ENCADRANT', 'STAGIAIRE')
def get_stagiaire(numero):
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.*, rh.NOMRH, rh.PRENOMRH, e.NOMENCADRANT, e.PRENOMENCADRANT
            FROM STAGIAIRE s
            LEFT JOIN RH rh ON s.IDRH = rh.IDRH
            LEFT JOIN ENCADRANT e ON s.IDENCADRANT = e.IDENCADRANT
            WHERE s.NUMERO = %s
        """, (numero,))
        stagiaire = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not stagiaire:
            return jsonify({'error': 'Stagiaire non trouvé'}), 404
        return jsonify(stagiaire), 200
    except Exception as err:
        return jsonify({'error': str(err)}), 500

@app.route('/api/stagiaires', methods=['POST'])
@require_role('ADMIN', 'RH')
def create_stagiaire():
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO STAGIAIRE 
            (NUMERO, IDRH, IDENCADRANT, NOMSTAGIAIRE, PRENOMSTAGIAIRE, DOMAINE, SATATUSSTAGIAIRE, DATEVALIDATION, DECISION)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get('NUMERO'),
            data.get('IDRH'),
            data.get('IDENCADRANT'),
            data.get('NOMSTAGIAIRE'),
            data.get('PRENOMSTAGIAIRE'),
            data.get('DOMAINE'),
            data.get('SATATUSSTAGIAIRE', 'En cours'),
            data.get('DATEVALIDATION'),
            data.get('DECISION')
        ))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Stagiaire créé', 'NUMERO': data.get('NUMERO')}), 201
    except Exception as err:
        return jsonify({'error': str(err)}), 500

@app.route('/api/stagiaires/<int:numero>', methods=['PUT'])
@require_role('ADMIN', 'RH')
def update_stagiaire(numero):
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE STAGIAIRE SET
            IDRH = %s, IDENCADRANT = %s, NOMSTAGIAIRE = %s, PRENOMSTAGIAIRE = %s,
            DOMAINE = %s, SATATUSSTAGIAIRE = %s, DATEVALIDATION = %s, DECISION = %s
            WHERE NUMERO = %s
        """, (
            data.get('IDRH'),
            data.get('IDENCADRANT'),
            data.get('NOMSTAGIAIRE'),
            data.get('PRENOMSTAGIAIRE'),
            data.get('DOMAINE'),
            data.get('SATATUSSTAGIAIRE'),
            data.get('DATEVALIDATION'),
            data.get('DECISION'),
            numero
        ))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Stagiaire modifié'}), 200
    except Exception as err:
        return jsonify({'error': str(err)}), 500

@app.route('/api/stagiaires/<int:numero>', methods=['DELETE'])
@require_role('ADMIN', 'RH')
def delete_stagiaire(numero):
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        cursor.execute("DELETE FROM STAGIAIRE WHERE NUMERO = %s", (numero,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Stagiaire supprimé'}), 200
    except Exception as err:
        return jsonify({'error': str(err)}), 500

# ==================== CANDIDATURE ====================

@app.route('/api/candidatures', methods=['GET'])
@require_role('ADMIN', 'RH')
def get_candidatures():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.*, s.NOMSTAGIAIRE, s.PRENOMSTAGIAIRE, s.DOMAINE
            FROM CANDIDATURE c
            LEFT JOIN STAGIAIRE s ON c.NUMERO = s.NUMERO
        """)
        candidatures = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(candidatures), 200
    except Exception as err:
        return jsonify({'error': str(err)}), 500

@app.route('/api/candidatures', methods=['POST'])
@require_role('ADMIN', 'RH')
def create_candidature():
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO CANDIDATURE (NUMERODECANDIDAT, NUMERO, STATUSCANDIDATURE)
            VALUES (%s, %s, %s)
        """, (
            data.get('NUMERODECANDIDAT'),
            data.get('NUMERO'),
            data.get('STATUSCANDIDATURE', 'Pending')
        ))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Candidature créée'}), 201
    except Exception as err:
        return jsonify({'error': str(err)}), 500

@app.route('/api/candidatures/<int:numerodecandidat>', methods=['PUT'])
@require_role('ADMIN', 'RH')
def update_candidature(numerodecandidat):
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE CANDIDATURE SET STATUSCANDIDATURE = %s WHERE NUMERODECANDIDAT = %s
        """, (data.get('STATUSCANDIDATURE'), numerodecandidat))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Candidature modifiée'}), 200
    except Exception as err:
        return jsonify({'error': str(err)}), 500

# ==================== ENCADRANT ====================

@app.route('/api/encadrants', methods=['GET'])
@require_role('ADMIN', 'RH')
def get_encadrants():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.*, rh.NOMRH, rh.PRENOMRH
            FROM ENCADRANT e
            LEFT JOIN RH rh ON e.IDRH = rh.IDRH
        """)
        encadrants = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(encadrants), 200
    except Exception as err:
        return jsonify({'error': str(err)}), 500

@app.route('/api/encadrants', methods=['POST'])
@require_role('ADMIN', 'RH')
def create_encadrant():
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ENCADRANT (IDENCADRANT, IDRH, NOMENCADRANT, PRENOMENCADRANT, REMARQUE, EVALUATIONSTAGIAIRE)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data.get('IDENCADRANT'),
            data.get('IDRH'),
            data.get('NOMENCADRANT'),
            data.get('PRENOMENCADRANT'),
            data.get('REMARQUE'),
            data.get('EVALUATIONSTAGIAIRE')
        ))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Encadrant créé'}), 201
    except Exception as err:
        return jsonify({'error': str(err)}), 500

@app.route('/api/encadrants/<int:idencadrant>', methods=['PUT'])
@require_role('ADMIN', 'RH')
def update_encadrant(idencadrant):
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE ENCADRANT SET 
            IDRH = %s, NOMENCADRANT = %s, PRENOMENCADRANT = %s, 
            REMARQUE = %s, EVALUATIONSTAGIAIRE = %s
            WHERE IDENCADRANT = %s
        """, (
            data.get('IDRH'),
            data.get('NOMENCADRANT'),
            data.get('PRENOMENCADRANT'),
            data.get('REMARQUE'),
            data.get('EVALUATIONSTAGIAIRE'),
            idencadrant
        ))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Encadrant modifié'}), 200
    except Exception as err:
        return jsonify({'error': str(err)}), 500

# ==================== RH ====================

@app.route('/api/rh', methods=['GET'])
@require_role('ADMIN', 'RH')
def get_rh():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM RH")
        rh_list = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rh_list), 200
    except Exception as err:
        return jsonify({'error': str(err)}), 500

@app.route('/api/rh', methods=['POST'])
@require_role('ADMIN', 'RH')
def create_rh():
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO RH (IDRH, NOMRH, PRENOMRH)
            VALUES (%s, %s, %s)
        """, (data.get('IDRH'), data.get('NOMRH'), data.get('PRENOMRH')))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'RH créé'}), 201
    except Exception as err:
        return jsonify({'error': str(err)}), 500

@app.route('/api/rh/<int:idrh>', methods=['PUT'])
@require_role('ADMIN', 'RH')
def update_rh(idrh):
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE RH SET NOMRH = %s, PRENOMRH = %s WHERE IDRH = %s
        """, (data.get('NOMRH'), data.get('PRENOMRH'), idrh))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'RH modifié'}), 200
    except Exception as err:
        return jsonify({'error': str(err)}), 500

# ==================== HEALTH ====================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'API internship running'}), 200

if __name__ == '__main__':
    app.run(
        debug=os.getenv('FLASK_DEBUG', '0') == '1',
        host='0.0.0.0',
        port=int(os.getenv('PORT', '5000'))
    )

# ==================== HELPERS ====================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_token(user_id, role, username):
    payload = {
        'user_id': user_id,
        'role': role,
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_auth_header():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    return auth_header.split(' ')[1]

def check_auth():
    token = get_auth_header()
    if not token:
        return None, None
    
    user = verify_token(token)
    if not user:
        return None, None
    
    return user, user.get('role')

def require_role(*roles):
    def decorator(f):
        def wrapper(*args, **kwargs):
            user, role = check_auth()
            if not user or role not in roles:
                return jsonify({'error': 'Unauthorized'}), 403
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

# ==================== AUTH ====================

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM USERS WHERE USERNAME = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if user['PASSWORD'] != password:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        token = create_token(user['IDUSER'], user['ROLE'], user['USERNAME'])
        
        return jsonify({
            'token': token,
            'user': {
                'id': user['IDUSER'],
                'username': user['USERNAME'],
                'role': user['ROLE'],
                'firstname': user['FIRSTNAME'],
                'lastname': user['LASTNAME']
            }
        }), 200
    except Exception as err:
        return jsonify({'error': str(err)}), 500

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    user, role = check_auth()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT IDUSER, USERNAME, ROLE, FIRSTNAME, LASTNAME, EMAIL FROM USERS WHERE IDUSER = %s", (user['user_id'],))
        current_user = cursor.fetchone()
        cursor.close()
        
        return jsonify(current_user), 200
    except Exception as err:
        return jsonify({'error': str(err)}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    return jsonify({'message': 'Logged out'}), 200

# ==================== STAGIAIRE ====================

@app.route('/api/stagiaires', methods=['GET'])
@require_role('ADMIN', 'RH', 'ENCADRANT')
def get_stagiaires():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT s.*, rh.NOMRH, rh.PRENOMRH, e.NOMENCADRANT, e.PRENOMENCADRANT
            FROM STAGIAIRE s
            LEFT JOIN RH rh ON s.IDRH = rh.IDRH
            LEFT JOIN ENCADRANT e ON s.IDENCADRANT = e.IDENCADRANT
        """)
        stagiaires = cursor.fetchall()
        cursor.close()
        return jsonify(stagiaires), 200
    except Exception as err:
        return jsonify({'error': str(err)}), 500

@app.route('/api/stagiaires/<int:numero>', methods=['GET'])
@require_role('ADMIN', 'RH', 'ENCADRANT', 'STAGIAIRE')
def get_stagiaire(numero):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT s.*, rh.NOMRH, rh.PRENOMRH, e.NOMENCADRANT, e.PRENOMENCADRANT
            FROM STAGIAIRE s
            LEFT JOIN RH rh ON s.IDRH = rh.IDRH
            LEFT JOIN ENCADRANT e ON s.IDENCADRANT = e.IDENCADRANT
            WHERE s.NUMERO = %s
        """, (numero,))
        stagiaire = cursor.fetchone()
        cursor.close()
        
        if not stagiaire:
            return jsonify({'error': 'Stagiaire non trouvé'}), 404
        return jsonify(stagiaire), 200
    except Exception as err:
        return jsonify({'error': str(err)}), 500

@app.route('/api/stagiaires', methods=['POST'])
@require_role('ADMIN', 'RH')
def create_stagiaire():
    try:
        data = request.get_json()
        
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO STAGIAIRE 
            (NUMERO, IDRH, IDENCADRANT, NOMSTAGIAIRE, PRENOMSTAGIAIRE, DOMAINE, SATATUSSTAGIAIRE, DATEVALIDATION, DECISION)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get('NUMERO'),
            data.get('IDRH'),
            data.get('IDENCADRANT'),
            data.get('NOMSTAGIAIRE'),
            data.get('PRENOMSTAGIAIRE'),
            data.get('DOMAINE'),
            data.get('SATATUSSTAGIAIRE', 'En cours'),
            data.get('DATEVALIDATION'),
            data.get('DECISION')
        ))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'message': 'Stagiaire créé', 'NUMERO': data.get('NUMERO')}), 201
    except Exception as err:
        mysql.connection.rollback()
        return jsonify({'error': str(err)}), 500

@app.route('/api/stagiaires/<int:numero>', methods=['PUT'])
@require_role('ADMIN', 'RH')
def update_stagiaire(numero):
    try:
        data = request.get_json()
        
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE STAGIAIRE SET
            IDRH = %s, IDENCADRANT = %s, NOMSTAGIAIRE = %s, PRENOMSTAGIAIRE = %s,
            DOMAINE = %s, SATATUSSTAGIAIRE = %s, DATEVALIDATION = %s, DECISION = %s
            WHERE NUMERO = %s
        """, (
            data.get('IDRH'),
            data.get('IDENCADRANT'),
            data.get('NOMSTAGIAIRE'),
            data.get('PRENOMSTAGIAIRE'),
            data.get('DOMAINE'),
            data.get('SATATUSSTAGIAIRE'),
            data.get('DATEVALIDATION'),
            data.get('DECISION'),
            numero
        ))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'message': 'Stagiaire modifié'}), 200
    except Exception as err:
        mysql.connection.rollback()
        return jsonify({'error': str(err)}), 500

@app.route('/api/stagiaires/<int:numero>', methods=['DELETE'])
@require_role('ADMIN', 'RH')
def delete_stagiaire(numero):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM STAGIAIRE WHERE NUMERO = %s", (numero,))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'message': 'Stagiaire supprimé'}), 200
    except Exception as err:
        mysql.connection.rollback()
        return jsonify({'error': str(err)}), 500

# ==================== CANDIDATURE ====================

@app.route('/api/candidatures', methods=['GET'])
@require_role('ADMIN', 'RH')
def get_candidatures():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT c.*, s.NOMSTAGIAIRE, s.PRENOMSTAGIAIRE, s.DOMAINE
            FROM CANDIDATURE c
            LEFT JOIN STAGIAIRE s ON c.NUMERO = s.NUMERO
        """)
        candidatures = cursor.fetchall()
        cursor.close()
        return jsonify(candidatures), 200
    except Exception as err:
        return jsonify({'error': str(err)}), 500

@app.route('/api/candidatures', methods=['POST'])
@require_role('ADMIN', 'RH')
def create_candidature():
    try:
        data = request.get_json()
        
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO CANDIDATURE (NUMERODECANDIDAT, NUMERO, STATUSCANDIDATURE)
            VALUES (%s, %s, %s)
        """, (
            data.get('NUMERODECANDIDAT'),
            data.get('NUMERO'),
            data.get('STATUSCANDIDATURE', 'Pending')
        ))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'message': 'Candidature créée'}), 201
    except Exception as err:
        mysql.connection.rollback()
        return jsonify({'error': str(err)}), 500

@app.route('/api/candidatures/<int:numerodecandidat>', methods=['PUT'])
@require_role('ADMIN', 'RH')
def update_candidature(numerodecandidat):
    try:
        data = request.get_json()
        
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE CANDIDATURE SET STATUSCANDIDATURE = %s WHERE NUMERODECANDIDAT = %s
        """, (data.get('STATUSCANDIDATURE'), numerodecandidat))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'message': 'Candidature modifiée'}), 200
    except Exception as err:
        mysql.connection.rollback()
        return jsonify({'error': str(err)}), 500

# ==================== ENCADRANT ====================

@app.route('/api/encadrants', methods=['GET'])
@require_role('ADMIN', 'RH')
def get_encadrants():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT e.*, rh.NOMRH, rh.PRENOMRH
            FROM ENCADRANT e
            LEFT JOIN RH rh ON e.IDRH = rh.IDRH
        """)
        encadrants = cursor.fetchall()
        cursor.close()
        return jsonify(encadrants), 200
    except Exception as err:
        return jsonify({'error': str(err)}), 500

@app.route('/api/encadrants', methods=['POST'])
@require_role('ADMIN', 'RH')
def create_encadrant():
    try:
        data = request.get_json()
        
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO ENCADRANT (IDENCADRANT, IDRH, NOMENCADRANT, PRENOMENCADRANT, REMARQUE, EVALUATIONSTAGIAIRE)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data.get('IDENCADRANT'),
            data.get('IDRH'),
            data.get('NOMENCADRANT'),
            data.get('PRENOMENCADRANT'),
            data.get('REMARQUE'),
            data.get('EVALUATIONSTAGIAIRE')
        ))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'message': 'Encadrant créé'}), 201
    except Exception as err:
        mysql.connection.rollback()
        return jsonify({'error': str(err)}), 500

@app.route('/api/encadrants/<int:idencadrant>', methods=['PUT'])
@require_role('ADMIN', 'RH')
def update_encadrant(idencadrant):
    try:
        data = request.get_json()
        
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE ENCADRANT SET 
            IDRH = %s, NOMENCADRANT = %s, PRENOMENCADRANT = %s, 
            REMARQUE = %s, EVALUATIONSTAGIAIRE = %s
            WHERE IDENCADRANT = %s
        """, (
            data.get('IDRH'),
            data.get('NOMENCADRANT'),
            data.get('PRENOMENCADRANT'),
            data.get('REMARQUE'),
            data.get('EVALUATIONSTAGIAIRE'),
            idencadrant
        ))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'message': 'Encadrant modifié'}), 200
    except Exception as err:
        mysql.connection.rollback()
        return jsonify({'error': str(err)}), 500

# ==================== RH ====================

@app.route('/api/rh', methods=['GET'])
@require_role('ADMIN', 'RH')
def get_rh():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM RH")
        rh_list = cursor.fetchall()
        cursor.close()
        return jsonify(rh_list), 200
    except Exception as err:
        return jsonify({'error': str(err)}), 500

@app.route('/api/rh', methods=['POST'])
@require_role('ADMIN', 'RH')
def create_rh():
    try:
        data = request.get_json()
        
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO RH (IDRH, NOMRH, PRENOMRH)
            VALUES (%s, %s, %s)
        """, (data.get('IDRH'), data.get('NOMRH'), data.get('PRENOMRH')))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'message': 'RH créé'}), 201
    except Exception as err:
        mysql.connection.rollback()
        return jsonify({'error': str(err)}), 500

@app.route('/api/rh/<int:idrh>', methods=['PUT'])
@require_role('ADMIN', 'RH')
def update_rh(idrh):
    try:
        data = request.get_json()
        
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE RH SET NOMRH = %s, PRENOMRH = %s WHERE IDRH = %s
        """, (data.get('NOMRH'), data.get('PRENOMRH'), idrh))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'message': 'RH modifié'}), 200
    except Exception as err:
        mysql.connection.rollback()
        return jsonify({'error': str(err)}), 500

# ==================== HEALTH ====================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'API internship running'}), 200

if __name__ == '__main__':
    app.run(
        debug=os.getenv('FLASK_DEBUG', '0') == '1',
        host='0.0.0.0',
        port=int(os.getenv('PORT', '5000'))
    )
