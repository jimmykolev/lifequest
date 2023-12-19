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
    def __init__(self, user_id):
        super().__init__(timeout=60.0)
        self.user_id = user_id

    @discord.ui.button(label='Yes', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, Button: discord.ui.Button):
        await interaction.response.send_message(content = f'<@{self.user_id}> Your character has been deleted.', ephemeral=True)
        await collection.delete_one({'user_id': self.user_id, 'character': { '$exists': True }})
        self.stop()

    @discord.ui.button(label='No', style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, Button: discord.ui.Button):
        # Use follow-up response
        await interaction.response.send_message(content = f'<@{self.user_id}> Your character has not been deleted.', ephemeral=True)
        self.stop()





class Delete(commands.Cog):
    def __init__(self, client: commands.Bot):
            self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(Fore.CYAN + '- Delete Cog is loaded and active.')
    
    @app_commands.command(name="delete", description="Delete your current character")
    @app_commands.guilds(discord.Object(id=1070668718713085983))  # Replace with your guild ID
    async def delete(self, interaction: discord.Interaction):
        user = collection.find_one({'user_id': interaction.user.id, 'character': { '$exists': True }})
        if user is None:
            await interaction.response.send_message('You do not have a character. Use **/start** to create one.', ephemeral=True)
        else:
            view = Confirm(interaction.user.id)
            await interaction.response.send_message('Are you sure you want to delete your character? This action is irreversible.', view=view, ephemeral=True)


        
        
        
async def setup(client):
    await client.add_cog(Delete(client))