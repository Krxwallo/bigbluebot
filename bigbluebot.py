# bigbluebot.py
import os
import sys
from queue import Queue

import discord
from _queue import Empty
from discord.ext import commands
from dotenv import load_dotenv

import asyncio

from native_messaging import NativeMessagingThread

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
BIG_BLUE_CHANNEL_ID = 806143660172640306

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='+', intents=intents)


@bot.event
async def on_ready():
    # logging.info("Starting up...")
    if len(sys.argv) > 3 and sys.argv[1] == "restart":
        # logging.info(f'Restarted.')
        await bot.get_channel(int(sys.argv[2])).send("Restarted.")
    else:
        await bot.get_channel(BIG_BLUE_CHANNEL_ID).send("Bot is online.")
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
    await ctx.send("Online.")


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


# logging.debug("Started thread.")


async def onStatusChange(name, status):
    for guild in bot.guilds:
        for member in guild.members:
            if member.nick == name:
                if status == "muted":
                    await member.edit(mute=False, deafen=False)
                elif status == "voice":
                    await member.edit(mute=True, deafen=True)


async def get_data():
    global q
    while True:
        try:
            data = q.get(block=False)
            if data:
                # Process data
                await onStatusChange(data.split("_")[0], data.split("_")[1])
                pass
        except Empty as e:
            pass
        await asyncio.sleep(0.02)


bot.loop.create_task(get_data())
bot.run(TOKEN)
