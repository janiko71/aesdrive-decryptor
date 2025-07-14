"""AES Drive Decryptor - Package principal.

Ce package fournit une implémentation Python pour déchiffrer des fichiers
individuels chiffrés de la solution AES Drive.
"""

__version__ = "1.0.0"
__author__ = "Équipe AES Drive Decryptor"
__license__ = "MIT"

from .decryptor import AESDecryptor
from .constants import SUPPORTED_EXTENSIONS, DEFAULT_FILE

__all__ = [
    "AESDecryptor",
    "SUPPORTED_EXTENSIONS", 
    "DEFAULT_FILE"
]