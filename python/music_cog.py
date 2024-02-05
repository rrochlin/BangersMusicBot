import asyncio
import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
from SQL_Connection_Handler import SQL_Connection_Handler


class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # all the music related stuff
        self.is_playing = dict()
        # music_queue is an object containing keys for different servers and 2d arrays containing [song, channel] for values
        self.music_queue = dict()
        self.sql_handler = SQL_Connection_Handler()
        self.YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True"}
        self.FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }
        self.vc = dict()

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
        return {"source": source, "title": info["title"]}

    def play_next(self, server):
        if server in self.music_queue and len(self.music_queue[server]) > 0:
            self.is_playing[server] = True
            # get the first url
            m_url = self.music_queue[server][0][0]["source"]
            # remove the first element as you are currently playing it
            self.music_queue[server].pop(0)
            self.vc[server].play(
                discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
                after=lambda e: self.play_next(server),
            )
        else:
            self.is_playing[server] = False

    # infinite loop checking
    async def play_music(self, ctx):
        server = str(ctx.guild.name)
        if server in self.music_queue and len(self.music_queue[server]) > 0:
            self.is_playing[server] = True
            m_url = self.music_queue[server][0][0]["source"]
            if (
                server not in self.vc
                or self.vc[server] == ""
                or not self.vc[server].is_connected()
                or self.vc[server] is None
            ):
                self.vc[server] = await self.music_queue[server][0][1].connect()
            else:
                await self.vc[server].move_to(self.music_queue[server][0][1])
            current = self.music_queue[server].pop(0)
            self.vc[server].play(
                discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
                after=lambda e: self.play_next(server),
            )
            await ctx.send(f"Now playing: {current[0]['title']}")
        else:
            self.is_playing[server] = False

    @commands.command(name="p", help="Plays a selected song from youtube")
    async def p(self, ctx, *args):
        query = " ".join(args)
        voice_channel = ctx.author.voice.channel
        server = str(ctx.guild.name)
        if voice_channel is None:
            await ctx.send("Connect to a voice channel!")
        else:
            song = self.search_yt(query)
            if song is False:
                await ctx.send(
                    "Could not download the song. Incorrect format try another keyword or url. This could be due to playlist or a livestream format."
                )
            else:
                await ctx.send("Song added to the queue")
                self.sql_handler.song_played(song, ctx.author.id)
                if server not in self.music_queue:
                    self.music_queue[server] = []
                self.music_queue[server].append([song, voice_channel])
                if server not in self.is_playing or self.is_playing[server] is False:
                    await self.play_music(ctx)

    @commands.command(name="queue", help="Displays the current songs in queue")
    async def q(self, ctx):
        retval = ""
        server = str(ctx.guild.name)
        try:
            for i in range(0, len(self.music_queue[server])):
                retval += self.music_queue[server][i][0]["title"] + "\n"
        except Exception:
            await ctx.send("No songs in queue!")
        print(retval)
        if retval != "":
            await ctx.send(retval)
        else:
            await ctx.send("No music in queue")

    @commands.command(name="skip", help="Skips the current song being played")
    async def skip(self, ctx):
        server = str(ctx.guild.name)
        if server in self.vc and self.vc[server]:
            self.sql_handler.song_skipped(ctx.author.id)
            self.vc[server].stop()
            # play next in the queue
            await self.play_music(ctx)

    @commands.command(name="stop", help="Stop music")
    async def stop(self, ctx):
        server = str(ctx.guild.name)
        if server in self.vc and self.vc[server]:
            self.sql_handler.song_skipped(ctx.author.id)
            self.vc[server].stop()

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
