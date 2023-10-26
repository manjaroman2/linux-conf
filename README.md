## Save and load linux state from remote with rclone 

You have multiple machines because youre rich? You want to modify the config and mirror it to another one? Just run [setup.sh](setup.sh), it's totally safe!!! if you let me write to your bin_path in config.py you will be able to just `$ pushconf` and `$ pullconf` to fetch the latest state. 

For this to work you need to configure [rclone](https://rclone.org/) on your system. All the relevant settings are in [config.py](config.py). 

### CAUTION Overriding config files could lead to loss of configurations!!!

Run `$ pushconf --ask` and save the backup if you want to be very safe. 

#### How to use quick

(0. Know a little bit of python :] ) 
1. Setup rclone 
2. `git clone git@github.com:manjaroman2/linux-conf.git && cd linux-conf && chmod +x setup.sh && ./setup.sh`
3. `pushconf --ask`
4. `pullconf`

#### How configure rclone???? 
1. Open some bash or zsh or whatever and install rclone from your package manager
2. `rclone config` and follow instructions
3. It will create a rclone.conf file somewhere, you probably want to include it in [config.py](config.py)

#### TODO for Developers

* print out directories nicely 
* Local storage if no internet

* Implement loading local backups 