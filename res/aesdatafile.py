"""Analyseur de fichiers de données chiffrés AES Drive.

Ce module fournit la classe DataFile pour analyser et valider
les en-têtes de fichiers chiffrés AES Drive.

Référence: https://cdn.nsoftware.com/help/NEH/app/nsoftware.AESDrive.htm#pg_aesdfileformat
"""

import os
import sys
import json
import base64
import binascii as ba
from typing import Optional


class DataFile:
    """Analyseur pour les fichiers de données chiffrés AES Drive.
    
    Cette classe gère l'analyse et la validation des en-têtes de fichiers chiffrés AES Drive.
    L'en-tête fait 144 octets de long et contient les métadonnées cryptographiques nécessaires
    pour le déchiffrement.
    
    Attributes:
        raw_header: Octets bruts de l'en-tête (144 octets)
        file_type: Identifiant du type de fichier (4 octets, devrait être "AESD")
        file_type_version: Octet de version
        reserved_1: Octets réservés (7 octets)
        crc32_checksum: Somme de contrôle CRC32 pour la validation de l'en-tête
        global_salt: Salt global pour la dérivation de clé (16 octets)
        file_salt: Salt spécifique au fichier (16 octets)
        aes_gcm_header: Données d'en-tête chiffrées (80 octets)
        aes_gcm_auth_tag: Tag d'authentification pour le mode GCM (16 octets)
    """

    def __init__(self, header: bytes) -> None:
        """Initialiser DataFile avec les octets d'en-tête.

        Args:
            header: En-tête de 144 octets du fichier chiffré

        Raises:
            ValueError: Si la longueur de l'en-tête est invalide
            SystemExit: Si la validation de la somme de contrôle CRC32 échoue
        """
        if len(header) != 144:
            raise ValueError(f"L'en-tête doit faire exactement 144 octets, reçu {len(header)}")

        self.raw_header = header
        self._parse_header()
        self._validate_checksum()

    def _parse_header(self) -> None:
        """Analyser les octets d'en-tête en composants individuels."""
        file_header = self.raw_header

        # Analyse de l'en-tête
        self.file_type = file_header[0:4].decode("utf-8")
        self.file_type_version = file_header[4]
        self.reserved_1 = file_header[5:12]
        self.crc32_checksum = ba.hexlify(file_header[12:16])
        self.global_salt = file_header[16:32]
        self.file_salt = file_header[32:48]
        self.aes_gcm_header = file_header[48:128]
        self.aes_gcm_auth_tag = file_header[128:144]

    def _validate_checksum(self) -> None:
        """Valider la somme de contrôle CRC32 de l'en-tête.
        
        Raises:
            SystemExit: Si la validation de la somme de contrôle échoue
        """
        # Créer une copie de l'en-tête avec la somme de contrôle mise à zéro pour la validation
        header_copy = (self.raw_header[0:12] + 
                      b'\x00\x00\x00\x00' + 
                      self.raw_header[16:144])
        
        calculated_crc = ba.crc32(header_copy)
        calculated_hex = ba.hexlify(calculated_crc.to_bytes(4, 'big'))

        if calculated_hex != self.crc32_checksum:
            print("❌ Erreur de somme de contrôle : La validation de l'en-tête a échoué")
            sys.exit(1)



if __name__ == '__main__':
    print('Ceci est un module et ne doit pas être exécuté directement.')

