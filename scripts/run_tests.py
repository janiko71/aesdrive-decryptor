#!/usr/bin/env python3
"""Script pour exécuter tous les tests du projet."""

import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Exécute une commande et affiche le résultat."""
    print(f"\n🔧 {description}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCÈS")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ {description} - ÉCHEC")
            if result.stderr:
                print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ {description} - ERREUR: {e}")
        return False
    
    return True

def main():
    """Point d'entrée principal."""
    print("🧪 Tests du Projet AES Drive Decryptor")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent
    
    tests = [
        ("python tests/test_extensions.py", "Test des extensions"),
        ("python tests/test_setup.py", "Test de configuration"),
        ("python -m aesdrive_decryptor --help", "Test interface moderne"),
        ("python aesdecryptor.py --help", "Test script de compatibilité"),
    ]
    
    success_count = 0
    total_tests = len(tests)
    
    for cmd, description in tests:
        if run_command(cmd, description):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Résultats: {success_count}/{total_tests} tests réussis")
    
    if success_count == total_tests:
        print("🎉 Tous les tests sont passés avec succès !")
        return 0
    else:
        print("⚠️ Certains tests ont échoué.")
        return 1

if __name__ == "__main__":
    sys.exit(main())