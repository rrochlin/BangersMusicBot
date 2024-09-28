import configparser
import os
import logging
from sqlalchemy import create_engine, URL
from models import Song, Queue, User, PlaylistPointer
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy_cockroachdb import run_transaction
from sqlalchemy.orm.exc import NoResultFound
from typing import List


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
            database=f"{config['SECRETS']['cluster']}.defaultdb",
            host=f"{config['SECRETS']['cluster']}.{config['SECRETS']['host']}",
            port="26257",
            query={"sslmode": "require"}
            )
        self.engine = create_engine(connection_string)
        self.conn = self.engine.connect()
        self.conn.auto_reconnect = True
        self.cursor = self.engine.raw_connection().cursor()

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.current_song = None
        self.__current_queue__ = None

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

    def next_song(self) -> None:
        self.logger.info("grabbing song from queue")
        run_transaction(sessionmaker(bind=self.engine), lambda s: self.__next_song__(s))
        self.logger.info(f"next song is {self.current_song.title}")

    def queue_song(self, song_title: str, song_url: str, source: str, thumbnail: str, user: str) -> None:
        self.logger.info(f"adding song to queue: {song_title}")
        run_transaction(sessionmaker(bind=self.engine),
                        lambda s: self.__queue_song__(
                            session=s, song_title=song_title, song_url=song_url, source=source, thumbnail=thumbnail, user=user))

    def fetch_queue(self) -> List[str]:
        run_transaction(sessionmaker(bind=self.engine), lambda s: self.__fetch_queue__(s))
        return self.__current_queue__

    def clear_queue(self) -> None:
        pass

    def __fetch_queue__(self, session: Session) -> None:
        old_song = self.__get_pointer__(session)
        current_q = session.query(Queue).order_by(Queue.id).where(Queue.id > old_song.id)
        if current_q:
            self.__current_queue__ = [q.title for q in current_q]
        else:
            self.__current_queue__ = None

    def __next_song__(self, session: Session) -> None:
        # will raise NoResultFound if theres no songs in the queue
        self.logger.debug("getting next song")
        pp = self.__get_pointer__(session)
        self.logger.debug(f"retrieved pointer {pp}")
        new_song = session.query(Queue).order_by(Queue.id).where(Queue.id > pp.id).first()
        self.logger.debug(f"retrieved next song {new_song}")
        if not new_song:
            self.current_song = None
            raise NoResultFound
        new_pp = PlaylistPointer.from_queue(new_song)
        self.logger.debug(f"creating new pointer {new_pp}")
        try:
            session.delete(pp)
        except Exception as e:
            self.logger.error(e)
        session.add(new_pp)
        song = Song(title=new_song.title, url=new_song.url, source=new_song.source, thumbnail=new_song.thumbnail, createdById=new_song.createdById)
        session.add(song)
        self.current_song = Song(title=new_song.title, url=new_song.url, source=new_song.source, thumbnail=new_song.thumbnail, createdById=new_song.createdById)

    def __queue_song__(self, session: Session, song_title: str, song_url: str, source: str, thumbnail: str, user: str):
        try:
            user_id = self.__get_user__(session=session, username=user).id
        except Exception as e:
            self.logger.error(f"error finding user ID {e}")
            return
        session.add(Queue(title=song_title, url=song_url, source=source, thumbnail=thumbnail, createdById=user_id))

    def __get_user__(self, session: Session, username: str) -> User:
        try:
            user = session.query(User).filter(User.name == username).first()
            if not user:
                self.logger.error("trying to add user to database")
                session.add(User(name=username))
                self.logger.error("added user to db")
                return session.query(User).filter(User.name == username).first()
            return user
        except Exception as e:
            self.logger.error(f"user creation failed {e}")
            raise Exception(e)

    def __get_pointer__(self, session: Session) -> PlaylistPointer:
        self.logger.debug("grabbing pointer")
        pointer = session.query(PlaylistPointer).first()
        self.logger.debug(f"pointer is {pointer}")
        if pointer:
            return pointer
        else:
            return PlaylistPointer(id=-1)
