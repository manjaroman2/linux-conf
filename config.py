from pre_common import add_files_from_dir, files
from pathlib import Path
# --- START OF CONFIG 
rclonedir = "remote:arch-conf"
compression = "xz" # gz, bz2

# ------ Paths 
home = Path.home()

# Uncomment if you want to write pushconf / pullconf scripts to bin_path 
bin_path = home / "bin/"  
add_files_from_dir(
    bin_path, 
    "duh gt pwb uni connect-wifi sampdl "
)

# add more paths 
config_path = home / ".config/"

more_files = [
    home / "docs/bitwardenpw",
    home / "todo", 
    home / ".bashrc",
    home / ".nvimrc",
    home / ".xinitrc",
    config_path / "libreoffice/4/user/template/", 
    config_path / "awesome/themes/",
    config_path / "awesome/rc.lua",
    config_path / "picom/picom.conf", 
    config_path / "alacritty/alacritty.yml",
    config_path / "mimeapps.list", 
    config_path / "rclone/rclone.conf",
    config_path / "xournalpp/",
    config_path / "user-dirs.dirs",
]

# --- END OF CONFIG 

files.extend(more_files)