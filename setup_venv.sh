#!/bin/bash
echo "🚀 Configuration de l'environnement virtuel AES Drive Decryptor"
echo

# Créer l'environnement virtuel
echo "📦 Création de l'environnement virtuel..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de la création de l'environnement virtuel"
    exit 1
fi

# Activer l'environnement virtuel et installer les dépendances
echo "📥 Installation des dépendances..."
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de l'installation des dépendances"
    exit 1
fi

echo
echo "✅ Configuration terminée avec succès!"
echo
echo "📋 Prochaines étapes:"
echo "   1. Activez l'environnement virtuel: source venv/bin/activate"
echo "   2. Lancez le décrypteur: python aesdecryptor.py [fichier] [options]"
echo
echo "💡 Pour désactiver l'environnement virtuel plus tard: deactivate"
echo