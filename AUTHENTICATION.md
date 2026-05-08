# Internship Management Platform - Authentification & Rôles

Plateforme complète. Login JWT. Contrôle d'accès par rôle.

---

## 🔐 Système Authentification

### Backend Flask
- Routes `/api/auth/login` — Authentification utilisateur
- Génération token JWT 24h
- Vérification token sur chaque requête
- Contrôle rôles `@require_role()`

### Frontend
- Page login responsive
- Stockage token localStorage
- Restauration session automatique
- Redirection si token expiré

---

## 👥 Rôles & Permissions

### ADMIN
**Accès complet** à tous modules:
- Dashboard ✅
- Stagiaires ✅ (Create, Read, Update, Delete)
- Candidatures ✅ (Create, Read, Update, Delete)
- Encadrants ✅ (Create, Read, Update, Delete)
- Ressources Humaines ✅ (Create, Read, Update, Delete)

### RH
**Gestion complets** stagiaires/candidatures:
- Dashboard ✅
- Stagiaires ✅ (Create, Read, Update, Delete)
- Candidatures ✅ (Create, Read, Update, Delete)
- Encadrants ✅ (Create, Read, Update, Delete)
- Ressources Humaines ✅ (Create, Read, Update, Delete)

### ENCADRANT
**Lecture seule** stagiaires:
- Dashboard ✅
- Stagiaires ✅ (Read only)
- Candidatures ❌
- Encadrants ❌
- Ressources Humaines ❌

### STAGIAIRE
**Vue personnel**:
- Dashboard ✅
- Stagiaires ❌
- Candidatures ❌
- Encadrants ❌
- Ressources Humaines ❌

---

## 🧪 Comptes Test

### Admin (Accès total)
```
Username: admin
Password: admin123
Role: ADMIN
```

### RH (Gestion complète)
```
Username: rh_jean
Password: password123
Role: RH

Username: rh_marie
Password: password123
Role: RH
```

### Encadrant (Lecture seule)
```
Username: encadrant_pierre
Password: password123
Role: ENCADRANT
```

### Stagiaire
```
Username: stagiaire_ali
Password: password123
Role: STAGIAIRE
```

---

## 🚀 Installation & Démarrage

### 1. MySQL Setup
```bash
mysql -u root < setup_database.sql
```

### 2. Backend
```bash
pip install -r requirements.txt
python app.py
```

Backend tourne: `http://localhost:5000`

### 3. Frontend
Ouvrir `index.html` dans navigateur (ou servir avec Python)

Frontend sur: `http://localhost:8000` (optionnel)

---

## 📡 API Endpoints (Protégés par JWT)

Tous endpoints nécessitent header:
```
Authorization: Bearer <token>
```

### Authentication
- `POST /api/auth/login` — Pas de token requis
- `GET /api/auth/me` — Token requis
- `POST /api/auth/logout` — Token requis

### Stagiaires (RH, ENCADRANT, ADMIN)
- `GET /api/stagiaires` — Lister
- `GET /api/stagiaires/<id>` — Détail
- `POST /api/stagiaires` — Créer (RH, ADMIN)
- `PUT /api/stagiaires/<id>` — Modifier (RH, ADMIN)
- `DELETE /api/stagiaires/<id>` — Supprimer (RH, ADMIN)

### Candidatures (RH, ADMIN)
- `GET /api/candidatures` — Lister
- `POST /api/candidatures` — Créer
- `PUT /api/candidatures/<id>` — Modifier
- `DELETE /api/candidatures/<id>` — Supprimer

### Encadrants (RH, ADMIN)
- `GET /api/encadrants` — Lister
- `POST /api/encadrants` — Créer
- `PUT /api/encadrants/<id>` — Modifier
- `DELETE /api/encadrants/<id>` — Supprimer

### RH (ADMIN seulement)
- `GET /api/rh` — Lister
- `POST /api/rh` — Créer
- `PUT /api/rh/<id>` — Modifier
- `DELETE /api/rh/<id>` — Supprimer

---

## 🔑 Flow Authentification

### Login
1. User saisit username/password
2. Frontend `POST /api/auth/login`
3. Backend vérifie credentials BD
4. Génère JWT token
5. Frontend stocke token localStorage
6. Affiche dashboard avec permissions

### Token Usage
```javascript
const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
};
fetch('/api/stagiaires', { headers });
```

### Vérification Backend
```python
@require_role('ADMIN', 'RH')
def create_stagiaire():
    # Seulement ADMIN et RH
    pass
```

### Session Restauration
- Token stocké localStorage
- Page reload → vérifie token
- Si valide → affiche dashboard
- Si expiré → retour login

---

## 🛡️ Sécurité

**En PRODUCTION, faire:**
1. ✅ Hasher mots de passe (bcrypt)
2. ✅ HTTPS obligatoire
3. ✅ CORS restrictif
4. ✅ Rate limiting
5. ✅ Vérification CSRF
6. ✅ Validation inputs côté serveur
7. ✅ Logging & monitoring

**Actuellement (développement):**
- ⚠️ Mots de passe stockés plain text
- ⚠️ CORS ouvert
- ⚠️ DEBUG mode

---

## 🐛 Troubleshooting

### "Token expiré" après 24h
→ Redirection login automatique

### "Accès refusé" (403)
→ Votre rôle manque permission
→ Voir tableau rôles ci-dessus

### "Identifiants invalides"
→ Vérifier username/password
→ Voir comptes test

### Pas de données affichées
→ Vérifier API running (`localhost:5000/api/health`)
→ Vérifier MySQL running
→ Consulter console F12

---

## 🔄 Exemple Workflow RH

1. **Login** → `rh_jean / password123`
2. **Dashboard** → Voir stats
3. **Stagiaires** → Créer nouveau stagiaire
4. **Candidatures** → Valider candidatures
5. **Encadrants** → Ajouter encadrant
6. **Déconnexion** → Logout

Encadrant (`encadrant_pierre`):
- Voit Dashboard
- Voit Stagiaires (lecture seule)
- Autres onglets grisés/désactivés

---

## 📝 Fichiers

```
.
├── app.py                    # Backend Flask + JWT + Rôles
├── index.html               # Frontend Login + Dashboard
├── setup_database.sql       # BD avec table USERS
├── requirements.txt         # Dépendances (+ PyJWT)
└── README.md                # Ce fichier
```

---

## 🎯 Prochaines Étapes (Optionnel)

- [ ] Hasher mots de passe bcrypt
- [ ] 2FA/MFA
- [ ] Audit logging
- [ ] Refresh tokens
- [ ] Role-based UI rendering
- [ ] Email notifications
- [ ] Permission matrix dynamic

---

**Besoin aide?** Consulter logs console F12 (Frontend) ou terminal (Backend).
