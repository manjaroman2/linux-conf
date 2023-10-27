import subprocess
from pathlib import Path
from datetime import datetime
import tarfile
import shutil
import sys 
from common import (
    rclonedir,
    rclone_lsf,
    rclone_copy,
    basepath,
    init_state,
    write_state,
    hash_bytes,
    has_bin_path,
)
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--force", action="store_true")
parser.add_argument("--just-dl", action="store_true", help="Just download, don't overwrite")
args = parser.parse_args()

state = init_state()

remotebackups = []
print(f"Checking {rclonedir}")
for f in (
    subprocess.run(rclone_lsf, capture_output=True, text=True)
    .stdout.strip("\n")
    .split("\n")
):
    x = Path(Path(f).stem)
    while x.suffixes:
        x = Path(x.stem)
    if x.name.startswith("backup-"):
        d = datetime.fromisoformat(x.name[7:])
        remotebackups.append((d, f))
        # print(f"backup #{i}:", d)

print(f"  Found {len(remotebackups)} backups")
print('  ' + state[1][:16] + "...  <-- local state")
if not args.force:
    valid_remote_backups = [
        (d, f) for d, f in remotebackups if (d - state[0]).total_seconds() > 0
    ]
else:
    valid_remote_backups = remotebackups
if not args.just_dl:
    if len(valid_remote_backups) == 0:
        print("  Is already on newest state. Exiting")
        exit(1)
    print(f" Found {len(valid_remote_backups)} newer backups on remote. ")
valid_remote_backups = sorted(valid_remote_backups, key=lambda x: x[0])
i = len(valid_remote_backups) - 1
for d, f in valid_remote_backups:
    dt = datetime.now() - d
    days = dt.days
    if days == 0:
        days = ""
    else:
        days = f"{days:3} days "
    hours = dt.seconds // 3600
    if hours == 0:
        hours = " 0 hours"
    else:
        hours = f"{hours:2} hours "
    j = f"[{i:2}"
    if i % 2 == 0:
        j += "]--"
        if days == "":
            days = "--------"
    else:
        j += "]  "
    print(f"{j}{days:9} {hours:9}ago  ({''.join(Path(f).suffixes)})")

    i -= 1
idx = (
    len(valid_remote_backups)
    - 1
    - int(
        input(f" Which backup to load [0-{len(valid_remote_backups)-1}]  [0]") or "0"
    )
)
f = valid_remote_backups[idx][1]

print(f"-> fetching {f}!")
subprocess.run(rclone_copy(f))
backuptar = basepath / f

backup_path = basepath / "backup"
if backup_path.exists():
    try:
        shutil.rmtree(backup_path)
    except shutil.Error as e:
        if sys.platform == "linux":
            python_code = f"""
    from pathlib import Path
    backup_path=Path("{backup_path}")
    import shutil
    shutil.rmtree(backup_path)
            """
            subprocess.call(["/usr/bin/sudo", "python", "-c", python_code])
with tarfile.open(backuptar) as tar:
    tar.extractall(basepath)
if args.just_dl:
    Path(backuptar).unlink()
    exit(0)
if args.force:
    input()
root_path = Path.home().parts[0]
needs_sudo = False  
for obj in Path(backup_path).glob("*"):
    dst = root_path / obj.relative_to(backup_path)
    print(dst)
    if obj.is_dir():
        try:
            shutil.copytree(obj, dst, dirs_exist_ok=True)
        except shutil.Error as e:
            needs_sudo = True
            if sys.platform == "linux":
                python_code = f"""
from pathlib import Path 
obj=Path("{obj}")
dst=Path("{dst}")
import shutil
shutil.copytree(obj, dst, dirs_exist_ok=True)
                """
                # print(python_code)
                ret = subprocess.call(["/usr/bin/sudo", "python", "-c", python_code])
            else:
                print(e)
    elif obj.is_file():
        try:
            shutil.copyfile(obj, dst)
        except:
            needs_sudo = True
            if sys.platform == "linux":
                python_code = f"""
from pathlib import Path 
obj=Path("{obj}")
dst=Path("{dst}")
import shutil
shutil.copyfile(obj, dst)
                """
                # print(python_code)
                ret = subprocess.call(["/usr/bin/sudo", "python", "-c", python_code])
            else:
                print(e)
    else:
        raise Exception(obj)
if needs_sudo:
    if sys.platform == "linux":
        python_code = f"""
from pathlib import Path
backup_path=Path("{backup_path}")
import shutil
shutil.rmtree(backup_path)
        """
        subprocess.call(["/usr/bin/sudo", "python", "-c", python_code])
else:        
    shutil.rmtree(backup_path)
write_state(d, hash_bytes(backuptar.read_bytes()))
print("config has been updated")

# Make all files in bin_path executable because some remotes don't keep file permissions (too bad)
if has_bin_path:
    from config import bin_path
    import stat

    for file in bin_path.glob("./*"):
        file.chmod(file.stat().st_mode | stat.S_IEXEC)

exit(0)
