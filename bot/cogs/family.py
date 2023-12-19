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

class Family(commands.Cog):
    def __init__(self, client: commands.Bot):
            self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('- Family Cog is loaded and active.')
    
    @app_commands.command(name="family", description="See information about your current life's family")
    async def family(self, interaction: discord.Interaction):
        user = collection.find_one({'user_id': interaction.user.id, 'character': { '$exists': True }})
        if user is None:
            await interaction.response.send_message('You do not have a character. Use **/start** to create one.')
            return
        else:
            character = collection.find_one({'user_id': interaction.user.id})['character']
            embed = discord.Embed(title = 'Family Information', description = 'Details about your character\'s family', color = discord.Color.blue()) 
            embed.set_author(name=f'Requested by {interaction.user}', icon_url=interaction.user.avatar)
            # Parents Information
            for i, parent in enumerate(character['parents'], start=1):
              parent_role = 'Mother' if parent['gender'].lower() == 'female' else 'Father'
              embed.add_field(name=f"{parent_role}", value=f"**Name:** {parent['name']}\n**Age:** {parent['age']}\n**Occupation:** {parent['occupation']}", inline=True)

            # Siblings Information
            if character['siblings']:
              siblings_info = '\n'.join([f"**Sibling {i}:** {sibling['name']} - Age: {sibling['age']}" for i, sibling in enumerate(character['siblings'], start=1)])
              embed.add_field(name='Siblings', value=siblings_info, inline=False)

        await interaction.response.send_message(embed=embed)

        
        
        
async def setup(client):
    await client.add_cog(Family(client))