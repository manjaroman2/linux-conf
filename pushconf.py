import os
import math
from pathlib import Path
import shutil
import tarfile
import datetime
import subprocess
from config import files, compression
from common import init_state, rclone_send, datetime_serialize, write_state, hash_bytes, state_print
from common import backup_path as backup
import argparse 

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--ask", action='store_true')
parser.add_argument("--debug", action='store_true')
args = parser.parse_args()

state = init_state()
abs_files = []

if not backup.is_dir():
    if backup.exists():
        ow = input(
            f"File {backup} already exists. Do you want to delete it? [y/N] " or "N")
        if ow != "y":
            exit(1)
        backup.unlink()
    backup.mkdir()
else:
    if f := list(backup.glob("./*")):
        if (ow := str(input(
            f"{len(f)} files exist in {backup}. \nDo you want to delete everything in the directory? [Y|n] " or "Y")).lower()) == "y":
            exit(1)
        shutil.rmtree(backup)
        backup.mkdir()

for f in files:
    if not f.exists():
        print(f"{f} does not exist. Skipping")
        continue
    # if f not in home.parents: 
    #     abs_files.append(f)
    p = backup / f.relative_to("/")
    # else:
    #     p = backup / f.relative_to(home)
    if not p.parent.exists():
        p.parent.mkdir(parents=True)
    if f.is_dir():
        shutil.copytree(f, p)
    else:
        shutil.copyfile(f, p)
    # print(f"  {f} -> {p}")


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def make_tarfile(output_filename, source_dir: Path, compression="xz"):
    class T:
        def __init__(self) -> None:
            self.fillchar = "--"
            self.level = 0
            self.curr_dir: Path = None
            self.levelcount = 0
            self.max_level_count = 5
        def fill(self):
            return self.fillchar*self.level
    def filter_func(info: tarfile.TarInfo, t: T):
        this_path = Path(info.name)
        print(t.curr_dir, this_path.as_posix().upper())
        if info.isdir():
            if t.curr_dir:
                # print(t.curr_dir, list(this_path.parents))
                if t.curr_dir not in this_path.parents: # Not subdir
                    # print(t.curr_dir.parts, this_path.parent.name) 
                    t.level = t.curr_dir.parts.index(this_path.parent.name)
                    t.levelcount = 0
            t.curr_dir = this_path 
            print(t.fill() + "📁 " + t.curr_dir.parts[t.level])
            t.level += 1
            t.levelcount = 0
        elif t.curr_dir:
            # print(t.curr_dir)
            if t.curr_dir not in this_path.parents:
                t.level = 0
                t.levelcount = 0
                t.curr_dir = None 
                print("+ " + this_path.as_posix())
            else:
                print(t.fill(), this_path.name)
        else:
            print("+ " + info.name)
            
        info.mtime = 0 # So the hashes will match
        info.uid = 0
        info.uname = ''
        info.gid = 0
        info.gname = ''
        info.pax_headers = {}
        return info 
    t = T()
    with tarfile.open(output_filename, f"w:{compression}") as tar:
        tar.add(source_dir, arcname=source_dir.stem, filter=lambda info: filter_func(info, t))


def dirsize(path):
    return sum(os.path.getsize(os.path.join(dirpath, filename)) for dirpath, _, filenames in os.walk(path) for filename in filenames)


c = f".{compression}" if compression else ""
d = datetime.datetime.now()
backup_compressed = backup.parent / f"backup-{datetime_serialize(d)}.tar{c}"


print(f"Compressing {compression} file: {backup_compressed.name}")
make_tarfile(backup_compressed, backup, compression)
if args.debug:
    exit(0)

hashed = hash_bytes(backup_compressed.read_bytes())

print(state_print(state), "<-- old")
print(state_print([0, hashed]), "<-- new")
if hashed == state[1]:
    print("  No changes since last backup. Exiting.")
    # if (ask := str(input("  New backup is identical to current state. \nDo you want to proceed? [y|N]") or "N").lower()) != "y":
    shutil.rmtree(backup)
    backup_compressed.unlink()
    quit(1)
        
bs = dirsize(backup)
bcs = backup_compressed.stat().st_size
print(
    f"Backup size: {convert_size(bs)}\t>>>\t{convert_size(bcs)} compressed ({round(bcs/bs*100, 1)}%)")
shutil.rmtree(backup)

if args.ask: 
    if (ask := str(input("Send it?  [Y|n]") or "Y").lower()) == "y":
        subprocess.run(rclone_send(backup_compressed))
        print(f"{backup_compressed} pushed!")
else:
    subprocess.run(rclone_send(backup_compressed))
    print(f"{backup_compressed} pushed!")
backup_compressed.unlink()
if (d - state[0]).total_seconds() > 0: 
    print(f"local state -> {write_state(d, hashed)}")
