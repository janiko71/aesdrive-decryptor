# Guide d'Utilisation - AES Drive Decryptor

> 📖 **Navigation :** [README](../README.md) | **Guide d'Utilisation** | [Sécurité](SECURITY.md)

Ce guide fournit des instructions détaillées pour installer et utiliser AES Drive Decryptor.

## 🚀 Installation Rapide

### 1. Configuration de l'Environnement Virtuel

**Windows :**
```cmd
setup_venv.bat
```

**Linux/macOS :**
```bash
chmod +x setup_venv.sh
./setup_venv.sh
```

### 2. Activation de l'Environnement

**Windows :**
```cmd
venv\Scripts\activate.bat
```

**Linux/macOS :**
```bash
source venv/bin/activate
```

## 💻 Utilisation

### Commande de Base
```bash
python aesdecryptor.py fichier.aesd
# ou pour les fichiers .aesf
python aesdecryptor.py fichier.aesf
```

### Avec Mot de Passe en Paramètre
```bash
python aesdecryptor.py fichier.aesd -p votre_mot_de_passe
python aesdecryptor.py fichier.aesf -p votre_mot_de_passe
```

### Aide
```bash
python aesdecryptor.py --help
```

## 📝 Exemples d'Utilisation

### Exemple 1 : Déchiffrement Interactif (.aesd)
```bash
$ python aesdecryptor.py document.pdf.aesd
🔐 AES Drive Decryptor - Implémentation Python Non Officielle
========================================================================
🔓 Déchiffrement du fichier 'document.pdf.aesd'...
Mot de passe AES Drive: [saisie masquée]
```

### Exemple 2 : Déchiffrement avec Mot de Passe (.aesf)
```bash
$ python aesdecryptor.py photo.jpg.aesf -p monmotdepasse
🔐 AES Drive Decryptor - Implémentation Python Non Officielle
========================================================================
🔓 Déchiffrement du fichier 'photo.jpg.aesf'...
```

### Exemple 3 : Sans Spécifier de Fichier
```bash
$ python aesdecryptor.py
🔐 AES Drive Decryptor - Implémentation Python Non Officielle
========================================================================
Fichier de données: document.aesd
```

### Exemple 4 : Extensions Supportées
```bash
# Fichiers .aesd (AES Drive Standard)
$ python aesdecryptor.py archive.zip.aesd

# Fichiers .aesf (AES Drive File)
$ python aesdecryptor.py video.mp4.aesf
```

## 📊 Sortie du Programme

Le programme affiche des informations détaillées pendant le processus :

```
🔐 AES Drive Decryptor - Implémentation Python Non Officielle
========================================================================
🔓 Déchiffrement du fichier 'example.txt.aesd'...
------------------------------------------------------------------------
Répertoire de données..................... (28) C:\Users\User\Documents
Nom de fichier (entrée)................... (15) example.txt.aesd
Nom de fichier (sortie)................... (11) example.txt
Version du type de fichier................ (1) 1
CRC32 du fichier (vérifié)................ (8) a1b2c3d4
Salt global........................... (32) 1234567890abcdef...
Salt du fichier....................... (32) fedcba0987654321...
Tag d'authentification............... (32) abcdef1234567890...
------------------------------------------------------------------------
Création de clé dérivée du mot de passe...... (2) OK
Clé dérivée............................... (64) 9876543210fedcba...
------------------------------------------------------------------------
En-tête déchiffré......................... (160) 0010000000000000...
------------------------------------------------------------------------
Longueur de padding....................... (1) 0
Clé XTS AES #1............................ (64) abcd1234efgh5678...
Clé XTS AES #2............................ (64) 9876wxyz5432abcd...
Longueur de données attendue.............. (4) 1024
------------------------------------------------------------------------

🔄 Début du déchiffrement...
------------------------------------------------------------------------

------------------------------------------------------------------------
✅ Fichier déchiffré en 0.05 secondes
------------------------------------------------------------------------
🎉 Déchiffrement terminé avec succès!
========================================================================
```

## ⚠️ Messages d'Erreur Courants

### Fichier Introuvable
```
❌ Fichier 'inexistant.aesd' introuvable!
```

### Extension Incorrecte
```
❌ Erreur: Le fichier doit avoir l'extension .aesd ou .aesf, reçu: .txt
   Extensions supportées: .aesd, .aesf
```

### Mot de Passe Incorrect
```
En-tête déchiffré......................... ❌ Erreur (InvalidTag), mauvais mot de passe?
```

### En-tête Corrompu
```
❌ Erreur de somme de contrôle : La validation de l'en-tête a échoué
```

## 🔧 Dépannage

### Problème : Module non trouvé
**Solution :** Assurez-vous que l'environnement virtuel est activé
```bash
# Windows
venv\Scripts\activate.bat

# Linux/macOS
source venv/bin/activate
```

### Problème : Erreur de dépendances
**Solution :** Réinstallez les dépendances
```bash
pip install -r requirements.txt
```

### Problème : Validation de l'installation
**Solution :** Utilisez le script de validation
```bash
python validate_setup.py
```

### Problème : Permissions insuffisantes
**Solution :** Exécutez avec les permissions appropriées ou changez le répertoire de sortie

> 🔧 **Pour plus de détails techniques, consultez le [README](../README.md)**

## 📁 Structure des Fichiers de Sortie

Le fichier déchiffré sera créé dans le même répertoire que le fichier source, sans l'extension `.aesd` ou `.aesf` :

```
Fichiers .aesd :
Avant : document.pdf.aesd
Après : document.pdf

Fichiers .aesf :
Avant : video.mp4.aesf
Après : video.mp4
```

## 🛡️ Sécurité

- Les mots de passe ne sont jamais stockés en mémoire plus longtemps que nécessaire
- La saisie de mot de passe est masquée dans le terminal
- Aucune information sensible n'est écrite dans les logs

> 🔒 **Pour les détails complets sur la sécurité mémoire, consultez [SECURITY.md](SECURITY.md)**

## 📞 Support

Pour signaler des problèmes ou demander de l'aide :
1. Vérifiez d'abord ce guide de dépannage
2. Consultez le [README.md](../README.md) principal
3. Exécutez `python tests/test_setup.py` pour diagnostiquer l'installation
4. Consultez le [README](../README.md) pour comprendre l'architecture
5. Vérifiez les issues existantes dans le projet

## 📚 Voir Aussi

- **[README.md](../README.md)** - Vue d'ensemble du projet
- **[SECURITY.md](SECURITY.md)** - Mesures de sécurité mémoire