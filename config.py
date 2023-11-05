from pre_common import add_files_from_dir, files, home 
from pathlib import Path

# ------------------------------------------------------------------ # 
# -------------------------- START OF CONFIG ----------------------- #
# --------------------- DO NOT TOUCH ANYTHING ELSE ----------------- # 
# ------------------------------------------------------------------ #



# INFO: This is just a default config, that I, the developer, use
# Read the comments if you don't know what you're doing. 



# ----------------- Rclone config ----------------- #
# 
# MODIFY THIS!!!! 
# You need to setup rclone first -> README.md  
# <remote>:<path>
rclonedir = "remote:arch-conf"  



# ------------- Compression algorithm ------------- # 
# You can also use gz or bz2 if you want. (faster compresison but not as good) 
# If your rclone remote doesn't have a lot of storage, it is better to leave
# it as xz. 
# But don't change it if you don't know what you're doing. 
compression = "xz"              



# ----------------- Add files from directories ----------------- #
# Binary paths. bin_path is the directory that points to all your little 
# Shell scripts or executables that you want to copy 
# It is recommended to specify a directoy here and to add it 
# to the $PATH (linux) or %PATH% (windows) enviroment 
# 
# If you decide to specify a directory 
# pushconf and pullconf bash scripts will be added to this path
# TODO make it work on windows :)   
bin_path = home / "bin/"  
add_files_from_dir(
    bin_path, 
    # write the names of the scripts here
    # If you don't want to save any scripts
    # just leave it blank ""
    "duh gt pwb uni connect-wifi sampdl fix_wacom.sh "
)

# Add more paths to backup 
# Config path is nice on linux but if you don't want it you 
# can comment it out. Remember to comment out everything 
# you don't want to have
config_path = home / ".config/"
more_files = [
    config_path / "rclone/rclone.conf", # This mirrors the rclone config file 
    home / ".ssh/", # if ssh is protected, we ask for sudo (RIP windows)  

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
    home / ".ipython", # IPython configs 

    home / "docs_old/bitwardenpw",      # Super secret password file
    home / "todo",                  # Todo list 
]
# ------------------------------------------------------------------ # 
# -------------------------- END OF CONFIG ------------------------- #
# --------------------- DO NOT TOUCH ANYTHING ELSE ----------------- # 
# ------------------------------------------------------------------ #





files.extend(more_files) # Don't mind me
