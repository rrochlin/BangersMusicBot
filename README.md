# BangersMusicBot
Music Bot JUST for the Boys AND NO ONE ELSE!


## dependancies
I added support to store logging info into MariaDB.  
The system you use will need to have mariaDB installed then you need to download the dependancies
* `sudo apt-get update -y`
* `sudo apt-get install -y libmariadb-dev`
* `pip3 install mariadb==1.0.11`


## managing services
sudo systemctl restart BangersMusicService.service

## configuring MariaDB to remote connections
* [documentation](https://mariadb.com/kb/en/configuring-mariadb-for-remote-client-access/).
* need to open port 3306
* configure user account to allow conections from LAN
