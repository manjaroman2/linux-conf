## Save and load linux state from remote with rclone 

You have multiple machines because youre rich? You want to modify the config and mirror it to another one? Just run [setup.sh](setup.sh), it's totally safe!!! if you let me write to your bin_path in config.py you will be able to just `$ pushconf` and `$ pullconf` to fetch the latest state. 

For this to work you need to configure [rclone](https://rclone.org/) on your system. All the relevant settings are in [config.py](config.py). 

### CAUTION Overriding config files could lead to loss of configurations!!!

Run `$ pushconf --ask` and save the backup if you want to be very safe. 

#### How to use quick

1. Setup rclone 
2. `git clone git@github.com:manjaroman2/linux-conf.git && cd linux-conf && chmod +x setup.sh && ./setup.sh`
3. `pushconf --ask`
4. `pullconf`


#### TODO for Developers

* Implement loading local backups 