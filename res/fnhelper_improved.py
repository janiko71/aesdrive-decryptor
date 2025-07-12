#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AES Drive Helper Functions Module

This module provides utility functions for the AES Drive decryptor application,
including argument parsing, formatting, and display functions.
"""

import os
import sys
from typing import Dict, Optional, List, Any, Union
import colorama
from colorama import Fore, Style

# Initialize colorama for cross-platform colored terminal output
colorama.init()

# Terminal formatting constants
TERM_UNDERLINE = '\033[04m'
TERM_RESET = '\033[0m'
TERM_RED = '\033[31m'
TERM_BOLD = '\033[01m'


def check_arguments(arguments: List[str]) -> Optional[Dict[str, str]]:
    """
    Parse command line arguments for the AES Drive decryptor.
    
    Args:
        arguments: List of command line arguments
        
    Returns:
        Dictionary containing the parsed arguments, or None if help was requested
        
    Example:
        >>> check_arguments(["program.py", "file.aesd", "-p", "password"])
        {"file": "file.aesd", "pwd": "password"}
    """
    new_arguments = {}
    arg_error = False
    p_ind = 0
    
    # Check for file argument (first non-option argument)
    if len(arguments) > 1 and not arguments[1].startswith('-'):
        new_arguments["file"] = arguments[1]
    
    # Check for help option
    if "-h" in arguments or "--help" in arguments:
        print_help()
        arg_error = True
    
    # Check for password option
    if "-p" in arguments:
        p_ind = arguments.index("-p")
    if "--pwd" in arguments:
        p_ind = arguments.index("--pwd")
    
    if p_ind > 0 and p_ind + 1 < len(arguments):
        new_arguments["pwd"] = arguments[p_ind + 1]
    
    return None if arg_error else new_arguments


def print_help() -> None:
    """
    Print help information for the AES Drive decryptor.
    """
    print(Fore.LIGHTWHITE_EX + "USAGE" + Fore.RESET + "\n")
    print("\tpython3 aesdecryptor.py [file] [options]\n")
    print(Fore.LIGHTWHITE_EX + "DESCRIPTION" + Fore.RESET + "\n")
    print("\tAES Drive decryptor, unofficial Python version. \n")
    print("\tThis program is for information purpose only, no warranty of any kind (see license).\n")
    print("\tThe file you want to decrypt must be the first argument.\n")
    print("\t\tIf no filepath provided, you will be prompted to enter one.\n")
    print("\t" + Fore.LIGHTWHITE_EX + "-p,--pwd " + Fore.RESET + TERM_UNDERLINE + "password\n" + TERM_RESET)
    print("\t\tAES Drive's user password. If not provided, it will be asked (through the console input).\n")
    print("\t" + Fore.LIGHTWHITE_EX + "-h,--help" + Fore.RESET + "\n")
    print("\t\tDisplay this help message and exit.\n")


def print_parameter(label: str, value: Any) -> None:
    """
    Print a parameter with consistent formatting.
    
    Args:
        label: The name of the parameter
        value: The value of the parameter
    """
    # Convert value to string if it's not already
    if not isinstance(value, str):
        value = str(value)
    
    # Get length of value for formatting
    value_length = len(value)
    
    # Format the output
    txt_format = label.ljust(44 - len(str(value_length)), ".") + " " + Fore.LIGHTWHITE_EX + "({}) {}" + Fore.RESET
    formatted_text = txt_format.format(str(value_length), value)
    print(formatted_text)


def print_data_file_info(data_file: Any) -> None:
    """
    Print information about an AES Drive data file.
    
    Args:
        data_file: An AES Drive DataFile object
    """
    print('-' * 72)
    print_parameter("File type version", data_file.file_type_version)
    print_parameter("File CRC32 (verified)", str(data_file.crc32_checksum.decode()))
    print_parameter("Global salt", str(data_file.global_salt.hex()))
    print_parameter("File salt", str(data_file.file_salt.hex()))
    print_parameter("Auth tag", str(data_file.aes_gcm_auth_tag.hex()))
    print('-' * 72)


def print_error(message: str) -> None:
    """
    Print an error message with consistent formatting.
    
    Args:
        message: The error message to print
    """
    print(f"{Fore.RED}{Style.BRIGHT}ERROR: {message}{Style.RESET_ALL}")


def print_success(message: str) -> None:
    """
    Print a success message with consistent formatting.
    
    Args:
        message: The success message to print
    """
    print(f"{Fore.GREEN}{Style.BRIGHT}{message}{Style.RESET_ALL}")


def print_warning(message: str) -> None:
    """
    Print a warning message with consistent formatting.
    
    Args:
        message: The warning message to print
    """
    print(f"{Fore.YELLOW}{Style.BRIGHT}WARNING: {message}{Style.RESET_ALL}")


# Module guard
if __name__ == '__main__':
    print('This is a module and should not be executed directly.')
    sys.exit(1)