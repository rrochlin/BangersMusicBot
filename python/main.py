import discord
from configparser import ConfigParser
from discord.ext import commands
from music_cog import music_cog
import asyncio

intents = discord.Intents(
    messages=True, guilds=True, message_content=True, voice_states=True
)
bot = commands.Bot(command_prefix="-", intents=intents)


async def main():
    await bot.add_cog(music_cog(bot))


if __name__ == "__main__":
    asyncio.run(main())
    config = ConfigParser()
    config.read("Web.config")
    TOKEN = config["SECRETS"]["TOKEN"]
    print(TOKEN)
    bot.run(TOKEN)
