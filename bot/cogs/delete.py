import discord
from discord.ext import commands
from discord import app_commands
from colorama import Fore, Back, Style
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
DB = os.getenv('DB')

mongoClient = MongoClient(DB) 
db = mongoClient['lifequest']
collection = db['users']

class Confirm(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60.0)
    
    @discord.ui.button(label='Yes', style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        collection.delete_one({'user_id': interaction.user.id, 'character': { '$exists': True }})
        await interaction.response.send_message('Character deleted.', ephemeral=True)
        # Add your code to delete the character here.

    @discord.ui.button(label='No', style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message('Character deletion cancelled.', ephemeral=True)
        self.stop()  # This will stop the View from listening for more interactions.



class Delete(commands.Cog):
    def __init__(self, client: commands.Bot):
            self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(Fore.CYAN + '- Delete Cog is loaded and active.')
    
    @app_commands.command(name="delete", description="Delete your current character")
    async def delete(self, interaction: discord.Interaction):
        user = collection.find_one({'user_id': interaction.user.id, 'character': { '$exists': True }})
        if user is None:
            await interaction.response.send_message('You do not have a character. Use **/start** to create one.')
            return
        else:
            view = Confirm()
            
            await interaction.response.send_message('Are you sure you want to delete your character? This action is irreversible.', view=view, ephemeral=True)

        
        
        
async def setup(client):
    await client.add_cog(Delete(client))