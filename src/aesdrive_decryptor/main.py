"""Point d'entrée principal pour AES Drive Decryptor."""

import sys
from colorama import Fore, init

# Configuration de l'encodage pour Windows
if sys.platform == "win32":
    import codecs
    try:
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
    except:
        pass  # Ignorer les erreurs d'encodage

from .decryptor import AESDecryptor
from .constants import PWD_ENCODING
from .security import secure_zero_memory

# Import du module res pour la compatibilité
try:
    from res import check_arguments
except ImportError:
    print("⚠️ Module res non trouvé. Fonctionnalité limitée.")
    def check_arguments(args):
        """Fallback simple pour l'analyse des arguments."""
        if len(args) > 1 and args[1] in ['--help', '-h']:
            print("Usage: python -m aesdrive_decryptor [fichier] [-p mot_de_passe]")
            return None
        
        result = {}
        if len(args) > 1:
            result['file'] = args[1]
        if len(args) > 3 and args[2] in ['-p', '--pwd']:
            result['pwd'] = args[3]
        
        return result

# Initialiser colorama pour la compatibilité Windows
init(autoreset=True)


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