#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OneDrive/P: Directory Comparer

This module provides functionality to compare two directories, accounting for
.aesd/.aesf extensions added by AES Drive on OneDrive. It helps identify files
that exist in one location but not the other.

Usage:
    python compare_directories.py [onedrive_path] [p_drive_path] [options]
    
    Options:
        --sqlite            Use SQLite to store results
        --db-path DB_PATH   Path to SQLite database (default: comparison.db)
        --help              Show help message and exit
"""

import os
import sys
import sqlite3
import argparse
import logging
from pathlib import Path
from typing import Set, Tuple, Dict, Optional, List
from datetime import datetime


class DirectoryComparer:
    """
    A class that compares files between OneDrive and P: drive directories.
    
    This class handles the comparison of files between two directories,
    accounting for the .aesd/.aesf extensions that AES Drive adds to files
    on OneDrive.
    """
    
    def __init__(self, onedrive_path: str, p_drive_path: str, use_sqlite: bool = False):
        """
        Initialize the DirectoryComparer with paths to compare.
        
        Args:
            onedrive_path: Path to the OneDrive directory
            p_drive_path: Path to the P: drive directory
            use_sqlite: Whether to store results in a SQLite database
        """
        self.onedrive_path = Path(onedrive_path)
        self.p_drive_path = Path(p_drive_path)
        self.use_sqlite = use_sqlite
        self.db_path = "comparison.db" if use_sqlite else None
        
        # Extensions to remove on OneDrive
        self.onedrive_extensions = {'.aesd', '.aesf'}
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_database(self) -> Optional[sqlite3.Connection]:
        """
        Initialize SQLite database for storing comparison results.
        
        Returns:
            SQLite connection object if use_sqlite is True, None otherwise
            
        Raises:
            sqlite3.Error: If there's an error creating the database
        """
        if not self.use_sqlite:
            return None
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS files_onedrive (
                    id INTEGER PRIMARY KEY,
                    original_name TEXT,
                    normalized_name TEXT,
                    full_path TEXT,
                    size INTEGER,
                    modified_time TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS files_p_drive (
                    id INTEGER PRIMARY KEY,
                    file_name TEXT,
                    full_path TEXT,
                    size INTEGER,
                    modified_time TEXT
                )
            """)
            
            # Clear existing data
            cursor.execute("DELETE FROM files_onedrive")
            cursor.execute("DELETE FROM files_p_drive")
            
            conn.commit()
            return conn
            
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise
    
    def normalize_onedrive_filename(self, filename: str) -> str:
        """
        Remove .aesd or .aesf extension from OneDrive file.
        
        Args:
            filename: The filename to normalize
            
        Returns:
            Normalized filename with AES Drive extension removed if present
        """
        path = Path(filename)
        if path.suffix in self.onedrive_extensions:
            return str(path.with_suffix(''))
        return filename
    
    def scan_directory(self, directory: Path, is_onedrive: bool = False) -> Dict[str, dict]:
        """
        Scan a directory and return a dictionary of files.
        
        Args:
            directory: The directory to scan
            is_onedrive: Whether this is an OneDrive directory
            
        Returns:
            Dictionary mapping normalized filenames to file metadata
        """
        files_dict = {}
        
        if not directory.exists():
            self.logger.warning(f"Directory {directory} does not exist!")
            return files_dict
        
        try:
            for root, _, files in os.walk(directory):
                for file in files:
                    full_path = Path(root) / file
                    relative_path = full_path.relative_to(directory)
                    
                    if is_onedrive:
                        # Normalize name for OneDrive
                        normalized_name = self.normalize_onedrive_filename(str(relative_path))
                        key = normalized_name
                    else:
                        key = str(relative_path)
                    
                    # Get metadata
                    try:
                        stat = full_path.stat()
                        files_dict[key] = {
                            'original_name': str(relative_path),
                            'full_path': str(full_path),
                            'size': stat.st_size,
                            'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'is_onedrive': is_onedrive
                        }
                    except OSError as e:
                        self.logger.error(f"Error accessing file {full_path}: {e}")
                        continue
                        
        except PermissionError as e:
            self.logger.error(f"Permission error for {directory}: {e}")
        except Exception as e:
            self.logger.error(f"Error scanning {directory}: {e}")
            
        return files_dict
    
    def store_in_database(self, conn: Optional[sqlite3.Connection], 
                         onedrive_files: Dict[str, dict], 
                         p_drive_files: Dict[str, dict]) -> None:
        """
        Store files in SQLite database.
        
        Args:
            conn: SQLite connection object
            onedrive_files: Dictionary of OneDrive files
            p_drive_files: Dictionary of P: drive files
        """
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            
            # Insert OneDrive files
            for normalized_name, file_info in onedrive_files.items():
                cursor.execute("""
                    INSERT INTO files_onedrive 
                    (original_name, normalized_name, full_path, size, modified_time)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    file_info['original_name'],
                    normalized_name,
                    file_info['full_path'],
                    file_info['size'],
                    file_info['modified_time']
                ))
            
            # Insert P: drive files
            for file_name, file_info in p_drive_files.items():
                cursor.execute("""
                    INSERT INTO files_p_drive 
                    (file_name, full_path, size, modified_time)
                    VALUES (?, ?, ?, ?)
                """, (
                    file_name,
                    file_info['full_path'],
                    file_info['size'],
                    file_info['modified_time']
                ))
            
            conn.commit()
            
        except sqlite3.Error as e:
            self.logger.error(f"Database error while storing data: {e}")
            conn.rollback()
    
    def compare_directories(self) -> Tuple[Set[str], Set[str]]:
        """
        Compare both directories and return files unique to each side.
        
        Returns:
            Tuple containing sets of files unique to OneDrive and P: drive
        """
        self.logger.info(f"Scanning OneDrive directory: {self.onedrive_path}")
        onedrive_files = self.scan_directory(self.onedrive_path, is_onedrive=True)
        
        self.logger.info(f"Scanning P: drive directory: {self.p_drive_path}")
        p_drive_files = self.scan_directory(self.p_drive_path, is_onedrive=False)
        
        print(f"📁 Files found on OneDrive: {len(onedrive_files)}")
        print(f"📁 Files found on P: drive: {len(p_drive_files)}")
        
        # Use SQLite if requested
        conn = None
        if self.use_sqlite:
            try:
                conn = self.setup_database()
                self.store_in_database(conn, onedrive_files, p_drive_files)
                print(f"💾 Data stored in {self.db_path}")
            except Exception as e:
                self.logger.error(f"Failed to store data in database: {e}")
        
        # Compare file sets
        onedrive_set = set(onedrive_files.keys())
        p_drive_set = set(p_drive_files.keys())
        
        only_onedrive = onedrive_set - p_drive_set
        only_p_drive = p_drive_set - onedrive_set
        
        # Display detailed results
        self.display_results(only_onedrive, only_p_drive, onedrive_files, p_drive_files)
        
        if conn:
            conn.close()
            
        return only_onedrive, only_p_drive
    
    def display_results(self, only_onedrive: Set[str], only_p_drive: Set[str], 
                       onedrive_files: Dict[str, dict], p_drive_files: Dict[str, dict]) -> None:
        """
        Display comparison results.
        
        Args:
            only_onedrive: Set of files only on OneDrive
            only_p_drive: Set of files only on P: drive
            onedrive_files: Dictionary of all OneDrive files
            p_drive_files: Dictionary of all P: drive files
        """
        print("\n" + "="*60)
        print("📊 COMPARISON RESULTS")
        print("="*60)
        
        if only_onedrive:
            print(f"\n🟦 FILES ONLY ON ONEDRIVE ({len(only_onedrive)}):")
            print("-" * 50)
            for file in sorted(only_onedrive):
                file_info = onedrive_files[file]
                size_mb = file_info['size'] / (1024 * 1024)
                print(f"  📄 {file_info['original_name']}")
                print(f"      └─ Size: {size_mb:.2f} MB | Modified: {file_info['modified_time'][:19]}")
                print(f"      └─ Path: {file_info['full_path']}")
                print()
        
        if only_p_drive:
            print(f"\n🟨 FILES ONLY ON P: DRIVE ({len(only_p_drive)}):")
            print("-" * 50)
            for file in sorted(only_p_drive):
                file_info = p_drive_files[file]
                size_mb = file_info['size'] / (1024 * 1024)
                print(f"  📄 {file}")
                print(f"      └─ Size: {size_mb:.2f} MB | Modified: {file_info['modified_time'][:19]}")
                print(f"      └─ Path: {file_info['full_path']}")
                print()
        
        if not only_onedrive and not only_p_drive:
            print("\n✅ PERFECT! All files are present on both sides.")
        
        # Statistics
        print(f"\n📈 STATISTICS:")
        print(f"   • Files identical on both sides: {len(set(onedrive_files.keys()) & set(p_drive_files.keys()))}")
        print(f"   • Files only on OneDrive: {len(only_onedrive)}")
        print(f"   • Files only on P: drive: {len(only_p_drive)}")
        print(f"   • Total OneDrive files: {len(onedrive_files)}")
        print(f"   • Total P: drive files: {len(p_drive_files)}")


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        Namespace containing the parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Compare files between OneDrive directory and P: drive directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python compare_directories.py 'C:/Users/User/OneDrive/MySubdirectory' 'P:/MyDirectory'
  python compare_directories.py 'C:/Users/User/OneDrive/MySubdirectory' 'P:/MyDirectory' --sqlite
        """
    )
    parser.add_argument("onedrive_path", help="Path to OneDrive subdirectory")
    parser.add_argument("p_drive_path", help="Path to P: drive directory")
    parser.add_argument("--sqlite", action="store_true", 
                       help="Use SQLite to store results")
    parser.add_argument("--db-path", default="comparison.db", 
                       help="Path to SQLite database (default: comparison.db)")
    
    return parser.parse_args()


def main() -> None:
    """
    Main function to run the directory comparison.
    """
    # If no arguments provided, show usage example
    if len(sys.argv) == 1:
        print("📖 USAGE EXAMPLE:")
        print("python compare_directories.py 'C:/Users/User/OneDrive/MySubdirectory' 'P:/MyDirectory'")
        print("python compare_directories.py 'C:/Users/User/OneDrive/MySubdirectory' 'P:/MyDirectory' --sqlite")
        print("\n🔧 To see all options:")
        print("python compare_directories.py --help")
        return
    
    # Parse arguments
    args = parse_arguments()
    
    # Create comparer
    comparer = DirectoryComparer(args.onedrive_path, args.p_drive_path, args.sqlite)
    if args.sqlite:
        comparer.db_path = args.db_path
    
    try:
        # Run comparison
        comparer.compare_directories()
    except KeyboardInterrupt:
        print("\n⏹️ Comparison interrupted by user.")
    except Exception as e:
        logging.error(f"Error during comparison: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()