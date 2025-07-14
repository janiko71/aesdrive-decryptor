# AES Drive Decryptor

🔐 **Implémentation Python non officielle pour déchiffrer les fichiers chiffrés AES Drive**

Ce projet fournit une implémentation Python pour déchiffrer des fichiers individuels chiffrés de la solution AES Drive par /n Software. Il implémente la spécification du format de fichier AES Drive et utilise XTS-AES pour le déchiffrement des données.

## ✨ Fonctionnalités

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

3. **Activer l'environnement virtuel:**
   
   **Windows:**
   ```cmd
   venv\Scripts\activate.bat
   ```
   
   **macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

### Utilisation

**Utilisation de base:**
```bash
python aesdecryptor.py fichier_chiffre.aesd
```

**Avec mot de passe en argument:**
```bash
python aesdecryptor.py fichier_chiffre.aesd -p votre_mot_de_passe
```

**Obtenir de l'aide:**
```bash
python aesdecryptor.py --help
```

## 📁 Structure du Projet

```
aesdrive-decryptor/
├── aesdecryptor.py          # Application principale de déchiffrement
├── compare_directories.py   # Utilitaire de comparaison de répertoires
├── res/                     # Modules de ressources
│   ├── __init__.py         # Initialisation du package
│   ├── aesdatafile.py      # Classe DataFile pour analyser les en-têtes
│   └── fnhelper.py         # Fonctions d'aide et utilitaires
├── requirements.txt         # Dépendances de production
├── setup_venv.bat          # Script de configuration d'environnement virtuel (Windows)
├── setup_venv.sh           # Script de configuration d'environnement virtuel (Unix)
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

## 🛠️ Développement

### Qualité du Code

Ce projet suit les meilleures pratiques Python:

- **Conformité PEP 8** avec longueur de ligne de 100 caractères
- **Annotations de type** pour une meilleure documentation du code et support IDE
- **Docstrings** suivant le style Google
- **Gestion d'erreurs** avec exceptions appropriées
- **Conception modulaire** avec séparation claire des préoccupations

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour les détails.

## ⚠️ Avertissement

Ce programme est à des **fins éducatives et de recherche uniquement**. Aucune garantie d'aucune sorte n'est fournie. Utilisez à vos propres risques.

## 🤝 Contribution

Les contributions sont les bienvenues! N'hésitez pas à soumettre une Pull Request.

## 📚 Références

- [Documentation du Format de Fichier AES Drive](https://cdn.nsoftware.com/help/NEH/app/nsoftware.AESDrive.htm#pg_aesdfileformat)
- [Bibliothèque Cryptographique Python](https://cryptography.io/)
- [Mode XTS-AES](https://cryptography.io/en/latest/hazmat/primitives/symmetric-encryption/#cryptography.hazmat.primitives.ciphers.modes.XTS)
