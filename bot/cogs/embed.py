import discord
from discord.ext import commands
from discord import app_commands
from colorama import Fore, Back, Style

class Embed(commands.Cog):
    def __init__(self, client: commands.Bot):
            self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(Fore.CYAN + '- Embed Cog is loaded and active.')
    
        
    @app_commands.command(name="embed", description="Returns an embed.")
    async def embed(self, interaction: discord.Interaction):
        embed = discord.Embed(title = 'Title', description = 'Description', color = discord.Color.blue()) 
        embed.set_author(name=f'Requested by {interaction.user}', icon_url=interaction.user.avatar)
        embed.add_field(name = 'Field Name', value = 'Field Value', inline = False)
        await interaction.response.send_message(embed = embed)
        
async def setup(client):
    await client.add_cog(Embed(client))        