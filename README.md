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


## Common Issues 
- yt_dlp need to be frequently updated to adapt with youtubes changing api

## Known Issues
The project is deployed on a raspberrypi so there can be noticeable stuttering while downloading songs,
inconsistent playback etc.


