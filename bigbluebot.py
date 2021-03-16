# bigbluebot.py
import asyncio
import os
import sys
from _queue import Empty
from queue import Queue

import discord
from discord.ext import commands
from dotenv import load_dotenv

from native_messaging import NativeMessagingThread

VERSION = "1.0.0-alpha"

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
BIG_BLUE_CHANNEL_ID = 806143660172640306

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='+', intents=intents)

print("bigbluebot.py called.")


@bot.event
async def on_ready():
    print("Starting up...")

    if len(sys.argv) > 3 and sys.argv[1] == "restart":
        # logging.info(f'Restarted.')
        await bot.get_channel(int(sys.argv[2])).send("Restarted.")
    else:
        await bot.get_channel(BIG_BLUE_CHANNEL_ID).send("Bot is online.")
#    for guild in bot.guilds:
#        if guild.name == "9a":
#            for member in guild.members:
#                try:
#                    await member.edit(nick=None)
#                except discord.errors.Forbidden:
#                    pass
    # logging.info("Started up.")


@commands.has_permissions(administrator=True)
@bot.command(aliases=["rs"])
async def restart(ctx):
    global thread
    await ctx.send(f'Restarting...')
    thread.stop()
    os.execl(sys.executable, os.path.abspath(__file__), *sys.argv, "restart", str(ctx.message.channel.id))


@bot.command(aliases=["state"])
async def status(ctx):
    await ctx.send("Online." + ctx.message.author.name)


@commands.has_permissions(administrator=True)
@bot.command(aliases=["stp"])
async def stop(ctx):
    await ctx.send(f'Stopping...')
    thread.stop()
    await bot.get_channel(BIG_BLUE_CHANNEL_ID).send("Bot is offline.")
    sys.exit()


@commands.has_permissions(administrator=True)
@bot.command(aliases=["p", "pl"])
async def play(ctx, game=""):
    if game == "":
        await ctx.send("Please specify a game.")
    else:
        await bot.change_presence(activity=discord.Game(name=game))
        await ctx.send("Changed playing game to '" + game + "'.")


# Create native messaging thread.
q = Queue()
thread = NativeMessagingThread(q)
thread.start()


# test
# logging.debug("Started thread.")


async def onStatusChange(name, status):
    name = str(name).lower()
    for guild in bot.guilds:
        for member in guild.members:
            surname = name.split(' ')[0]
            nickname = str(member.nick).lower()
            if surname in nickname:
                if status == "muted":
                    try:
                        await member.edit(mute=False, deafen=False)
                    except discord.errors.Forbidden:
                        print("Not allowed to mute/unmute " + member.name)
                    except discord.errors.HTTPException as e:
                        print("HTTPError: " + e.text)
                    print("Unmuted " + member.name)
                    try:
                        await member.edit(nick=member.nick.replace(" | talking", ""))
                    except discord.errors.Forbidden:
                        pass
                elif status == "voice":
                    try:
                        await member.edit(mute=True, deafen=True)
                    except discord.errors.HTTPException as e:
                        print("HTTPError: " + e.text)

                    try:
                        await member.edit(nick=member.nick + " | talking")
                    except discord.errors.Forbidden:
                        pass
                    print("Muted " + member.name)


async def get_data():
    global q
    while True:
        try:
            data = q.get(block=False)
            if data:
                print("Got DATA")
                # Process data
                await onStatusChange(data.split("_")[0], data.split("_")[1])
        except Empty:
            pass
        await asyncio.sleep(0.05)


DELAY = 30

bot.loop.create_task(get_data())

print("Starting to run bot.")
bot.run(TOKEN)
