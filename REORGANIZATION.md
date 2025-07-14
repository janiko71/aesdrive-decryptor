# Réorganisation du Projet AES Drive Decryptor

## 🎯 Objectif
Réorganiser le projet pour respecter les structures classiques de projets Python et améliorer la maintenabilité.

## 📁 Nouvelle Structure

```
aesdrive-decryptor/
├── src/                     # Code source principal (nouvelle structure)
│   └── aesdrive_decryptor/  # Package principal
│       ├── __init__.py      # Interface du package
│       ├── __main__.py      # Point d'entrée pour -m
│       ├── main.py          # Point d'entrée principal
│       ├── decryptor.py     # Logique de déchiffrement
│       ├── constants.py     # Constantes
│       └── security.py     # Gestion mémoire sécurisée
├── tests/                   # Tests unitaires (réorganisés)
│   ├── __init__.py         # Initialisation des tests
│   ├── test_extensions.py   # Tests des extensions
│   └── test_setup.py        # Tests d'installation
├── scripts/                 # Scripts utilitaires (réorganisés)
│   ├── setup_venv.py        # Configuration environnement
│   ├── setup_venv.bat       # Script Windows
│   ├── setup_venv.sh        # Script Unix/Linux
│   ├── compare_directories.py # Utilitaire de comparaison
│   ├── dev.py              # Script de développement
│   └── run_tests.py        # Script de test global
├── docs/                    # Documentation (réorganisée)
│   ├── SECURITY.md         # Documentation sécurité
│   └── (autres docs...)    # Autres fichiers de documentation
├── res/                     # Modules utilitaires (legacy, conservé)
│   ├── __init__.py         # Initialisation du package
│   ├── aesdatafile.py      # Classe DataFile
│   └── fnhelper.py         # Fonctions d'aide
├── aesdecryptor.py          # Script de compatibilité (nouveau)
├── requirements.txt         # Dépendances de production
├── requirements-dev.txt     # Dépendances de développement
├── setup.py                 # Configuration d'installation (mis à jour)
├── MANIFEST.in             # Configuration des fichiers à inclure
├── pytest.ini             # Configuration des tests
└── README.md               # Documentation principale (mise à jour)
```

## 🔄 Changements Effectués

### 1. Structure du Code Source
- **Avant**: Code dans la racine (`aesdecryptor.py`)
- **Après**: Code dans `src/aesdrive_decryptor/` (structure de package moderne)

### 2. Tests
- **Avant**: Tests éparpillés dans la racine
- **Après**: Tests centralisés dans `tests/`

### 3. Scripts Utilitaires
- **Avant**: Scripts dans la racine
- **Après**: Scripts dans `scripts/`

### 4. Documentation
- **Avant**: Documentation dans la racine
- **Après**: Documentation dans `docs/`

### 5. Compatibilité
- **Nouveau**: Script `aesdecryptor.py` pour maintenir la compatibilité
- **Nouveau**: Support de `python -m aesdrive_decryptor`

## 🚀 Utilisation

### Interface Moderne (Recommandée)
```bash
python -m aesdrive_decryptor fichier.aesd
python -m aesdrive_decryptor fichier.aesf
```

### Interface de Compatibilité
```bash
python aesdecryptor.py fichier.aesd
python aesdecryptor.py fichier.aesf
```

### Installation en Mode Développement
```bash
pip install -e .
```

### Exécution des Tests
```bash
python scripts/run_tests.py
```

## 📦 Configuration du Package

### setup.py
- Mis à jour pour la nouvelle structure `src/`
- Point d'entrée: `aesdrive_decryptor.main:main`
- Support des packages dans `src/`

### MANIFEST.in
- Inclusion des fichiers de documentation
- Inclusion des scripts utilitaires
- Exclusion des fichiers temporaires

### pytest.ini
- Configuration des tests
- Chemins de test définis
- Options par défaut

## 🔧 Avantages de la Nouvelle Structure

1. **Séparation Claire**: Code source, tests, scripts et documentation séparés
2. **Standards Python**: Respect des conventions PEP 518/621
3. **Maintenabilité**: Structure plus facile à maintenir et étendre
4. **Compatibilité**: Maintien de la compatibilité avec l'ancienne interface
5. **Tests**: Organisation claire des tests unitaires
6. **Distribution**: Facilite la création de packages distribués

## 🔄 Migration

### Pour les Utilisateurs
- L'ancienne interface `python aesdecryptor.py` continue de fonctionner
- La nouvelle interface `python -m aesdrive_decryptor` est recommandée

### Pour les Développeurs
- Code source maintenant dans `src/aesdrive_decryptor/`
- Tests dans `tests/`
- Scripts utilitaires dans `scripts/`
- Installation en mode développement: `pip install -e .`

## ✅ Validation

La réorganisation a été testée et validée :
- ✅ Interface moderne fonctionnelle
- ✅ Script de compatibilité fonctionnel
- ✅ Tests unitaires opérationnels
- ✅ Installation du package réussie
- ✅ Documentation mise à jour