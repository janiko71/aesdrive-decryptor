#!/usr/bin/env python3
"""Script de compatibilité pour AES Drive Decryptor.

Ce script maintient la compatibilité avec l'ancienne interface tout en
utilisant la nouvelle structure de package.

Pour la nouvelle interface, utilisez:
    python -m aesdrive_decryptor [fichier] [options]

Auteur: Équipe AES Drive Decryptor
Licence: MIT
"""

import sys
from pathlib import Path

# Ajouter le répertoire src au path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Importer et exécuter le point d'entrée principal
from aesdrive_decryptor.main import main

if __name__ == "__main__":
    main()