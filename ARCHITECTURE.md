# 🏗️ Architecture des Fichiers - Pong Force

## 📋 Vue d'Ensemble

Ce projet est composé de **deux parties principales** :
1. **Site Web** : Site promotionnel interactif pour Pong Force
2. **Jeu Pong Force** : Application Python/Pygame compilée en exécutable Windows

---

## 📁 Structure Racine du Projet

```
pong game/
│
├── 📄 Fichiers HTML (Site Web)
│   ├── index.html              # Page d'accueil principale
│   ├── demo.html               # Page de démo jouable dans le navigateur
│   ├── integration_test.html   # Page de test d'intégration
│   └── test.html               # Page de test générale
│
├── 📁 css/                     # Styles du site web
│   ├── style.css              # Styles principaux (thème néon arcade)
│   └── responsive.css         # Styles responsives (mobile/tablette)
│
├── 📁 js/                      # Scripts JavaScript du site web
│   ├── main.js                # Animations, interactions, navigation
│   ├── demo.js                # Logique du jeu de démo (Canvas HTML5)
│   └── particles.js           # Effets de particules en arrière-plan
│
├── 📁 assets/                  # Ressources du site web
│   ├── images/
│   │   ├── ping-pong.ico      # Icône du site
│   │   └── splash_art.png     # Image de splash/hero
│   ├── sounds/                # Sons du site (placeholder)
│   └── videos/                # Vidéos (placeholder)
│
├── 📁 pong_force/              # Code source du jeu Python
│   ├── main.py                # Point d'entrée principal du jeu
│   ├── build.py               # Script de compilation PyInstaller
│   ├── build.bat              # Script batch Windows pour build
│   ├── config.py              # Configuration du jeu
│   ├── encryptor.py           # Utilitaires de chiffrement
│   ├── payload.py             
│   ├── PongForce.spec         # Fichier de spécification PyInstaller
│   ├── version.txt            # Version du jeu
│   ├── version_info.txt       # Métadonnées de version Windows
│   ├── upx.exe                # Compresseur UPX (optionnel)
│   │
│   ├── 📁 game/               # Modules de jeu
│   │   ├── __init__.py
│   │   ├── ball.py           # Logique de la balle
│   │   ├── paddle.py         # Logique des raquettes
│   │   ├── scoreboard.py     # Système de score
│   │   ├── power.py          # Mécanique Force Push
│   │   ├── effects.py        # Effets visuels (particules, trails)
│   │   ├── game_loop.py      # Boucle principale du jeu
│   │   └── menu.py           # Menu graphique interactif
│   │
│   ├── 📁 network/            # Réseau multijoueur
│   │   ├── __init__.py
│   │   ├── server.py         # Serveur de jeu réseau
│   │   └── client.py         # Client de jeu réseau
│   │
│   ├── 📁 assets/             # Ressources du jeu
│   │   ├── images/
│   │   │   ├── icon.png      # Icône du jeu
│   │   │   └── splash_art.png
│   │   ├── fonts/            # Polices personnalisées
│   │   ├── sounds/           # Sons du jeu
│   │   └── ping-pong.ico     # Icône Windows
│   │
│   └── 📁 build/              # Fichiers temporaires de build
│       └── PongForce/        # Artéfacts PyInstaller
│
├── 📁 fonts/                  # Polices du site web (placeholder)
│
├── 📄 Scripts et Utilitaires
│   ├── deploy.bat            # Script de déploiement
│   ├── setup_download.bat    # Configuration du téléchargement
│   ├── install_pong_force.bat # Installation du jeu
│   ├── LANCER_PONG_FORCE.bat # Lanceur rapide du jeu
│   ├── create_cert.ps1       # Création de certificat (Windows Defender)
│   ├── create_custom_icon.py  # Génération d'icône
│   ├── fix_windows_defender.py # Fix pour Windows Defender
│   ├── verifier_telechargement.ps1 # Vérification du téléchargement
│   ├── test_download.py      # Tests automatisés
│   └── test_game.py          # Tests du jeu
│
└── 📄 Documentation
    ├── README.md              # Documentation principale
    ├── ARCHITECTURE.md        # Ce fichier
    ├── GAME_INSTRUCTIONS.md   # Instructions de jeu
    ├── CHANGELOG_FIX.md       # Journal des corrections
    ├── RESUME_AMELIORATIONS.md # Résumé des améliorations
    ├── VERIFICATION_TELECHARGEMENT.md # Guide de vérification
    ├── WINDOWS_DEFENDER_FIX.txt # Fix Windows Defender
    ├── WINDOWS_DEFENDER_GUIDE.md # Guide Windows Defender
    └── LIRE_MOI_IMPORTANT.txt # Notes importantes
```

---

## 🎯 Détails par Composant

### 🌐 Site Web (Frontend)

#### **index.html**
- **Rôle** : Page d'accueil principale du site
- **Contenu** :
  - Section Hero avec titre animé "PONG FORCE"
  - Présentation des fonctionnalités
  - Showcase de la mécanique Force Push
  - Section de téléchargement
  - Footer avec liens sociaux
- **Dépendances** : `css/style.css`, `css/responsive.css`, `js/main.js`, `js/particles.js`

#### **demo.html**
- **Rôle** : Page de démo jouable dans le navigateur
- **Contenu** :
  - Canvas HTML5 pour le jeu
  - Contrôles clavier (flèches, W/S, Espace/Shift)
  - Score en temps réel
- **Dépendances** : `js/demo.js`, `css/style.css`

#### **css/style.css**
- **Rôle** : Styles principaux du site
- **Thème** : Néon arcade futuriste
- **Couleurs** :
  - Fond : `#0B0C10`
  - Néon Bleu : `#00FFFF`
  - Néon Rose : `#FF00CC`
  - Accent Jaune : `#FFD700`
- **Effets** : Glow, animations, transitions

#### **css/responsive.css**
- **Rôle** : Adaptation mobile/tablette
- **Breakpoints** : Desktop, tablette, mobile
- **Fonctionnalités** : Navigation hamburger, grilles adaptatives

#### **js/main.js**
- **Rôle** : Logique principale du site
- **Fonctionnalités** :
  - Animations au scroll
  - Gestion des événements
  - Navigation fluide
  - Interactions des boutons

#### **js/demo.js**
- **Rôle** : Implémentation du jeu de démo
- **Technologie** : Canvas HTML5
- **Mécaniques** :
  - Mouvement des raquettes
  - Physique de la balle
  - Force Push (boost de vitesse)
  - Système de score

#### **js/particles.js**
- **Rôle** : Effets de particules animées
- **Fonctionnalités** : Particules flottantes en arrière-plan

---

### 🎮 Jeu Pong Force (Backend/Application)

#### **pong_force/main.py**
- **Rôle** : Point d'entrée principal du jeu
- **Fonctionnalités** :
  - Initialisation Pygame
  - Gestion du menu
  - Lancement des modes de jeu (local, réseau)
  - Extraction de payload depuis image (LSB steganography)
  - Gestion des arguments en ligne de commande

#### **pong_force/build.py**
- **Rôle** : Script de compilation PyInstaller
- **Fonctionnalités** :
  - Vérification des dépendances
  - Configuration PyInstaller
  - Compilation en `.exe`
  - Copie vers `assets/PongForceSetup.exe`
  - Compression UPX (optionnelle)

#### **pong_force/config.py**
- **Rôle** : Configuration centralisée
- **Contenu** :
  - Paramètres de jeu (vitesse, taille, etc.)
  - Configuration réseau
  - Chemins de fichiers

#### **pong_force/game/ball.py**
- **Rôle** : Logique de la balle
- **Fonctionnalités** :
  - Mouvement et collision
  - Physique de rebond
  - Gestion de la vitesse

#### **pong_force/game/paddle.py**
- **Rôle** : Logique des raquettes
- **Fonctionnalités** :
  - Mouvement des joueurs
  - Détection de collision avec la balle
  - Effets visuels (glow)

#### **pong_force/game/power.py**
- **Rôle** : Système Force Push
- **Fonctionnalités** :
  - Activation du boost
  - Gestion du cooldown
  - Effets sur la balle

#### **pong_force/game/scoreboard.py**
- **Rôle** : Affichage et gestion du score
- **Fonctionnalités** :
  - Comptage des points
  - Affichage graphique
  - Détection de victoire

#### **pong_force/game/effects.py**
- **Rôle** : Effets visuels
- **Fonctionnalités** :
  - Trails de la balle
  - Particules
  - Effets de glow

#### **pong_force/game/game_loop.py**
- **Rôle** : Boucle principale du jeu
- **Fonctionnalités** :
  - Gestion du temps (FPS)
  - Mise à jour des entités
  - Rendu graphique
  - Gestion des événements

#### **pong_force/game/menu.py**
- **Rôle** : Menu graphique interactif
- **Fonctionnalités** :
  - Interface utilisateur Pygame
  - Sélection des modes de jeu
  - Navigation au clavier/souris

#### **pong_force/network/server.py**
- **Rôle** : Serveur de jeu réseau
- **Fonctionnalités** :
  - Écoute des connexions
  - Synchronisation des joueurs
  - Gestion de la partie multijoueur

#### **pong_force/network/client.py**
- **Rôle** : Client de jeu réseau
- **Fonctionnalités** :
  - Connexion au serveur
  - Envoi/réception des données
  - Synchronisation de l'état du jeu

---

## 🔄 Flux de Données

### Site Web
```
Utilisateur → index.html → main.js → API/Events
                ↓
            demo.html → demo.js → Canvas API
```

### Jeu
```
main.py → menu.py → game_loop.py
                    ↓
            ball.py, paddle.py, power.py, scoreboard.py
                    ↓
            network/ (si multijoueur)
```

### Build
```
build.py → PyInstaller → PongForce.exe → assets/PongForceSetup.exe
```

---

## 📦 Dépendances

### Site Web
- **Aucune dépendance externe** (HTML5, CSS3, JavaScript vanilla)
- **Polices** : Google Fonts (Orbitron)

### Jeu Python
- **pygame** >= 2.1.0 : Moteur de jeu
- **pyinstaller** >= 5.0.0 : Compilation en exécutable
- **cryptography** : Chiffrement (Fernet)
- **Pillow** : Traitement d'images (LSB steganography)

---

## 🛠️ Scripts Utilitaires

### **build.bat**
- Lance `build.py` pour compiler le jeu
- Windows uniquement

### **deploy.bat**
- Script de déploiement du site
- Peut inclure upload vers serveur

### **test_download.py**
- Tests automatisés
- Vérifie l'existence des fichiers
- Valide les liens de téléchargement

### **fix_windows_defender.py**
- Solutions pour éviter les faux positifs Windows Defender
- Génération de certificats

---

## 📊 Organisation des Assets

### **assets/** (Site Web)
- Images du site
- Sons (optionnels)
- Vidéos (optionnels)

### **pong_force/assets/** (Jeu)
- Images du jeu (splash, icônes)
- Polices personnalisées
- Sons du jeu
- Fichiers de configuration

---

## 🎯 Points d'Entrée

1. **Site Web** : `index.html` (ouvrir dans navigateur)
2. **Démo** : `demo.html` (ouvrir dans navigateur)
3. **Jeu Local** : `pong_force/main.py` (Python) ou `PongForce.exe` (compilé)
4. **Build** : `pong_force/build.py` ou `pong_force/build.bat`

---

## 🔐 Sécurité et Build

### Fichiers de Build
- **PongForce.spec** : Configuration PyInstaller
- **version_info.txt** : Métadonnées Windows (version, auteur, etc.)
- **upx.exe** : Compresseur optionnel pour réduire la taille

### Protection
- **encryptor.py** : Utilitaires de chiffrement
- **payload.py** : Gestion de payload (steganography LSB)

---

## 📝 Notes Importantes

1. **Fichiers temporaires** :
   - `__pycache__/` : Cache Python (peut être ignoré)
   - `build/` : Artéfacts de compilation (peut être nettoyé)

2. **Fichiers de test** :
   - `test.html`, `test_download.html`, `integration_test.html`
   - `test_download.py`, `test_game.py`

3. **Documentation** :
   - Tous les fichiers `.md` contiennent de la documentation
   - `LIRE_MOI_IMPORTANT.txt` : Notes critiques

4. **Placeholders** :
   - Certains dossiers contiennent `placeholder.txt` (à remplacer par de vrais assets)

---

## 🚀 Déploiement

### Structure pour Déploiement
```
Pour GitHub Pages / Vercel / Netlify :
- index.html
- demo.html
- css/
- js/
- assets/ (incluant PongForceSetup.exe)
```

### Fichiers à Exclure
- `pong_force/` (code source, pas nécessaire pour le site)
- `__pycache__/`
- `*.py` (sauf si nécessaire)
- Fichiers de test

---

## 📈 Évolution Future

### Structure Proposée
- Séparation claire site/jeu
- Assets partagés centralisés
- Tests automatisés dans `tests/`
- Documentation dans `docs/`

---

**Dernière mise à jour** : 2024
**Version** : 1.0.0

