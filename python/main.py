import discord
from configparser import ConfigParser
from discord.ext import commands
from music_cog import music_cog
import asyncio
import sys
import logging

intents = discord.Intents(
    messages=True, guilds=True, message_content=True, voice_states=True
)
bot = commands.Bot(command_prefix="-", intents=intents)

root = logging.getLogger(__name__)
root.propagate = True
root.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)


async def main():
    await bot.add_cog(music_cog(bot))


if __name__ == "__main__":

    asyncio.run(main())
    config = ConfigParser()
    config.read("Web.config")
    TOKEN = config["SECRETS"]["TOKEN"]
    bot.run(TOKEN)
