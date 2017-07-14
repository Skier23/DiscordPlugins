import discord
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
from __main__ import send_cmd_help
import os
from .utils.chat_formatting import *

class Register:
    """The Register Cog. Also will handle currency/reputation"""

    def __init__(self, bot):
        self.bot = bot
        self.profile = "data/account/accounts.json"
        self.usersArray = dataIO.load_json(self.profile)
    
    @commands.command(name="signup", pass_context=True, invoke_without_command=True, no_pm=True)
    async def _reg(self, ctx, rockstarID : str):
        """Sign up with your SocialClub name to join channels and drops"""
		
		
        server = ctx.message.server
        user = ctx.message.author
        
        if server.id not in self.usersArray:
            self.usersArray[server.id] = {}
        if user.id not in self.usersArray[server.id]:
            for key in self.usersArray[server.id]:
                if "SocialClub" in self.usersArray[server.id][key]:
                    if self.usersArray[server.id][key]["SocialClub"] == rockstarID:
                        data = discord.Embed(colour=user.colour)
                        data.add_field(name="Failure!:warning:",value="This SocialClub is already registered to another member.\n Please try again or contact an administrator if this is your SocialClub.")
                        await self.bot.say(embed=data)
                        return
                pass
            self.usersArray[server.id][user.id] = {}
            self.usersArray[server.id][user.id].update({"SocialClub" : rockstarID})
            dataIO.save_json(self.profile, self.usersArray)
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Congrats!:sparkles:", value="You have officially created your account for **{}**, {}.".format(server, user.mention))
            role = discord.utils.get(server.roles, name="Member")
            await self.bot.add_roles(user, role)
            await self.bot.server_voice_state(user, mute=False)
            await self.bot.say(embed=data)
        else: 
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Error:warning:",value="Oops, it seems like you already have an account, {}.".format(user.mention))
            await self.bot.say(embed=data)
    @commands.command(name="account", pass_context=True, invoke_without_command=True, no_pm=True)
    async def _acc(self, ctx, user : discord.Member=None):
        """Your/Others account"""
                    
        server = ctx.message.server
        
        if server.id not in self.usersArray:
            self.usersArray[server.id] = {}
        else:
            pass
        if not user:
            user = ctx.message.author
            if user.id in self.usersArray[server.id]:
                data = discord.Embed(colour=user.colour)
                boolValue = True
                data.add_field(name="Discord:", value="{}".format(user.mention), inline=boolValue)
                data.add_field(name="SocialClub:", value=self.usersArray[server.id][user.id]["SocialClub"])
                if "About" in self.usersArray[server.id][user.id]:
                    about = self.usersArray[server.id][user.id]["About"]
                    data.add_field(name="About:", value=about)
                if user.avatar_url:
                    data.set_thumbnail(url=user.avatar_url)
                await self.bot.say(embed=data)
            else:
                prefix = ctx.prefix
                data = discord.Embed(colour=user.colour)
                data.add_field(name="Error:warning:",value="Sadly, this feature is only available for people who had registered for an account. \n\nYou can register for a account today for free. All you have to do is say `{}signup` and you'll be all set.".format(prefix))
                await self.bot.say(embed=data)
        else:
            server = ctx.message.server
            if user.id in self.usersArray[server.id]:
                data = discord.Embed(colour=user.colour)
                boolValue = True
                data.add_field(name="Discord:", value="{}".format(user.mention), inline=boolValue)
                data.add_field(name="SocialClub:", value=self.usersArray[server.id][user.id]["SocialClub"])
                if "About" in self.usersArray[server.id][user.id]:
                    about = self.usersArray[server.id][user.id]["About"]
                    data.add_field(name="About:", value=about)
                if user.avatar_url:
                    data.set_thumbnail(url=user.avatar_url)
                await self.bot.say(embed=data)
            else:
                data = discord.Embed(colour=user.colour)
                data.add_field(name="Error:warning:",value="{} doesn't have an account at the moment, sorry.".format(user.mention))
                await self.bot.say(embed=data)

    @commands.group(name="update", pass_context=True, invoke_without_command=True, no_pm=True)
    async def update(self, ctx):
        """Update your TPC"""
        await send_cmd_help(ctx)

    @update.command(pass_context=True, no_pm=True)
    async def about(self, ctx, *, about):
        """Tell us about yourself"""
        
        server = ctx.message.server
        user = ctx.message.author
        prefix = ctx.prefix

        if server.id not in self.usersArray:
            self.usersArray[server.id] = {}
        else:
            pass
        
        if user.id not in self.usersArray[server.id]:
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Error:warning:",value="Sadly, this feature is only available for people who had registered for an account. \n\nYou can register for a account today for free. All you have to do is say `{}sign up` and you'll be all set.".format(prefix))
            await self.bot.say(embed=data)
        else:
            self.usersArray[server.id][user.id].update({"About" : about})
            dataIO.save_json(self.profile, self.usersArray)
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Congrats!:sparkles:",value="You have updated your About Me to{}".format(about))
            await self.bot.say(embed=data)
    @commands.command(name="remove", pass_context=True, invoke_without_command=True, no_pm=True)
    async def remove(self, ctx, user : discord.Member=None):
        """Remove the specified member from the registry"""
        
        server = ctx.message.server
        if not user:
            user = ctx.message.author
        if server.id not in self.usersArray:
            self.usersArray[server.id] = {}
        if user.id not in self.usersArray[server.id]:
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Failure", value="{} is not registered.".format(user.mention))
            await self.bot.say(embed=data)
        else:
            del self.usersArray[server.id][user.id]
            dataIO.save_json(self.profile, self.usersArray)
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Removed", value="You have removed {}'s record from the registrar.".format(user.mention))
            role = discord.utils.get(server.roles, name="Member")
            await self.bot.remove_roles(user, role)
            await self.bot.say(embed=data)
    async def member_join(self, member):
        await self.bot.say("user joined")
        await self.bot.send_message("hello user")
def check_folder():
    if not os.path.exists("data/account"):
        print("Creating data/account folder...")
        os.makedirs("data/account")

def check_file():
    data = {}
    f = "data/account/accounts.json"
    if not dataIO.is_valid_json(f):
        print("I'm creating the file, so relax bruh.")
        dataIO.save_json(f, data)

def setup(bot):
    check_folder()
    check_file()
    x = Register(bot)
    bot.add_listener(x.member_join, "on_member_join")
    bot.add_cog(x)
