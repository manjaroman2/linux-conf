## Save and load linux state from remote with rclone 

You have multiple machines because youre rich? You want to modify the config and mirror it to another one? You execute any script from the internet that was hacked together by some n00b? Just run [setup.sh](setup.sh), it's totally safe!!! if you let me write to your bin_path in config.py you will be able to just `$ pushconf` and `$ pullconf` to fetch the latest state. 

For this to work you need to configure [rclone](https://rclone.org/) on your system. All the relevant settings are in [config.py](config.py). 

### CAUTION Overriding config files could lead to loss of configurations!!!

Run `$ pushconf --ask` and save the backup if you want to be very safe. 

#### How to use quick

(0. Know a little bit of python :] ) 
1. Setup rclone 
2. Fork the repo (required atm)
3. `git clone git@github.com:<YOUR NAME>/linux-conf.git && cd linux-conf && chmod +x setup.sh && ./setup.sh`
3. `pushconf --ask`
4. `pullconf`
OR 
4. `pullconf --newest`
if you don't want any questions. You could put this command in .xinitrc or a comparable file (strongly discouraged)

#### How configure rclone???? 
1. Open some bash or zsh or whatever and install rclone from your package manager
2. `rclone config` and follow instructions
3. It will create a rclone.conf file somewhere, you probably want to include it in [config.py](config.py)

#### TODO for Developers

* print out directories nicely 
* Local storage if no internet

* Implement loading local backups 