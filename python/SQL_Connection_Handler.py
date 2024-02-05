import mariadb
import configparser
import os


class SQL_Connection_Handler:

    def __init__(self):
        secrets_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "Web.config"
        )
        config = configparser.ConfigParser()
        config.read(secrets_path)
        self.conn = mariadb.connect(
            user=config["sql_username"],
            password=config["sql_password"],
            host="localhost",
        )
        self.cursor = self.conn.cursor()

    def song_played(self, song_url: str, user: str = "default") -> None:
        # record the song and user
        sql = (
            f"INSERT INTO MusicDB.history (timestamp, song_url, user, stop_or_skip) "
            f"VALUES (NOW(), {song_url}, {user}, False);"
        )
        self.cursor.execute(sql)

    def song_skipped(self, user: str = "default") -> None:
        sql = (
            f"UPDATE MusicDB.history "
            f"SET stop_or_skip = True, stopped_skipped_by = {user} "
            f"WHERE timestamp=(SELECT MAX(timestamp) FROM MusicDB.history)"
        )
        self.cursor.execute(sql)
