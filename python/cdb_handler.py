import configparser
import os
import logging
import sys
from sqlalchemy import create_engine, URL
from models import Song, Queue, User
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy_cockroachdb import run_transaction
from sqlalchemy.orm.exc import NoResultFound


class cdb_handler:

    def __init__(self):
        secrets_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "Web.config"
        )
        config = configparser.ConfigParser()
        config.read(secrets_path)
        connection_string = URL(
            drivername="cockroachdb",
            username=config["SECRETS"]["cdb_username"],
            password=config["SECRETS"]["cdb_password"],
            database="defaultdb",
            host=config["SECRETS"]["host"],
            port="26257",
            query={"sslmode": "require"}
            )
        self.engine = create_engine(connection_string)
        self.conn = self.engine.connect()
        self.conn.auto_reconnect = True
        self.cursor = self.engine.raw_connection().cursor()

        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        root.addHandler(handler)
        self.logger = root
        self.current_song = None

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

    def pop_song(self) -> None:
        self.logger.info("grabbing song from queue")
        run_transaction(sessionmaker(bind=self.engine), lambda s: self.__pop_song__(s))

    def queue_song(self, song_title: str, song_url: str, thumbnail: str, user: str) -> None:
        self.logger.info(f"adding song to queue: {song_title}")
        run_transaction(sessionmaker(bind=self.engine),
                        lambda s: self.__queue_song__(
                            session=s, song_title=song_title, song_url=song_url, thumbnail=thumbnail, user=user))

    def __pop_song__(self, session: Session) -> Song:
        next = session.query(Queue).order_by(Queue.id).first()
        session.delete(next)
        song = Song(title=next.title, url=next.url, thumbnail=next.thumbnail, createdById=next.createdById)
        session.add(song)
        self.current_song = Song(title=next.title, url=next.url, thumbnail=next.thumbnail, createdById=next.createdById)

    def __queue_song__(self, session: Session, song_title: str, song_url: str, thumbnail: str, user: str):
        try:
            user_id = self.__get_user__(session=session, username=user).id
        except Exception as e:
            self.logger.error(f"error finding user ID {e}")
            return
        session.add(Queue(title=song_title, url=song_url, thumbnail=thumbnail, createdById=user_id))

    def __get_user__(self, session: Session, username: str) -> str:
        try:
            return session.query(User).filter(User.name == username).first()
        except NoResultFound:
            session.add(User(name=username))
            return session.query(User).filter(User.name == username).first()
        except Exception as e:
            self.logger.error(f"user creation failed {e}")
            raise Exception(e)
