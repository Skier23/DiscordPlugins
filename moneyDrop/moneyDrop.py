import discord
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
from __main__ import send_cmd_help
import os
from typing import Any, Dict, List
from .utils.chat_formatting import *

class moneyDrop:
    """The moneyDrop Cog. Also will handle currency/reputation"""

    def __init__(self, bot):
        self.bot = bot    
    async def _schedule_close(self, member, survey_id: str, delay: int):
        new_handle = self.bot.loop.call_later(
            delay, self._mark_as_closed, survey_id, member)
    @commands.command(name="startdrop", pass_context=True, invoke_without_command=True)
    async def startDrop(self, ctx, member: discord.Member):
        print("testinconsole")
        await self._schedule_close(member, "test1", 5)   
    def _get_users_with_role(self, server: discord.Server,
                             role: discord.Role) -> List[discord.User]:
        roled = []
        for member in server.members:
            if (not member.bot) and self._member_has_role(member, role):
                roled.append(member)
        return roled
    async def _mark_as_closed(self, message: str, user: discord.Member):
        print("test1inconsole")
        await self.bot.send_message(user, "test")
def setup(bot):
    n = moneyDrop(bot)
    bot.add_cog(n)
