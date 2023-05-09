
import subprocess
from pathlib import Path 
import datetime
import tarfile
import shutil
from common import rclonedir


basepath = Path(__file__).resolve().parent

# homedir = basepath / "testdir"
homedir = Path().home().resolve()


print("HOME:", homedir)
statefile = basepath / ".state"
if not statefile.is_file() or statefile.read_text() == "": 
    print("new machine!")
    # statefile.write_text(datetime.datetime.now().isoformat(timespec='seconds'))
    statefile.touch()
    state = datetime.datetime.fromtimestamp(0)
else:
    state = datetime.datetime.fromisoformat(statefile.read_text())

remotebackups = []
i = 1
for f in subprocess.run(["rclone", "lsf", rclonedir], capture_output=True, text=True).stdout.strip("\n").split("\n"):
    x = Path(Path(f).stem)
    while x.suffixes:
        x = Path(x.stem)
    if x.name.startswith("backup-"):
        d = datetime.datetime.fromisoformat(x.name[7:])
        remotebackups.append((d, f)) 
        print(f"backup #{i}:", d)
        i += 1

print("local state:", state)
remotebackups = sorted(remotebackups, key=lambda x: x[0], reverse=True)

for d, f in remotebackups:
    if (d - state).total_seconds() > 0: 
        print(f"-> fetching {f}!")
        subprocess.run(["rclone", "copy", f"{rclonedir}/{f}", basepath])
        backuptar = basepath / f 
        def filter_func(info):
            print(info)
            return info 
        with tarfile.open(backuptar) as tar: 
            tar.extractall()
        backup_path = basepath / "backup"
        for obj in Path(backup_path).glob("*"):
            if obj.is_dir():
                dst = homedir / obj.relative_to(backup_path)
                shutil.copytree(obj, dst, dirs_exist_ok=True)
            elif obj.is_file():
                shutil.copyfile(obj, homedir / obj.relative_to(backup_path))
            else:
                raise Exception(obj)
        shutil.rmtree(backup_path)
        Path(backuptar).unlink()
        print("config has been updated")
        
        statefile.write_text(d.isoformat(timespec='seconds'))
        break
else:
    print("No updates!")
