import discord
from discord.ext import commands
from discord import app_commands
from colorama import Fore, Back, Style
from faker import Faker
import random
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
DB = os.getenv('DB')

mongoClient = MongoClient(DB) 
db = mongoClient['lifequest']
collection = db['users']

class Start(commands.Cog):
    def __init__(self, client: commands.Bot):
            self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(Fore.CYAN + '- Start Cog is loaded and active.')
    

    
    def insert_character(self, user_id, character):
           collection.update_one({'user_id': user_id}, {'$set': {'character': character}}, upsert=True)

    def generate_character(self):
        country_to_locale = {
            'Italy': 'it_IT',
            'France': 'fr_FR',
            'Germany': 'de_DE',
            'China': 'zh_CN',
            'India': 'hi_IN',
            'Japan': 'ja_JP',
            'United States': 'en_US',
            'United Kingdom': 'en_GB',
        }
        
        country, locale = random.choice(list(country_to_locale.items()))
        
        fake = Faker(locale)
        
        print('Genterating gender')
        gender = random.choice(['Male', 'Female'])
        if gender == 'Male':
            firstName = fake.first_name_male()
        else:
            firstName = fake.first_name_female()  
            
        lastName = fake.last_name()      
        city = fake.city()
        
        print('Generated ' + firstName + ' ' + lastName + ' in ' + city + ', ' + country + " Gender: " + gender)
           
        siblings = []
        max_sibling_age = 18
        print('Generating siblings')
        for _ in range(random.randint(0, 3)): 
           sibling_gender = random.choice(['Male', 'Female'])
           sibling_name = fake.first_name_male() if sibling_gender == 'Male' else fake.first_name_female()
           sibling_age = random.randint(0, max_sibling_age)
           siblings.append({'name': f"{sibling_name} {lastName}", 'age': sibling_age, 'gender': sibling_gender})
           # print each sibling
        print(siblings)
            
        

        print('Generating parents')
        youngest_parent_age = random.randint(max_sibling_age + 20, + max_sibling_age + 40)
        print(youngest_parent_age)
        father_name = fake.first_name_male()
        print(father_name)
        mother_name = fake.first_name_female()
        print(mother_name)
        parents = [
        {'name': f"{father_name} {lastName}", 'occupation': fake.job(), 'age': youngest_parent_age, 'gender': 'Male'},
        {'name': f"{mother_name} {lastName}", 'occupation': fake.job(), 'age': youngest_parent_age + random.randint(-5, 5), 'gender': 'Female'}
    ]
        
        
        attributes = {
            'happiness': random.randint(80, 100),
            'health': random.randint(60, 100),
            'smart': random.randint(0, 100),
            'looks': random.randint(0, 100),
        }
        
        age = 0
        life_stage = 'baby'
        
        education = {
            'pre_school': False,
            'elementary_school': False,
            'middle_school': False,
            'high_school': False,
            'university': False,
            'graduate_school': False,
            'none': True
        }
        
        degree = None
        occupation = None
        doing_degree = False
        
        character = {
            'name': {'first': firstName, 'last': lastName},
            'location': {'country': country, 'city': city},
            'parents': parents,
            'siblings': siblings,
            'attributes': attributes,
            'age': age,
            'gender': gender,
            'life_stage': life_stage,
            'education': education,
            'occupation': occupation,
            'degree': degree,
            'doing_degree': doing_degree
        }
        
        return character
    
        
    @app_commands.command(name="start", description="Start a new life!")
    async def start(self, interaction: discord.Interaction):
        
        character = collection.find_one({'user_id': interaction.user.id, 'character': { '$exists': True }})
        if character:
            await interaction.response.send_message("You already have a character, view it with **/character**!")
            return
        else:    
         def attribute_to_progress_bar(attribute_value, max_value=100, bar_length=10):
            percentage = attribute_value / max_value
            filled_squares = round(percentage * bar_length)
            empty_squares = bar_length - filled_squares
            progress_bar = '🟩' * filled_squares + '⬛' * empty_squares
            return progress_bar
        
         print('Generating character')
         char = self.generate_character()
         print('Inserting character')
         self.insert_character(interaction.user.id, char)
         print('Character inserted')
         embed = discord.Embed(title = 'Character', description = 'Information about your current Life', color = discord.Color.blue())
         embed.add_field(name = 'Name', value = f"{char['name']['first']} {char['name']['last']}", inline = True)
         embed.add_field(name = 'Location', value = f"{char['location']['city']}, {char['location']['country']}", inline = False)
         embed.add_field(name = 'Age', value = str(char['age']), inline = True)
         embed.add_field(name = 'Gender', value = f"{char['gender']}", inline = True)
         embed.add_field(name = 'Life Stage', value = char['life_stage'], inline = True)
         embed.add_field(name = 'Happiness', value = f"{attribute_to_progress_bar(char['attributes']['happiness'])} {char['attributes']['happiness']}%", inline = False)
         embed.add_field(name = 'Health', value = f"{attribute_to_progress_bar(char['attributes']['health'])} {char['attributes']['health']}%", inline = False)
         embed.add_field(name = 'Smarts', value = f"{attribute_to_progress_bar(char['attributes']['smart'])} {char['attributes']['smart']}%", inline = False)
         embed.add_field(name = 'Looks', value = f"{attribute_to_progress_bar(char['attributes']['looks'])} {char['attributes']['looks']}%", inline = False)
        print(char)
        await interaction.response.send_message(embed = embed)
     
async def setup(client):
    await client.add_cog(Start(client))        