"""Module de sécurité mémoire pour AES Drive Decryptor."""

import secrets


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