# AES Drive Tools

A collection of Python tools for working with AES Drive encrypted files and directories.

## Overview

This repository contains tools for:

1. **AES Decryptor**: Decrypt files encrypted with AES Drive
2. **Directory Comparer**: Compare directories between OneDrive (with encrypted files) and P: drive (with unencrypted files)

## Requirements

- Python 3.6+
- Required packages:
  - cryptography
  - colorama
  - typing

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/aesdrive-zendev.git
   cd aesdrive-zendev
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## AES Decryptor

The AES Decryptor tool allows you to decrypt files that have been encrypted with AES Drive.

### Usage

```
python aesdecryptor.py [file] [options]
```

#### Options:
- `-p, --pwd PASSWORD`: Specify the AES Drive password
- `-h, --help`: Show help message and exit

#### Example:

```
python aesdecryptor.py myfile.docx.aesd -p mypassword
```

If no file is specified, you will be prompted to enter one. If no password is specified, you will be prompted to enter one.

## Directory Comparer

The Directory Comparer tool helps you compare files between an OneDrive directory (with encrypted files) and a P: drive directory (with unencrypted files).

### Usage

```
python compare_directories.py [onedrive_path] [p_drive_path] [options]
```

#### Options:
- `--sqlite`: Use SQLite to store results
- `--db-path DB_PATH`: Path to SQLite database (default: comparison.db)
- `--help`: Show help message and exit

#### Example:

```
python compare_directories.py "C:/Users/User/OneDrive/MySubdirectory" "P:/MyDirectory"
```

## File Format

The AES Drive file format is documented in the `res/aesdatafile.py` module. The format consists of:

- A 144-byte header containing:
  - File type identifier (4 bytes)
  - File type version (1 byte)
  - Reserved bytes (7 bytes)
  - CRC32 checksum (4 bytes)
  - Global salt (16 bytes)
  - File salt (16 bytes)
  - AES-GCM encrypted header (80 bytes)
  - AES-GCM authentication tag (16 bytes)
- Encrypted data in XTS-AES mode with 512-byte sectors

## Project Structure

```
aesdrive-zendev/
├── aesdecryptor.py           # Main AES decryption tool
├── compare_directories.py    # Directory comparison tool
├── res/
│   ├── aesdatafile.py        # AES Drive file format parser
│   └── fnhelper.py           # Helper functions
├── README.md                 # This file
└── LICENSE                   # License information
```

## License

See the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.