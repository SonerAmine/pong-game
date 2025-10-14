# Script de Vérification du Téléchargement - Pong Force
# Ce script vérifie que le fichier téléchargeable est bien synchronisé avec la version source

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Vérification du Téléchargement" -ForegroundColor Cyan
Write-Host "  Pong Force - Official Website" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Chemins des fichiers
$sourceFile = "pong_force\dist\PongForce.exe"
$downloadFile = "assets\PongForceSetup.exe"

# Vérifier l'existence des fichiers
Write-Host "📁 Vérification des fichiers..." -ForegroundColor Yellow
Write-Host ""

if (-not (Test-Path $sourceFile)) {
    Write-Host "❌ ERREUR: Fichier source introuvable: $sourceFile" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $downloadFile)) {
    Write-Host "❌ ERREUR: Fichier de téléchargement introuvable: $downloadFile" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Fichier source trouvé: $sourceFile" -ForegroundColor Green
Write-Host "✅ Fichier de téléchargement trouvé: $downloadFile" -ForegroundColor Green
Write-Host ""

# Obtenir les informations des fichiers
$sourceInfo = Get-Item $sourceFile
$downloadInfo = Get-Item $downloadFile

# Afficher les informations
Write-Host "📊 Informations des fichiers:" -ForegroundColor Yellow
Write-Host ""

Write-Host "  SOURCE (pong_force\dist\PongForce.exe):" -ForegroundColor Cyan
Write-Host "    Taille: $($sourceInfo.Length) octets" -ForegroundColor White
Write-Host "    Date: $($sourceInfo.LastWriteTime)" -ForegroundColor White
Write-Host ""

Write-Host "  TÉLÉCHARGEMENT (assets\PongForceSetup.exe):" -ForegroundColor Cyan
Write-Host "    Taille: $($downloadInfo.Length) octets" -ForegroundColor White
Write-Host "    Date: $($downloadInfo.LastWriteTime)" -ForegroundColor White
Write-Host ""

# Calculer les hashes pour comparaison
Write-Host "🔐 Calcul des hashes SHA256..." -ForegroundColor Yellow
$sourceHash = (Get-FileHash $sourceFile -Algorithm SHA256).Hash
$downloadHash = (Get-FileHash $downloadFile -Algorithm SHA256).Hash

Write-Host "  Source:       $sourceHash" -ForegroundColor White
Write-Host "  Téléchargement: $downloadHash" -ForegroundColor White
Write-Host ""

# Comparaison finale
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RÉSULTAT DE LA VÉRIFICATION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($sourceHash -eq $downloadHash) {
    Write-Host "✅ SUCCÈS: Les fichiers sont IDENTIQUES!" -ForegroundColor Green
    Write-Host ""
    Write-Host "👍 Les utilisateurs téléchargeront la bonne version du jeu." -ForegroundColor Green
    Write-Host "📦 Fichier téléchargé: assets\PongForceSetup.exe" -ForegroundColor Green
    Write-Host ""
    
    # Vérifier les liens dans les fichiers HTML
    Write-Host "🔗 Vérification des liens HTML..." -ForegroundColor Yellow
    
    $indexContent = Get-Content "index.html" -Raw
    $demoContent = Get-Content "demo.html" -Raw
    
    $indexLinks = ([regex]::Matches($indexContent, 'href="([^"]*\.exe)"')).Count
    $demoLinks = ([regex]::Matches($demoContent, 'href="([^"]*\.exe)"')).Count
    
    Write-Host "  index.html: $indexLinks lien(s) de téléchargement" -ForegroundColor White
    Write-Host "  demo.html: $demoLinks lien(s) de téléchargement" -ForegroundColor White
    
    # Vérifier que tous les liens pointent vers le bon fichier
    $wrongLinks = [regex]::Matches($indexContent + $demoContent, 'href="(?!assets/PongForceSetup\.exe)([^"]*\.exe)"')
    
    if ($wrongLinks.Count -eq 0) {
        Write-Host ""
        Write-Host "✅ Tous les liens pointent vers assets/PongForceSetup.exe" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "⚠️ ATTENTION: Des liens pointent vers d'autres fichiers .exe!" -ForegroundColor Yellow
        foreach ($link in $wrongLinks) {
            Write-Host "  - $($link.Groups[1].Value)" -ForegroundColor Yellow
        }
    }
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✅ VÉRIFICATION RÉUSSIE" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    
    exit 0
} else {
    Write-Host "❌ ERREUR: Les fichiers sont DIFFÉRENTS!" -ForegroundColor Red
    Write-Host ""
    Write-Host "⚠️ Les utilisateurs téléchargeront une version OBSOLÈTE!" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 Solution: Exécutez cette commande pour synchroniser:" -ForegroundColor Yellow
    Write-Host "   Copy-Item `"$sourceFile`" -Destination `"$downloadFile`" -Force" -ForegroundColor White
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  ❌ VÉRIFICATION ÉCHOUÉE" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    
    exit 1
}













