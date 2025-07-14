"""Fonctions d'aide pour AES Drive Decryptor.

Ce module fournit des fonctions utilitaires pour l'analyse des arguments,
le formatage et les opérations d'affichage utilisées dans l'application
AES Drive Decryptor.
"""

import json
import os
import pprint
import base64
import binascii as ba
import getpass
from typing import Dict, List, Optional, Any

from cryptography.hazmat.primitives import hmac
from cryptography.hazmat.primitives import hashes

from colorama import Fore, Back, Style, init

# Initialiser colorama pour la compatibilité Windows
init(autoreset=True)

# Constantes de formatage terminal
TERM_UNDERLINE = '\033[04m'
TERM_RESET = '\033[0m'
TERM_RED = '\033[31m'
TERM_BOLD = '\033[01m'



def check_arguments(arguments: List[str]) -> Optional[Dict[str, str]]:
    """Vérifier et analyser les arguments de ligne de commande.

    Args:
        arguments: Liste des arguments de ligne de commande depuis sys.argv

    Returns:
        Dictionnaire contenant les arguments analysés, ou None si l'aide a été
        demandée ou si une erreur s'est produite.

    Example:
        >>> check_arguments(['script.py', 'file.aesd', '-p', 'password'])
        {'file': 'file.aesd', 'pwd': 'password'}
    """
    new_arguments = {}
    arg_error = False
    p_ind = 0

    # Vérifier l'argument fichier (premier argument non-option)
    if len(arguments) > 1:
        first_arg = arguments[1]
        if not first_arg.startswith('-'):
            new_arguments["file"] = first_arg

    # Vérifier les drapeaux d'aide
    if "-h" in arguments or "--help" in arguments:
        print_help()
        arg_error = True

    # Vérifier les drapeaux de mot de passe
    if "-p" in arguments:
        p_ind = arguments.index("-p")
    elif "--pwd" in arguments:
        p_ind = arguments.index("--pwd")
    
    if p_ind > 0 and p_ind + 1 < len(arguments):
        new_arguments["pwd"] = arguments[p_ind + 1]

    return None if arg_error else new_arguments


def print_help() -> None:
    """Afficher les informations d'aide pour le programme."""
    print(f"{Fore.LIGHTWHITE_EX}UTILISATION{Fore.RESET}\n")
    print("\tpython aesdecryptor.py [fichier] [options]\n")
    print(f"{Fore.LIGHTWHITE_EX}DESCRIPTION{Fore.RESET}\n")
    print("\tDécrypteur AES Drive, version Python non officielle.\n")
    print("\tCe programme est à des fins d'information uniquement, aucune garantie d'aucune sorte (voir licence).\n")
    print("\tLe fichier que vous voulez décrypter doit être le premier argument.\n")
    print(f"\t\tSi aucun chemin de fichier n'est fourni, il vous sera demandé d'en saisir un.\n")
    print(f"\t{Fore.LIGHTWHITE_EX}-p,--pwd {Fore.RESET}{TERM_UNDERLINE}mot_de_passe{TERM_RESET}\n")
    print("\t\tMot de passe utilisateur AES Drive. S'il n'est pas fourni, il sera demandé (via la saisie console).\n")


def print_parameter(txt: str, param: Any) -> None:
    """Afficher un paramètre formaté avec sa valeur et sa longueur.

    Args:
        txt: Nom/description du paramètre
        param: Valeur du paramètre à afficher

    Example:
        >>> print_parameter("Taille du fichier", 1024)
        Taille du fichier.................... (4) 1024
    """
    param_str = str(param)
    length = len(param_str)
    txt_format = txt.ljust(44 - len(str(length)), ".") + " " + Fore.LIGHTWHITE_EX + "({}) {}" + Fore.RESET
    formatted_text = txt_format.format(str(length), param_str)
    print(formatted_text)

def print_data_file_info(data_file) -> None:
    """Afficher les informations sur le fichier de données chiffré.

    Args:
        data_file: Instance DataFile contenant les métadonnées du fichier
    """
    print('-' * 72)
    print_parameter("Version du type de fichier", data_file.file_type_version)
    print_parameter("CRC32 du fichier (vérifié)", data_file.crc32_checksum.decode())
    print_parameter("Salt global", data_file.global_salt.hex())
    print_parameter("Salt du fichier", data_file.file_salt.hex())
    print_parameter("Tag d'authentification", data_file.aes_gcm_auth_tag.hex())
    print('-' * 72)


if __name__ == '__main__':
    print('Ceci est un module et ne doit pas être exécuté directement.')
