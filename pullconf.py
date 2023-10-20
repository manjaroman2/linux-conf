
import subprocess
from pathlib import Path 
from datetime import datetime
import tarfile
import shutil
from common import rclone_lsf, rclone_copy, basepath, init_state, write_state, hash_bytes, has_bin_path
from config import home

state = init_state()

remotebackups = []
for f in subprocess.run(rclone_lsf, capture_output=True, text=True).stdout.strip("\n").split("\n"):
    x = Path(Path(f).stem)
    while x.suffixes:
        x = Path(x.stem)
    if x.name.startswith("backup-"):
        d = datetime.fromisoformat(x.name[7:])
        remotebackups.append((d, f)) 
        # print(f"backup #{i}:", d)

print(f" Found {len(remotebackups)} backups on remote. ")
print(state[1] + "  <-- local state")
valid_remote_backups = [(d, f) for d, f in remotebackups if (d - state[0]).total_seconds() > 0]
if len(valid_remote_backups) == 0: 
    print("  No newer backups on remote than local state")
    exit(1)
print(f" Found {len(valid_remote_backups)} newer backups on remote. ")
valid_remote_backups = sorted(valid_remote_backups, key=lambda x: x[0])
i = len(valid_remote_backups)-1
for d, f in valid_remote_backups:
    dt = (datetime.now() - d)
    days = dt.days
    if days == 0:
        days = ""
    else:
        days = f"{days:3} days "
    hours = dt.seconds//3600
    if hours == 0:
        hours = ""
    else:
        hours = f"{hours:2} hours "
    # minutes = (dt.seconds//60)%60
    # if (minutes == 0):
    #     minutes = ""
    # else:
    #     minutes = f"{minutes:2} minutes "
    j = f"[{i:2}"
    if i % 2 == 0:
        j += "]--"
        if days == "":
            days = "--------"
    else:
        j += "]  "
    # print(f"{j:5} {days:9}{hours:9}{minutes:11}ago  ({''.join(Path(f).suffixes)})")
    print(f"{j}{days:9} {hours:9}ago  ({''.join(Path(f).suffixes)})")

    i -= 1
idx = len(valid_remote_backups) - 1- int(input(f" Which backup to load [0-{len(valid_remote_backups)-1}]?  [0]") or "0")
print(idx)
f = valid_remote_backups[idx][1]

print(f"-> fetching {f}!")
subprocess.run(rclone_copy(f))
backuptar = basepath / f 
with tarfile.open(backuptar) as tar: 
    tar.extractall(basepath)
backup_path = basepath / "backup"
root_path = Path.home().parts[0]
for obj in Path(backup_path).glob("*"):
    dst = root_path / obj.relative_to(backup_path)
    print(dst)
    if obj.is_dir():
        try:
            shutil.copytree(obj, dst, dirs_exist_ok=True)
        except shutil.Error as e:
            print(e)
    elif obj.is_file():
        shutil.copyfile(obj, dst) 
    else:
        raise Exception(obj)
shutil.rmtree(backup_path)
write_state(d, hash_bytes(backuptar.read_bytes()))
Path(backuptar).unlink()
print("config has been updated")

# Make all files in bin_path executable because some remotes don't keep file permissions (too bad)
if has_bin_path:
    from config import bin_path 
    import stat
    for file in bin_path.glob("./*"):
        file.chmod(file.stat().st_mode | stat.S_IEXEC)

exit(0)
