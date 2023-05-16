import math
from pathlib import Path
import shutil
import tarfile
import datetime
import subprocess
from common import rclonedir, compression, files, home, statefile, basepath

backup = basepath / "backup"

if not statefile.is_file() or statefile.read_text() == "": 
    print("new machine!")
    # statefile.write_text(datetime.datetime.now().isoformat(timespec='seconds'))
    statefile.touch()
    state = datetime.datetime.fromtimestamp(0)
else:
    state = datetime.datetime.fromisoformat(statefile.read_text())

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
        ow = input(
            f"{len(f)} files exist in {backup}. \nDo you want to delete everything in the directory? [y/N] " or "N")
        if ow != "y":
            exit(1)
        shutil.rmtree(backup)
        backup.mkdir()

for f in files:
    if not f.exists():
        print(f"{f} does not exist. Skipping")
        continue
    p = backup / f.relative_to(home)
    if not p.parent.exists():
        p.parent.mkdir(parents=True)
    if f.is_dir():
        shutil.copytree(f, p)
    else:
        shutil.copyfile(f, p)
    print(f"  {f} -> {p}")


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def make_tarfile(output_filename, source_dir: Path, compression="xz"):
    def filter_func(info):
        print(info.name)
        return info 
    with tarfile.open(output_filename, f"w:{compression}") as tar:
            
        tar.add(source_dir, arcname=source_dir.stem, filter=filter_func)


def dirsize(path):
    import os
    return sum(os.path.getsize(os.path.join(dirpath, filename)) for dirpath, _, filenames in os.walk(path) for filename in filenames)


c = f".{compression}" if compression else ""
d = datetime.datetime.now()
backup_compressed = backup.parent / f"backup-{d.isoformat(timespec='seconds')}.tar{c}"
print(f"Compressing {compression} file: {backup_compressed.name}")
make_tarfile(backup_compressed, backup, compression)

bs = dirsize(backup)
bcs = backup_compressed.stat().st_size
print(
    f"Backup size: {convert_size(bs)}\t>>>\t{convert_size(bcs)} compressed ({round(bcs/bs*100, 1)}%)")
shutil.rmtree(backup) 
subprocess.run(["rclone", "copy", "-L", "-P", "-M", backup_compressed, rclonedir])
backup_compressed.unlink()
if (d - state).total_seconds() > 0: 
    statefile.write_text(d.isoformat(timespec='seconds'))
    print(f"local state -> {d.isoformat(timespec='seconds')}")
print(f"{backup_compressed} pushed!")
exit(0)
