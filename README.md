## Save and load linux state from remote with rclone 

You have multiple machines because youre rich? You want to modify the config and mirror it to another one? Just run [setup.sh](setup.sh), it's totally safe!!! if you let me write to your bin_path in config.py you will be able to just `$ pushconf` and `$ pullconf` to fetch the latest state. 

For this to work you need to configure [rclone](https://rclone.org/) on your system. All the relevant settings are in [config.py](config.py). 