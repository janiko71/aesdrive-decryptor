@echo off
echo 🚀 Configuration de l'environnement virtuel AES Drive Decryptor
echo.

REM Créer l'environnement virtuel
echo 📦 Création de l'environnement virtuel...
python -m venv venv
if %errorlevel% neq 0 (
    echo ❌ Erreur lors de la création de l'environnement virtuel
    pause
    exit /b 1
)

REM Activer l'environnement virtuel et installer les dépendances
echo 📥 Installation des dépendances...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ Erreur lors de l'installation des dépendances
    pause
    exit /b 1
)

echo.
echo ✅ Configuration terminée avec succès!
echo.
echo 📋 Prochaines étapes:
echo    1. Activez l'environnement virtuel: venv\Scripts\activate.bat
echo    2. Lancez le décrypteur: python aesdecryptor.py [fichier] [options]
echo.
echo 💡 Pour désactiver l'environnement virtuel plus tard: deactivate
echo.
pause