import mariadb
import configparser
import os
import logging
import sys


class SQL_Connection_Handler:

    def __init__(self):
        secrets_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "Web.config"
        )
        config = configparser.ConfigParser()
        config.read(secrets_path)
        self.conn = mariadb.connect(
            user=config["SECRETS"]["sql_username"],
            password=config["SECRETS"]["sql_password"],
            host="localhost",
        )
        self.cursor = self.conn.cursor()

        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        root.addHandler(handler)
        self.logger = root

    def song_played(self, song_title: str, song_url: str, user: str = "default") -> None:
        # record the song and user
        sql = (
            f"INSERT INTO MusicDB.history (timestamp, song_title, song_url, user, stop_or_skip) "
            f"VALUES (NOW(), '{song_title}', '{song_url}', '{user}', False);"
        )
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            self.logger.error(sql)
            self.logger.error(e)

    def song_skipped(self, user: str = "default") -> None:
        sql = (
            f"UPDATE MusicDB.history "
            f"SET stop_or_skip = True, stopped_skipped_by = '{user}' "
            f"WHERE timestamp=(SELECT MAX(timestamp) FROM MusicDB.history);"
        )
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            self.logger.error(sql)
            self.logger.error(e)
