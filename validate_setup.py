#!/usr/bin/env python3
"""Script de validation de l'installation AES Drive Decryptor."""

import sys
import importlib.util
from pathlib import Path


def check_python_version():
    """Vérifier la version de Python."""
    print("🐍 Vérification de la version Python...")
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ requis, version actuelle: {sys.version}")
        return False
    else:
        print(f"✅ Python {sys.version.split()[0]} - OK")
        return True


def check_required_modules():
    """Vérifier que les modules requis sont installés."""
    print("\n📦 Vérification des modules requis...")
    
    required_modules = [
        ('cryptography', 'Bibliothèque cryptographique'),
        ('colorama', 'Support des couleurs terminal'),
    ]
    
    all_ok = True
    for module_name, description in required_modules:
        try:
            importlib.import_module(module_name)
            print(f"✅ {module_name} - {description}")
        except ImportError:
            print(f"❌ {module_name} - {description} (MANQUANT)")
            all_ok = False
    
    return all_ok


def check_project_structure():
    """Vérifier la structure du projet."""
    print("\n📁 Vérification de la structure du projet...")
    
    required_files = [
        ('aesdecryptor.py', 'Script principal'),
        ('requirements.txt', 'Fichier des dépendances'),
        ('res/__init__.py', 'Package res'),
        ('res/aesdatafile.py', 'Module DataFile'),
        ('res/fnhelper.py', 'Fonctions utilitaires'),
        ('README.md', 'Documentation'),
    ]
    
    all_ok = True
    for file_path, description in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} - {description}")
        else:
            print(f"❌ {file_path} - {description} (MANQUANT)")
            all_ok = False
    
    return all_ok


def check_imports():
    """Vérifier que les imports du projet fonctionnent."""
    print("\n🔗 Vérification des imports du projet...")
    
    try:
        # Test import du module principal
        import aesdecryptor
        print("✅ Module principal aesdecryptor")
        
        # Test import des modules res
        from res import DataFile, check_arguments, print_parameter
        print("✅ Modules res (DataFile, check_arguments, print_parameter)")
        
        # Test création d'une instance
        decryptor = aesdecryptor.AESDecryptor()
        print("✅ Création d'instance AESDecryptor")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'import: {e}")
        return False


def check_functionality():
    """Tester la fonctionnalité de base."""
    print("\n⚙️ Test de fonctionnalité de base...")
    
    try:
        from res import check_arguments
        
        # Test avec arguments d'aide
        result = check_arguments(['script.py', '--help'])
        if result is None:
            print("✅ Fonction check_arguments (aide)")
        else:
            print("⚠️ Fonction check_arguments - comportement inattendu")
        
        # Test avec arguments normaux
        result = check_arguments(['script.py', 'test.aesd', '-p', 'password'])
        if result and result.get('file') == 'test.aesd' and result.get('pwd') == 'password':
            print("✅ Analyse des arguments")
        else:
            print("⚠️ Analyse des arguments - résultat inattendu")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur de test de fonctionnalité: {e}")
        return False


def main():
    """Fonction principale de validation."""
    print("🔍 Validation de l'Installation AES Drive Decryptor")
    print("=" * 60)
    
    checks = [
        check_python_version,
        check_required_modules,
        check_project_structure,
        check_imports,
        check_functionality,
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        if check():
            passed += 1
        print()  # Ligne vide entre les sections
    
    print("=" * 60)
    print(f"📊 Résultat: {passed}/{total} vérifications réussies")
    
    if passed == total:
        print("🎉 Installation validée avec succès!")
        print("\n📋 Prochaines étapes:")
        print("   1. Activez l'environnement virtuel si ce n'est pas fait")
        print("   2. Utilisez: python aesdecryptor.py [fichier.aesd] [options]")
        print("   3. Consultez USAGE.md pour plus d'exemples")
        return 0
    else:
        print("⚠️ Problèmes détectés dans l'installation.")
        print("\n🔧 Actions recommandées:")
        if passed < 2:
            print("   1. Vérifiez que Python 3.8+ est installé")
            print("   2. Exécutez: pip install -r requirements.txt")
        print("   3. Consultez README.md pour l'installation complète")
        return 1


if __name__ == "__main__":
    sys.exit(main())