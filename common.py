from pathlib import Path 
rclonedir = "remote:arch-conf"
compression = "xz" # gz, bz2

home = Path.home()
files = [
    # home / ".config/VsCodium/product.json", 
    # home / ".config/picom/picom.conf", 
    # home / ".config/alacritty/alacritty.yml",
    # home / ".config/awesome/rc.lua",
    # home / ".config/awesome/themes/",
    home / "bin/sampdl", 
    home / "bin/imgur", 
    home / "docs/bitwardenpw",
    home / "todo", 
    home / ".bashrc",
    home / ".nvimrc",
    home / ".xinitrc"
]

basepath = Path(__file__).resolve().parent
statefile = basepath / ".state"
