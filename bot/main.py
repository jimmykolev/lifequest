import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import certifi
from colorama import Fore, Back, Style
import random

# Load SSL Certificates
os.environ['SSL_CERT_FILE'] = certifi.where()

# Load .env file
load_dotenv()
TOKEN = os.getenv('TOKEN')

# Create client
client = commands.Bot(command_prefix = '!', intents = discord.Intents.all())

# On Ready Event
@client.event
async def on_ready():
    print(Fore.GREEN + 'Success: Client is loaded and active.')

@client.command()
async def ping(ctx):
    await ctx.author.send('Pong!')
    
    
@client.command(aliases=['8ball'])
async def eightball(ctx, *, question):
    list = ['Yes', 'No', 'Maybe', 'Probably', 'Probably Not', 'Ask Again Later']
    await ctx.send(f'<@{ctx.author.id}> ' + random.choice(list))   



# Run client
client.run(TOKEN)
