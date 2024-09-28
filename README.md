# BangersMusicBot
Music Bot JUST for the Boys AND NO ONE ELSE!


## dependancies
### PostgreSQL
You will need this for cockroachdb
- `sudo apt-get update -y`
- `sudo apt install postgresql`
### FFMPEG
ffmpeg is used to stream the audio to discord
- `sudo apt-get update -y`
- `sudo apt install ffmpeg`


## Grabbing Logs
```scp raspi@raspberrypi:/home/raspi/logs/BangersMusicBot.log python/BangersMusicBot.log```

## Pushing Web.Config to raspi
```scp python/Web.config raspi@raspberrypi:/home/raspi/Documents/BangersMusicBot/python/Web.config```

## managing services
```sudo systemctl restart BangersMusicService.service```

## configuring MariaDB to remote connections
* [documentation](https://mariadb.com/kb/en/configuring-mariadb-for-remote-client-access/)
* need to open port 3306
* configure user account to allow conections from LAN

## Compatibility for raspi and cockroachDB
* cockroachDB requires postgresql to work properly. run `sudo apt install postgresql`
