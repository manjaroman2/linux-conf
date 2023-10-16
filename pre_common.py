from pathlib import Path 

files = []

def add_files_from_dir(path: Path, files_str: str):
    for x in files_str.strip().split(' '):
        files.append(path / x)
