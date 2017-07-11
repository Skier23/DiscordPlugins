import discord
from discord.ext import commands

class Mycog:
    """My custom cog that does stuff!"""

    def __init__(self, bot):
        self.bot = bot

	@commands.command()
    async def repeatText(self, ctx, *, format_msg):
        """Use repeatText channel text"""

        await self.bot.say(format_msg)

def setup(bot):
    bot.add_cog(Mycog(bot))
