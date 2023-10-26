from pathlib import Path 

home = Path.home()

files = []

def add_files_from_dir(path: Path, files_str: str):
    for x in files_str.strip().split(' '):
        files.append(path / x)
