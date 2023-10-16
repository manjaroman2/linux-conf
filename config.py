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
    config_path / "rclone/rclone.conf", # This is important, don't remove this
    home / ".ssh/",
    home / "docs/bitwardenpw",
    home / "todo", 
    home / ".bashrc",
    home / ".nvimrc",
    home / ".xinitrc",
    config_path / "Code/User/settings.json",
    config_path / "Code/User/keybindings.json",
    config_path / "Code/User/snippets/",
    config_path / "libreoffice/4/user/template/", 
    config_path / "awesome/themes/",
    config_path / "awesome/rc.lua",
    config_path / "picom/picom.conf", 
    config_path / "alacritty/alacritty.yml",
    config_path / "mimeapps.list", 
    config_path / "xournalpp/colornames.ini",
    config_path / "xournalpp/palette.gpl",
    config_path / "xournalpp/plugins/",
    config_path / "xournalpp/settings.xml",
    config_path / "user-dirs.dirs",
]

# --- END OF CONFIG 

files.extend(more_files)