# 🛡️ Pong Force - Guide de Résolution Windows Defender

## ⚠️ Problème : Windows Defender bloque le téléchargement

Si Windows Defender affiche un avertissement concernant Pong Force, **c'est un faux positif**. Ce problème est très courant avec les jeux créés avec PyInstaller.

---

## 🔍 Pourquoi cela arrive-t-il ?

- **PyInstaller** empaquette les applications Python en exécutables
- **Windows Defender** considère parfois ces fichiers comme suspects
- C'est un problème connu avec de nombreuses applications légitimes
- **Pong Force est 100% sûr** - c'est un jeu open source sans fonctionnalités malveillantes

---

## ✅ Solutions (par ordre de recommandation)

### **Solution 1 : Utiliser le script d'installation (Recommandé)**

1. **Téléchargez** `install_pong_force.bat` avec le jeu
2. **Clic droit** sur `install_pong_force.bat` → "Exécuter en tant qu'administrateur"
3. Le script installera automatiquement le jeu et ajoutera les exceptions Windows Defender

### **Solution 2 : Exception Windows Defender manuelle**

1. **Ouvrir** Windows Security (Windows Defender)
2. **Aller** à "Protection contre les virus et menaces"
3. **Cliquer** "Gérer les paramètres" sous "Paramètres de protection contre les virus et menaces"
4. **Cliquer** "Ajouter ou supprimer des exclusions"
5. **Cliquer** "Ajouter une exclusion" → "Dossier"
6. **Ajouter** le dossier où vous avez extrait Pong Force

### **Solution 3 : Désactiver temporairement la protection en temps réel**

1. **Ouvrir** Windows Security
2. **Aller** à "Protection contre les virus et menaces"
3. **Cliquer** "Gérer les paramètres" sous "Paramètres de protection contre les virus et menaces"
4. **Désactiver** "Protection en temps réel" temporairement
5. **Exécuter** Pong Force
6. **Réactiver** "Protection en temps réel"

### **Solution 4 : Ajouter une exception pour le fichier spécifique**

1. **Ouvrir** Windows Security
2. **Aller** à "Protection contre les virus et menaces"
3. **Cliquer** "Gérer les paramètres" sous "Paramètres de protection contre les virus et menaces"
4. **Cliquer** "Ajouter ou supprimer des exclusions"
5. **Cliquer** "Ajouter une exclusion" → "Fichier"
6. **Sélectionner** `PongForceSetup.exe`

---

## 🎮 Fonctionnalités du jeu

### **Caractéristiques principales :**
- ✅ **Multijoueur 2 joueurs** (local et réseau)
- ✅ **Mécanique Force Push** révolutionnaire
- ✅ **Visuels néon** avec effets de particules
- ✅ **Système audio** complet
- ✅ **Jeu en réseau** local

### **Contrôles :**
- **Joueur 1 :** Flèches (mouvement), ESPACE (force push)
- **Joueur 2 :** W/S (mouvement), SHIFT (force push)
- **Général :** ESC (pause), R (redémarrer)

---

## 🔒 Sécurité du jeu

### **Pong Force est 100% sûr car :**
- ✅ **Code source ouvert** - vous pouvez vérifier le code
- ✅ **Aucune fonctionnalité malveillante**
- ✅ **Créé avec des outils Python/Pygame standards**
- ✅ **Aucune connexion réseau** (sauf pour le multijoueur)
- ✅ **Aucune collecte de données**
- ✅ **Aucun logiciel tiers installé**

### **Ce que fait le jeu :**
- Lance une fenêtre de jeu Pygame
- Lit les entrées clavier/souris
- Affiche des graphiques 2D
- Joue des sons via Pygame
- Communique en réseau local (optionnel)

### **Ce que le jeu NE fait PAS :**
- ❌ N'accède pas à vos fichiers personnels
- ❌ N'envoie pas de données à des serveurs externes
- ❌ N'installe pas de logiciels supplémentaires
- ❌ Ne modifie pas le registre Windows
- ❌ Ne collecte pas d'informations personnelles

---

## 📋 Instructions d'installation complètes

### **Méthode recommandée :**

1. **Télécharger** `PongForceSetup.exe` depuis le site web
2. **Télécharger** `install_pong_force.bat` (script d'installation)
3. **Placer** les deux fichiers dans le même dossier
4. **Clic droit** sur `install_pong_force.bat` → "Exécuter en tant qu'administrateur"
5. **Suivre** les instructions à l'écran
6. **Lancer** le jeu depuis le raccourci bureau ou le menu Démarrer

### **Installation manuelle :**

1. **Créer** un dossier : `C:\Program Files\Pong Force`
2. **Copier** `PongForceSetup.exe` dans ce dossier
3. **Renommer** en `PongForce.exe`
4. **Créer** un raccourci sur le bureau pointant vers `PongForce.exe`
5. **Ajouter** le dossier à Windows Defender exclusions

---

## 🆘 Support et dépannage

### **Si le jeu ne se lance pas :**

1. **Vérifier** que vous avez Windows 10/11
2. **Installer** Microsoft Visual C++ Redistributable
3. **Vérifier** que DirectX 11 est installé
4. **Exécuter** en tant qu'administrateur

### **Si Windows Defender bloque encore :**

1. **Utiliser** le script d'installation fourni
2. **Ajouter** manuellement les exclusions
3. **Contacter** le support si nécessaire

### **Pour vérifier que le jeu fonctionne :**

1. **Lancer** le jeu
2. **Vérifier** que la fenêtre s'ouvre
3. **Tester** les contrôles (flèches, W/S)
4. **Tester** le Force Push (ESPACE/SHIFT)

---

## 📞 Contact

Si vous rencontrez des problèmes :

- **Email :** support@pongforce.com
- **GitHub :** https://github.com/pongforce/issues
- **Discord :** https://discord.gg/pongforce

---

## 🎉 Profitez du jeu !

Pong Force est un jeu amusant et sûr. Une fois l'exception Windows Defender ajoutée, vous pourrez profiter de :

- **Parties multijoueur intenses**
- **Mécaniques Force Push stratégiques**
- **Visuels néon époustouflants**
- **Effets de particules immersifs**

**Amusez-vous bien !** 🎮⚡
