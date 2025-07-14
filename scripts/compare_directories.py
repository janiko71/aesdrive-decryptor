#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OneDrive/P: Directory Comparer
Compares two directories accounting for .aesd/.aesf extensions added on OneDrive
"""

import os
import sqlite3
from pathlib import Path
from typing import Set, Tuple, Dict
import argparse
from datetime import datetime

class DirectoryComparer:
    def __init__(self, onedrive_path: str, p_drive_path: str, use_sqlite: bool = False):
        self.onedrive_path = Path(onedrive_path)
        self.p_drive_path = Path(p_drive_path)
        self.use_sqlite = use_sqlite
        self.db_path = "comparison.db" if use_sqlite else None
        
        # Extensions to remove on OneDrive
        self.onedrive_extensions = {'.aesd', '.aesf'}
        
    def setup_database(self):
        """Initialize SQLite database if requested"""
        if not self.use_sqlite:
            return None
            
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
        
        cursor.execute("DELETE FROM files_onedrive")
        cursor.execute("DELETE FROM files_p_drive")
        
        conn.commit()
        return conn
    
    def normalize_onedrive_filename(self, filename: str) -> str:
        """
        Remove .aesd or .aesf extension from OneDrive file
        """
        path = Path(filename)
        if path.suffix in self.onedrive_extensions:
            return str(path.with_suffix(''))
        return filename
    
    def scan_directory(self, directory: Path, is_onedrive: bool = False) -> Dict[str, dict]:
        """
        Scan a directory and return a dictionary of files
        """
        files_dict = {}
        
        if not directory.exists():
            print(f"⚠️ Warning: Directory {directory} does not exist!")
            return files_dict
        
        try:
            for root, dirs, files in os.walk(directory):
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
                        print(f"⚠️ Error accessing file {full_path}: {e}")
                        continue
                        
        except PermissionError as e:
            print(f"❌ Permission error for {directory}: {e}")
        except Exception as e:
            print(f"❌ Error scanning {directory}: {e}")
            
        return files_dict
    
    def store_in_database(self, conn, onedrive_files: Dict, p_drive_files: Dict):
        """Store files in SQLite database"""
        if not conn:
            return
            
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
    
    def compare_directories(self) -> Tuple[Set[str], Set[str]]:
        """
        Compare both directories and return files unique to each side
        """
        print(f"🔍 Scanning OneDrive directory: {self.onedrive_path}")
        onedrive_files = self.scan_directory(self.onedrive_path, is_onedrive=True)
        
        print(f"🔍 Scanning P: drive directory: {self.p_drive_path}")
        p_drive_files = self.scan_directory(self.p_drive_path, is_onedrive=False)
        
        print(f"📁 Files found on OneDrive: {len(onedrive_files)}")
        print(f"📁 Files found on P: drive: {len(p_drive_files)}")
        
        # Use SQLite if requested
        conn = None
        if self.use_sqlite:
            conn = self.setup_database()
            self.store_in_database(conn, onedrive_files, p_drive_files)
            print(f"💾 Data stored in {self.db_path}")
        
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
                       onedrive_files: Dict, p_drive_files: Dict):
        """Display comparison results"""
        
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

def main():
    parser = argparse.ArgumentParser(
        description="Compare files between OneDrive directory and P: drive directory"
    )
    parser.add_argument("onedrive_path", help="Path to OneDrive subdirectory")
    parser.add_argument("p_drive_path", help="Path to P: drive directory")
    parser.add_argument("--sqlite", action="store_true", 
                       help="Use SQLite to store results")
    parser.add_argument("--db-path", default="comparison.db", 
                       help="Path to SQLite database (default: comparison.db)")
    
    args = parser.parse_args()
    
    comparer = DirectoryComparer(args.onedrive_path, args.p_drive_path, args.sqlite)
    if args.sqlite:
        comparer.db_path = args.db_path
    
    try:
        comparer.compare_directories()
    except KeyboardInterrupt:
        print("\n⏹️ Comparison interrupted by user.")
    except Exception as e:
        print(f"❌ Error during comparison: {e}")

if __name__ == "__main__":
    # Usage example if script is run directly
    if len(os.sys.argv) == 1:
        print("📖 USAGE EXAMPLE:")
        print("python compare_directories.py 'C:/Users/User/OneDrive/MySubdirectory' 'P:/MyDirectory'")
        print("python compare_directories.py 'C:/Users/User/OneDrive/MySubdirectory' 'P:/MyDirectory' --sqlite")
        print("\n🔧 To see all options:")
        print("python compare_directories.py --help")
    else:
        main()
