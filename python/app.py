from litestar import Litestar, get
import discord
from configparser import ConfigParser
from discord.ext import commands
from music_cog import music_cog
import asyncio
import sys
import logging
from threading import Thread

intents = discord.Intents(
    messages=True, guilds=True, message_content=True, voice_states=True
)
bot = commands.Bot(command_prefix="-", intents=intents)

root = logging.getLogger(__name__)
root.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)


async def main():
    await bot.add_cog(music_cog(bot))


@get("/")
async def hello_world() -> str:
    return str(bot.status)


@get("/skip")
async def skip() -> str:
    root.info("running skip function")
    try:
        cog: music_cog = bot.get_cog("music_cog")
        cog.vc.stop()
        return str(cog.cdb.current_song)
    except Exception as e:
        root.error(e)

asyncio.run(main())
config = ConfigParser()
config.read("Web.config")
TOKEN = config["SECRETS"]["TOKEN"]
thread = Thread(target=bot.run, args=(TOKEN,), daemon=True)
thread.start()

app = Litestar([hello_world, skip])
