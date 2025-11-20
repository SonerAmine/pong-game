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

