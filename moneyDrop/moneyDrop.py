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
    @commands.bot_has_role("Dropper")
    @commands.command(name="startdrop", pass_context=True, invoke_without_command=True, no_pm=True)
    async def startDrop(self, ctx, role : discord.Role=None):
        member = ctx.message.author
        server = ctx.message.server
        channel1 = ctx.message.channel    
        print("starting drop")
        self.drops[member.id] = {}
        self.drops[member.id].update({"dropstate": dropState.PICKING})
        players = []
        self.drops[member.id].update({"enteredplayers": players})
        await self.bot.send_message(channel1, "How many users would you like to accept for the drop (2-20)?")
        amountOfPlayers = await self.bot.wait_for_message(author=member, channel=channel1)
        amountOfPlayers = amountOfPlayers.content
        if not str.isnumeric(amountOfPlayers):
            await self.bot.send_message(channel1, "Try again but next time enter a number you dummy!")
            return
        playersInt = int(amountOfPlayers)
        if not playersInt >= 2 and playersInt <= 20:
            await self.bot.send_message(channel1, "Try again but next time enter a number between 2 and 20 you dummy!")
            return
        self.drops[member.id].update({"numplayers": playersInt})
        await self.bot.send_message(channel1, "How many minutes would you like the drop to be open for (3-10)?")
        minutes = await self.bot.wait_for_message(author=member, channel=channel1)
        minutes = minutes.content
        if not str.isnumeric(minutes):
            await self.bot.send_message(channel1, "Try again but next time enter a number you dummy!")
            return
        minutesInt = int(minutes)
        if not minutesInt >= 3 and playersInt <= 10:
            await self.bot.send_message(channel1, "Try again but next time enter a number between 3 and 10 you dummy!")
            return
        self.drops[member.id].update({"timetoenter": 60 * minutesInt})
        self.drops[member.id].update({"timeleft": self.drops[member.id]["timetoenter"]})
        channel = server.get_channel(self.dropChannelId)
        data = self.msg_builder(member)
        self.drops[member.id].update({"message": await self.bot.send_message(channel, embed = data)})
        if role is None:
            role = server.role_hierarchy[0]
        developers = self.get_users_with_role(server, role)
        data2 = discord.Embed(colour=discord.Colour.green())
        boolValue = False
        data2.add_field(name="Drop Alert", value="{} has started a drop!".format(member.mention), inline=boolValue)
        data2.add_field(name="Enter the drop", value="Reply with \"!enter {}\" to enter the drop.".format(member.name), inline=boolValue)
        for user in developers:
            await self.bot.send_message(user, embed=data2)
        await asyncio.gather(self.schedule_update(member, self.drops[member.id]["message"], 30), self.schedule_drop_close(member, self.drops[member.id]["timetoenter"], self.drops[member.id]["numplayers"], server))
    @commands.command(name="enter", pass_context=True, invoke_without_command=True)
    async def enterDrop(self, ctx, dropper: discord.Member):
        user = ctx.message.author
        account = self.bot.get_cog("Register")
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
                registered = await account.registered(user, dropper.server)
                if not registered:
                    await self.bot.send_message(user, "You need to register before you can enter drops!")
                    return
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
        self.drops[user.id].update({"selectedplayers": selectedPlayers})
        role = discord.utils.get(server.roles, name="Drop")
        for id in selectedPlayers:
            thisMember = server.get_member(id)
            await self.bot.send_message(thisMember, "Congrats you have been accepted to the drop!")
            await self.bot.send_message(thisMember, "Go over to #drop-1 for instructions for the drop.")
            await self.bot.add_roles(user, role)
        for id in self.drops[user.id]["enteredplayers"]:
            if id not in selectedPlayers:
                thisMember = server.get_member(id)
                await self.bot.send_message(thisMember, "Unfortunately you have not been accepted to this drop. Try again next time.")
        account = self.bot.get_cog("Register")
        counter = 1
        socialClubs = "```Social Club names:\n"
        for id in selectedPlayers:
            thisMember = server.get_member(id)
            socialClub = await account.get_socialclub(thisMember, server)
            socialClubs = socialClubs + str(counter) + ". " + socialClub + "\n"
            counter += 1
        socialClubs = socialClubs + "```"
        await self.bot.send_message(user, socialClubs)
        await asyncio.sleep(4875)
        await self.end_drop(user)
    @commands.command(name="enddrop", pass_context=True, invoke_without_command=True, no_pm=True)
    async def end_drop_cmd(self, ctx):
        dropper = ctx.message.author
        server = dropper.server
        if dropper.id not in self.drops:
            await self.bot.send_message(dropper, "You are not dropping")
            return
        if self.drops[dropper.id]["dropstate"] is not dropState.ACTIVE:
            await self.bot.send_message(dropper, "You are not dropping")
            return
        await self.end_drop(dropper)
    async def end_drop(self, user: discord.Member):
        if self.drops[user.id]["dropstate"] is not dropState.ACTIVE:
            return
        role = discord.utils.get(user.server.roles, name="Drop")
        for id in self.drops[user.id]["selectedplayers"]:
            thisMember = user.server.get_member(id)
            await self.bot.send_message(thisMember, "This drop is now over.")
            await self.bot.send_message(thisMember, "Thanks for participating!")
            await self.bot.remove_roles(user, role)
        await self.bot.send_message(user, "Your drop is now over.")
        self.drops[user.id].update({"dropstate": dropState.INACTIVE})
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
            data.add_field(name="Drop Alert", value="{} has started a drop for {} players!".format(member.mention, self.drops[member.id]["numplayers"]), inline=boolValue)
            data.add_field(name="Drop Info", value="There are {} left to enter the drop. \n{} users have entered the drop so far.".format(self.sec_to_min(self.drops[member.id]["timeleft"]), len(self.drops[member.id]["enteredplayers"])), inline=boolValue)
            data.add_field(name="Enter the drop", value="Message {} \"!enter {}\".".format(self.bot.user.mention ,member.name), inline=boolValue)
        else:
            data.add_field(name="Ended Drop Alert", value="{} did a drop for {} players!".format(member.mention, self.drops[member.id]["numplayers"]), inline=boolValue)
            data.add_field(name="Drop Info", value="This drop has ended. \n{} users entered the drop.".format(len(self.drops[member.id]["enteredplayers"])), inline=boolValue)
        return data
    async def schedule_update(self, member, message, delay):
        if (self.drops[member.id]["timeleft"] - 30) >= 0:   
            #self.bot.loop.call_later(
            #    delay, self.update_delay_msg, member, message)
            #print("flag 1")
            await asyncio.sleep(delay)
            await self.update_delay_msg(member, message)
    async def update_delay_msg(self, member: discord.Member, message):
        #print("update delay")
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
            return str(int(seconds / 60)) + " minutes"
        else:
            return str(int(seconds / 60)) + " minutes and " + str(seconds % 60) + " seconds"
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
