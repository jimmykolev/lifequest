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


class LifeChoice(discord.ui.View):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.value = None
    
    @discord.ui.button(label='University', style=discord.ButtonStyle.primary)
    async def university(self, interaction: discord.Interaction, Button: discord.ui.Button):
        character = collection.find_one({'user_id': self.user_id})['character']
        character['education']['university'] = True
        character['education']['high_school'] = False
        character['education']['none'] = False
        collection.update_one({'user_id': self.user_id}, {'$set': {'character': character}})
        embed = discord.Embed(title="University", description="You've chosen to go to university! Use **/degree** to choice your degree", color=discord.Color.green())
        await interaction.response.send_message(embed=embed)
        self.stop()
    @discord.ui.button(label='Work', style=discord.ButtonStyle.primary)
    async def work(self, interaction: discord.Interaction, Button: discord.ui.Button):
        character = collection.find_one({'user_id': self.user_id})['character']
        character['education']['none'] = True
        character['education']['high_school'] = False
        collection.update_one({'user_id': self.user_id}, {'$set': {'character': character}})
        embed = discord.Embed(title="Work", description="You've chosen to go straight into work! Use **/job** to choice your job", color=discord.Color.green())
        await interaction.response.send_message(embed=embed)
        self.stop()
        
        


class NextDecisionView(discord.ui.View):
    def __init__(self, user_id, decisions, impact):
        super().__init__()
        self.user_id = user_id
        self.decisions = decisions
        self.impact = impact

    @discord.ui.button(label='Next Decision', style=discord.ButtonStyle.secondary)
    async def next_decision(self, interaction: discord.Interaction, Button: discord.ui.Button):
        # Create a new DecisionTwo view
        view = DecisionTwo(self.user_id, self.decisions, self.impact)
        view.children[0].label = self.decisions[1]['options'][0]['text']
        view.children[0].impact = self.decisions[1]['options'][0]['impact']
        view.children[1].label = self.decisions[1]['options'][1]['text']
        view.children[1].impact = self.decisions[1]['options'][1]['impact']
        # Create the next decision embed
        embed = discord.Embed(title=f"{self.decisions[1]['decision']}", description=f"{self.decisions[1]['description']}", color=discord.Color.blue())
        # Send the next decision embed with the DecisionTwo view
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class DecisionOne(discord.ui.View):
    def __init__(self, user_id, decisions):
        super().__init__()
        self.user_id = user_id
        self.decisions = decisions
        self.value = None
        self.impact = None

    @discord.ui.button(label='Option 1', style=discord.ButtonStyle.primary)
    async def option_1(self,interaction: discord.Interaction, Button: discord.ui.Button):
        character = collection.find_one({'user_id': self.user_id})['character']
        impact = self.decisions[0]['options'][0]['impact']
        self.impact = impact
        for attribute, value in impact.items():
          current_value = character['attributes'].get(attribute)
          if current_value is not None:
           character['attributes'][attribute] = min(max(current_value + value, 0), 100)
        self.value = 'Option 1'
        impact_embed = discord.Embed(title="Impact of your decision", description=f"You chose {self.decisions[0]["options"][0]["text"]}", color=discord.Color.green())
        for attribute, value in impact.items():
            impact_embed.add_field(name=f"{attribute.capitalize()}", value=f"+{str(value)}", inline=True)
            
        try:
            print(type(interaction))
            next_decision_view = NextDecisionView(self.user_id, self.decisions, self.impact)
            await interaction.response.send_message(embed=impact_embed, view=next_decision_view, ephemeral=True)
        except Exception as e:
            print(f"Error while sending impact embed: {e}")
        self.stop()

    @discord.ui.button(label='Option 2', style=discord.ButtonStyle.primary)
    async def option_2(self, interaction: discord.Interaction, Button: discord.ui.Button):
        character = collection.find_one({'user_id': self.user_id})['character']
        impact = self.decisions[0]['options'][1]['impact']  # Changed index to 1 for Option 2
        self.impact = impact
        for attribute, value in impact.items():
            current_value = character['attributes'].get(attribute)
            if current_value is not None:
                character['attributes'][attribute] = min(max(current_value + value, 0), 100)
        self.value = 'Option 2'  # Changed value to Option 2
        impact_embed = discord.Embed(title="Impact of your decision", description=f"You chose {self.decisions[0]['options'][1]['text']}", color=discord.Color.green())  # Changed index to 1 for Option 2
        for attribute, value in impact.items():
            impact_embed.add_field(name=f"{attribute.capitalize()}", value=f"+{str(value)}", inline=True)
        try:
            print(type(interaction))
            next_decision_view = NextDecisionView(self.user_id, self.decisions, self.impact)
            await interaction.response.send_message(embed=impact_embed, view=next_decision_view, ephemeral=True)
        except Exception as e:
            print(f"Error while sending impact embed: {e}")
        self.stop()

    
class DecisionTwo(discord.ui.View):
    def __init__(self, user_id, decisions, impact):
        super().__init__()
        self.user_id = user_id
        self.decisions = decisions
        self.value = None
        self.impact = impact

    @discord.ui.button(label='Option 1', style=discord.ButtonStyle.primary)
    async def option_1(self, interaction: discord.Interaction, Button: discord.ui.Button):
        character = collection.find_one({'user_id': self.user_id})['character']
        impact = self.decisions[1]['options'][0]['impact']  # Changed index to 1 for Option 2
        print(impact)
        print(self.impact)
        total_impact = {}
        for attribute, value in self.impact.items():
            total_impact[attribute] = value + impact.get(attribute, 0)
        print(total_impact)
        print(f"Before update: {character['attributes']}")
        for attribute, value in total_impact.items():
            current_value = character['attributes'].get(attribute)
            if current_value is not None:
                character['attributes'][attribute] = min(max(current_value + value, 0), 100)
                print(f"Updated {attribute} to {character['attributes'][attribute]}")
        character['age'] += 1
        if character['life_stage'] == 'baby' and character['age'] >= 2:
            character['life_stage'] = 'toddler'
        elif character['life_stage'] == 'toddler' and character['age'] >= 6:
            character['life_stage'] = 'child'
        elif character['life_stage'] == 'child' and character['age'] >= 13:
            character['life_stage'] = 'teen'
        elif character['life_stage'] == 'teen' and character['age'] >= 20:
            character['life_stage'] = 'young adult'
        elif character['life_stage'] == 'young adult' and character['age'] >= 30:
            character['life_stage'] = 'adult'
        elif character['life_stage'] == 'adult' and character['age'] >= 65:
            character['life_stage'] = 'senior'       
        character['parents'][0]['age'] += 1
        character['parents'][1]['age'] += 1
        if character['siblings']:
          for sibling in character['siblings']:
            sibling['age'] += 1
            
        if character['age'] >= 3:
            character['education']['pre_school'] = True
            character['education']['none'] = False
        if character['age'] >= 5:
            character['education']['elementary_school'] = True
            character['education']['pre_school'] = False
        if character['age'] >= 11:
            character['education']['middle_school'] = True
            character['education']['elementary_school'] = False
        if character['age'] >= 14:
            character['education']['high_school'] = True
            character['education']['middle_school'] = False
        if character['age'] >= 18:
            character['education']['none'] = True
            character['education']['high_school'] = False
            
            
                    
        print(f"After update: {character['attributes']}")
        self.value = 'Option 2'  # Changed value to Option 2
        impact_embed = discord.Embed(title="Impact of your decision", description=f"You chose {self.decisions[1]['options'][0]['text']}", color=discord.Color.green())  # Changed index to 1 for Option 2
        print(impact_embed)
        for attribute, value in impact.items():
            print(attribute + " " + str(value))
            impact_embed.add_field(name=f"{attribute.capitalize()}", value=f"+{str(value)}", inline=True)
            print(attribute.capitalize() + " " + str(value))
        try:
            collection.update_one({'user_id': self.user_id}, {'$set': {'character': character}})
        except Exception as e:
            print(f"Error while updating character: {e}")

        try:
            print(type(interaction))
            impact_embed.add_field(name="You've Aged Up!", value=f"+1", inline=False)
            if character['age'] >= 18:
                embed = discord.Embed(title="You've Graduated High School!", description="You've graduated high school! You can now choose to go to university or straight into work.", color=discord.Color.green())
                await interaction.user.send(embed=embed, view=LifeChoice(self.user_id))
            await interaction.response.send_message(embed=impact_embed)
        except Exception as e:
            print(f"Error while sending impact embed: {e}")
        self.stop()

    @discord.ui.button(label='Option 2', style=discord.ButtonStyle.primary)
    async def option_2(self, interaction: discord.Interaction, Button: discord.ui.Button):
        character = collection.find_one({'user_id': self.user_id})['character']
        print("get attributes")
        impact = self.decisions[1]['options'][1]['impact']  # Changed index to 1 for Option 2
        print(impact)
        print(self.impact)
        total_impact = {}
        for attribute, value in self.impact.items():
            total_impact[attribute] = value + impact.get(attribute, 0)
        print(total_impact)
        print(f"Before update: {character['attributes']}")
        for attribute, value in total_impact.items():
            current_value = character['attributes'].get(attribute)
            if current_value is not None:
                character['attributes'][attribute] = min(max(current_value + value, 0), 100)
                print(f"Updated {attribute} to {character['attributes'][attribute]}")
        character['age'] += 1
        character['parents'][0]['age'] += 1
        character['parents'][1]['age'] += 1
        if character['siblings']:
          for sibling in character['siblings']:
            sibling['age'] += 1
            
        if character['age'] >= 3:
            character['education']['pre_school'] = True
            character['education']['none'] = False
        if character['age'] >= 5:
            character['education']['elementary_school'] = True
            character['education']['pre_school'] = False
        if character['age'] >= 11:
            character['education']['middle_school'] = True
            character['education']['elementary_school'] = False
        if character['age'] >= 14:
            character['education']['high_school'] = True
            character['education']['middle_school'] = False
        if character['age'] >= 18:
            character['education']['none'] = True
            character['education']['high_school'] = False
 
                    
        print(f"After update: {character['attributes']}")
        self.value = 'Option 2'  # Changed value to Option 2
        impact_embed = discord.Embed(title="Impact of your decision", description=f"You chose {self.decisions[1]['options'][1]['text']}", color=discord.Color.green())  # Changed index to 1 for Option 2
        print(impact_embed)
        for attribute, value in impact.items():
            print(attribute + " " + str(value))
            impact_embed.add_field(name=f"{attribute.capitalize()}", value=f"+{str(value)}", inline=True)
            print(attribute.capitalize() + " " + str(value))
        try:
            collection.update_one({'user_id': self.user_id}, {'$set': {'character': character}})
        except Exception as e:
            print(f"Error while updating character: {e}")

        try:
            print(type(interaction))
            impact_embed.add_field(name="You've Aged Up!", value=f"+1", inline=False)
            if character['age'] >= 18:
                embed = discord.Embed(title="You've Graduated High School!", description="You've graduated high school! You can now choose to go to university or straight into work.", color=discord.Color.green())
                await interaction.user.send(embed=embed, view=LifeChoice(self.user_id))
            await interaction.response.send_message(embed=impact_embed)
        except Exception as e:
            print(f"Error while sending impact embed: {e}")
        self.stop()

class Progress(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        with open('decisions.json') as f:
            self.decisions = json.load(f)
            
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(Fore.CYAN + '- Progress Cog is loaded and active.')
    
    @app_commands.command(name="progress", description="Age up your character by one year.")
    @app_commands.guilds(discord.Object(id=1070668718713085983))
    async def progress(self, interaction: discord.Interaction):
        user = collection.find_one({'user_id': interaction.user.id, 'character': { '$exists': True }})
        
        if user is None:
            await interaction.response.send_message('You do not have a character. Use **/start** to create one.')
        else:
            character = collection.find_one({'user_id': interaction.user.id})['character']
            # get the current life stage
            life_stage = character['life_stage']
            # get all the decisions for the current life stage
            life_stage_decisions = [decision for decision in self.decisions if decision['lifestage'] == life_stage]
            # choose 2 random decisions
            decisions = random.sample(life_stage_decisions, 2)
            view = DecisionOne(interaction.user.id, decisions)
            view.children[0].label = decisions[0]['options'][0]['text']
            view.children[0].impact = decisions[0]['options'][0]['impact']
            view.children[1].label = decisions[0]['options'][1]['text']
            view.children[1].impact = decisions[0]['options'][1]['impact']
            embed = discord.Embed(title = f"{decisions[0]['decision']}", description = f"{decisions[0]['description']}", color = discord.Color.blue())
            
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        


        
        
        
async def setup(client):
    await client.add_cog(Progress(client))