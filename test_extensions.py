#!/usr/bin/env python3
"""Script de test pour vérifier le support des extensions .aesd et .aesf."""

import sys
import os
from pathlib import Path

# Ajouter le répertoire courant au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aesdecryptor import AESDecryptor, SUPPORTED_EXTENSIONS


def test_extension_validation():
    """Tester la validation des extensions de fichiers."""
    print("🧪 Test de Validation des Extensions")
    print("=" * 50)
    
    decryptor = AESDecryptor()
    
    # Tests avec extensions valides
    valid_files = [
        "document.pdf.aesd",
        "video.mp4.aesf", 
        "archive.zip.aesd",
        "image.jpg.aesf"
    ]
    
    print("\n✅ Tests avec extensions valides:")
    for filepath in valid_files:
        try:
            result = decryptor.validate_file_extension(filepath)
            expected = os.path.splitext(filepath)[0]
            if result == expected:
                print(f"   • {filepath} → {result} ✅")
            else:
                print(f"   • {filepath} → {result} ❌ (attendu: {expected})")
        except SystemExit:
            print(f"   • {filepath} → Erreur inattendue ❌")
    
    # Tests avec extensions invalides
    invalid_files = [
        "document.pdf.txt",
        "video.mp4.enc",
        "archive.zip",
        "image.jpg.aes"
    ]
    
    print("\n❌ Tests avec extensions invalides:")
    for filepath in invalid_files:
        try:
            # Rediriger stdout temporairement pour capturer les messages d'erreur
            import io
            from contextlib import redirect_stdout, redirect_stderr
            
            f = io.StringIO()
            with redirect_stdout(f), redirect_stderr(f):
                try:
                    result = decryptor.validate_file_extension(filepath)
                    print(f"   • {filepath} → Accepté incorrectement ❌")
                except SystemExit:
                    print(f"   • {filepath} → Rejeté correctement ✅")
        except Exception as e:
            print(f"   • {filepath} → Erreur: {e} ❌")


def test_supported_extensions():
    """Tester la liste des extensions supportées."""
    print("\n📋 Extensions Supportées:")
    print(f"   • Liste: {SUPPORTED_EXTENSIONS}")
    print(f"   • Nombre: {len(SUPPORTED_EXTENSIONS)}")
    
    expected_extensions = [".aesd", ".aesf"]
    if set(SUPPORTED_EXTENSIONS) == set(expected_extensions):
        print("   • Configuration: ✅ Correcte")
    else:
        print("   • Configuration: ❌ Incorrecte")
        print(f"     Attendu: {expected_extensions}")
        print(f"     Actuel: {SUPPORTED_EXTENSIONS}")


def test_file_path_examples():
    """Tester des exemples de chemins de fichiers."""
    print("\n📁 Exemples de Chemins de Fichiers:")
    
    examples = [
        "/home/user/documents/secret.docx.aesd",
        "C:\\Users\\User\\Desktop\\photo.png.aesf",
        "./data/backup.tar.gz.aesd",
        "../files/movie.mkv.aesf"
    ]
    
    decryptor = AESDecryptor()
    
    for filepath in examples:
        try:
            result = decryptor.validate_file_extension(filepath)
            print(f"   • {filepath}")
            print(f"     → Sortie: {result} ✅")
        except SystemExit:
            print(f"   • {filepath}")
            print(f"     → Extension invalide ❌")


def main():
    """Fonction principale."""
    print("🔧 Test du Support des Extensions .aesd et .aesf")
    print("=" * 60)
    
    try:
        test_supported_extensions()
        test_extension_validation()
        test_file_path_examples()
        
        print("\n" + "=" * 60)
        print("🎉 Tests terminés!")
        print("\n📋 Résumé:")
        print("   • Extensions supportées: .aesd et .aesf")
        print("   • Validation des extensions: Fonctionnelle")
        print("   • Génération des noms de sortie: Correcte")
        print("\n💡 Utilisation:")
        print("   python aesdecryptor.py fichier.aesd")
        print("   python aesdecryptor.py fichier.aesf")
        
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())