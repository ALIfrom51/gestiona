-- ==============================================================
-- Création Base Internship. MySQL. XAMPP Compatible.
-- ==============================================================

-- Créer la base si n'existe pas
CREATE DATABASE IF NOT EXISTS internship_db;
USE internship_db;

-- ==============================================================
-- Supprimer les tables existantes (clés étrangères d'abord)
-- ==============================================================

SET FOREIGN_KEY_CHECKS=0;

DROP TABLE IF EXISTS CANDIDATURE;
DROP TABLE IF EXISTS STAGIAIRE;
DROP TABLE IF EXISTS ENCADRANT;
DROP TABLE IF EXISTS USERS;
DROP TABLE IF EXISTS RH;

SET FOREIGN_KEY_CHECKS=1;

-- ==============================================================
-- Table USERS (Authentification + Rôles)
-- ==============================================================

CREATE TABLE USERS (
   IDUSER INT NOT NULL AUTO_INCREMENT,
   USERNAME VARCHAR(100) NOT NULL UNIQUE,
   PASSWORD VARCHAR(255) NOT NULL,
   ROLE ENUM('ADMIN', 'RH', 'ENCADRANT', 'STAGIAIRE') NOT NULL DEFAULT 'STAGIAIRE',
   FIRSTNAME VARCHAR(255) NULL,
   LASTNAME VARCHAR(255) NULL,
   EMAIL VARCHAR(255) NULL,
   CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   PRIMARY KEY (IDUSER),
   INDEX idx_username (USERNAME)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================
-- Table RH (dépendances d'autres tables)
-- ==============================================================

CREATE TABLE RH (
   IDRH INT NOT NULL AUTO_INCREMENT,
   NOMRH VARCHAR(255) NULL,
   PRENOMRH VARCHAR(255) NULL,
   PRIMARY KEY (IDRH)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================
-- Table ENCADRANT
-- ==============================================================

CREATE TABLE ENCADRANT (
   IDENCADRANT INT NOT NULL AUTO_INCREMENT,
   IDRH INT NULL,
   NOMENCADRANT VARCHAR(255) NULL,
   PRENOMENCADRANT VARCHAR(255) NULL,
   REMARQUE LONGTEXT NULL,
   EVALUATIONSTAGIAIRE LONGTEXT NULL,
   PRIMARY KEY (IDENCADRANT),
   FOREIGN KEY (IDRH)
      REFERENCES RH (IDRH)
      ON UPDATE RESTRICT
      ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================
-- Table STAGIAIRE
-- ==============================================================

CREATE TABLE STAGIAIRE (
   NUMERO INT NOT NULL AUTO_INCREMENT,
   IDRH INT NOT NULL,
   IDENCADRANT INT NOT NULL,
   NOMSTAGIAIRE VARCHAR(255) NULL,
   PRENOMSTAGIAIRE VARCHAR(255) NULL,
   DOMAINE VARCHAR(255) NULL,
   SATATUSSTAGIAIRE VARCHAR(255) NULL,
   DATEVALIDATION DATE NULL,
   DECISION VARCHAR(255) NULL,
   PRIMARY KEY (NUMERO),
   FOREIGN KEY (IDRH)
      REFERENCES RH (IDRH)
      ON UPDATE RESTRICT
      ON DELETE RESTRICT,
   FOREIGN KEY (IDENCADRANT)
      REFERENCES ENCADRANT (IDENCADRANT)
      ON UPDATE RESTRICT
      ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================
-- Table CANDIDATURE
-- ==============================================================

CREATE TABLE CANDIDATURE (
   NUMERODECANDIDAT INT NOT NULL AUTO_INCREMENT,
   NUMERO INT NOT NULL,
   STATUSCANDIDATURE VARCHAR(255) NULL,
   PRIMARY KEY (NUMERODECANDIDAT),
   FOREIGN KEY (NUMERO)
      REFERENCES STAGIAIRE (NUMERO)
      ON UPDATE RESTRICT
      ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================
-- Index pour optimisation
-- ==============================================================

CREATE INDEX IX_ENCADRANT_IDRH ON ENCADRANT(IDRH);
CREATE INDEX IX_STAGIAIRE_IDRH ON STAGIAIRE(IDRH);
CREATE INDEX IX_STAGIAIRE_IDENCADRANT ON STAGIAIRE(IDENCADRANT);
CREATE INDEX IX_CANDIDATURE_NUMERO ON CANDIDATURE(NUMERO);

-- ==============================================================
-- Données d'exemple
-- ==============================================================

-- Utilisateurs test (password: password123)
-- Hash SHA256('password123') = 482c811da5d5b4bc6d497ffa98491e38
INSERT INTO USERS (USERNAME, PASSWORD, ROLE, FIRSTNAME, LASTNAME, EMAIL) VALUES 
('admin', 'admin123', 'ADMIN', 'Admin', 'System', 'admin@internship.com'),
('rh_jean', 'password123', 'RH', 'Jean', 'Dupont', 'jean@internship.com'),
('rh_marie', 'password123', 'RH', 'Marie', 'Martin', 'marie@internship.com'),
('encadrant_pierre', 'password123', 'ENCADRANT', 'Pierre', 'Durand', 'pierre@internship.com'),
('stagiaire_ali', 'password123', 'STAGIAIRE', 'Ali', 'Ahmed', 'ali@internship.com');

INSERT INTO RH (NOMRH, PRENOMRH) VALUES ('Dupont', 'Jean');
INSERT INTO RH (NOMRH, PRENOMRH) VALUES ('Martin', 'Marie');

INSERT INTO ENCADRANT (IDRH, NOMENCADRANT, PRENOMENCADRANT, REMARQUE, EVALUATIONSTAGIAIRE) VALUES 
(1, 'Durand', 'Pierre', 'Bon encadrement', 'Très bon stagiaire');

INSERT INTO STAGIAIRE (IDRH, IDENCADRANT, NOMSTAGIAIRE, PRENOMSTAGIAIRE, DOMAINE, SATATUSSTAGIAIRE, DATEVALIDATION, DECISION) VALUES 
(1, 1, 'Ahmed', 'Ali', 'Informatique', 'Validé', '2026-05-01', 'Accepté');

INSERT INTO CANDIDATURE (NUMERO, STATUSCANDIDATURE) VALUES 
(1, 'Acceptée');

-- ==============================================================
-- FIN Script
-- ==============================================================
