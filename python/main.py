import discord

from discord.ext import commands
import os
from music_cog import music_cog
from ping_bot import ping_bot

bot = commands.Bot(command_prefix="-", intents=discord.Intents.default())
bot.add_cog(music_cog(bot))

if __name__ == "__main__":
    ping_bot()
    bot.run(os.getenv("TOKEN"))
