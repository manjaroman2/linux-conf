import os
import math
from pathlib import Path
import shutil
import tarfile
import datetime
from config import files, compression
from common import (
    state_init,
    rclone_cmd_send,
    hash_bytes,
    state_write,
    state_print,
    has_internet,
    run_command,
    datetime_serialize,
    parse_rclone_transfer
)
from common import backup_path as backup
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--ask", action="store_true")
parser.add_argument("--debug", action="store_true")
args = parser.parse_args()


print("checking internet connection")
if has_internet():
    print("  ✓ has internet")
    run_command("git pull", lambda line: print(' ', line.strip()))
    run_command("git commit -am pushconf", lambda line: print(' ', line.strip()))
    run_command("git push", lambda line: print(' ', line.strip()))
else:
    print("  ❌ no internet, exiting")
    exit(1)

state = state_init()

print("  local state:", state_print(state, True))

abs_files = []

if not backup.is_dir():
    if backup.exists():
        ow = input(
            f"File {backup} already exists. Do you want to delete it? [y/N] " or "N"
        )
        if ow != "y":
            exit(1)
        backup.unlink()
    backup.mkdir()
else:
    if f := list(backup.glob("./*")):
        shutil.rmtree(backup)
        backup.mkdir()

for f in files:
    if not f.exists():
        print(f"{f} does not exist. Skipping")
        continue
    p = backup / f.relative_to("/")
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
            self.last: Path = None
            self.levelcount = 0
            self.max_level_count = 5

        def fill(self):
            return self.fillchar * self.level

    def filter_func(info: tarfile.TarInfo, t: T):
        this_path = Path(info.name)
        """
        yeah, am hyp-no-tised by the liight
        I'm coming home I'm coming down toniight
        """
        # TODO display directories nicely (I'm too stupid for this)

        # Remove all the metadata, so the hashes will match
        info.mtime = 0
        info.uid = 0
        info.uname = ""
        info.gid = 0
        info.gname = ""
        info.pax_headers = {}
        return info

    t = T()
    with tarfile.open(output_filename, f"w:{compression}") as tar:
        tar.add(
            source_dir,
            arcname=source_dir.stem,
            filter=lambda info: filter_func(info, t),
        )


def dirsize(path):
    return sum(
        os.path.getsize(os.path.join(dirpath, filename))
        for dirpath, _, filenames in os.walk(path)
        for filename in filenames
    )


c = f".{compression}" if compression else ""
d = datetime.datetime.now()
backup_compressed: Path = backup.parent / f"backup-{datetime_serialize(d)}.tar{c}"


print(f"compressing {compression} file: {backup_compressed.name}")
make_tarfile(backup_compressed, backup, compression)
if args.debug:
    exit(0)

hashed = hash_bytes(backup_compressed.read_bytes())

print("  local state:     ", state_print(state))
print("  compressed state:", state_print([0, hashed]))
if hashed == state[1]:
    print("  No local changes since last backup. Exiting.")
    shutil.rmtree(backup)
    backup_compressed.unlink()
    exit(0)

bs = dirsize(backup)
bcs = backup_compressed.stat().st_size
print(
    f"  backup size: {convert_size(bs)} >>> {convert_size(bcs)} compressed ({round(bcs/bs*100, 1)}%)"
)
shutil.rmtree(backup)

def send():
    run_command(rclone_cmd_send(backup_compressed), parse_rclone_transfer, end="\n")
    print(f"{backup_compressed} pushed!")

if args.ask:
    if (ask := str(input("  send it?  [Y|n]") or "Y").lower()) == "y":
        send()
else:
    send()

backup_compressed.unlink()
if (d - state[0]).total_seconds() > 0:
    state = (d, hashed)
    state_write(state)
    print("local state:", state_print(state, date=True))
