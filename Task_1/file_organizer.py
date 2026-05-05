# -*- coding: utf-8 -*-
"""
Created on Tue May  5 20:29:17 2026

@author: SHITANSHU KUMAR
"""

import os
import shutil
import logging
import argparse
from pathlib import Path

# Logging setup: Records all operations in organizer.log[cite: 1]
logging.basicConfig(
    filename='organizer.log', 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Extension mapping[cite: 1]
CATEGORIES = {
    ".py": "Python_Code",
    ".txt": "Documents",
    ".pdf": "Documents",
    ".docx": "Documents",
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".mp3": "Music",
    ".mp4": "Videos",
    ".zip": "Archives",
}

def get_unique_path(path):
    """Handles filename conflicts[cite: 1]"""
    counter = 1
    original_path = path
    while path.exists():
        path = original_path.with_name(f"{original_path.stem}({counter}){original_path.suffix}")
        counter += 1
    return path

def organize_directory(source_path, dry_run=False):
    """Main function to organize files[cite: 1]"""
    source = Path(source_path)
    if not source.exists() or not source.is_dir():
        print(f"Error: Invalid path '{source_path}'")
        return

    print(f"Status: {'Dry-run' if dry_run else 'Organizing'}...")
    for item in source.iterdir():
        if item.is_file() and item.name not in ['file_organizer.py', 'organizer.log']:
            try:
                ext = item.suffix.lower()
                category = CATEGORIES.get(ext, "Other")
                target_dir = source / category
                
                if not dry_run:
                    target_dir.mkdir(exist_ok=True)
                    target_path = get_unique_path(target_dir / item.name)
                    shutil.move(str(item), str(target_path))
                    logging.info(f"Moved: {item.name} to {category}")
                else:
                    print(f"[PREVIEW] Would move {item.name} to {category}")
            except Exception as e:
                logging.error(f"Error: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    organize_directory(args.source, args.dry_run)