#!/usr/bin/env python3
"""AES Drive Decryptor - Implémentation Python non officielle.

Ce programme déchiffre des fichiers individuels chiffrés de la solution AES Drive.
Il implémente la spécification du format de fichier AES Drive et utilise XTS-AES
pour le déchiffrement des données.

Auteur: Équipe AES Drive Decryptor
Licence: MIT
"""

import os
import sys
import getpass
import time
import hashlib
import secrets
import ctypes
from pathlib import Path
from typing import Optional, Tuple

from colorama import Fore, init

# Imports cryptographiques
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

# Imports locaux
from res import DataFile, check_arguments, print_parameter, print_data_file_info, TERM_RED, TERM_BOLD, TERM_RESET

# Initialiser colorama pour la compatibilité Windows
init(autoreset=True)

# Constantes
DEFAULT_FILE = "test.png.aesd"
KDF_ITERATIONS = 50000
DEFAULT_PWD = "aesdformatguide"
PWD_ENCODING = "UTF-8"
HEADER_LENGTH = 144
SECTOR_LENGTH = 512


class SecureMemory:
    """Gestionnaire de mémoire sécurisée pour les données cryptographiques sensibles."""
    
    def __init__(self, data: bytes):
        """Initialiser avec des données sensibles.
        
        Args:
            data: Données sensibles à protéger
        """
        self._data = bytearray(data)
        self._original_length = len(data)
    
    def get(self) -> bytes:
        """Obtenir les données (lecture seule)."""
        return bytes(self._data)
    
    def clear(self) -> None:
        """Effacer de manière sécurisée les données de la mémoire."""
        if self._data:
            # Écraser avec des données aléatoires plusieurs fois
            for _ in range(3):
                for i in range(len(self._data)):
                    self._data[i] = secrets.randbits(8)
            
            # Écraser avec des zéros
            for i in range(len(self._data)):
                self._data[i] = 0
            
            # Vider le bytearray
            self._data.clear()
    
    def __del__(self):
        """Nettoyage automatique lors de la destruction."""
        self.clear()
    
    def __enter__(self):
        """Support du context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Nettoyage automatique à la sortie du context."""
        self.clear()


def secure_zero_memory(data: bytearray) -> None:
    """Effacer de manière sécurisée un bytearray.
    
    Args:
        data: Bytearray à effacer
    """
    if data:
        # Écraser avec des données aléatoires
        for _ in range(3):
            for i in range(len(data)):
                data[i] = secrets.randbits(8)
        
        # Écraser avec des zéros
        for i in range(len(data)):
            data[i] = 0



class AESDecryptor:
    """Classe principale pour le déchiffrement de fichiers AES Drive."""

    def __init__(self):
        """Initialiser le décrypteur."""
        self.backend = default_backend()

    def get_file_path(self, arguments: dict) -> str:
        """Obtenir le chemin du fichier depuis les arguments ou la saisie utilisateur.
        
        Args:
            arguments: Arguments de ligne de commande analysés
            
        Returns:
            Chemin vers le fichier à déchiffrer
        """
        if arguments.get("file"):
            return arguments.get("file")
        else:
            return input("Fichier de données: ") or DEFAULT_FILE

    def validate_file_extension(self, filepath: str) -> str:
        """Valider l'extension du fichier et retourner le nom de fichier de sortie.
        
        Args:
            filepath: Chemin vers le fichier chiffré
            
        Returns:
            Nom de fichier de sortie sans l'extension .aesd
            
        Raises:
            SystemExit: Si le fichier n'a pas l'extension .aesd
        """
        encrypted_filename, file_ext = os.path.splitext(filepath)
        
        if file_ext != ".aesd":
            print(f"❌ Erreur: Le fichier doit avoir l'extension .aesd, reçu: {file_ext}")
            sys.exit(1)
            
        return encrypted_filename

    def load_encrypted_file(self, filepath: str) -> Tuple[DataFile, os.stat_result, object]:
        """Charger et analyser le fichier chiffré.
        
        Args:
            filepath: Chemin vers le fichier chiffré
            
        Returns:
            Tuple de (instance DataFile, stats du fichier, handle du fichier)
            
        Raises:
            SystemExit: Si le fichier n'existe pas ou ne peut pas être lu
        """
        if not os.path.isfile(filepath):
            print(f"❌ Fichier '{filepath}' introuvable!")
            sys.exit(1)

        try:
            f_in = open(filepath, "rb")
            file_header = f_in.read(HEADER_LENGTH)
            
            if len(file_header) != HEADER_LENGTH:
                print(f"❌ Longueur d'en-tête de fichier invalide: {len(file_header)} octets (attendu {HEADER_LENGTH})")
                sys.exit(1)
                
            print(f"🔓 Déchiffrement du fichier '{filepath}'...")
            data_file = DataFile(file_header)
            file_stats = os.stat(filepath)
            
            return data_file, file_stats, f_in
            
        except Exception as e:
            print(f"❌ Erreur lors de la lecture du fichier: {e}")
            sys.exit(1)

    def get_password(self, arguments: dict) -> str:
        """Obtenir le mot de passe depuis les arguments ou la saisie utilisateur.
        
        Args:
            arguments: Arguments de ligne de commande analysés
            
        Returns:
            Mot de passe utilisateur
        """
        if arguments.get("pwd"):
            return arguments.get("pwd")
        else:
            return getpass.getpass(prompt="Mot de passe AES Drive: ") or DEFAULT_PWD

    def derive_keys(self, password: str, data_file: DataFile) -> Tuple[bytes, bytes]:
        """Dériver les clés de chiffrement depuis le mot de passe et les salts.
        
        Args:
            password: Mot de passe utilisateur
            data_file: Instance DataFile contenant les salts
            
        Returns:
            Tuple de (clé de chiffrement d'en-tête, vecteur d'initialisation)
        """
        # Convertir le mot de passe en bytes de manière sécurisée
        password_bytes = bytearray(password.encode(PWD_ENCODING))
        
        try:
            # Dériver la clé en utilisant PBKDF2
            kdf_v = PBKDF2HMAC(
                algorithm=hashes.SHA512(),
                length=32,
                salt=data_file.global_salt,
                iterations=KDF_ITERATIONS,
                backend=self.backend
            )

            # Utiliser SecureMemory pour les clés dérivées
            with SecureMemory(kdf_v.derive(bytes(password_bytes))) as pwd_derived_key_verif_mem:
                pwd_derived_key_verif = pwd_derived_key_verif_mem.get()
                
                pwd_derived_key = hashlib.pbkdf2_hmac(
                    "sha512", 
                    bytes(password_bytes), 
                    data_file.global_salt, 
                    KDF_ITERATIONS, 
                    32
                )

                print_parameter("Création de clé dérivée du mot de passe", "OK")
                # Ne pas afficher les clés complètes en production - seulement les premiers octets
                print_parameter("Clé dérivée (aperçu)", pwd_derived_key[:8].hex() + "...")
                print_parameter("Vérification de clé dérivée", 
                               f"{pwd_derived_key_verif[:8].hex()}... ({pwd_derived_key == pwd_derived_key_verif})")

                # Utiliser SecureMemory pour la graine de fichier
                with SecureMemory(data_file.file_salt + pwd_derived_key) as file_seed_mem:
                    file_seed = file_seed_mem.get()
                    print_parameter("Graine de fichier (aperçu)", file_seed[:8].hex() + "...")

                    # Générer le hash de clé de fichier
                    sha512 = hashlib.sha512()
                    sha512.update(file_seed)
                    file_key_hash = sha512.digest()
                    print_parameter("Hash de clé calculé", "OK")
                    print_parameter("Hash de clé de fichier (aperçu)", file_key_hash[:8].hex() + "...")

                    # Extraire la clé de chiffrement d'en-tête et l'IV
                    header_encryption_key = file_key_hash[0:32]
                    init_vector = file_key_hash[32:44]
                    
                    print_parameter("Clé de chiffr. d'en-tête (aperçu)", header_encryption_key[:8].hex() + "...")
                    print_parameter("Vecteur d'initialisation", init_vector.hex())
                    print_parameter("Tag d'authentification", data_file.aes_gcm_auth_tag.hex())
                    print_parameter("Clés et IV calculés", "OK")

                    # Effacer les données sensibles intermédiaires
                    secure_zero_memory(bytearray(pwd_derived_key))
                    secure_zero_memory(bytearray(file_key_hash))

                    return header_encryption_key, init_vector
                    
        finally:
            # Effacer le mot de passe de la mémoire
            secure_zero_memory(password_bytes)

    def decrypt_header(self, header_key: bytes, iv: bytes, data_file: DataFile) -> bytes:
        """Déchiffrer l'en-tête du fichier en utilisant AES-GCM.
        
        Args:
            header_key: Clé de chiffrement d'en-tête
            iv: Vecteur d'initialisation
            data_file: Instance DataFile
            
        Returns:
            Octets d'en-tête déchiffrés
            
        Raises:
            SystemExit: Si le déchiffrement échoue (mauvais mot de passe)
        """
        aesgcm = AESGCM(header_key)
        encrypted_msg = data_file.aes_gcm_header + data_file.aes_gcm_auth_tag

        try:
            decrypted_header = aesgcm.decrypt(iv, encrypted_msg, None)
            print_parameter("En-tête déchiffré", decrypted_header.hex())
            return decrypted_header
            
        except InvalidTag:
            print_parameter("En-tête déchiffré", 
                          f"{TERM_RED}{TERM_BOLD}Erreur (InvalidTag), mauvais mot de passe?{TERM_RESET}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Erreur de déchiffrement inattendue: {e}")
            sys.exit(1)

    def parse_decrypted_header(self, decrypted_header: bytes) -> Tuple[int, bytes, bytes]:
        """Analyser l'en-tête déchiffré pour extraire les clés XTS.
        
        Args:
            decrypted_header: Octets d'en-tête déchiffrés
            
        Returns:
            Tuple de (longueur de padding, clé XTS 1, clé XTS 2)
        """
        header_padding_length = int.from_bytes(decrypted_header[0:2], 'big')
        header_reserved_1 = decrypted_header[2:16]
        header_xts_key1 = decrypted_header[16:48]
        header_xts_key2 = decrypted_header[48:80]

        print_parameter("Longueur de padding", header_padding_length)
        print_parameter("Clé XTS AES #1", header_xts_key1.hex())
        print_parameter("Clé XTS AES #2", header_xts_key2.hex())

        return header_padding_length, header_xts_key1, header_xts_key2

    def decrypt_file_data(self, f_in, output_filename: str, xts_key1: bytes, 
                         xts_key2: bytes, file_length: int) -> float:
        """Déchiffrer les données du fichier en utilisant XTS-AES.
        
        Args:
            f_in: Handle du fichier d'entrée
            output_filename: Chemin du fichier de sortie
            xts_key1: Première clé XTS
            xts_key2: Seconde clé XTS
            file_length: Longueur de données attendue
            
        Returns:
            Temps d'exécution en secondes
        """
        print("🔄 Début du déchiffrement...")
        print("-" * 72)
        print()

        start_time = time.time()
        
        # Utiliser SecureMemory pour la clé XTS combinée
        with SecureMemory(xts_key1 + xts_key2) as xts_key_mem:
            xts_key = xts_key_mem.get()
            
            with open(output_filename, "wb") as f_out:
                current_sector_offset = 0
                byte_offset = 0

                while True:
                    chunk = f_in.read(SECTOR_LENGTH)
                    if not chunk:
                        break

                    tweak = current_sector_offset.to_bytes(16, 'little')
                    decryptor_xts = Cipher(algorithms.AES(xts_key), modes.XTS(tweak)).decryptor()
                    decrypted_chunk = decryptor_xts.update(chunk)

                    byte_offset += SECTOR_LENGTH

                    if byte_offset > file_length:
                        # Fin des données - écrire seulement les octets restants
                        last_block_length = file_length % SECTOR_LENGTH
                        f_out.write(decrypted_chunk[0:last_block_length])
                        break
                    else:
                        f_out.write(decrypted_chunk)

                    current_sector_offset += 1

        # Effacer les clés XTS de la mémoire
        secure_zero_memory(bytearray(xts_key1))
        secure_zero_memory(bytearray(xts_key2))

        return time.time() - start_time

    def decrypt_file(self, filepath: str, password: str) -> None:
        """Méthode principale de déchiffrement.
        
        Args:
            filepath: Chemin vers le fichier chiffré
            password: Mot de passe de déchiffrement
        """
        # Convertir le mot de passe en bytearray pour un nettoyage sécurisé
        password_bytes = bytearray(password.encode(PWD_ENCODING))
        
        try:
            # Valider le fichier et obtenir le nom de sortie
            output_filename = self.validate_file_extension(filepath)
            original_dir, original_file = os.path.split(filepath)

            # Charger le fichier chiffré
            data_file, file_stats, f_in = self.load_encrypted_file(filepath)

            try:
                # Afficher les informations du fichier
                print('-' * 72)
                print_parameter("Répertoire de données", os.path.abspath(original_dir))
                print_parameter("Nom de fichier (entrée)", original_file)
                print_parameter("Nom de fichier (sortie)", os.path.basename(output_filename))
                print_data_file_info(data_file)

                # Dériver les clés de chiffrement (utilise le nettoyage sécurisé interne)
                header_key, iv = self.derive_keys(password, data_file)

                # Utiliser SecureMemory pour les clés sensibles
                with SecureMemory(header_key) as header_key_mem, SecureMemory(iv) as iv_mem:
                    # Déchiffrer l'en-tête
                    print('-' * 72)
                    decrypted_header = self.decrypt_header(header_key_mem.get(), iv_mem.get(), data_file)

                    # Utiliser SecureMemory pour l'en-tête déchiffré
                    with SecureMemory(decrypted_header) as decrypted_header_mem:
                        # Analyser l'en-tête pour les clés XTS
                        print('-' * 72)
                        padding_length, xts_key1, xts_key2 = self.parse_decrypted_header(decrypted_header_mem.get())

                        # Calculer la longueur réelle du fichier
                        file_length = file_stats.st_size - HEADER_LENGTH - padding_length
                        print_parameter("Longueur de données attendue", file_length)

                        print("-" * 72)
                        print()

                        # Déchiffrer les données du fichier (gère le nettoyage des clés XTS)
                        execution_time = self.decrypt_file_data(f_in, output_filename, xts_key1, xts_key2, file_length)

                        # Message de succès
                        print('-' * 72)
                        print(f"✅ Fichier déchiffré en {execution_time:.2f} secondes")
                        print()
                        print("-" * 72)
                        print("🎉 Déchiffrement terminé avec succès!")
                        print("=" * 72)

            finally:
                f_in.close()
                
        finally:
            # Effacer le mot de passe de la mémoire de manière sécurisée
            secure_zero_memory(password_bytes)


def main() -> None:
    """Point d'entrée principal de l'application."""
    print(f"{Fore.CYAN}🔐 AES Drive Decryptor - Implémentation Python Non Officielle{Fore.RESET}")
    print("=" * 72)
    
    # Analyser les arguments de ligne de commande
    arguments = check_arguments(sys.argv)
    if arguments is None:
        sys.exit(0)

    # Créer une instance du décrypteur
    decryptor = AESDecryptor()

    # Obtenir le chemin du fichier
    filepath = decryptor.get_file_path(arguments)
    
    # Obtenir le mot de passe et le gérer de manière sécurisée
    password = decryptor.get_password(arguments)
    password_bytes = bytearray(password.encode(PWD_ENCODING))
    
    try:
        # Déchiffrer le fichier
        decryptor.decrypt_file(filepath, password)
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⏹️ Déchiffrement interrompu par l'utilisateur.{Fore.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}❌ Erreur inattendue: {e}{Fore.RESET}")
        sys.exit(1)
    finally:
        # Effacer le mot de passe de la mémoire principale
        secure_zero_memory(password_bytes)
        # Effacer la variable string (moins efficace mais mieux que rien)
        password = None


if __name__ == "__main__":
    main()
