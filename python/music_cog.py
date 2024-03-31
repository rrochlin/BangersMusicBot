import asyncio
import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
from cdb_handler import cdb_handler
from sqlalchemy.orm.exc import NoResultFound
import logging
import sys


class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # all the music related stuff
        self.cdb = cdb_handler()
        self.YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True"}
        self.FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }
        self.vc: discord.guild.VocalGuildChannel = None
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        root.addHandler(handler)
        self.logger = root

    # searching the item on youtube
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                if "http" in item:
                    info = ydl.extract_info(item, download=False)
                else:
                    info = ydl.extract_info("ytsearch:%s" % item, download=False)["entries"][0]
            except Exception as e:
                print(e)
                return False
            source = next((item['url'] for item in info["formats"] if 'asr' in item.keys()), None)
        return {
            "source": source,
            "title": info["title"],
            "thumbnail": info["thumbnail"],
            "song_url": rf"https://www.youtube.com/watch?v={info['id']}"
        }

    def play_next(self):
        try:
            self.cdb.pop_song()
            m_url = self.cdb.current_song.source
            self.vc.play(
                discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
                after=lambda e: self.play_next(),
            )
        except NoResultFound:
            return
        except Exception as e:
            self.logger.error(f"error playing next song {e}")

    # infinite loop checking
    async def play_music(self, ctx: commands.Context):
        self.cdb.pop_song()
        m_url = self.cdb.current_song.source
        if (not self.vc.is_connected() or self.vc is None):
            self.vc = await ctx.author.voice.channel.connect()
        else:
            await self.vc.move_to(ctx.author.voice.channel)
        self.vc.play(
            discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
            after=lambda e: self.play_next(),
        )
        await ctx.send(f"Now playing: {self.cdb.current_song.title}")

    @commands.command(name="p", help="Plays a selected song from youtube")
    async def p(self, ctx: commands.Context, *args):
        query = " ".join(args)
        if ctx.author.voice.channel is None:
            await ctx.send("Connect to a voice channel!")
            return
        elif self.vc is None:
            self.vc = await ctx.author.voice.channel.connect()
        else:
            await self.vc.move_to(ctx.author.voice.channel)
        song = self.search_yt(query)
        if song is False:
            await ctx.send(
                "Could not download the song. Incorrect format try another keyword or url. This could be due to playlist or a livestream format."
            )
        else:
            await ctx.send("Song added to the queue")
            self.cdb.queue_song(song_title=song["title"], song_url=song["song_url"], source=song["source"], thumbnail=["thumbnail"], user="default_system")
            if self.cdb.current_song is None:
                await self.play_music(ctx)

    @commands.command(name="queue", help="Displays the current songs in queue")
    async def q(self, ctx: commands.Context):
        retval = "\n".join(self.cdb.fetch_queue())
        if retval != "":
            await ctx.send(retval)
        else:
            await ctx.send("No music in queue")

    @commands.command(name="skip", help="Skips the current song being played")
    async def skip(self, ctx: commands.Context):
        if self.vc.is_connected():
            self.vc.stop()
            # play next in the queue
            await self.play_music(ctx)

    @commands.command(name="stop", help="Stop music")
    async def stop(self):
        if self.vc.is_connected():
            self.vc.stop()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.id == self.bot.user.id:
            return
        elif before.channel is None:
            voice = after.channel.guild.voice_client
            time = 0
            while True:
                await asyncio.sleep(1)
                time = time + 1
                if voice.is_playing() and not voice.is_paused():
                    time = 0
                if time == 500:
                    await voice.disconnect()
                if not voice.is_connected():
                    break
