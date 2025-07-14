#!/usr/bin/env python3
"""Script de vérification des liens de navigation dans la documentation."""

import os
import re
from pathlib import Path


def check_file_exists(filepath):
    """Vérifier si un fichier existe."""
    return Path(filepath).exists()


def extract_markdown_links(content):
    """Extraire tous les liens Markdown d'un contenu."""
    # Pattern pour les liens Markdown [texte](lien)
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    return re.findall(pattern, content)


def check_navigation_in_file(filepath):
    """Vérifier la navigation dans un fichier spécifique."""
    print(f"\n🔍 Vérification de {filepath}")
    
    if not check_file_exists(filepath):
        print(f"❌ Fichier {filepath} introuvable")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier la présence de la barre de navigation
    has_navigation = "📖 **Navigation :**" in content
    if has_navigation:
        print("✅ Barre de navigation présente")
    else:
        print("⚠️ Barre de navigation manquante")
    
    # Extraire et vérifier les liens
    links = extract_markdown_links(content)
    broken_links = []
    
    for text, link in links:
        # Ignorer les liens externes (http/https)
        if link.startswith(('http://', 'https://')):
            continue
            
        # Ignorer les ancres (#)
        if link.startswith('#'):
            continue
            
        # Vérifier si le fichier lié existe
        if not check_file_exists(link):
            broken_links.append((text, link))
    
    if broken_links:
        print(f"❌ {len(broken_links)} lien(s) cassé(s):")
        for text, link in broken_links:
            print(f"   • [{text}]({link})")
        return False
    else:
        print(f"✅ Tous les {len([l for l in links if not l[1].startswith(('http', '#'))])} liens internes fonctionnent")
        return True


def main():
    """Fonction principale."""
    print("🔗 Vérification de la Navigation de la Documentation")
    print("=" * 60)
    
    # Fichiers à vérifier
    files_to_check = [
        'README.md',
        'docs/USAGE.md', 
        'docs/SECURITY.md',
        'TOC.md'
    ]
    
    all_good = True
    
    for filepath in files_to_check:
        if not check_navigation_in_file(filepath):
            all_good = False
    
    print("\n" + "=" * 60)
    
    if all_good:
        print("🎉 Toute la navigation fonctionne correctement!")
        print("\n📋 Résumé de la navigation:")
        print("   • README.md - Point d'entrée avec navigation complète")
        print("   • docs/USAGE.md - Guide avec liens contextuels")
        print("   • docs/SECURITY.md - Sécurité avec liens vers autres docs")
        print("   • TOC.md - Table des matières technique")
        return 0
    else:
        print("⚠️ Problèmes de navigation détectés!")
        print("Vérifiez les liens cassés ci-dessus.")
        return 1


if __name__ == "__main__":
    exit(main())