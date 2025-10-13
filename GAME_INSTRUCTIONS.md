# 🎮 Pong Force - Instructions de Jeu

## ✅ Problème Résolu

**Problème:** Le jeu se lançait mais n'affichait aucune fenêtre (visible seulement dans le Task Manager)

**Cause:** Le jeu utilisait un menu console (`input()`) alors que la console était désactivée (`console=False`)

**Solution:** Création d'un menu graphique interactif avec Pygame

---

## 🚀 Comment Jouer

### Option 1: Télécharger depuis le site web
1. Visitez le site web Pong Force
2. Cliquez sur "Download Now"
3. Le fichier `PongForceSetup.exe` sera téléchargé
4. Double-cliquez sur le fichier pour lancer le jeu
5. **Un menu graphique apparaîtra** avec les options:
   - **Local Multiplayer** - Jouer à deux sur le même PC
   - **Host Game (Server)** - Héberger une partie en ligne
   - **Join Game (Client)** - Rejoindre une partie en ligne
   - **Exit** - Quitter

### Option 2: Lancer avec des arguments
Vous pouvez aussi lancer le jeu directement depuis la ligne de commande:

```bash
# Lancer directement en mode local (2 joueurs sur le même PC)
PongForce.exe --local

# Héberger un serveur
PongForce.exe --server

# Rejoindre un serveur
PongForce.exe --client --host 192.168.1.100

# Mode debug
PongForce.exe --debug
```

---

## 🎮 Contrôles

### Joueur 1 (Gauche - Bleu)
- **↑** (Flèche Haut) - Monter
- **↓** (Flèche Bas) - Descendre
- **ESPACE** - Force Push (boost de vitesse)

### Joueur 2 (Droite - Rose)
- **W** - Monter
- **S** - Descendre
- **SHIFT** - Force Push (boost de vitesse)

### Contrôles Généraux
- **ESC** - Pause / Reprendre
- **R** - Recommencer (après Game Over)

---

## 🎯 Règles du Jeu

1. **Objectif:** Marquer 10 points avant l'adversaire
2. **Force Push:** Utilisez votre pouvoir pour booster la vitesse de la balle
   - Temps de recharge: 10 secondes
   - Multiplicateur de vitesse: 2.5x
   - Timing crucial: utilisez-le au bon moment!
3. **Points:** Un point est marqué quand la balle passe le paddle adverse

---

## 🔧 Modes de Jeu

### 1. Local Multiplayer (Recommandé pour débuter)
- 2 joueurs sur le même ordinateur
- Pas besoin de connexion internet
- Idéal pour jouer entre amis

### 2. Host Game (Serveur)
- Hébergez une partie en ligne
- D'autres joueurs peuvent vous rejoindre
- Nécessite que le port 5555 soit ouvert

### 3. Join Game (Client)
- Rejoignez une partie hébergée par quelqu'un
- Entrez l'adresse IP du serveur
- Port par défaut: 5555

---

## 📋 Résolution des Problèmes

### Le jeu ne démarre pas
- ✅ Vérifiez que Windows Defender ne bloque pas le fichier
- ✅ Cliquez droit → Propriétés → Débloquer (si l'option existe)
- ✅ Lancez en tant qu'administrateur si nécessaire

### Le menu n'apparaît pas
- ✅ Assurez-vous que c'est bien la nouvelle version (avec menu graphique)
- ✅ Vérifiez que le fichier n'est pas corrompu
- ✅ Essayez de lancer avec `--local` pour aller directement au jeu

### Problème de performance
- Fermez les autres applications gourmandes
- Lancez avec `--debug` pour voir les FPS
- Le jeu cible 60 FPS

### Connexion réseau ne fonctionne pas
- Vérifiez que le firewall autorise le jeu
- Assurez-vous que le port 5555 est ouvert
- Utilisez l'IP locale (192.168.x.x) pour le LAN

---

## 📊 Configuration Système Requise

### Minimum
- OS: Windows 7 ou supérieur
- RAM: 256 MB
- Processeur: 1 GHz
- Stockage: 50 MB

### Recommandé
- OS: Windows 10/11
- RAM: 512 MB
- Processeur: 2 GHz
- Stockage: 100 MB

---

## 🎨 Fonctionnalités

- ✨ Design néon arcade futuriste
- 🎮 Mécanique Force Push unique
- 👥 Multijoueur local et en ligne
- 🔊 Effets visuels et particules
- 📊 Système de score
- ⚡ Physique de balle dynamique
- 🎯 Interface graphique intuitive

---

## 🆕 Nouveautés Version Actuelle

### Menu Graphique
- Navigation avec souris ou clavier
- Effets visuels glow animés
- Interface utilisateur moderne
- Plus besoin de console texte

### Améliorations
- Lancement immédiat du jeu
- Meilleure expérience utilisateur
- Interface cohérente avec le design du jeu
- Dialogue pour entrer l'IP du serveur

---

## 💡 Conseils

1. **Maîtrisez le Force Push:** Le timing est essentiel!
2. **Anticipez:** Regardez la trajectoire de la balle
3. **Positionnement:** Restez au centre pour réagir rapidement
4. **Force Push défensif:** Utilisez-le aussi pour sauver des situations difficiles
5. **Contrôle d'angle:** Frappez la balle avec différentes parties du paddle

---

## 📞 Support

Si vous rencontrez des problèmes:
1. Vérifiez ce guide de dépannage
2. Consultez les fichiers dans le dossier du jeu
3. Assurez-vous d'avoir la dernière version

---

## 🎉 Amusez-vous bien!

**Pong Force** - Smash. Push. Win.

© 2024 Pong Force Studios

