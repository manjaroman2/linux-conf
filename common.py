from pathlib import Path 
import datetime
import subprocess
import hashlib

import config 
from config import rclonedir, files

import socket

def has_internet(host="8.8.8.8", port=53, timeout=3) -> bool:
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(' ', ex)
        return False


def run_command(cmd, callback = None):
    print(f'$ {cmd}')
    if not callback:
        callback = lambda line: print(repr(line))
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
    for line in p.stdout:
        callback(line.decode())         


pullconf_sh_build = lambda p: f"""#!/usr/bin/bash
oldpwd=$(pwd)
cd {p}
python pullconf.py $@ 
cd $oldpwd
""" 
pushconf_sh_build = lambda p: f"""#!/usr/bin/bash
oldpwd=$(pwd)
cd {p} 
python pushconf.py $@ 
cd $oldpwd
"""

hash_algorithm = hashlib.sha512

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

rclone_cmd_lsf = lambda: f"rclone lsf {rclonedir}"
rclone_cmd_copy = lambda remote_path = "": ["rclone", "copy", "-P", "-vvv", "-M", (Path(rclonedir) / remote_path).as_posix(), basepath.as_posix()]
rclone_send = lambda backup_compressed: ["rclone", "copy", "-L", "-P", "-M", backup_compressed, rclonedir]
datetime_serialize = lambda d: d.isoformat(timespec='seconds')

def init_state() -> datetime.datetime:
    print("initializing state")
    if has_bin_path:
        import stat 
        pushconf_sh[0].write_text(pushconf_sh[1])
        pullconf_sh[0].write_text(pullconf_sh[1])
        pushconf_sh[0].chmod(pushconf_sh[0].stat().st_mode | stat.S_IEXEC)
        pullconf_sh[0].chmod(pullconf_sh[0].stat().st_mode | stat.S_IEXEC)
    if not statefile.is_file() or statefile.read_text() == "": 
        print("  New machine!")
        statefile.touch()
        dt = datetime.datetime.fromtimestamp(0)
        hashed = None
    else:
        sp = statefile.read_text().split(' ')
        dt = datetime.datetime.fromisoformat(sp[0])
        hashed = sp[1]
    return dt, hashed

def get_state_hash(state):
    if not state[1]:
        return "<NO HASH>" 
    return f"{state[1][:16]}..."

def write_state(d: datetime.datetime, hashed: str) -> str:
    s = datetime_serialize(d)
    statefile.write_text(f"{s} {hashed}")
    return s 

def hash_bytes(data: bytes) -> str:
    o = hash_algorithm() 
    o.update(data)
    return o.hexdigest()

def state_print(state, date=False) -> str:
    r = f"{get_state_hash(state):19} ({hash_algorithm.__name__})"
    if date:
        r = f"{state[0]} | {r}"
    return r