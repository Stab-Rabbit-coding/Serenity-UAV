import os
import subprocess
from pathlib import Path
from datetime import datetime

# Root directory configuration
ROOT_DIR = "."
# Directories to always ignore (system, git metadata, and internal caches)
IGNORE_DIRS = {'.git', '__pycache__', 'venv', 'env', '.ipynb_checkpoints'}
# Directories requiring index tracking (including hidden ones)
TRACKED_DIRS = {'.github', '.githooks', 'airframe', 'archives', 'avionics', 'current-specification', 'deferred', 'docs', 'gcs', 'graphical-build-guide', 'node_modules', 'tools'}

INDEX_CONFIG = {
    "PROJECT_INDEX.md": 3,
    "ARCHIVE_INDEX.md": 4
}

def get_ignored_files():
    try:
        cmd = ["git", "ls-files", "--others", "--ignored", "--exclude-standard"]
        return set(subprocess.check_output(cmd).decode("utf-8").splitlines())
    except subprocess.CalledProcessError:
        return set()

def sync_and_format():
    # Discover all files in TRACKED_DIRS recursively
    current_files = set()
    for d in TRACKED_DIRS:
        if os.path.exists(d):
            for root, dirs, files in os.walk(d):
                # Modify dirs in-place to prevent walking into ignored directories
                dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
                for f in files:
                    if not f.endswith(('.FCBak', '.rpt')):
                        current_files.add(os.path.join(root, f))
    
    ignored_files = get_ignored_files()

    for index_name, date_line_idx in INDEX_CONFIG.items():
        index_path = Path(index_name)
        if not index_path.exists(): continue
        
        with open(index_path, 'r') as f:
            lines = f.readlines()

        clean_lines = []
        indexed_paths = set()
        for line in lines:
            if " — " in line and not line.strip().startswith(('#', '-')):
                path = line.split(" — ")[0].strip()
                if os.path.exists(path):
                    clean_lines.append(line)
                    indexed_paths.add(path)
            else:
                clean_lines.append(line)

        new_items = []
        for f in sorted(current_files):
            if f not in indexed_paths:
                new_items.append(f"{f} — [PENDING AI CLASSIFICATION]\n")
        for f in sorted(ignored_files):
            if f not in indexed_paths and any(f.startswith(d) for d in TRACKED_DIRS):
                new_items.append(f"{f} — [IGNORED/VCS-EXCLUDED]\n")

        if new_items or len(clean_lines) != len(lines):
            if new_items:
                # Append new items before existing auto-discovered headers if possible, 
                # or just append to end
                clean_lines.append(f"\n## --- AUTO-DISCOVERED ({datetime.now().strftime('%Y-%m-%d')}) ---\n")
                clean_lines.extend(new_items)
            
            if len(clean_lines) > date_line_idx:
                clean_lines[date_line_idx] = f"<!-- Last updated: {datetime.now().strftime('%Y-%m-%d')} — Automated reconciliation pass -->\n"
            
            with open(index_path, 'w') as f:
                f.writelines(clean_lines)

if __name__ == "__main__":
    sync_and_format()