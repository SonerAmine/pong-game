#!/usr/bin/env python3
"""
Script pour créer une icône personnalisée pour Pong Force
basée sur l'image ping-pong fournie
"""

import pygame
import os
from pathlib import Path

def create_ping_pong_icon():
    """Créer une icône ping-pong personnalisée"""
    print("Creating custom ping-pong icon...")
    
    # Initialiser pygame
    pygame.init()
    
    # Créer une surface pour l'icône (32x32, 48x48, 64x64, 128x128, 256x256)
    sizes = [32, 48, 64, 128, 256]
    
    for size in sizes:
        # Créer la surface avec transparence
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Couleurs
        BLACK = (0, 0, 0, 255)
        RED = (220, 20, 60, 255)  # Rouge vif pour la raquette
        BROWN = (139, 69, 19, 255)  # Marron pour le manche
        WHITE = (255, 255, 255, 255)  # Blanc pour la balle
        BACKGROUND = (0, 0, 0, 0)  # Transparent
        
        # Remplir avec transparence
        surface.fill(BACKGROUND)
        
        # Calculer les proportions basées sur la taille
        scale = size / 64.0
        
        # Dessiner la raquette (forme ovale)
        paddle_width = int(20 * scale)
        paddle_height = int(30 * scale)
        paddle_x = int(size * 0.3)
        paddle_y = int(size * 0.2)
        
        # Dessiner la tête de la raquette (ovale rouge)
        pygame.draw.ellipse(surface, RED, 
                           (paddle_x, paddle_y, paddle_width, paddle_height))
        
        # Dessiner le contour noir de la raquette
        pygame.draw.ellipse(surface, BLACK, 
                           (paddle_x, paddle_y, paddle_width, paddle_height), 
                           max(1, int(2 * scale)))
        
        # Dessiner le manche (rectangle marron)
        handle_width = int(6 * scale)
        handle_height = int(15 * scale)
        handle_x = int(paddle_x + paddle_width * 0.3)
        handle_y = int(paddle_y + paddle_height * 0.7)
        
        pygame.draw.rect(surface, BROWN, 
                       (handle_x, handle_y, handle_width, handle_height))
        
        # Dessiner le contour noir du manche
        pygame.draw.rect(surface, BLACK, 
                       (handle_x, handle_y, handle_width, handle_height), 
                       max(1, int(2 * scale)))
        
        # Dessiner la balle (cercle blanc)
        ball_radius = int(4 * scale)
        ball_x = int(paddle_x + paddle_width * 0.8)
        ball_y = int(paddle_y + paddle_height * 0.3)
        
        pygame.draw.circle(surface, WHITE, (ball_x, ball_y), ball_radius)
        pygame.draw.circle(surface, BLACK, (ball_x, ball_y), ball_radius, 
                          max(1, int(2 * scale)))
        
        # Ajouter un effet de rebond (petite ligne)
        bounce_x1 = ball_x - ball_radius
        bounce_x2 = ball_x + ball_radius
        bounce_y = ball_y - int(3 * scale)
        pygame.draw.line(surface, BLACK, (bounce_x1, bounce_y), (bounce_x2, bounce_y), 
                        max(1, int(2 * scale)))
        
        # Sauvegarder l'icône
        icon_path = f"assets/images/icon_{size}x{size}.png"
        pygame.image.save(surface, icon_path)
        print(f"Created: {icon_path}")
    
    # Créer l'icône principale (64x64)
    main_icon = pygame.Surface((64, 64), pygame.SRCALPHA)
    main_icon.fill((0, 0, 0, 0))
    
    # Dessiner la raquette principale
    pygame.draw.ellipse(main_icon, RED, (20, 15, 25, 30))
    pygame.draw.ellipse(main_icon, BLACK, (20, 15, 25, 30), 2)
    
    # Dessiner le manche
    pygame.draw.rect(main_icon, BROWN, (27, 35, 6, 15))
    pygame.draw.rect(main_icon, BLACK, (27, 35, 6, 15), 2)
    
    # Dessiner la balle
    pygame.draw.circle(main_icon, WHITE, (40, 25), 4)
    pygame.draw.circle(main_icon, BLACK, (40, 25), 4, 2)
    
    # Sauvegarder l'icône principale
    pygame.image.save(main_icon, "assets/images/ping-pong.png")
    print("Created: assets/images/ping-pong.png")
    
    pygame.quit()
    return True

def create_ico_file():
    """Créer un fichier .ico pour Windows"""
    print("Creating Windows .ico file...")
    
    # Pour créer un fichier .ico, nous utiliserons PIL si disponible
    try:
        from PIL import Image
        
        # Charger l'image PNG principale
        img = Image.open("assets/images/ping-pong.png")
        
        # Créer différentes tailles pour l'ICO
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # Redimensionner l'image pour chaque taille
        icons = []
        for size in sizes:
            resized = img.resize(size, Image.Resampling.LANCZOS)
            icons.append(resized)
        
        # Sauvegarder comme fichier ICO
        icons[0].save("assets/images/icon.ico", format='ICO', sizes=[(icon.width, icon.height) for icon in icons])
        print("Created: assets/images/icon.ico")
        
        return True
        
    except ImportError:
        print("PIL not available. Installing...")
        import subprocess
        subprocess.run(["pip", "install", "Pillow"])
        
        # Réessayer
        try:
            from PIL import Image
            
            img = Image.open("assets/images/ping-pong.png")
            sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            
            icons = []
            for size in sizes:
                resized = img.resize(size, Image.Resampling.LANCZOS)
                icons.append(resized)
            
            icons[0].save("assets/images/icon.ico", format='ICO', sizes=[(icon.width, icon.height) for icon in icons])
            print("Created: assets/images/icon.ico")
            
            return True
            
        except Exception as e:
            print(f"Error creating ICO file: {e}")
            return False

def update_build_script():
    """Mettre à jour le script de build pour utiliser la nouvelle icône"""
    print("Updating build script to use new icon...")
    
    build_script_path = "pong_force/build.py"
    
    if os.path.exists(build_script_path):
        with open(build_script_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Remplacer l'ancienne icône par la nouvelle
        content = content.replace(
            'icon_path = "assets/images/icon.ico"',
            'icon_path = "../assets/images/icon.ico"'
        )
        
        with open(build_script_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print("Build script updated to use new icon.")

def rebuild_executable():
    """Reconstruire l'exécutable avec la nouvelle icône"""
    print("Rebuilding executable with new icon...")
    
    # Aller dans le dossier pong_force
    os.chdir("pong_force")
    
    # Reconstruire l'exécutable
    import subprocess
    result = subprocess.run([
        "python", "-m", "PyInstaller", 
        "--onefile", 
        "--windowed", 
        "--name=PongForce", 
        "--add-data=assets;assets",
        "--icon=../assets/images/icon.ico",
        "main.py"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("Executable rebuilt successfully!")
        
        # Copier le nouvel exécutable
        import shutil
        shutil.copy("dist/PongForce.exe", "../assets/PongForceSetup.exe")
        print("New executable copied to assets/PongForceSetup.exe")
        
        return True
    else:
        print(f"Build failed: {result.stderr}")
        return False
    
    # Retourner au dossier parent
    os.chdir("..")

def main():
    """Fonction principale"""
    print("Pong Force - Custom Icon Creator")
    print("=" * 40)
    
    # Créer l'icône ping-pong
    if create_ping_pong_icon():
        print("Ping-pong icon created successfully!")
    
    # Créer le fichier ICO
    if create_ico_file():
        print("Windows ICO file created successfully!")
    
    # Mettre à jour le script de build
    update_build_script()
    
    # Reconstruire l'exécutable
    if rebuild_executable():
        print("Executable rebuilt with new icon!")
    
    print("\n" + "=" * 40)
    print("Custom Icon Setup Complete!")
    print("=" * 40)
    print("\nFiles created:")
    print("- assets/images/ping-pong.png (main icon)")
    print("- assets/images/icon.ico (Windows icon)")
    print("- assets/images/icon_*.png (various sizes)")
    print("- assets/PongForceSetup.exe (updated executable)")
    print("\nThe downloaded file will now have the ping-pong icon!")

if __name__ == "__main__":
    main()
