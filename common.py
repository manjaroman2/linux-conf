from pathlib import Path 
import datetime
import hashlib

import config 
from config import rclonedir, files

pullconf_sh_build = lambda p: f"""#!/usr/bin/bash
oldpwd=$(pwd)
cd {p}
echo "checking internet connection" 
python checkhimpc.py
hasNet=$?
if [ $hasNet -ne 0 ]; then
    echo "  ✓ has internet" 
    git pull &> /dev/null 
    python pullconf.py $@ 
else
    echo "  ❌ no internet, exiting"
fi 
cd $oldpwd
""" 
pushconf_sh_build = lambda p: f"""#!/usr/bin/bash
oldpwd=$(pwd)
cd {p} 
git commit -am "pushconf" &> /dev/null 
git push &> /dev/null 
python pushconf.py $@ 
cd $oldpwd
"""
basepath = Path(__file__).resolve().parent
has_bin_path = hasattr(config, "bin_path") 
if has_bin_path:
    from config import bin_path 
    pushconf_sh = (bin_path / "pushconf", pushconf_sh_build(basepath.as_posix()))   
    pullconf_sh = (bin_path / "pullconf", pullconf_sh_build(basepath.as_posix())) 
    files.append(pushconf_sh[0])
    files.append(pullconf_sh[0])

backup_path = basepath / "backup"
statefile = basepath / ".state"

rclone_lsf = ["rclone", "lsf", rclonedir]
rclone_copy = lambda remote_path = "": ["rclone", "copy", "-P", "-M", Path(rclonedir) / remote_path, basepath]
rclone_send = lambda backup_compressed: ["rclone", "copy", "-L", "-P", "-M", backup_compressed, rclonedir]
datetime_serialize = lambda d: d.isoformat(timespec='seconds')

def init_state() -> datetime.datetime:
    if has_bin_path:
        import stat 
        pushconf_sh[0].write_text(pushconf_sh[1])
        pullconf_sh[0].write_text(pullconf_sh[1])
        pushconf_sh[0].chmod(pushconf_sh[0].stat().st_mode | stat.S_IEXEC)
        pullconf_sh[0].chmod(pullconf_sh[0].stat().st_mode | stat.S_IEXEC)
    if not statefile.is_file() or statefile.read_text() == "": 
        print("New machine!")
        statefile.touch()
        dt = datetime.datetime.fromtimestamp(0)
        hashed = ''
    else:
        sp = statefile.read_text().split(' ')
        dt = datetime.datetime.fromisoformat(sp[0])
        hashed = sp[1]
    return dt, hashed

def write_state(d: datetime.datetime, hashed: str) -> str:
    s = datetime_serialize(d)
    statefile.write_text(f"{s} {hashed}")
    return s 

def hash_bytes(data: bytes) -> str:
    o = hashlib.sha512()
    o.update(data)
    return o.hexdigest()
