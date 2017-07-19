import discord
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
from __main__ import send_cmd_help
import os
from typing import Any, Dict, List
from .utils.chat_formatting import *
from enum import Enum

class dropState(Enum):
    INACTIVE = 1
    PICKING = 2
    ACTIVE = 3
class moneyDrop:
    """The moneyDrop Cog. Also will handle currency/reputation"""

    def __init__(self, bot):
        self.bot = bot  
        self.drops = {}
        self.dropChannelId = 337035351862542346
    def schedule_drop_close(self, member, delay: int):
        new_task = self.bot.loop.call_later(
            delay, self.close_drop, member)
        self.drops[member.id].update({"task": new_task})
    @commands.command(name="startdrop", pass_context=True, invoke_without_command=True)
    async def startDrop(self, ctx):
        member = ctx.message.author
        server = ctx.message.server
        print("starting drop")
        self.drops[member.id] = {}
        self.schedule_drop_close(member, 5)   
        self.drops[member.id].update({"dropstate": dropState.PICKING})
        channel = server.get_channel(337035351862542346)
        await self.bot.send_message(channel, "Testing message")
    def close_drop(self, user: discord.Member):
        print("test1inconsole")
        #self.bot.loop.create_task(self.bot.send_message(user, "test"))
    def _get_users_with_role(self, server: discord.Server,
                                 role: discord.Role) -> List[discord.User]:
            roled = []
            for member in server.members:
                if (not member.bot) and self._member_has_role(member, role):
                    roled.append(member)
            return roled
def setup(bot):
    n = moneyDrop(bot)
    bot.add_cog(n)
