from pre_common import add_files_from_dir, files
from pathlib import Path

# ----------------------------------------------------------------------------- # 
# -----------------------------START OF CONFIG -------------------------------- #
# ------------------------DONT TOUCH ANYTHING ELSE ---------------------------- # 
# ----------------------------------------------------------------------------- #

# ----------------- Rclone config ----------------- #
# <remote>:<path>
rclonedir = "remote:arch-conf"  

# Compression algorithm to use
compression = "xz"              
# You can also use gz or bz2 if you want. 
# But don't change it if you don't know what you're doing. 

# ----------------- Add files from directories ----------------- #
home = Path.home()

# Uncomment if you want to write pushconf / pullconf scripts to bin_path 
bin_path = home / "bin/"  
add_files_from_dir(
    bin_path, 
    "duh gt pwb uni connect-wifi sampdl fix_wacom.sh " # write the names of the scripts here
    # If you don't want to save any scripts, just leave it blank
)

# Add more 
config_path = home / ".config/"
more_files = [
    config_path / "rclone/rclone.conf", # This mirrors the rclone config file 
    home / ".ssh/", # Failes on pull, because of permissions. Probably just leave it for now TODO:Solution? 

    home / ".bashrc", # This is very nice 
    home / ".nvimrc",
    home / ".xinitrc",
    config_path / "mimeapps.list", # No more annoying file associations 
    config_path / "user-dirs.dirs",

    config_path / "awesome/themes/", # If you use awesome wm, this is very nice
    config_path / "awesome/rc.lua",
    config_path / "picom/picom.conf", # Picom settings 

    config_path / "xournalpp/colornames.ini", # Xournalpp settings
    config_path / "xournalpp/palette.gpl",
    config_path / "xournalpp/plugins/",
    config_path / "xournalpp/settings.xml",
    config_path / "xournalpp/metadata",
    
    Path("/usr/share/xournalpp/"), 

    config_path / "fontconfig/conf.d",

    config_path / "alacritty/alacritty.yml", # Alacritty settings

    config_path / "libreoffice/4/user/template/", # Libreoffice templates 

    home / "docs/bitwardenpw",      # Super secret password file
    home / "todo",                  # Todo list 
]

# ----------------------------------------------------------------------------- #
# -----------------------------END OF CONFIG ---------------------------------- #
# ------------------------DONT TOUCH ANYTHING ELSE ---------------------------- #
# ----------------------------------------------------------------------------- #

files.extend(more_files) # Don't mind me
