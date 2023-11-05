from pathlib import Path
from datetime import datetime
import tarfile
import shutil
import sys
from os import get_terminal_size
from common import (
    rclone_cmd_lsf,
    rclone_cmd_copy,
    basepath,
    state_init,
    state_write,
    hash_bytes,
    has_bin_path,
    has_internet,
    state_print,
    run_command,
)
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--force", action="store_true")
parser.add_argument(
    "--just-dl", action="store_true", help="Just download, don't overwrite"
)
args = parser.parse_args()

print("checking internet connection")
if has_internet():
    print("  ✓ has internet")
    run_command("git pull", lambda line: print(" ", line.strip()))
else:
    print("  ❌ no internet, exiting")
    exit(1)

state = state_init()

print(f"  local state: {state_print(state, date=True)}")
# print(f"  local state: \n    {state[0]} | {get_state_hash(state)} ({hash_algorithm.__name__})")

remotebackups = []


def parse_rclone_cmd_lsf(line):
    line = line.strip("\n")
    x = Path(Path(line).stem)
    while x.suffixes:
        x = Path(x.stem)
    if x.name.startswith("backup-"):
        d = datetime.fromisoformat(x.name[7:])
        remotebackups.append((d, line))


run_command(rclone_cmd_lsf(), parse_rclone_cmd_lsf)

print(f"  Found {len(remotebackups)} backups")
print(f"    -- Date -- -- Time --")
for d, f in remotebackups[-5:]:
    print(f"    {d}")

if args.force:
    valid_remote_backups = remotebackups
else:
    valid_remote_backups = [
        (d, f) for d, f in remotebackups if (d - state[0]).total_seconds() > 0
    ]

valid_remote_backups = sorted(valid_remote_backups, key=lambda x: x[0])
print(f"  Found {len(valid_remote_backups)} newer backups")
if len(valid_remote_backups) == 0:
    print("  Is already on newest state. Exiting")
    exit(1)
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
    print(f"  {j}{days:9} {hours:9}ago  ({''.join(Path(f).suffixes)})")

    i -= 1
idx = (
    len(valid_remote_backups)
    - 1
    - int(
        input(f"  Which backup to load [0-{len(valid_remote_backups)-1}]  [0]") or "0"
    )
)
f = valid_remote_backups[idx][1]


def parse_rclone_cmd_copy(line):
    i = 1
    if line.startswith("Transferred"):
        msg = ["\r    ", line.strip().replace("\t", ""), "." * i]
        padding = " " * (get_terminal_size().columns - len("".join(msg)))
        msg.append(padding)
        print("".join(msg), end="", flush=True)
        i += 1
    print()


run_command(rclone_cmd_copy(f), parse_rclone_cmd_copy)

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
            run_command(f"/usr/bin/sudo python -c {python_code}")
            # subprocess.call(["/usr/bin/sudo", "python", "-c", python_code])
with tarfile.open(backuptar) as tar:
    tar.extractall(basepath)
if args.just_dl:
    Path(backuptar).unlink()
    print("just-dl flag was passed, exiting")
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
                run_command(f"/usr/bin/sudo python -c {python_code}")
                # ret = subprocess.call(["/usr/bin/sudo", "python", "-c", python_code])
            else:
                print(e)
                exit(1)
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
                run_command(f"/usr/bin/sudo python -c {python_code}")
            else:
                print(e)
                exit(1)
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
        run_command(f"/usr/bin/sudo python -c {python_code}")
else:
    shutil.rmtree(backup_path)

state_write((d, hash_bytes(backuptar.read_bytes())))
print("config has been updated")

# Make all files in bin_path executable because some remotes don't keep file permissions (too bad)
if has_bin_path:
    from config import bin_path
    import stat

    for file in bin_path.glob("./*"):
        file.chmod(file.stat().st_mode | stat.S_IEXEC)

exit(0)
