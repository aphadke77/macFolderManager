#!/usr/bin/env python3
"""
File Organizer
--------------
Automatically organizes files in a source folder into category folders
(Images, Docs, PDF, etc.) based on file extension.

Usage:
    python file_organizer.py --src downloads
    python file_organizer.py --src downloads --dry-run
    python file_organizer.py --src downloads --dest ~/Organized --recursive
"""

import os
import shutil
import argparse
from datetime import datetime

# --- Extension -> Category mapping -----------------------------------------
CATEGORY_MAP = {
    "Images": ["jpg", "jpeg", "png", "gif", "bmp", "svg", "webp", "heic"],
    "PDF": ["pdf"],
    "Docs": ["doc", "docx", "txt", "rtf", "odt", "md"],
    "Spreadsheets": ["xls", "xlsx", "csv"],
    "Slides": ["ppt", "pptx", "key"],
    "Audio": ["mp3", "wav", "aac", "flac", "m4a"],
    "Video": ["mp4", "mov", "avi", "mkv", "webm"],
    "Archives": ["zip", "rar", "7z", "tar", "gz"],
    "Code": ["py", "js", "html", "css", "json", "java", "cpp", "c", "sh"],
}

# Build reverse lookup: extension -> category
EXT_TO_CATEGORY = {
    ext: category for category, exts in CATEGORY_MAP.items() for ext in exts
}

MISC_CATEGORY = "Misc"


def get_category(filename: str) -> str:
    """Return the category folder name for a given filename."""
    if "." not in filename:
        return MISC_CATEGORY
    ext = filename.rsplit(".", 1)[-1].lower()
    return EXT_TO_CATEGORY.get(ext, MISC_CATEGORY)


def unique_destination(dest_folder: str, filename: str) -> str:
    """Avoid overwriting existing files by appending (1), (2), etc."""
    base, ext = os.path.splitext(filename)
    candidate = os.path.join(dest_folder, filename)
    counter = 1
    while os.path.exists(candidate):
        candidate = os.path.join(dest_folder, f"{base} ({counter}){ext}")
        counter += 1
    return candidate


def organize(src: str, dest: str, dry_run: bool = False, recursive: bool = False):
    if not os.path.isdir(src):
        print(f"Source folder not found: {src}")
        return

    summary = {}
    log_lines = []

    def process_folder(folder):
        for name in os.listdir(folder):
            full_path = os.path.join(folder, name)

            if os.path.isdir(full_path):
                if recursive:
                    process_folder(full_path)
                continue

            category = get_category(name)
            target_folder = os.path.join(dest, category)

            if not dry_run:
                os.makedirs(target_folder, exist_ok=True)

            target_path = unique_destination(target_folder, name) if os.path.isdir(target_folder) else os.path.join(target_folder, name)

            if dry_run:
                log_lines.append(f"[DRY RUN] {full_path}  ->  {target_path}")
            else:
                shutil.move(full_path, target_path)
                log_lines.append(f"{full_path}  ->  {target_path}")

            summary[category] = summary.get(category, 0) + 1

    process_folder(src)

    # Print log
    for line in log_lines:
        print(line)

    # Print summary
    total = sum(summary.values())
    print("\n--- Summary ---")
    if total == 0:
        print("No files found to organize.")
    else:
        for category, count in sorted(summary.items(), key=lambda x: -x[1]):
            print(f"{category}: {count} file(s)")
        print(f"Total: {total} file(s)")
        if dry_run:
            print("(dry run - no files were actually moved)")

    # Write a log file for real runs
    if not dry_run and log_lines:
        log_path = os.path.join(dest, f"organize_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(log_path, "w") as f:
            f.write("\n".join(log_lines))
        print(f"\nLog saved to: {log_path}")


def main():
    parser = argparse.ArgumentParser(description="Organize files into category folders.")
    parser.add_argument("--src", required=True, help="Source folder to organize")
    parser.add_argument("--dest", default=None, help="Destination root folder (default: same as src)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without moving files")
    parser.add_argument("--recursive", action="store_true", help="Also organize files in subfolders")
    args = parser.parse_args()

    dest = args.dest or args.src
    organize(args.src, dest, dry_run=args.dry_run, recursive=args.recursive)


if __name__ == "__main__":
    main()
