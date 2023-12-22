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

class Character(commands.Cog):
    def __init__(self, client: commands.Bot):
            self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('- Character Cog is loaded and active.')
    
    @app_commands.command(name="character", description="See information about your current life")
    async def character(self, interaction: discord.Interaction):
        user = collection.find_one({'user_id': interaction.user.id, 'character': { '$exists': True }})
        
        if user is None:
            await interaction.response.send_message('You do not have a character. Use **/start** to create one.')
        else:
            character = collection.find_one({'user_id': interaction.user.id})['character']
            def attribute_to_progress_bar(attribute_value, max_value=100, bar_length=10):
               percentage = attribute_value / max_value
               filled_squares = round(percentage * bar_length)
               empty_squares = bar_length - filled_squares
               progress_bar = '🟩' * filled_squares + '⬛' * empty_squares
               return progress_bar
           
            if character['education']['pre_school'] == True:
               education = 'Pre-School'
            elif character['education']['elementary_school'] == True:
                education = 'Elementary School'
            elif character['education']['middle_school'] == True:
                education = 'Middle School'
            elif character['education']['high_school'] == True:
                education = 'High School'
            elif character['education']['university'] == True:
                education = 'University'
            elif character['education']['none'] == True:
                education = 'None'
                
            if character['occupation'] == None:
                occupation = 'None'
            embed = discord.Embed(title = 'Character', description = 'Information about your current Life', color = discord.Color.blue()) 
            embed.set_author(name=f'Requested by {interaction.user}', icon_url=interaction.user.avatar)
            embed.add_field(name = 'Name', value = f"{character['name']['first']} {character['name']['last']}", inline = True)
            embed.add_field(name = 'Location', value = f"{character['location']['city']}, {character["location"]["country"]}", inline = False)
            embed.add_field(name = 'Age', value =str(character['age']), inline = True)
            embed.add_field(name = 'Life Stage', value = character['life_stage'], inline = True)
            embed.add_field(name = 'Education', value = education, inline = True)
            embed.add_field(name = 'Occupation', value = occupation, inline = True)
            embed.add_field(name = 'Happiness', value = f'{attribute_to_progress_bar(character["attributes"]["happiness"])} {character["attributes"]["happiness"]}%', inline = False)
            embed.add_field(name = 'Health', value = f'{attribute_to_progress_bar(character["attributes"]["health"])} {character["attributes"]["health"]}%', inline = False)
            embed.add_field(name = 'Smarts', value = f'{attribute_to_progress_bar(character["attributes"]["smart"])} {character["attributes"]["smart"]}%', inline = False)
            embed.add_field(name = 'Looks', value = f'{attribute_to_progress_bar(character["attributes"]["looks"])} {character["attributes"]["looks"]}%', inline = False)
            await interaction.response.send_message(embed = embed)
        
        
        
async def setup(client):
    await client.add_cog(Character(client))