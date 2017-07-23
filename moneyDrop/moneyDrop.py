import discord
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
from __main__ import send_cmd_help
import os
from typing import Any, Dict, List
from .utils.chat_formatting import *
from enum import Enum
import random
import asyncio

class dropState(Enum):
    INACTIVE = 1
    PICKING = 2
    ACTIVE = 3
class moneyDrop:
    """The moneyDrop Cog. Also will handle currency/reputation"""

    def __init__(self, bot):
        self.bot = bot  
        self.drops = {}
        self.dropChannelId = "337035351862542346"
    async def schedule_drop_close(self, member, delay: int, playersToPick, server):
        #new_task = self.bot.loop.call_later(
        #    delay, self.close_drop, member, playersToPick, server)
        #self.drops[member.id].update({"task": new_task})
        await asyncio.sleep(delay)
        await self.close_drop(member, playersToPick, server)
    @commands.command(name="startdrop", pass_context=True, invoke_without_command=True)
    async def startDrop(self, ctx):
        member = ctx.message.author
        server = ctx.message.server
        print("starting drop")
        self.drops[member.id] = {}
        self.drops[member.id].update({"dropstate": dropState.PICKING})
        players = []
        self.drops[member.id].update({"enteredplayers": players})
        self.drops[member.id].update({"timetoenter": 60})
        self.drops[member.id].update({"timeleft": self.drops[member.id]["timetoenter"]})
        channel = server.get_channel(self.dropChannelId)
        data = self.msg_builder(member)
        self.drops[member.id].update({"message": await self.bot.send_message(channel, embed = data)})
        developers = self.get_users_with_role(server, server.role_hierarchy[0])
        data2 = discord.Embed(colour=discord.Colour.green())
        boolValue = False
        data2.add_field(name="Drop Alert", value="{} has started a drop!".format(member.mention), inline=boolValue)
        data2.add_field(name="Enter the drop", value="Reply with \"!enter {}\" to enter the drop.".format(member.name), inline=boolValue)
        for user in developers:
            await self.bot.send_message(user, embed=data2)
        await asyncio.gather(self.schedule_update(member, self.drops[member.id]["message"], 30), self.schedule_drop_close(member, self.drops[member.id]["timetoenter"], 1, server))
    @commands.command(name="enter", pass_context=True, invoke_without_command=True)
    async def enterDrop(self, ctx, dropper: discord.Member):
        user = ctx.message.author
        if not ctx.message.channel.is_private:
            await self.bot.send_message(user, "This command can only be used in DM's")
            return
        if dropper.id not in self.drops:
            await self.bot.send_message(user, "It does not appear this person is dropping! \nPlease make sure you spelled their name correctly if they are currently dropping.")
            return
        if dropper.id in self.drops:
            if self.drops[dropper.id]["dropstate"] == dropState.INACTIVE:
                await self.bot.send_message(user, "This dropper is not dropping right now!")
                return 
            elif self.drops[dropper.id]["dropstate"] == dropState.ACTIVE:
                await self.bot.send_message(user, "This drop has already started and it is too late to join now!")
                return 
            elif self.drops[dropper.id]["dropstate"] == dropState.PICKING:
                players = self.drops[dropper.id]["enteredplayers"]
                if user.id in players:
                    await self.bot.send_message(user, "You already entered in this drop!")
                    return
                players.append(user.id)
                self.drops[dropper.id].update({"enteredplayers": players})
                await self.bot.send_message(user, "You have entered into the drop. You will receive a pm notifying you if you are accepted or not.") 
                await self.update_msg(dropper, self.drops[dropper.id]["message"])
    async def close_drop(self, user: discord.Member, playersToPick, server):
        print("drop close")
        self.drops[user.id].update({"dropstate": dropState.ACTIVE})
        selectedPlayers = self.random_select(self.drops[user.id]["enteredplayers"], playersToPick)
        for id in selectedPlayers:
            thisMember = server.get_member(id)
            await self.bot.send_message(thisMember, "Congrats you have been accepted to the drop!")
        for id in self.drops[user.id]["enteredplayers"]:
            if id not in selectedPlayers:
                thisMember = server.get_member(id)
                await self.bot.send_message(thisMember, "Unfortunately you have not been accepted to this drop. Try again next time.")
    def random_select(self, entPlayers: List, numOfPlayers):
        playersSize = len(entPlayers)
        if playersSize < numOfPlayers:
            numOfPlayers = playersSize
        randomPlayers = random.sample(range(playersSize), numOfPlayers)
        randomPlayers[:] = [entPlayers[i] for i in randomPlayers]
        return randomPlayers
    def msg_builder(self, member: discord.Member):
        data = discord.Embed(colour=discord.Colour.green())
        boolValue = False
        if self.drops[member.id]["timeleft"] != 0:
            data.add_field(name="Drop Alert", value="{} has started a drop!".format(member.mention), inline=boolValue)
            data.add_field(name="Drop Info", value="There are {} left to enter the drop. \n{} users have entered the drop so far.".format(self.sec_to_min(self.drops[member.id]["timeleft"]), len(self.drops[member.id]["enteredplayers"])), inline=boolValue)
            data.add_field(name="Enter the drop", value="Message {} \"!enter {}\".".format(self.bot.user.mention ,member.name), inline=boolValue)
        else:
            data.add_field(name="Ended Drop Alert", value="{} did a drop!".format(member.mention), inline=boolValue)
            data.add_field(name="Drop Info", value="This drop has ended. \n{} users entered the drop.".format(len(self.drops[member.id]["enteredplayers"])), inline=boolValue)
        return data
    async def schedule_update(self, member, message, delay):
        if (self.drops[member.id]["timeleft"] - 30) >= 0:   
            #self.bot.loop.call_later(
            #    delay, self.update_delay_msg, member, message)
            print("flag 1")
            await asyncio.sleep(delay)
            await self.update_delay_msg(member, message)
    async def update_delay_msg(self, member: discord.Member, message):
        print("update delay")
        self.drops[member.id].update({"timeleft": self.drops[member.id]["timeleft"] - 30})
        await self.update_msg(member, message)
        await self.schedule_update(member, message, 30)
    async def update_msg(self, member: discord.Member, message):
        editedMessage = await self.bot.edit_message(message, embed=self.msg_builder(member))
        self.drops[member.id].update({"message": editedMessage})
    def sec_to_min(self, seconds):
        if seconds < 60:
            return str(seconds) + " seconds"
        elif seconds % 60 == 0:
            return str(seconds / 60) + " minutes"
        else:
            return str(seconds / 60) + " minutes and " + str(seconds % 60) + " seconds"
    def get_users_with_role(self, server: discord.Server,
                                 role: discord.Role) -> List[discord.User]:
            roled = []
            for member in server.members:
                if (not member.bot) and self._member_has_role(member, role):
                    roled.append(member)
            return roled
    def _member_has_role(self, member: discord.Member, role: discord.Role):
        return role in member.roles
def setup(bot):
    n = moneyDrop(bot)
    bot.add_cog(n)
