"""
Unit Tests for AES Drive Decryptor - Open source full version

Comprehensive test suite for the AES Drive Decryptor application.
Tests all major components and edge cases.
"""

import hashlib
import pytest
import tempfile
import binascii
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from res.aes_data_file import AESDataFile, AESDataFileError
from res.config import Config
from res.crypto_helper import CryptoHelper, DisplayFormatter
from aes_decryptor import AESDecryptor, AESDecryptorError


class TestAESDataFile:
    """Test cases for AESDataFile class."""
    
    def test_valid_header_parsing(self):
        """Test parsing of a valid AES Drive header."""
        # Create a mock valid header
        header = bytearray(144)
        header[0:4] = b"AESD"  # File type
        header[4] = 1  # Version
        
        # Set some mock salts
        header[16:32] = b"global_salt_16_b"
        header[32:48] = b"file_salt_16_byt"
        
        # Calculate and set CRC32
        header_for_crc = bytes(header[0:12] + b'\x00\x00\x00\x00' + header[16:144])
        crc = binascii.crc32(header_for_crc)
        header[12:16] = crc.to_bytes(4, 'big')
        
        # Create AESDataFile instance
        data_file = AESDataFile(bytes(header))
        
        assert data_file.file_type == "AESD"
        assert data_file.file_type_version == 1
        assert data_file.global_salt == b"global_salt_16_b"
        assert data_file.file_salt == b"file_salt_16_byt"
        assert data_file.is_valid
    
    def test_invalid_header_length(self):
        """Test handling of invalid header length."""
        with pytest.raises(AESDataFileError, match="Invalid header length"):
            AESDataFile(b"too_short")
    
    def test_invalid_file_type(self):
        """Test handling of invalid file type."""
        header = bytearray(144)
        header[0:4] = b"XXXX"  # Invalid file type
        
        with pytest.raises(AESDataFileError, match="Invalid file type"):
            AESDataFile(bytes(header))
    
    def test_checksum_validation_failure(self):
        """Test handling of invalid checksum."""
        header = bytearray(144)
        header[0:4] = b"AESD"
        header[4] = 1
        header[12:16] = b"bad!"  # Invalid checksum
        
        with pytest.raises(AESDataFileError, match="Checksum mismatch"):
            AESDataFile(bytes(header))
    
    def test_get_info_dict(self):
        """Test the get_info_dict method."""
        header = bytearray(144)
        header[0:4] = b"AESD"
        header[4] = 2
        header[16:32] = b"global_salt_test"
        header[32:48] = b"file_salt_test_!"
        
        # Calculate proper CRC32
        header_for_crc = bytes(header[0:12] + b'\x00\x00\x00\x00' + header[16:144])
        crc = binascii.crc32(header_for_crc)
        header[12:16] = crc.to_bytes(4, 'big')
        
        data_file = AESDataFile(bytes(header))
        info = data_file.get_info_dict()
        
        assert info['file_type'] == "AESD"
        assert info['file_type_version'] == 2
        assert info['is_valid'] == True
        assert 'global_salt_hex' in info
        assert 'file_salt_hex' in info


class TestConfig:
    """Test cases for Config class."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = Config()
        
        assert config.HEADER_LENGTH == 144
        assert config.SECTOR_LENGTH == 512
        assert config.KDF_ITERATIONS == 50000
        assert config.PWD_ENCODING == "UTF-8"
        assert config.DEFAULT_FILE_EXTENSION == ".aesd"
    
    @patch.dict('os.environ', {'AES_KDF_ITERATIONS': '25000'})
    def test_environment_override(self):
        """Test configuration override from environment variables."""
        config = Config()
        assert config.KDF_ITERATIONS == 25000
    
    def test_validation_success(self):
        """Test successful configuration validation."""
        config = Config()
        assert config.validate() == True
    
    def test_validation_failure(self):
        """Test configuration validation failure."""
        config = Config()
        config.KDF_ITERATIONS = 500  # Too low
        assert config.validate() == False


class TestCryptoHelper:
    """Test cases for CryptoHelper class."""
    
    def test_derive_key_from_password(self):
        """Test password key derivation."""
        password = "test_password"
        salt = b"test_salt_16_byt"
        
        key = CryptoHelper.derive_key_from_password(password, salt, iterations=1000)
        
        assert len(key) == 32
        assert isinstance(key, bytes)
        
        # Test deterministic behavior
        key2 = CryptoHelper.derive_key_from_password(password, salt, iterations=1000)
        assert key == key2
    
    def test_generate_file_hash(self):
        """Test file hash generation."""
        file_seed = b"test_file_seed_data"
        hash_result = CryptoHelper.generate_file_hash(file_seed)
        
        assert len(hash_result) == 64  # SHA512 produces 64 bytes
        assert isinstance(hash_result, bytes)
        
        # Test against known hash
        expected = hashlib.sha512(file_seed).digest()
        assert hash_result == expected
    
    def test_secure_compare(self):
        """Test secure byte comparison."""
        data1 = b"identical_data"
        data2 = b"identical_data"
        data3 = b"different_data"
        
        assert CryptoHelper.secure_compare(data1, data2) == True
        assert CryptoHelper.secure_compare(data1, data3) == False
    
    def test_format_hex_string(self):
        """Test hex string formatting."""
        data = b"\x01\x02\x03\x04\x05\x06\x07\x08"
        formatted = CryptoHelper.format_hex_string(data, group_size=4)
        
        assert "01020304" in formatted
        assert "05060708" in formatted
    
    def test_password_strength_validation(self):
        """Test password strength validation."""
        # Weak password
        weak_result = CryptoHelper.validate_password_strength("123")
        assert weak_result['is_strong'] == False
        assert len(weak_result['issues']) > 0
        
        # Strong password
        strong_result = CryptoHelper.validate_password_strength("StrongP@ssw0rd123")
        assert strong_result['is_strong'] == True
        assert strong_result['score'] >= 4


class TestDisplayFormatter:
    """Test cases for DisplayFormatter class."""
    
    def test_format_parameter(self):
        """Test parameter formatting."""
        result = DisplayFormatter.format_parameter("Test Param", "test_value")
        
        assert "Test Param" in result
        assert "test_value" in result
        assert "." in result  # Should contain dots for spacing
    
    def test_format_parameter_with_bytes(self):
        """Test parameter formatting with bytes."""
        test_bytes = b"\x01\x02\x03\x04"
        result = DisplayFormatter.format_parameter("Byte Param", test_bytes)
        
        assert "Byte Param" in result
        assert "01020304" in result
    
    def test_format_progress_bar(self):
        """Test progress bar formatting."""
        progress = DisplayFormatter.format_progress_bar(50, 100)
        
        assert "50.0%" in progress
        assert "[" in progress and "]" in progress
    
    def test_colorize(self):
        """Test text colorization."""
        colored = DisplayFormatter.colorize("test", "RED")
        
        assert "\033[31m" in colored  # RED color code
        assert "\033[0m" in colored   # RESET color code
        assert "test" in colored


class TestAESDecryptor:
    """Test cases for AESDecryptor class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.config = Config()
        self.decryptor = AESDecryptor(self.config)
    
    def test_initialization(self):
        """Test AESDecryptor initialization."""
        assert self.decryptor.config == self.config
        assert hasattr(self.decryptor, 'logger')
        assert hasattr(self.decryptor, 'backend')
    
    def test_validate_input_file_nonexistent(self):
        """Test validation of non-existent input file."""
        fake_path = Path("/non/existent/file.aesd")
        result = self.decryptor._validate_input_file(fake_path)
        assert result == False
    
    def test_validate_input_file_wrong_extension(self):
        """Test validation of file with wrong extension."""
        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
            path = Path(tmp.name)
            result = self.decryptor._validate_input_file(path)
            assert result == False
    
    def test_get_output_path(self):
        """Test output path generation."""
        input_path = Path("test_file.aesd")
        output_path = self.decryptor._get_output_path(input_path)
        
        assert output_path == Path("test_file")
        assert output_path.suffix == ""
    
    @patch('builtins.open', mock_open(read_data=b'x' * 144))
    def test_load_data_file_success(self):
        """Test successful data file loading."""
        # Create a proper mock header
        header = bytearray(144)
        header[0:4] = b"AESD"
        header[4] = 1
        header[16:32] = b"global_salt_test"
        header[32:48] = b"file_salt_test_!"
        
        # Calculate proper CRC32
        header_for_crc = bytes(header[0:12] + b'\x00\x00\x00\x00' + header[16:144])
        crc = binascii.crc32(header_for_crc)
        header[12:16] = crc.to_bytes(4, 'big')
        
        with patch('builtins.open', mock_open(read_data=bytes(header))):
            data_file = self.decryptor._load_data_file(Path("test.aesd"))
            assert isinstance(data_file, AESDataFile)
            assert data_file.file_type == "AESD"


class TestIntegration:
    """Integration tests for the complete system."""
    
    def test_crypto_workflow(self):
        """Test the complete cryptographic workflow."""
        # Test the key derivation and hash generation workflow
        password = "test_password"
        global_salt = b"global_salt_16_b"
        file_salt = b"file_salt_16_byt"
        
        # Derive password key
        pwd_key = CryptoHelper.derive_key_from_password(password, global_salt)
        assert len(pwd_key) == 32
        
        # Generate file seed and hash
        file_seed = file_salt + pwd_key
        file_hash = CryptoHelper.generate_file_hash(file_seed)
        assert len(file_hash) == 64
        
        # Extract components
        header_key = file_hash[:32]
        init_vector = file_hash[32:44]
        
        assert len(header_key) == 32
        assert len(init_vector) == 12


# Pytest configuration and fixtures
@pytest.fixture
def sample_config():
    """Provide a sample configuration for tests."""
    return Config()


@pytest.fixture
def sample_header():
    """Provide a sample valid AES Drive header for tests."""
    header = bytearray(144)
    header[0:4] = b"AESD"
    header[4] = 1
    header[16:32] = b"global_salt_test"
    header[32:48] = b"file_salt_test_!"
    
    # Calculate proper CRC32
    header_for_crc = bytes(header[0:12] + b'\x00\x00\x00\x00' + header[16:144])
    crc = binascii.crc32(header_for_crc)
    header[12:16] = crc.to_bytes(4, 'big')
    
    return bytes(header)


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v'])