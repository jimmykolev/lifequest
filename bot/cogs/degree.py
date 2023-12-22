import discord
from discord.ext import commands
from discord import app_commands
from colorama import Fore, Back, Style
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import json
import random

load_dotenv()
DB = os.getenv('DB')

mongoClient = MongoClient(DB) 
db = mongoClient['lifequest']
collection = db['users']

class Choices(discord.ui.View):
    def __init__(self, user_id, choices):
        super().__init__()
        self.user_id = user_id
        self.value = None
        self.choices = choices
        self.choice1 = choices[0]
        self.choice2 = choices[1]
        self.choice3 = choices[2]
        
        self.children[0].label = self.choice1['degree']
        self.children[1].label = self.choice2['degree']
        self.children[2].label = self.choice3['degree']
        
    @discord.ui.button(label='1', style=discord.ButtonStyle.blurple)
    async def one(self, interaction: discord.Interaction, Button: discord.ui.Button):
        character = collection.find_one({'user_id': self.user_id})['character']
        character['degree'] = self.choice1
        character['doing_degree'] = True
        self.value = self.choice1
        collection.update_one({'user_id': self.user_id}, {'$set': {'character': character}}, upsert=True)
        await interaction.response.send_message(f'You chose {self.choice1['degree']}', ephemeral=True)
        self.stop()
    @discord.ui.button(label='2', style=discord.ButtonStyle.blurple)
    async def two(self, interaction: discord.Interaction, Button: discord.ui.Button):
        character = collection.find_one({'user_id': self.user_id})['character']
        character['degree'] = self.choice2
        character['doing_degree'] = True
        self.value = self.choice2
        collection.update_one({'user_id': self.user_id}, {'$set': {'character': character}}, upsert=True)
        await interaction.response.send_message(f'You chose {self.choice2['degree']}', ephemeral=True)
        self.stop()
    @discord.ui.button(label='3', style=discord.ButtonStyle.blurple)
    async def three(self, interaction: discord.Interaction, Button: discord.ui.Button):
        character = collection.find_one({'user_id': self.user_id})['character']
        character['degree'] = self.choice3
        character['doing_degree'] = True
        self.value = self.choice3
        collection.update_one({'user_id': self.user_id}, {'$set': {'character': character}}, upsert=True)
        await interaction.response.send_message(f'You chose {self.choice3['degree']}', ephemeral=True)
        self.stop()


class Degree(commands.Cog):
    def __init__(self, client: commands.Bot):
            self.client = client
            with open('degrees.json') as f:
                self.degrees = json.load(f)
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(Fore.CYAN + '- Degree Cog is loaded and active.')
    
    @app_commands.command(name="degree", description="Choose your degree")
    @app_commands.guilds(discord.Object(id=1070668718713085983))
    async def degree(self, interaction: discord.Interaction):
        user = collection.find_one({'user_id': interaction.user.id, 'character': { '$exists': True }})
        if user['character']['education']['university'] == True and user['character']['doing_degree'] == False:
            embed = discord.Embed(title = 'Degree', description = 'Choose your degree, to reroll, use **/degree** again!', color = discord.Color.blue())
            embed.set_author(name=f'Requested by {interaction.user}', icon_url=interaction.user.avatar)
            selected_degrees = random.sample(self.degrees, 3)
            for i, degree in enumerate(selected_degrees, start=1):
                embed.add_field(name=f"{degree['degree']}", value=f"{degree['field']}, {str(degree['duration'])} years.", inline=False)
            view = Choices(interaction.user.id, selected_degrees)
        
            await interaction.response.send_message('Choose your degree', ephemeral=True, embed=embed, view=view)
        elif user is None:
            await interaction.response.send_message('You do not have a character. Use **/start** to create one.', ephemeral=True)
        elif user['character']['education']['university'] == False: 
            await interaction.response.send_message('You are not in university', ephemeral=True)
        elif user['character']['doing_degree'] == True:
            await interaction.response.send_message('You are already doing a degree', ephemeral=True)
      


        
        
        
async def setup(client):
    await client.add_cog(Degree(client))