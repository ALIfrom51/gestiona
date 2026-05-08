# Internship Management Platform

Plateforme full-stack gestion stagiaires. Python + Flask. MySQL. Frontend HTML/CSS/JS.

---

## 📋 Structure Fichiers

```
.
├── app.py                 # Backend Flask API
├── index.html             # Frontend Web
├── setup_database.sql     # Script création BD MySQL
├── requirements.txt       # Dépendances Python
└── README.md             # Ce fichier
```

---

## 🚀 Installation

### 1. **XAMPP Setup**

#### Démarrer MySQL
- Ouvrir XAMPP Control Panel
- Cliquer "Start" pour Apache et MySQL
- MySQL doit tourner sur port 3306

#### Créer la base données
1. Ouvrir phpMyAdmin: http://localhost/phpmyadmin
2. Aller à l'onglet "SQL"
3. Copier-coller contenu `setup_database.sql`
4. Exécuter

Ou via terminal MySQL:
```bash
mysql -u root < setup_database.sql
```

---

### 2. **Python Backend Setup**

#### Installer dépendances
```bash
pip install -r requirements.txt
```

#### Vérifier MySQL accessible
```bash
mysql -u root
```

Sortir: `exit`

#### Lancer Flask
```bash
python app.py
```

Backend démarre sur: **http://localhost:5000**

Vous devez voir:
```
 * Running on http://127.0.0.1:5000
```

---

### 3. **Frontend Web**

1. Ouvrir `index.html` dans navigateur
   - Clic droit > Ouvrir avec navigateur
   - Ou: File > Open > index.html

2. Ou servir avec Python:
```bash
python -m http.server 8000
```

Accéder: **http://localhost:8000**

---

## 🔧 Configuration

### Modifier paramètres MySQL dans `app.py`

```python
app.config['MYSQL_HOST'] = 'localhost'     # Serveur
app.config['MYSQL_USER'] = 'root'          # Utilisateur
app.config['MYSQL_PASSWORD'] = ''          # Mot de passe
app.config['MYSQL_DB'] = 'internship_db'   # Base données
```

### CORS Frontend

Si frontend sur port différent, modifier dans `app.py`:

```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8000"]
    }
})
```

---

## 📡 Endpoints API

### **Stagiaires**
- `GET /api/stagiaires` - Lister tous
- `GET /api/stagiaires/<id>` - Détail
- `POST /api/stagiaires` - Créer
- `PUT /api/stagiaires/<id>` - Modifier
- `DELETE /api/stagiaires/<id>` - Supprimer

### **Candidatures**
- `GET /api/candidatures` - Lister
- `POST /api/candidatures` - Créer
- `PUT /api/candidatures/<id>` - Modifier

### **Encadrants**
- `GET /api/encadrants` - Lister
- `POST /api/encadrants` - Créer
- `PUT /api/encadrants/<id>` - Modifier
- `DELETE /api/encadrants/<id>` - Supprimer

### **RH**
- `GET /api/rh` - Lister
- `POST /api/rh` - Créer
- `PUT /api/rh/<id>` - Modifier
- `DELETE /api/rh/<id>` - Supprimer

### **Health**
- `GET /api/health` - Vérifier API

---

## 🎯 Fonctionnalités Frontend

✅ Dashboard statistiques
✅ Gestion complets stagiaires
✅ Suivi candidatures
✅ Gestion encadrants
✅ Gestion RH
✅ Formulaires dynamiques
✅ Tables interactives
✅ Design dark mode moderne

---

## 🐛 Troubleshooting

### **"Erreur connexion MySQL"**
- Vérifier MySQL running XAMPP
- Vérifier credentials `app.py`
- Vérifier base `internship_db` existe

### **"Port 5000 déjà utilisé"**
```bash
python app.py --port 5001
```

### **"CORS erreur"**
- Vérifier URL frontend correcte
- Vérifier CORS activé `app.py`

### **Frontend ne charge pas**
- Vérifier fichier `index.html` path
- Ouvrir console F12 pour errors
- Vérifier API URL (`http://localhost:5000/api`)

---

## 📊 Exemple Flux

1. **Créer RH** → Onglet "Ressources Humaines"
2. **Créer Encadrant** → Attribuer RH
3. **Créer Stagiaire** → Attribuer RH + Encadrant
4. **Créer Candidature** → Lier Stagiaire
5. **Voir Dashboard** → Stats mis à jour

---

## 🔐 Sécurité Notes

⚠️ **En production:**
- Ajouter authentification (JWT)
- Valider inputs côté serveur
- HTTPS obligatoire
- SQL injection prévention (utiliser paramètres - déjà fait)
- Crypter mot de passe BD

---

## 📝 Licence

Libre d'utilisation. Attributions facultatives.

---

**Besoin aide?** Vérifier logs console F12 (Frontend) ou terminal (Backend).
