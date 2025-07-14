#!/usr/bin/env python3
"""Script de test pour vérifier la configuration du projet AES Drive Decryptor."""

import sys
import importlib
from pathlib import Path

def test_imports():
    """Tester les imports des modules."""
    print("🧪 Test des imports des modules...")
    
    try:
        # Test des imports standard
        import os
        import hashlib
        import getpass
        import time
        print("  ✅ Modules standard importés avec succès")
        
        # Test des imports cryptographiques
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.exceptions import InvalidTag
        print("  ✅ Modules cryptographiques importés avec succès")
        
        # Test de colorama
        from colorama import Fore, init
        print("  ✅ Colorama importé avec succès")
        
        # Test des modules locaux
        from res import DataFile, check_arguments, print_parameter, print_data_file_info
        print("  ✅ Modules locaux importés avec succès")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Erreur d'import: {e}")
        return False

def test_module_functionality():
    """Tester la fonctionnalité de base des modules."""
    print("\n🧪 Test de la fonctionnalité des modules...")
    
    try:
        # Test de check_arguments
        from res import check_arguments
        test_args = ['script.py', '--help']
        result = check_arguments(test_args)
        # Devrait retourner None car --help a été demandé
        if result is None:
            print("  ✅ Fonction check_arguments fonctionne")
        else:
            print("  ⚠️ Fonction check_arguments: comportement inattendu")
        
        # Test de DataFile avec des données factices
        from res import DataFile
        # Créer un en-tête factice de 144 octets
        fake_header = b'AESD' + b'\x01' + b'\x00' * 139
        try:
            # Cela devrait échouer à cause du CRC32, mais teste la structure
            data_file = DataFile(fake_header)
        except SystemExit:
            print("  ✅ Classe DataFile fonctionne (validation CRC32 active)")
        except Exception as e:
            print(f"  ⚠️ Classe DataFile: {e}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur de test de fonctionnalité: {e}")
        return False

def test_main_module():
    """Tester le module principal."""
    print("\n🧪 Test du module principal...")
    
    try:
        # Importer le module principal sans l'exécuter
        import aesdecryptor
        
        # Vérifier que la classe AESDecryptor existe
        if hasattr(aesdecryptor, 'AESDecryptor'):
            print("  ✅ Classe AESDecryptor trouvée")
            
            # Créer une instance
            decryptor = aesdecryptor.AESDecryptor()
            print("  ✅ Instance AESDecryptor créée avec succès")
            
            return True
        else:
            print("  ❌ Classe AESDecryptor non trouvée")
            return False
            
    except Exception as e:
        print(f"  ❌ Erreur de test du module principal: {e}")
        return False

def test_file_structure():
    """Tester la structure des fichiers."""
    print("\n🧪 Test de la structure des fichiers...")
    
    required_files = [
        'aesdecryptor.py',
        'requirements.txt',
        'res/__init__.py',
        'res/aesdatafile.py',
        'res/fnhelper.py',
        'README.md'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if not missing_files:
        print("  ✅ Tous les fichiers requis sont présents")
        return True
    else:
        print(f"  ❌ Fichiers manquants: {missing_files}")
        return False

def main():
    """Fonction principale de test."""
    print("🚀 Test de configuration du projet AES Drive Decryptor")
    print("=" * 60)
    
    tests = [
        test_file_structure,
        test_imports,
        test_module_functionality,
        test_main_module
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Résultats: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés! Le projet est correctement configuré.")
        return 0
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez la configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())