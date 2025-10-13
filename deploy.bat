@echo off
echo ========================================
echo   Pong Force - Deployment Script
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "index.html" (
    echo ERROR: index.html not found!
    echo Please run this script from the website root directory.
    pause
    exit /b 1
)

if not exist "assets\PongForceSetup.exe" (
    echo ERROR: PongForceSetup.exe not found in assets!
    echo Please build the game executable first.
    pause
    exit /b 1
)

echo Checking file sizes...
for %%F in (assets\PongForceSetup.exe) do (
    set /a size=%%~zF/1024/1024
    echo Game executable: !size! MB
)

echo.
echo ========================================
echo   DEPLOYMENT OPTIONS
echo ========================================
echo.
echo Choose your deployment method:
echo.
echo 1. GitHub Pages (Recommended)
echo    - Free hosting
echo    - Custom domain support
echo    - Automatic HTTPS
echo.
echo 2. Vercel
echo    - Fast global CDN
echo    - Automatic deployments
echo    - Great for static sites
echo.
echo 3. Netlify
echo    - Drag-and-drop deployment
echo    - Form handling
echo    - Branch-based deployments
echo.
echo 4. Local Testing
echo    - Test on your machine
echo    - Verify everything works
echo.
echo 5. Manual Upload
echo    - Upload to any web host
echo    - Traditional FTP/SFTP
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto github
if "%choice%"=="2" goto vercel
if "%choice%"=="3" goto netlify
if "%choice%"=="4" goto local
if "%choice%"=="5" goto manual
goto invalid

:github
echo.
echo ========================================
echo   GitHub Pages Deployment
echo ========================================
echo.
echo Steps to deploy on GitHub Pages:
echo.
echo 1. Create a new repository on GitHub
echo 2. Upload all files to the repository
echo 3. Go to Settings ^> Pages
echo 4. Select "Deploy from a branch"
echo 5. Choose "main" branch
echo 6. Save settings
echo.
echo Your site will be available at:
echo https://[username].github.io/[repository-name]
echo.
echo Opening GitHub in browser...
start https://github.com/new
goto end

:vercel
echo.
echo ========================================
echo   Vercel Deployment
echo ========================================
echo.
echo Installing Vercel CLI...
npm install -g vercel
echo.
echo Deploying to Vercel...
vercel
echo.
echo Your site will be available at the URL provided by Vercel.
goto end

:netlify
echo.
echo ========================================
echo   Netlify Deployment
echo ========================================
echo.
echo Steps to deploy on Netlify:
echo.
echo 1. Go to https://netlify.com
echo 2. Sign up or log in
echo 3. Drag and drop this entire folder
echo 4. Wait for deployment to complete
echo.
echo Opening Netlify in browser...
start https://netlify.com
goto end

:local
echo.
echo ========================================
echo   Local Testing
echo ========================================
echo.
echo Starting local server on port 8000...
echo.
echo Your site will be available at:
echo http://localhost:8000
echo.
echo Press Ctrl+C to stop the server.
echo.
python -m http.server 8000
goto end

:manual
echo.
echo ========================================
echo   Manual Upload Instructions
echo ========================================
echo.
echo Files to upload to your web host:
echo.
echo Required files:
echo - index.html
echo - demo.html
echo - assets\PongForceSetup.exe
echo - css\style.css
echo - css\responsive.css
echo - js\main.js
echo - js\demo.js
echo - js\particles.js
echo.
echo Optional files:
echo - assets\images\ (if you have custom images)
echo - assets\sounds\ (if you have custom sounds)
echo - assets\videos\ (if you have custom videos)
echo.
echo Make sure to maintain the folder structure!
echo.
echo Opening file explorer...
explorer .
goto end

:invalid
echo.
echo Invalid choice! Please run the script again and choose 1-5.
pause
exit /b 1

:end
echo.
echo ========================================
echo   Deployment Complete!
echo ========================================
echo.
echo Your Pong Force website is ready!
echo.
echo Don't forget to:
echo - Test the download functionality
echo - Verify the game runs correctly
echo - Check mobile responsiveness
echo - Share with friends!
echo.
pause
