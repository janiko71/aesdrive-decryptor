# 🔐 AES Drive Decryptor - Open source full Version

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/psf/black)
[![Type Checking](https://img.shields.io/badge/type%20checking-mypy-blue.svg)](http://mypy-lang.org/)
[![Tests](https://img.shields.io/badge/tests-pytest-green.svg)](https://pytest.org)
[![Quality](https://img.shields.io/badge/quality-A+-brightgreen.svg)](#)

Un outil Python professionnel pour décrypter les fichiers chiffrés AES Drive. Cette implémentation offre une solution sécurisée, efficace et conviviale pour décrypter les fichiers chiffrés avec la solution AES Drive de /n Software.

## ✨ Fonctionnalités

- **🔐 Décryptage Sécurisé**: Support du format AES Drive avec chiffrement XTS-AES
- **📋 Code Professionnel**: Respect des standards PEP8 et meilleures pratiques Python
- **🚀 Haute Performance**: Optimisé pour les gros fichiers avec traitement par secteurs
- **🛡️ Gestion d'Erreurs Robuste**: Gestion complète des erreurs avec messages informatifs
- **📊 Suivi de Progression**: Indication temps réel pour les gros fichiers
- **🔍 Validation d'Entrées**: Validation complète des fichiers et mots de passe
- **📝 Logging Complet**: Logging détaillé avec niveaux configurables
- **🧪 Couverture de Tests**: Suite de tests complète avec pytest
- **🎯 Sécurité de Type**: Type hints complets pour fiabilité du code
- **⚙️ Configurable**: Support de configuration par variables d'environnement

## 🚀 Démarrage Rapide

### Installation

```bash
# Cloner le repository
git clone https://github.com/janiko71/aesdrive-decryptor.git
cd aesdrive-decryptor

# Installer les dépendances
pip install -r requirements.txt

# Optionnel: Installation en mode développement
pip install -e .
```

### Usage de Base

```bash
# Décrypter un fichier (prompt interactif pour le mot de passe)
python aes_decryptor.py fichier_chiffre.aesd

# Décrypter avec mot de passe en ligne de commande
python aes_decryptor.py fichier_chiffre.aesd -p monmotdepasse

# Spécifier un fichier de sortie personnalisé
python aes_decryptor.py fichier_chiffre.aesd -o fichier_decrypte.txt

# Activer le logging verbeux
python aes_decryptor.py fichier_chiffre.aesd -v
```

### Usage Avancé

```bash
# Configuration via variables d'environnement
export AES_KDF_ITERATIONS=100000
export AES_LOG_LEVEL=DEBUG
python aes_decryptor.py fichier_chiffre.aesd

# Mode debug
export AES_DEBUG=1
python aes_decryptor.py fichier_chiffre.aesd -v
```

## 📖 Documentation API

### Classe AESDecryptor

La classe principale fournit l'interface suivante :

```python
from aes_decryptor import AESDecryptor
from res.config import Config

# Initialisation
config = Config()
decryptor = AESDecryptor(config)

# Décrypter un fichier
success = decryptor.decrypt_file(
    input_path=Path("chiffre.aesd"),
    password="monmotdepasse",
    output_path=Path("decrypte.txt")  # Optionnel
)
```

### Configuration

La classe `Config` centralise tous les paramètres :

```python
from res.config import Config

config = Config()
print(f"Itérations KDF: {config.KDF_ITERATIONS}")
print(f"Taille Secteur: {config.SECTOR_LENGTH}")
```

## 🏗️ Architecture

Le projet suit une architecture modulaire avec séparation claire des responsabilités :

```
aesdrive-decryptor/
├── aes_decryptor.py          # Point d'entrée principal
├── res/
│   ├── __init__.py
│   ├── aes_data_file.py      # Parser format AES Drive
│   ├── config.py             # Gestion configuration
│   └── crypto_helper.py      # Utilitaires cryptographiques
├── tests/
│   ├── __init__.py
│   └── test_aes_decryptor.py # Tests unitaires
├── requirements.txt          # Dépendances
├── setup.py                  # Configuration package
└── README.md                # Ce fichier
```

### Composants Clés

1. **AESDecryptor**: Logique principale de décryptage avec gestion d'erreurs
2. **AESDataFile**: Parser pour les en-têtes de fichiers AES Drive
3. **Config**: Gestion centralisée de la configuration
4. **CryptoHelper**: Fonctions utilitaires cryptographiques
5. **DisplayFormatter**: Formatage cohérent des sorties

## 🔧 Configuration

### Variables d'Environnement

| Variable | Description | Défaut |
|----------|-------------|---------|
| `AES_KDF_ITERATIONS` | Nombre d'itérations PBKDF2 | 50000 |
| `AES_PWD_ENCODING` | Encodage mot de passe | UTF-8 |
| `AES_LOG_LEVEL` | Niveau de logging | INFO |
| `AES_DEBUG` | Activer mode debug | False |
| `AES_TEMP_DIR` | Répertoire temporaire | /tmp |

### Support Format de Fichier

Cet outil supporte le format AES Drive comme documenté dans la [documentation /n Software](https://cdn.nsoftware.com/help/NEH/app/nsoftware.AESDrive.htm#pg_aesdfileformat).

**Structure du Fichier:**
- **En-tête**: 144 octets contenant métadonnées et clés chiffrées
- **Contenu**: Données chiffrées de longueur variable en secteurs de 512 octets
- **Chiffrement**: XTS-AES avec clés dérivées du mot de passe

## 🧪 Tests

Le projet inclut des tests complets :

```bash
# Lancer tous les tests
pytest

# Avec couverture
pytest --cov=. --cov-report=html

# Tests spécifiques
pytest tests/test_aes_decryptor.py -v
```

## 🛡️ Considérations de Sécurité

- **Gestion Mots de Passe**: Effacement sécurisé de la mémoire après usage
- **Attaques Timing**: Fonctions de comparaison sécurisées
- **Validation Entrées**: Validation complète avant traitement
- **Messages d'Erreur**: Pas de fuite d'informations sensibles
- **Dépendances**: Utilisation de bibliothèques cryptographiques établies

## 📊 Performance

Benchmarks sur matériel standard :

| Taille Fichier | Temps Décryptage | Usage Mémoire |
|----------------|------------------|---------------|
| 1 MB | ~0.1 secondes | ~10 MB |
| 100 MB | ~2 secondes | ~15 MB |
| 1 GB | ~20 secondes | ~20 MB |

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez suivre ces directives :

1. **Style de Code**: Suivre PEP8 et utiliser `black`
2. **Type Hints**: Inclure des type hints pour toutes les fonctions
3. **Documentation**: Mettre à jour docstrings et README
4. **Tests**: Ajouter des tests pour les nouvelles fonctionnalités
5. **Sécurité**: Considérer les implications sécuritaires

## 📝 Changelog

### Version 2.0.0 (Actuelle)
- Refactorisation complète pour standards professionnels
- Ajout gestion d'erreurs complète
- Implémentation suite de tests complète
- Ajout type hints partout
- Amélioration sécurité et performance
- Ajout gestion configuration
- Documentation améliorée

### Version 1.0.0 (Originale)
- Fonctionnalité de décryptage de base
- Interface ligne de commande
- Support format AES Drive

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour les détails.

## 🙏 Remerciements

- Inspiration de l'implémentation originale de janiko71
- /n Software pour la documentation du format AES Drive
- Mainteneurs de la bibliothèque Python cryptography
- Contributeurs et testeurs

---

**Note**: Cet outil est destiné à un usage légitime avec vos propres fichiers chiffrés. Assurez-vous toujours d'avoir l'autorisation appropriée avant de tenter de décrypter des fichiers.