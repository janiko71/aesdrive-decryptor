# AES Drive Decryptor

> 📖 **Navigation :** **README** | [Guide d'Utilisation](docs/USAGE.md) | [Sécurité](docs/SECURITY.md) | [📚 Documentation](docs/)

🔐 **Implémentation Python non officielle pour déchiffrer les fichiers chiffrés AES Drive**

Ce projet fournit une implémentation Python pour déchiffrer des fichiers individuels chiffrés de la solution AES Drive par /n Software. Il implémente la spécification du format de fichier AES Drive et utilise XTS-AES pour le déchiffrement des données.

## ✨ Fonctionnalités

- ✅ **Support multi-extensions**: Déchiffrement des fichiers `.aesd` et `.aesf`
- ✅ **Déchiffrement d'en-tête**: Implémentation complète utilisant AES-GCM
- ✅ **Déchiffrement de données XTS-AES**: Support complet utilisant les bibliothèques cryptographiques Python standard
- ✅ **Dérivation de clé**: Implémentation PBKDF2-HMAC-SHA512 correspondant aux fonctions crypto .NET
- ✅ **Structure de code professionnelle**: Suivant les meilleures pratiques Python
- ✅ **Support d'environnement virtuel**: Gestion des dépendances isolée
- ✅ **Compatibilité multiplateforme**: Fonctionne sur Windows, macOS et Linux

## 🚀 Démarrage Rapide

### Prérequis

- Python 3.8 ou supérieur
- pip (installateur de packages Python)

### Installation

1. **Cloner le dépôt:**
   ```bash
   git clone <url-du-dépôt>
   cd aesdrive-decryptor
   ```

2. **Configurer l'environnement virtuel et installer les dépendances:**
   
   **Windows:**
   ```cmd
   setup_venv.bat
   ```
   
   **macOS/Linux:**
   ```bash
   chmod +x setup_venv.sh
   ./setup_venv.sh
   ```

3. **Valider l'installation:**
   ```bash
   python tests/test_setup.py
   ```

4. **Activer l'environnement virtuel:**
   
   **Windows:**
   ```cmd
   venv\Scripts\activate.bat
   ```
   
   **macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

### Utilisation

**Utilisation moderne (recommandée):**
```bash
python -m aesdrive_decryptor fichier_chiffre.aesd
# ou
python -m aesdrive_decryptor fichier_chiffre.aesf
```

**Utilisation de compatibilité:**
```bash
python aesdecryptor.py fichier_chiffre.aesd
python aesdecryptor.py fichier_chiffre.aesf
```

**Avec mot de passe en argument:**
```bash
python -m aesdrive_decryptor fichier_chiffre.aesd -p votre_mot_de_passe
python aesdecryptor.py fichier_chiffre.aesf -p votre_mot_de_passe
```

**Obtenir de l'aide:**
```bash
python aesdecryptor.py --help
```

> 📖 **Pour des exemples détaillés et le dépannage, consultez le [Guide d'Utilisation](docs/USAGE.md)**

## 📁 Structure du Projet

```
aesdrive-decryptor/
├── src/                     # Code source principal
│   └── aesdrive_decryptor/  # Package principal
│       ├── __init__.py      # Interface du package
│       ├── main.py          # Point d'entrée principal
│       ├── decryptor.py     # Logique de déchiffrement
│       ├── constants.py     # Constantes
│       └── security.py     # Gestion mémoire sécurisée
├── tests/                   # Tests unitaires
│   ├── test_extensions.py   # Tests des extensions
│   └── test_setup.py        # Tests d'installation
├── scripts/                 # Scripts utilitaires
│   ├── setup_venv.py        # Configuration environnement
│   ├── setup_venv.bat       # Script Windows
│   └── setup_venv.sh        # Script Unix/Linux
├── docs/                    # Documentation
├── res/                     # Modules utilitaires (legacy)
│   ├── __init__.py         # Initialisation du package
│   ├── aesdatafile.py      # Classe DataFile pour analyser les en-têtes
│   └── fnhelper.py         # Fonctions d'aide et utilitaires
├── aesdecryptor.py          # Script de compatibilité
├── requirements.txt         # Dépendances de production
├── setup.py                 # Configuration d'installation
└── README.md               # Ce fichier
```

## 🔧 Détails Techniques

### Algorithme de Chiffrement

Le format AES Drive utilise:
- **Chiffrement d'en-tête**: AES-GCM avec clé 256-bit
- **Chiffrement de données**: XTS-AES avec clé 512-bit (deux clés 256-bit)
- **Dérivation de clé**: PBKDF2-HMAC-SHA512 avec 50 000 itérations
- **Taille de bloc**: 512 octets pour le mode XTS

### Format de Fichier

La structure du fichier chiffré:
1. **En-tête (144 octets)**: Contient les métadonnées et les clés chiffrées
2. **Données**: Contenu du fichier chiffré XTS-AES
3. **Padding**: Octets de padding optionnels

> 🔒 **Pour les détails sur la sécurité mémoire et la protection des données sensibles, voir [SECURITY.md](docs/SECURITY.md)**

## 🛠️ Développement

### Qualité du Code

Ce projet suit les meilleures pratiques Python:

- **Conformité PEP 8** avec longueur de ligne de 100 caractères
- **Annotations de type** pour une meilleure documentation du code et support IDE
- **Docstrings** suivant le style Google
- **Gestion d'erreurs** avec exceptions appropriées
- **Conception modulaire** avec séparation claire des préoccupations

> 📋 **Pour voir les détails des améliorations apportées au code, consultez la [documentation](docs/)**

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour les détails.

## ⚠️ Avertissement

Ce programme est à des **fins éducatives et de recherche uniquement**. Aucune garantie d'aucune sorte n'est fournie. Utilisez à vos propres risques.

## 📚 Documentation

> 🗺️ **[Documentation Complète](docs/)** - Navigation rapide vers tous les documents

### Documents Principaux
- **[Guide d'Utilisation](docs/USAGE.md)** - Exemples détaillés et dépannage
- **[Sécurité Mémoire](docs/SECURITY.md)** - Protection des données cryptographiques

### Outils
- **[Script de Validation](tests/test_setup.py)** - Vérification de l'installation

## 🤝 Contribution

Les contributions sont les bienvenues! N'hésitez pas à soumettre une Pull Request.

Avant de contribuer:
1. Consultez la [documentation](docs/) pour comprendre l'architecture
2. Respectez les pratiques de [sécurité mémoire](docs/SECURITY.md)
3. Testez avec `python tests/test_setup.py`

## 📚 Références Externes

- [Documentation du Format de Fichier AES Drive](https://cdn.nsoftware.com/help/NEH/app/nsoftware.AESDrive.htm#pg_aesdfileformat)
- [Bibliothèque Cryptographique Python](https://cryptography.io/)
- [Mode XTS-AES](https://cryptography.io/en/latest/hazmat/primitives/symmetric-encryption/#cryptography.hazmat.primitives.ciphers.modes.XTS)
