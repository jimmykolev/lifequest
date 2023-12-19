import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import certifi
from colorama import Fore, Back, Style
from itertools import cycle
import asyncio

# Load SSL Certificates
os.environ['SSL_CERT_FILE'] = certifi.where()

# Load .env file
load_dotenv()
TOKEN = os.getenv('TOKEN')

# Create client
client = commands.Bot(command_prefix = '!', intents = discord.Intents.all())

# Status Loop
status = cycle(['with Humans!', 'with LifeQuest!', 'with Life Decisions!'])

@tasks.loop(seconds=15)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))

# On Ready Event
@client.event
async def on_ready():
    await client.tree.sync()
    print(Fore.GREEN + 'Success: Client is loaded and active.')
    change_status.start()


@client.command(name="sync")
async def sync(ctx):
    synced = await client.tree.sync()
    print(f'Synced {len(synced)} commands')

async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await client.load_extension(f'cogs.{filename[:-3]}')

async def main():
    async with client:
        await load()
        await client.start(TOKEN)

asyncio.run(main())