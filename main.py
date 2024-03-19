# ---------- time imports -----------
import asyncio
import calendar
from datetime import datetime, timedelta
import datetime
import functools
import io
import typing
import os
from bson import ObjectId
import time
import json
from discord.ext import tasks
import random

# ----------- discord imports ---------
import discord
from discord import app_commands
from typing import Literal

# ----------- json imports ------------
import json

# --------- web imports ---------
import requests
from Helper_Functions.Scheduler import startup_sched
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from motor.motor_asyncio import AsyncIOMotorClient

# --------- other file imports ---------
from Web_Interaction.loopty_loop import master_loop
from Web_Interaction.curator import single_run
from Web_Interaction.scraping import single_scrape, get_image, single_scrape_v2
from Helper_Functions.create_embed import getEmbed
from Helper_Functions.roll_string import get_roll_string
from Helper_Functions.buttons import get_buttons
from Helper_Functions.update import update_p
from Web_Interaction.Screenshot import Screenshot
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from PIL import Image
from Helper_Functions.mongo_silly import get_mongo, dump_mongo, get_unix, collection #TODO: i dont need this anymore but too lazy to figure it out
from Helper_Functions.mongo_silly import *
from Helper_Functions.mongo_silly import _in_ce
from Helper_Functions.os import restart, add_to_windows_startup
from Helper_Functions.spreadsheet import csv_conversion


# ---------- command imports --------------
from Commands.Rolls.roll_solo import solo_command
from Commands.Rolls.roll_co_op import co_op_command

# --------------------------------------------------- ok back to the normal bot ----------------------------------------------
intents = discord.Intents.default()
intents.reactions = True
intents.members = True
intents.guilds = True



client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

intents.message_content = True

with open('Jasons/help_embed_data.json') as f:
    test = json.load(f)



# Grab information from json file
with open('Jasons/secret_info.json') as f :
    localJSONData = json.load(f)


if _in_ce:
    discord_token = localJSONData['discord_token']  
    guild_ID = localJSONData['ce_guild_ID']
else :
    discord_token = localJSONData['third_discord_token']
    guild_ID = localJSONData['test_guild_ID']






# test function that never really worked lol
"""
async def aaaa_auto(interaction : discord.Interaction, current:str) -> typing.List[app_commands.Choice[str]]:
    data = []
    database_name = await get_mongo("name")
    print(database_name) 

    for game in list(database_name.keys()):
        data.append(app_commands.Choice(name=game,value=game))
    print(data)
    return data
"""



"""
@tree.command(name="aaaaa", description="afjdals", guild=discord.Object(id=guild_ID))
#@app_commands.autocomplete(item=aaaa_auto)
async def aaaaa(interaction : discord.Interaction, item : str, date):
    await interaction.response.defer()  
"""













# ---------------------------------------------------------------------------------------------------------------------------------- #
# -----------------------------------------------                               ---------------------------------------------------- #
# -----------------------------------------------          HELP COMMAND         ---------------------------------------------------- #
# -----------------------------------------------                               ---------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
@tree.command(name="help", description="help", guild=discord.Object(id=guild_ID))
async def help(interaction : discord.Interaction) :
    await interaction.response.defer(ephemeral=True)

    page_data = json.loads(open("Jasons/help_embed_data.json").read())

    basic_options = page_data['Options']
    selections = []

    roll_options = page_data['Rollsy']
    rolls = []

    admin_options = page_data['Admin']
    admin = []

    mod_role = discord.utils.get(interaction.guild.roles, name = "Mod")
    admin_role = discord.utils.get(interaction.guild.roles, name = "Admin")


    embed = discord.Embed(
        title="Help",
        colour= 0x036ffc,
        timestamp=datetime.datetime.now(),
        description="Here you can use the drop down menu to learn about various features CE Assistant can help you with."
    )
    embed.set_thumbnail(url=ce_mountain_icon)


    for option in basic_options:
        if option == 'Admin Options' and (not mod_role in interaction.user.roles and not admin_role in interaction.user.roles and 413427677522034727 != interaction.user.id):
            continue
        selections.append(discord.SelectOption(
            label=basic_options[option]['Name'],
            emoji=basic_options[option]['Emoji'],
            description=basic_options[option]['Description']))

    for option in roll_options:
        rolls.append(discord.SelectOption(
            label=roll_options[option]['Name'],
            emoji=roll_options[option]['Emoji'],
            description=roll_options[option]['Description']))
        


    for option in admin_options:
        admin.append(discord.SelectOption(
            label=admin_options[option]['Name'],
            emoji=admin_options[option]['Emoji'],
            description=admin_options[option]['Description']))
    

    class HelpSelect(discord.ui.Select):
        def __init__(self, select, message="Select an option...", row=1):
            options=select
            super().__init__(placeholder=message, max_values=1,min_values=1,options=options, row=row)


        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer()
            embed = self.get_embed()
            if self.values[0] == 'Rolls' or self.values[0] in list(roll_options.keys()):
                await interaction.followup.edit_message(embed = embed, view=HelpSelectView(
                    menu=rolls, 
                    message="Select an option...", 
                    message_2="Select a roll option..."), 
                    message_id = interaction.message.id)
            elif self.values[0] == 'Admin Options' or self.values[0] in list(admin_options.keys()):
                await interaction.followup.edit_message(embed = embed, view=HelpSelectView(
                    menu=admin, 
                    message="Select an option...", 
                    message_2="Select an admin option..."), 
                    message_id = interaction.message.id)
            else:
                await interaction.followup.edit_message(embed=embed, view=HelpSelectView(message="Select an option..."), message_id = interaction.message.id)

        def get_embed(self):
            if self.values[0] in list(roll_options.keys()):
                dict = roll_options
            elif self.values[0] in list(admin_options.keys()):
                dict = admin_options
            else:
                dict = basic_options
            embed = discord.Embed(
                title=dict[self.values[0]]['Name'],
                colour= 0x036ffc,
                timestamp=datetime.datetime.now(),
                description=dict[self.values[0]]['Content']
            )
            embed.set_thumbnail(url=ce_mountain_icon)
            return embed


    class HelpSelectView(discord.ui.View):
        def __init__(self, *, timeout = 180, menu="", message="Select an option", message_2="Select an option"):
            super().__init__(timeout=timeout)
            self.add_item(HelpSelect(selections, message, 1))
            if menu != "" :
                self.add_item(HelpSelect(menu, message_2, 2))

        """async def on_timeout(self):
            self.clear_items()"""

    return await interaction.followup.send(embed=embed, view=HelpSelectView(), ephemeral=True)

















# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------- SOLO ROLL COMMAND ------------------------------------------------------------ # 
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
events_solo = Literal["One Hell of a Day", "One Hell of a Week", "One Hell of a Month", "Two Week T2 Streak", 
          "Two 'Two Week T2 Streak' Streak", "Never Lucky", "Triple Threat", "Let Fate Decide", "Fourward Thinking",
          "Russian Roulette"]
@tree.command(name="solo-roll", description="Participate in Challenge Enthusiast roll events!", guild=discord.Object(id=guild_ID))
@app_commands.describe(event="The event you'd like to participate in")
async def roll_solo_command(interaction : discord.Interaction, event: events_solo) :   

    await interaction.response.defer()

    # run 1/100 chance of pinging jarvis
    log_channel = client.get_channel(log_id)


    await solo_command(interaction, event, reroll = False, collection=collection, log_channel=log_channel)
    




















# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------- CO-OP ROLL COMMAND ------------------------------------------------------------ # 
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
events_co_op = Literal["Destiny Alignment", "Soul Mates", "Teamwork Makes the Dream Work", 
                       "Winner Takes All", "Game Theory"]

@tree.command(name="co-op-roll", description="Participate in Challenge Enthusiast Co-Op or PvP roll events!", guild=discord.Object(id=guild_ID))
@app_commands.describe(event="The event you'd like to participate in")
@app_commands.describe(partner="The user you'd like to enter the roll with")
async def roll_co_op_command(interaction : discord.Interaction, event : events_co_op, partner : discord.User) :
    await interaction.response.defer()

    await co_op_command(interaction, event, partner, reroll = False, collection=collection)





events_total = Literal["One Hell of a Day", "One Hell of a Week", "One Hell of a Month", "Two Week T2 Streak", 
          "Two 'Two Week T2 Streak' Streak", "Never Lucky", "Triple Threat", "Let Fate Decide", "Fourward Thinking",
          "Russian Roulette", "Destiny Alignment", "Soul Mates", "Teamwork Makes the Dream Work", 
          "Winner Takes All", "Game Theory"]
"""List of all events."""



@tree.command(name="force-add", description="Force add a roll completion to any user.", guild=discord.Object(id=guild_ID))
async def force_add(interaction: discord.Interaction, user: discord.Member, roll_event : events_total):
    await interaction.response.defer()

    database_user = await get_mongo('user')

    ce_id = await get_ce_id(user.id)

    if ce_id == None : return await interaction.followup.send(f"<@{user.id}> is not registered in the CE Assistant database. Please have them use /register.")

    database_user[ce_id]['Completed Rolls'].append({"Event Name" : roll_event})

    dump = await dump_mongo('user', database_user)
    return await interaction.followup.send(f"{roll_event} has been added to <@{user.id}>'s Completed Rolls array.")
    











"""
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------- CHECK_ROLLS COMMAND ----------------------------------------------------- # 
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
@tree.command(name="check-rolls", description="Check the active rolls of anyone on the server", guild=discord.Object(id=guild_ID))
@app_commands.describe(user="The user you'd like to check the rolls of")
async def checkRolls(interaction : discord.Interaction, user: discord.Member=None) :
    # defer the message
    print('balls')
    await interaction.response.defer()
    overflow = False

    # this is me trying to fix it but i will deal with this later

    if user is None : user = interaction.user

    # get mongo data
    database_user = await get_mongo('user')
    database_name = await get_mongo('name')

    ce_id = ""
    for u in database_user:
        if u == "_id" : continue
        elif database_user[u]['Discord ID'] == user.id:
            ce_id = u
            break
    
    if ce_id == "" : return await interaction.followup.send("This user is not registered in the CE Assistant database. Please make sure they use /register!")



    return await interaction.followup.send("Feature under construction!! Coming soon.")


    # if no user is provided default to sender
    selfy = False
    if user is None :
        selfy = True
        user = interaction.user

    # get mongo data
    userInfo = await get_mongo('user')
    database_name_info = await get_mongo('name')


    # iterate through the json file until you find the
    # designated user
    steam_user_name = await get_ce_id(user.id)
    
    if(steam_user_name == None) : 
        if selfy: return await interaction.followup.send("You are not registered in the CE Assistant database. Please use `/register`!")
        else: return await interaction.followup.send("This user is not registered in the CE Assistant database. Please make sure they use `/register`!")
    #print(steam_user_name) 

    current_roll_str = get_roll_string(userInfo, steam_user_name, database_name_info, user, 'Current Rolls')
    completed_roll_str = get_roll_string(userInfo, steam_user_name, database_name_info, user, 'Completed Rolls')

    if len(current_roll_str) > 1020 : 
        current_roll_str = current_roll_str[:1020]
        overflow = True
    if len(completed_roll_str) > 1020 : 
        completed_roll_str = completed_roll_str[:1020]
        overflow = True
    
    # make the embed that you're going to send
    embed = discord.Embed(colour=0x000000, timestamp=datetime.datetime.now())
    embed.add_field(name="User", value = "<@" + str(user.id) + "> " + str(icons[userInfo[steam_user_name]['Rank']]), inline=True)
    embed.add_field(name="Current Rolls", value=current_roll_str, inline=False)
    embed.add_field(name="Completed Rolls", value=completed_roll_str, inline=False)
    if overflow:
        embed.add_field(name="Overflow Error!", value="If this doesn't look right, please DM me <@413427677522034727>. This will be fixed in v1.1.", inline=False)
    embed.set_thumbnail(url=user.avatar.url)
    embed.set_footer(text="CE Assistant",
        icon_url=final_ce_icon)

    # send the embed
    await interaction.followup.send(embed=embed)

    del current_roll_str
    del completed_roll_str
    del embed
    del database_name_info
    del user
    """

def checkRollsEmbed(user : discord.Member, database_name, database_user, ce_id : str) -> discord.Embed :
    """Returns the embed for the /check-rolls command."""
    # iterate through the json file until you find the
    # designated user
    overflow = False
    steam_user_name = ce_id

    current_roll_str = get_roll_string(database_user, steam_user_name, database_name, user, 'Current Rolls')
    completed_roll_str = get_roll_string(database_user, steam_user_name, database_name, user, 'Completed Rolls')

    if len(current_roll_str) > 1020 : 
        current_roll_str = current_roll_str[:1020]
        overflow = True
    if len(completed_roll_str) > 1020 : 
        completed_roll_str = completed_roll_str[:1020]
        overflow = True
    
    # make the embed that you're going to send
    embed = discord.Embed(colour=0xff9494, timestamp=datetime.datetime.now())
    embed.add_field(name="User", value = "<@" + str(user.id) + "> " + str(icons[database_user[steam_user_name]['Rank']]), inline=True)
    embed.add_field(name="Current Rolls", value=current_roll_str, inline=False)
    embed.add_field(name="Completed Rolls", value=completed_roll_str, inline=False)
    if overflow:
        embed.add_field(name="Overflow Error!", value="If this doesn't look right, please DM me <@413427677522034727>. This will be fixed in v1.1.", inline=False)
    embed.set_thumbnail(url=user.avatar.url)
    embed.set_footer(text="CE Assistant",
        icon_url=final_ce_icon)

    return embed














# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------------- THREADING ------------------------------------------------------------ #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper






"""
@tasks.loop(time=datetime.time(hour=0, minute=20, tzinfo=datetime.timezone.utc))
async def check_roll_status():
    print('it ran omg it actually ran')
    log_channel = client.get_channel(log_id) 
    log_channel.send("check_roll_status has begun!!")
    # get databases
    database_user = await get_mongo('user')
    database_name = await get_mongo('name')

    # create a variable that holds all the messages that need to be sent
    all_returns = []

    # go through each user in database user. if they have any cooldowns or current rolls.... update their profiles.
    for user in database_user:
        if user == "_id" : continue
        # if their current rolls are empty and their cooldowns are empty keep checking
        if(database_user[user]['Current Rolls'] == [] and database_user[user]['Cooldowns'] == {}) : continue
        else:
            # update their profile.
            returns = update_p(database_user[user]['Discord ID'], "", database_user, database_name)
            
            # update database_user.
            database_user = returns[0]
            returns[0] = "NEW USER: " + str(database_user[user]['Discord ID'])
            
            # add all returned values to the array except database_user. that has been dealt with.
            for i in range(0, len(returns)):
                all_returns.append(returns[i])
            
            # make the returns array empty.
            returns = []
    
    # update the databases
    dump = await dump_mongo("user", database_user)


    # initialize the variables ##################################################################################################################
                                                                                          #
    casino_channel = client.get_channel(casino_id)                                                                                     #
                                                                                                                                                #
    # rank silliness                                                                                                                            #
    ranks = ["E Rank", "D Rank", "C Rank", "B Rank", "A Rank", "S Rank", "SS Rank", "SSS Rank", "EX Rank"]                                      #
    rankroles = []                                                                                                                              #
    ex_rank_role = discord.utils.get(correct_guild_2.roles, name = "EX Rank")                                                                 #
    sss_rank_role = discord.utils.get(correct_guild_2.roles, name = "SSS Rank")                                                               #
    ss_rank_role = discord.utils.get(correct_guild_2.roles, name = "SS Rank")                                                                 #
    s_rank_role = discord.utils.get(correct_guild_2.roles, name = "S Rank")                                                                   #
    a_rank_role = discord.utils.get(correct_guild_2.roles, name = "A Rank")                                                                   #
    b_rank_role = discord.utils.get(correct_guild_2.roles, name = "B Rank")                                                                   #
    c_rank_role = discord.utils.get(correct_guild_2.roles, name = "C Rank")                                                                   #
    d_rank_role = discord.utils.get(correct_guild_2.roles, name = "D Rank")                                                                   #
    e_rank_role = discord.utils.get(correct_guild_2.roles, name = "E Rank")                                                                   #
    rankroles = [a_rank_role, ex_rank_role, sss_rank_role, ss_rank_role, s_rank_role, b_rank_role, c_rank_role, d_rank_role, e_rank_role]       #
    
    correct_guild = discord.Object(id=guild_ID)
    correct_guild_2 = client.get_guild(id=guild_ID)
    discord.Guild.roles
    #############################################################################################################################################
       

    for return_value in all_returns :
        current_user = ""
        if return_value[:9:] == "NEW USER: ": 
            current_user_id = int(return_value[10::])
            current_user = correct_guild_2.get_member(current_user_id)


        # you've reached the end
        # if return_value == "Updated" :
        #     # Create confirmation embed
        #     embed = discord.Embed(
        #         title="Updated!",
        #         color=0x000000,
        #         timestamp=datetime.datetime.now()
        #     )
        #     embed.add_field(name="Information", value=f"Your information has been updated in the CE Assistant database.")
        #     embed.set_author(name="Challenge Enthusiasts", url="https://example.com")
        #     embed.set_footer(text="CE Assistant",
        #         icon_url=final_ce_icon)
        #     embed.set_thumbnail(url=interaction.user.avatar)


        # change the rank
        # TODO: maybe get folkius to give theron points to test this out? 
        # TODO: given that i have no way of knowing if it works rn
        elif return_value[:5:] == "rank:" :
            for rankrole in rankroles :
                if rankrole in current_user.roles :
                    role = rankrole
                    break
            if role.name == return_value[6::] : continue
            else :
                for rankrole in rankroles :
                    if rankrole in current_user.roles : await current_user.remove_roles(rankrole)
                    if rankrole.name == return_value[6::] : await current_user.add_roles(rankrole)
        
        # log channel shit
        elif return_value[:4:] == "log:" :
            await log_channel.send(return_value[5::])

        # casino channel shit
        elif return_value[:7:] == "casino:":
            await casino_channel.send(return_value[8::])

        # else
        else :
            await log_channel.send("BOT ERROR: recieved unrecognized update code: \n'{}'".format(return_value))

    await log_channel.send("holy fucking shit the once-a-day actually ran???")

    # delete all variables (mmmmm...... my precious ram.... mmmmmmffgggggggg......)
    del dump
    del database_user
    del database_name
    del all_returns
    del returns
"""
        





@tree.command(name='purge-roll', description="Remove a roll from a specific user (in the event of catastrophe)", 
              guild=discord.Object(id=guild_ID))
async def purge_roll(interaction : discord.Interaction, user : discord.User, roll_event : events_solo):
    await interaction.response.defer()
    
    # pull the database
    database_user = await get_mongo('user')
    
    # find the user
    ce_id = await get_ce_id(user.id)
    if ce_id == None:
        return await interaction.followup.send("<@{}> is not registered in the CE Assistant database.".format(user.id))
    
    # find the roll
    r_index = -1
    for i, r in enumerate(database_user[ce_id]['Current Rolls']):
        if r['Event Name'] == roll_event : r_index = i
    if r_index == -1:
        return await interaction.followup.send("<@{}> does not have {} in their Current Rolls array.".format(user.id, roll_event))


    
    # user does exist and has the roll in their array
    del database_user[ce_id]['Current Rolls'][r_index]
    if roll_event in database_user[ce_id]['Pending Rolls'] : del database_user[ce_id]['Pending Rolls'][roll_event]
    if roll_event in database_user[ce_id]['Cooldowns'] : del database_user[ce_id]['Pending Rolls'][roll_event]

    # dump the database
    await dump_mongo('user', database_user)

    # send message (dumbass!)
    return await interaction.followup.send(f"{roll_event} was dropped from <@{user.id}>'s Current Rolls array.")


# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------- SCRAPING --------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
@to_thread
def scrape_thread_call(curator_count):
    return single_scrape_v2(curator_count)


@tree.command(name="scrape", description="Force update every game without creating embeds. DO NOT RUN UNLESS NECESSARY.", guild=discord.Object(id=guild_ID))
async def scrape(interaction : discord.Interaction):
    await interaction.response.send_message('scraping... (v2)')

    curator_count = await get_mongo('curator')

    objects = await scrape_thread_call(curator_count)

    # add the id back to database_name
    objects[0]['_id'] = mongo_ids['name']
    objects[2]['_id'] = mongo_ids["tier"]
    
    # dump the databases back onto mongoDB
    dump1 = await dump_mongo('curator', objects[1]) #curator
    dump2 = await dump_mongo('name', objects[0]) #name
    dump3 = await dump_mongo('tier', objects[2]) #tier

    await interaction.channel.send('scraped')

    del dump3
    del dump1
    del dump2
    del curator_count
    del objects





















# godspeed, get_times :pray:
"""

@tree.command(name="get_times", description="Prints out a table of times fifteen minutes apart in UTC", guild=discord.Object(id=guild_ID))
async def get_times(interaction):
    await interaction.response.send_message('times...')
    fin = "times = ['
    for i in range(0, 24):
        for j in range(0, 4):
            fin += "\n  datetime.time(hour={}, minute={}, tzinfo=utc),".format(i,j*15)

    fin = fin[:-1:] + "\n]"

    print(fin)



"""

class NewModal(discord.ui.Modal):
    def __init__(self) :
        super().__init__(title="My first Modal!")

    name = discord.ui.TextInput(label="Peepo")
    answer = discord.ui.TextInput(label="Response", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction : discord.Interaction) :
        await interaction.response.send_message(f'Thank you for your response, {self.name}!', ephemeral=False)

class RequestCEGame(discord.ui.Modal):
    def __init__(self) :
        super().__init__(title="Request CE Game...")
    game_name = discord.ui.TextInput(label="Game Name", required=False, placeholder="Select a game name")
    tier = discord.ui.TextInput(label="Tier", style=discord.TextStyle.short, min_length=1, max_length=1, required=False, placeholder="Select a tier number.")
    max_points = discord.ui.TextInput(label="Min-Max Points", style=discord.TextStyle.short, required=False, placeholder="Please format as such: min-max, or 20-100", max_length=9)
    genre = discord.ui.TextInput(label="Genre", style=discord.TextStyle.short, required=False, placeholder="Select a genre.", max_length=12)
    owned = discord.ui.TextInput(label="Owned", style=discord.TextStyle.short, required=False, placeholder="Separate games by owned (\"true\") or not owned (\"false\").", max_length=5)

    async def on_submit(self, interaction : discord.Interaction) :
        # d efer
        await interaction.response.defer()

        # grab all submitted queries
        game_name = str(self.game_name)
        tier = str(self.tier)
        points = str(self.max_points)
        genre = str(self.genre)
        owned = str(self.owned)

        # format them correctly
        if tier != "": 
            try:
                tier = int(tier)
                if tier > 7 : tier = "invalid"
                elif tier < 1 : tier = "invalid"
            except ValueError:
                tier = "invalid"

        if points != "":
            splitter = points.find('-')
            if splitter == -1 : points = "invalid"
            try:
                min_points = points[0:splitter]
                max_points = points[splitter+1:]
                min_points = int(min_points)
                max_points = int(max_points)
                if max_points < min_points : points = "invalid"
            except ValueError:
                points = "invalid"
        
        if genre != "":
            genre = genre.replace('-','').replace(' ','')
            g_changed = False
            for g in all_genres:
                g_save = g
                g = g.replace('-','').replace(' ','')
                if g.lower() == genre.lower() : 
                    genre = g_save
                    g_changed = True
                    break
            if not g_changed : genre = "invalid"

        if owned == "False" or owned == "false" or owned == "f" : owned = False
        elif owned == "True" or owned == "true" or owned == "t" : owned = True
        elif owned != "" : owned = "invalid"

        # -------- all variables formatted. start grabbing -----------
        if True:
            description_str = ""
            description_str += f"✅Game recieved: {game_name}.\n" if game_name != "" else "" #"🛑No game name recieved.\n"
            if tier == "invalid" : 
                description_str += "⚠️Invalid tier recieved.\n"
                tier = None
            elif tier == "": 
                #description_str += "🛑No tier recieved.\n"
                tier = None
            else: description_str += f"✅Tier recieved: {icons['Tier {}'.format(tier)]}.\n"
            if points == "" : 
                #description_str += "🛑No min-max points recieved.\n"
                points = None
            elif points == "invalid" : 
                description_str += "⚠️Invalid min-max syntax."
                points = None
            else : description_str += f"✅Min points recieved: {min_points} {icons['Points']}\n✅Max points recieved: {max_points} {icons['Points']}.\n"
            if genre == "": 
                #description_str += "🛑No genre recieved.\n"
                genre = None
            elif genre == "invalid": 
                description_str += "⚠️Invalid genre recieved.\n"
                genre = None
            else: description_str += f"✅Genre recieved: {genre}{icons[genre]}.\n"
            if owned == "" : 
                #description_str += "🛑No ownership query recieved.\n"
                owned = None
            elif owned == "invalid" : 
                description_str += "⚠️Invalid ownership (not \"true\" or \"false\").\n"
                owned = None
            else: description_str += f"✅Ownership recieved: {owned}"

        database_name = await get_mongo('name')
        del database_name['_id']
        database_user = await get_mongo('user')
        if '_id' in database_user: del database_user['_id']
        game_list : list[str] = []

        ce_id = get_ce_id_normal(interaction.user.id, database_user)
        if ce_id == None and type(owned) == bool:
            return await interaction.followup.send("You selected \"true\" or \"false\" for Owned, but you are not registered. Please use `/register` with the link to your CE page!")
        elif game_name == "" and tier == None and points == None and genre == None and owned == None:
            return await interaction.followup.send("You either left all the options blank or inputted only invalid answers. Please try again!")
        

        for game_id in database_name:
            valid = True
            if game_name != "" and not database_name[game_id]['Name'].lower()[0:len(game_name)] == game_name.lower() : valid = False
            if tier != None :
                if tier == 6 or tier == 7:
                    total_points = 0
                    for obj_id in database_name[game_id]['Primary Objectives'] : total_points += database_name[game_id]['Primary Objectives'][obj_id]['Point Value']
                    if tier == 6 and (total_points < 500 or total_points >= 1000) : valid = False
                    elif tier == 7 and total_points < 1000 : valid = False 
                if not database_name[game_id]['Tier'] == f"Tier {tier}" and tier != 6 and tier != 7 : valid = False
            if points != None:
                total_points = 0
                for obj_id in database_name[game_id]['Primary Objectives'] : total_points += database_name[game_id]['Primary Objectives'][obj_id]['Point Value']
                if total_points < min_points or total_points > max_points : valid = False
            if genre != None and not database_name[game_id]['Genre'] == genre : valid = False
            if owned != None and not game_id in database_user[ce_id]['Owned Games'] : valid = False
            if valid : game_list.append(game_id)
        
        del database_user
        
        list_strings : list[str] = []
        for i in range(0, 25) :
            list_strings.append("")
        index = -1
        for i, item in enumerate(game_list):
            if(i % 10 == 0) : index += 1
            if index > 24 : return await interaction.followup.send("Too many games! Please lower your search queries.")
            list_strings[index] += f"[{database_name[item]['Name']}](https://cedb.me/game/{item})\n"

        if len(game_list) == 0: return await interaction.followup.send("No games on CE fit the queries provided.")

        embeds : list[discord.Embed] = []
        for i in range(0, index+1) :
            embed = discord.Embed(title="Requested games...", description=list_strings[i], timestamp=datetime.datetime.now(), color=0x000000)
            embed.add_field(name="Parameters", value=description_str)
            embed.set_author(name="Challenge Enthusiasts", url=f"https://cedb.me/user/{ce_id}", icon_url=final_ce_icon)
            embed.set_footer(text=f"Page {i+1} of {index+1}")
            embeds.append(embed)

        del database_name

        view = discord.ui.View(timeout=600)
        await get_buttons(view, embeds)

        try:
            await interaction.followup.send(embed=embeds[0], view=view)
        except:
            await interaction.followup.send('Too many games!')


@tree.command(name='test-moda', description='fhsdjaiklu', guild=discord.Object(id=guild_ID))
async def testagain(interaction : discord.Interaction) :
    await interaction.response.send_modal(RequestCEGame())













# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------- CURATE ---------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
@tree.command(name="curate", description="Sends as many of the latest curator messages as requested or the latest if none specified.", guild=discord.Object(id=guild_ID))
@app_commands.describe(num="Number of previous curator entries to pull")
async def curate(interaction : discord.Interaction, num : int = 0):
    await interaction.response.defer()
    await single_run(client, num, collection)

    if num > 0:
        await interaction.followup.send('Those are the last {} curator reviews!'.format(num))
    else:
        await interaction.followup.send('There are no new curator reviews.')



















# ----------------------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------- STEAM TEST COMMAND ------------------------------------------------------ #
# ----------------------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------------------------------------------------------------------------------------- #
@tree.command(name="steam-game", description="Get information on any steam game", guild=discord.Object(id=guild_ID))
@app_commands.describe(game_name="The name of the game you're trying to look up.")
@app_commands.describe(visible="Whether you want the message to be viewable to others (true) or only viewable to yourself (false)")
async def steam_command(interaction : discord.Interaction, game_name: str, visible : bool = False):

    # Log the command
    print("Recieved steam_game command with parameter: " + game_name + ".")
    # Defer the interaction
    await interaction.response.defer(ephemeral=(not visible))
    # open database
    database_name = await get_mongo('name')



    # Get the embed
    embed = getEmbed(game_name, interaction.user.id, database_name=database_name)
    embed.set_author(name="Requested Steam info on '" + game_name + "'")
    

    # Finally, send the embed
    await interaction.followup.send(embed=embed)

    # And log it
    print("Sent information on requested game " + game_name + ": " + embed.title +"\n")

    del database_name
    del embed

















# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------- COLORS ----------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
@tree.command(name="set-color", description="Set your name color to any color you've unlocked!", guild=discord.Object(id=guild_ID))
async def color(interaction) :
    await interaction.response.defer(ephemeral=True)

    ex_rank_role = discord.utils.get(interaction.guild.roles, name = "EX Rank")
    sss_rank_role = discord.utils.get(interaction.guild.roles, name = "SSS Rank")
    ss_rank_role = discord.utils.get(interaction.guild.roles, name = "SS Rank")
    s_rank_role = discord.utils.get(interaction.guild.roles, name = "S Rank")
    a_rank_role = discord.utils.get(interaction.guild.roles, name = "A Rank")
    b_rank_role = discord.utils.get(interaction.guild.roles, name = "B Rank")
    c_rank_role = discord.utils.get(interaction.guild.roles, name = "C Rank")
    d_rank_role = discord.utils.get(interaction.guild.roles, name = "D Rank")

    black_role = discord.utils.get(interaction.guild.roles, name = "Black")
    red_role = discord.utils.get(interaction.guild.roles, name = "Red")
    yellow_role = discord.utils.get(interaction.guild.roles, name = "Yellow")
    orange_role = discord.utils.get(interaction.guild.roles, name = "Orange")
    purple_role = discord.utils.get(interaction.guild.roles, name = "Purple")
    blue_role = discord.utils.get(interaction.guild.roles, name = "Blue")
    green_role = discord.utils.get(interaction.guild.roles, name = "Green")
    brown_role = discord.utils.get(interaction.guild.roles, name = "Brown")  
    grey_role = discord.utils.get(interaction.guild.roles, name = "Gray")


    view = discord.ui.View(timeout=60)

    black_button = (discord.ui.Button(label="⚫", disabled=(not ex_rank_role in interaction.user.roles)))
    red_button = discord.ui.Button(label = "🔴", disabled = (not sss_rank_role in interaction.user.roles
                                                             and not ex_rank_role in interaction.user.roles))
    yellow_button = (discord.ui.Button(label="🟡", disabled=(not ss_rank_role in interaction.user.roles
                                                            and not sss_rank_role in interaction.user.roles
                                                            and not ex_rank_role in interaction.user.roles)))  
    orange_button = (discord.ui.Button(label="🟠", disabled=(not s_rank_role in interaction.user.roles
                                                            and not ss_rank_role in interaction.user.roles
                                                            and not sss_rank_role in interaction.user.roles
                                                            and not ex_rank_role in interaction.user.roles)))
    purple_button = (discord.ui.Button(label="🟣", disabled=(not a_rank_role in interaction.user.roles
                                                            and not s_rank_role in interaction.user.roles
                                                            and not ss_rank_role in interaction.user.roles
                                                            and not sss_rank_role in interaction.user.roles
                                                            and not ex_rank_role in interaction.user.roles)))
    blue_button = (discord.ui.Button(label="🔵", disabled=(not b_rank_role in interaction.user.roles
                                                            and not a_rank_role in interaction.user.roles
                                                            and not s_rank_role in interaction.user.roles
                                                            and not ss_rank_role in interaction.user.roles
                                                            and not sss_rank_role in interaction.user.roles
                                                            and not ex_rank_role in interaction.user.roles)))
    green_button = (discord.ui.Button(label="🟢", disabled=(not c_rank_role in interaction.user.roles
                                                            and not b_rank_role in interaction.user.roles
                                                            and not a_rank_role in interaction.user.roles
                                                            and not s_rank_role in interaction.user.roles
                                                            and not ss_rank_role in interaction.user.roles
                                                            and not sss_rank_role in interaction.user.roles
                                                            and not ex_rank_role in interaction.user.roles)))
    brown_button = (discord.ui.Button(label="🟤", disabled=(not d_rank_role in interaction.user.roles
                                                            and not c_rank_role in interaction.user.roles
                                                            and not b_rank_role in interaction.user.roles
                                                            and not a_rank_role in interaction.user.roles
                                                            and not s_rank_role in interaction.user.roles
                                                            and not ss_rank_role in interaction.user.roles
                                                            and not sss_rank_role in interaction.user.roles
                                                            and not ex_rank_role in interaction.user.roles)))
    grey_button = discord.ui.Button(label="⚪")
    clear_button = discord.ui.Button(label="Clear")
    roles = [grey_role, brown_role, green_role, blue_role, purple_role, orange_role, yellow_role, red_role, black_role]
    
    async def black_callback(interaction) : return await assign_role(interaction, black_role)
    async def red_callback(interaction) : return await assign_role(interaction, red_role)
    async def yellow_callback(interaction) : return await assign_role(interaction, yellow_role)
    async def orange_callback(interaction) : return await assign_role(interaction, orange_role)
    async def purple_callback(interaction) : return await assign_role(interaction, purple_role)
    async def blue_callback(interaction) : return await assign_role(interaction, blue_role)
    async def green_callback(interaction) : return await assign_role(interaction, green_role)
    async def brown_callback(interaction) : return await assign_role(interaction, brown_role)
    async def grey_callback(interaction) : return await assign_role(interaction, grey_role)
    async def clear_callback(interaction : discord.Interaction) :
        for role in roles :
            if role in interaction.user.roles : await interaction.user.remove_roles(role)
        return await interaction.response.edit_message(embed=discord.Embed(title="Colors cleared."))


    black_button.callback = black_callback
    red_button.callback = red_callback
    yellow_button.callback = yellow_callback
    orange_button.callback = orange_callback
    purple_button.callback = purple_callback
    blue_button.callback = blue_callback
    green_button.callback = green_callback
    brown_button.callback = brown_callback
    grey_button.callback = grey_callback
    clear_button.callback = clear_callback

    view.add_item(black_button)
    view.add_item(red_button)
    view.add_item(yellow_button)
    view.add_item(orange_button)
    view.add_item(purple_button)
    view.add_item(blue_button)
    view.add_item(green_button)
    view.add_item(brown_button)
    view.add_item(grey_button)
    view.add_item(clear_button)

    async def assign_role(interaction, role) :
        if(role in interaction.user.roles) : return await interaction.response.edit_message(embed=discord.Embed(title = f"You already have the {role.name} role!", color = role.color))
        
        await (interaction.user.add_roles(role))

        if(black_role in interaction.user.roles and not(role == black_role)) : await interaction.user.remove_roles(black_role)
        if(red_role in interaction.user.roles and not(role == red_role)) : await interaction.user.remove_roles(red_role)
        if(yellow_role in interaction.user.roles and not(role == yellow_role)) : await interaction.user.remove_roles(yellow_role)
        if(orange_role in interaction.user.roles and not(role == orange_role)) : await interaction.user.remove_roles(orange_role)
        if(purple_role in interaction.user.roles and not(role == purple_role)) : await interaction.user.remove_roles(purple_role)
        if(blue_role in interaction.user.roles and not(role == blue_role)) : await interaction.user.remove_roles(blue_role)
        if(green_role in interaction.user.roles and not(role == green_role)) : await interaction.user.remove_roles(green_role)
        if(brown_role in interaction.user.roles and not(role == brown_role)) : await interaction.user.remove_roles(brown_role)
        if(grey_role in interaction.user.roles and not(role == grey_role)) : await interaction.user.remove_roles(grey_role)

        return await interaction.response.edit_message(embed=discord.Embed(title = f"You have recieved the {role.name} role!", color=role.color))
        
    embed = discord.Embed(title="COLORS", description="choose your colors wisely.")
    await interaction.followup.send(embed=embed, view=view, ephemeral=True)
















# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------TEST COMMAND-------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
@tree.command(name="initiate-loop", description="Initiate the curating and scraping loop. ONLY DO THIS IF NECESSARY.", guild=discord.Object(id=guild_ID))
async def initiate_master_loop(interaction : discord.Interaction) :
    await interaction.response.defer(ephemeral=True)

    await interaction.followup.send('looping....')

    await master_loop(client)

    

    

    #casino_channel = client.get_channel(811286469251039333)
    
    #await roll_failed(ended_roll_name='Triple Threat', casino_channel=casino_channel, user_name='d7cb0869-5ed9-465c-87bf-0fb95aaebbd5')


    #return await interaction.followup.send(embed=discord.Embed(title="this is the test command"))
    #print(role.id)
    
    # embed = discord.Embed(title="__Celeste__ has been updadted on the site", 
    #description="' ∀MAZING' increased from 120 :CE_points: ➡ 125 :CE_points: points: 
    #   Achievements '∀NOTHER ONE', and '∀DVENTED' removed New Primary Objective '∀WOKEN' added: 30 points :CE_points:
    #    Clear the Pandemonic Nightmare stage, and clear Hymeno Striker on AKASCHIC+RM difficulty.")
    # embed.set_thumbnail(url=ce_hex_icon)
    # embed.set_image(url="https://media.discordapp.net/attachments/1128742486416834570/1133903990090895440/image.png?width=1083&height=542")
    # embed.set_author(name="Challenge Enthusiasts", icon_url="https://cdn.akamai.steamstatic.com/steamcommunity/public/images/apps/504230/04cb7aa0b497a3962e6b1655b7fd81a2cc95d18b.jpg")

    # return await interaction.followup.send(embed=embed)





# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------- REGISTRATION COMMAND----------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
@tree.command(name="register", description="Register yourself in the CE Assistant database to unlock rolls.", guild=discord.Object(id=guild_ID))
@app_commands.describe(ce_id="Please use the link to your personal CE user page!")
async def register(interaction : discord.Interaction, ce_id: str) :
    await interaction.response.defer(ephemeral=True) # defer the message
    """
    if interaction.user.id == 476213685073739798 : return await interaction.followup.send("kingconn banned lol")
    if interaction.user.id == 73648432367013888  : return await interaction.followup.send(
        "hey laura when you fix /api/games/full/ i'll give you access")
    """
    #Open the user database
    database_user = await get_mongo('user')
    database_name = await get_mongo('name')

    # Set up total_points to calculate rank
    total_points = 0

    # Make sure the input is a valid CE-ID
    print(f"Input = {ce_id}")
    if(ce_id[:20:] == "https://cedb.me/user" and len(ce_id) >= 29 and (ce_id[29] == '-')) :
        if(ce_id[(len(ce_id)-5)::] == "games") : ce_id = ce_id[21:(len(ce_id)-6):]
        else : ce_id = ce_id[21::]
    elif ce_id[:22:] == "https://ce.iys.io/user" and len(ce_id) >= 31 and (ce_id[31] == '-'):
        if(ce_id[(len(ce_id)-5)::] == "games") : ce_id = ce_id[23:(len(ce_id)-6)]
        else : ce_id = ce_id[23::]
    else: return await interaction.followup.send(
        f"'{ce_id}' is not a valid user link. Please try again or contact <@413427677522034727> for assistance.")
    print(f"Working ID = {ce_id}")

    # Make sure user isn't already registered
    for user in database_user :
        if user == '_id' : continue
        if(database_user[user]['Discord ID'] == interaction.user.id) : return await interaction.followup.send(
            "You are already registered in the database!")
        elif(database_user[user]['CE ID'] == ce_id) : return await interaction.followup.send(
            f"This CE-ID is already registered to <@{database_user[user]['Discord ID']}>, silly!")
    
    
    # Grab user info from CE API
    user_ce_data = get_api("user", ce_id)

    # Set up the user's JSON file
    user_dict = {
        ce_id : {
            "CE ID" : ce_id,
            "Discord ID" : interaction.user.id,
            "Rank" : "",
            "Reroll Tickets" : 0,
            "Casino Score" : 0,
            "Owned Games" : {},
            "Cooldowns" : {},
            "Current Rolls" : [],
            "Completed Rolls" : [],
            "Pending Rolls" : {}
        }
    }

    # Go through owned games in CE JSON
    for game in user_ce_data['userGames'] :
        game_id = game['gameId']
        
        # Add the games to the local JSON
        user_dict[ce_id]['Owned Games'][game_id] = {}

    # Go through all objectives 
    for objective in user_ce_data['userObjectives'] :
        game_id = objective['objective']['gameId']
        obj_id = objective['objectiveId']
        
        # If the objective is community, set the value to true
        if objective['objective']['community'] : 
            if "Community Objectives" not in user_dict[ce_id]['Owned Games'][game_id]:
                user_dict[ce_id]['Owned Games'][game_id]['Community Objectives'] = {}
            user_dict[ce_id]['Owned Games'][game_id]['Community Objectives'][obj_id] = True

        # If the objective is primary...
        else : 
            # ... and there are partial points AND no one has assigned requirements...
            if(objective['partial']) :
                # ... set the points earned to the partial points value.
                points = objective['objective']['pointsPartial']
            # ... and there are no partial points, set the points earned to the total points value.
            else : points = objective['objective']['points']

            # Add the points to user's total points
            total_points += points

            # Now actually update the value in the user's dictionary.
            if(list(user_dict[ce_id]['Owned Games'][game_id].keys()).count("Primary Objectives") == 0) :
                user_dict[ce_id]['Owned Games'][game_id]['Primary Objectives'] = {}
            user_dict[ce_id]['Owned Games'][game_id]['Primary Objectives'][obj_id] = points


    # Get the user's rank
    rank = ""
    if total_points < 50 : rank = "E Rank"
    elif total_points < 250 : rank = "D Rank"
    elif total_points < 500 : rank = "C Rank"
    elif total_points < 1000 : rank = "B Rank"
    elif total_points < 2500 : rank = "A Rank"
    elif total_points < 5000 : rank = "S Rank"
    elif total_points < 7500 : rank = "SS Rank"
    elif total_points < 10000 : rank = "SSS Rank"
    else : rank = "EX Rank"

    user_dict[ce_id]['Rank'] = rank

    all_events = ["One Hell of a Day", "One Hell of a Week", "One Hell of a Month", "Two Week T2 Streak", 
                  "Two \"Two Week T2 Streak\" Streak", "Never Lucky", "Triple Threat", "Let Fate Decide", 
                  "Fourward Thinking", "Russian Roulette", "Destiny Alignment",
                  "Soul Mates", "Teamwork Makes the Dream Work", "Winner Takes All", "Game Theory"]
    all_events_final = {}
    for e in all_events:
        for o in database_name[ce_squared_id]['Community Objectives'] :
            if e == database_name[ce_squared_id]['Community Objectives'][o]['Name'] : 
                all_events_final[e] = o

    # Check and see if the user has any completed rolls
    if ce_squared_id in user_dict[ce_id]['Owned Games']:
        x=0
        
        for event in all_events_final :
            event_id = all_events_final[event]
            if event_id in user_dict[ce_id]['Owned Games'][ce_squared_id]['Community Objectives']:
                x=0
                user_dict[ce_id]['Completed Rolls'].append({"Event Name" : event})
            if(event == "Two \"Two Week T2 Streak\" Streak" 
               and "Two \"Two Week T2 Streak\" Streak" in 
               user_dict[ce_id]['Owned Games'][ce_squared_id]['Community Objectives']):
                    user_dict[ce_id]['Completed Rolls'].append({"Event Name" : "Two 'Two Week T2 Streak' Streak"})

    # Add the user file to the database
    database_user.update(user_dict)

    # Dump the data
    dump = await dump_mongo("user", database_user)
    del dump

    # Create confirmation embed
    embed = discord.Embed(
        title="Registered!",
        color=0x000000,
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="Information", value=f"You have been registered in the CE Assistant database. Your CE-ID is {ce_id}"
                    + f". You may now use all aspects of this bot.")
    embed.set_author(name="Challenge Enthusiasts", url="https://example.com")
    embed.set_footer(text="CE Assistant",
        icon_url=final_ce_icon)
    embed.set_thumbnail(url=interaction.user.avatar)

    registered_role = discord.utils.get(interaction.guild.roles, name = "CEA Registered")
    await interaction.user.add_roles(registered_role)

    # Send a confirmation message
    await interaction.followup.send(embed=embed)














@tree.command(name="update", description="Update your stats in the CE Assistant database.", guild=discord.Object(id=guild_ID))
async def update(interaction : discord.Interaction) :
    # Defer the message
    await interaction.response.defer(ephemeral=True)

    database_name = await get_mongo('name')
    database_user = await get_mongo('user')

    log_channel = client.get_channel(log_id)
    casino_channel = client.get_channel(casino_id)
    
    # rank silliness
    ranks = ["E Rank", "D Rank", "C Rank", "B Rank", "A Rank", "S Rank", "SS Rank", "SSS Rank", "EX Rank"]
    rankroles = []
    ex_rank_role = discord.utils.get(interaction.guild.roles, name = "EX Rank")
    sss_rank_role = discord.utils.get(interaction.guild.roles, name = "SSS Rank")
    ss_rank_role = discord.utils.get(interaction.guild.roles, name = "SS Rank")
    s_rank_role = discord.utils.get(interaction.guild.roles, name = "S Rank")
    a_rank_role = discord.utils.get(interaction.guild.roles, name = "A Rank")
    b_rank_role = discord.utils.get(interaction.guild.roles, name = "B Rank")
    c_rank_role = discord.utils.get(interaction.guild.roles, name = "C Rank")
    d_rank_role = discord.utils.get(interaction.guild.roles, name = "D Rank")
    e_rank_role = discord.utils.get(interaction.guild.roles, name = "E Rank")
    rankroles = [a_rank_role, ex_rank_role, sss_rank_role, ss_rank_role, s_rank_role, b_rank_role, c_rank_role, d_rank_role, e_rank_role]

    # actually update the user's database 
    # and store anything we need to report
    try:
        returns = update_p(interaction.user.id, False, database_user, database_name)
    except Exception as e:
        print(e)
        return await interaction.followup.send("something went wrong. please ping andy!!\n" + str(e))
    if returns == "failed" : return await interaction.followup.send("Something went wrong with the API. Please try again in five minutes.")
    if returns == "Unregistered" : return await interaction.followup.send("You have not registered. Please use /register with the link to your CE page.")

    dump = await dump_mongo('user', returns[0])
    del returns[0]
    del dump

    for return_value in returns :
        # you've reached the end
        if return_value == "Updated" :
            # Create confirmation embed
            embed = discord.Embed(
                title="Updated!",
                color=0x000000,
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="Information", value=f"Your information has been updated in the CE Assistant database.")
            embed.set_author(name="Challenge Enthusiasts", url="https://example.com")
            embed.set_footer(text="CE Assistant",
                icon_url=final_ce_icon)
            embed.set_thumbnail(url=interaction.user.avatar)

            # Send a confirmation message
            await interaction.followup.send(embed=embed)

        # change the rank
        # TODO: maybe get folkius to give theron points to test this out? 
        # TODO: given that i have no way of knowing if it works rn
        elif return_value[:5:] == "rank:" :
            for rankrole in rankroles :
                if rankrole in interaction.user.roles :
                    role = rankrole
                    break
            if role.name == return_value[6::] : continue
            else :
                for rankrole in rankroles :
                    if rankrole in interaction.user.roles : await interaction.user.remove_roles(rankrole)
                    if rankrole.name == return_value[6::] : 
                        await interaction.user.add_roles(rankrole)
                        await log_channel.send("Congratulations <@{}>! You've ranked up to {}!".format(interaction.user.id, return_value[6::]))

        
        # log channel shit
        elif return_value[:4:] == "log:" :
            await log_channel.send(return_value[5::])

        # casino channel shit
        elif return_value[:7:] == "casino:":
            await casino_channel.send(return_value[8::])

        # else
        else :
            await log_channel.send("BOT ERROR: recieved unrecognized update code: \n'{}'".format(return_value))
            



@tree.command(name='shutdown', description='(ONLY RUN IF NECESSARY) A command to shut down the bot', guild=discord.Object(id=guild_ID))
async def stop(interaction : discord.Interaction) :
    await interaction.response.defer()
    await interaction.followup.send("Bot is shutting down.... (goodbye).....")
    await client.close()
    exit()


"""
@tree.command(name='fix-my-horribleness', description='fix the onslaught of march 18', guild=discord.Object(id=guild_ID))
@tree.is_owner()
async def fix(interaction : discord.Interaction) :
    await interaction.response.defer()
    await interaction.followup.send('purging....')

    def meets_req(m : discord.Message) :
        return (m.author == client.user 
                and m.created_at > datetime.datetime(2024, 3, 18, 12, 30, 0) 
                and m.created_at < datetime.datetime(2024, 3, 18, 20, 30, 0))
    
    game_additions = client.get_channel(game_additions_id)
    
    deleted = await game_additions.purge(limit=1000, check=meets_req)
    await game_additions.send(f"Deleted {len(deleted)} of my messages. Sorry guys. May March 18 be forever remembered, and long live Soundodger 2 🙏")
"""



def calculate_cr(ce_id, database_user, database_name) :
    # set up grouping
    groups = {"Action" : [], "Arcade" : [], "Bullet Hell" : [], "First-Person" : [], "Platformer" : [], "Strategy" : []}

    # go through all of their games
    for game in database_user[ce_id]['Owned Games'] :

        points_in_game = 0

        # does the user have any points in the game?
        if "Primary Objectives" in database_user[ce_id]['Owned Games'][game] :

            # go through all of their objectives
            for obj in database_user[ce_id]['Owned Games'][game]['Primary Objectives'] :

                # add up all of their points
                points_in_game += database_user[ce_id]['Owned Games'][game]['Primary Objectives'][obj]
        
        if points_in_game != 0 :
            groups[database_name[game]['Genre']].append(points_in_game)
        else : continue


    # now that we have all the values, 
    # go through each category and actually calculate the CR
    total_cr = 0.0
    for genre in groups :
        genre_value = 0.0
        for index, value in enumerate(groups[genre]) :
            genre_value += (0.85**index)*(float(value))
        groups[genre] = round(genre_value, 2)
        total_cr += genre_value
    
    total_cr = round(total_cr, 2)
    return [total_cr, groups]





"""
@tree.command(name="calculate-cr", description="Calculate your CR for each individual genre!", guild=discord.Object(id=guild_ID))
@app_commands.describe(ephemeral="Decide if you want the reply to be visible to you only (ephemeral) or visible to everyone.")
async def cr(interaction : discord.Interaction, ephemeral : bool) :
    await interaction.response.defer(ephemeral=ephemeral)

    database_user = await get_mongo('user')
    database_name = await get_mongo('name')
    
    # find them in the users2.json
    ce_id = await get_ce_id(interaction.user.id)
    
    # if not found, stop
    if ce_id == None : return await interaction.followup.send('You have not registered with CE Assistant! Please use /register with the link to your personal CE page :)')

    # set up grouping
    groups = {"Action" : [], "Arcade" : [], "Bullet Hell" : [], "First-Person" : [], "Platformer" : [], "Strategy" : []}

    # go through all of their games
    for game in database_user[ce_id]['Owned Games'] :

        points_in_game = 0

        # does the user have any points in the game?
        if "Primary Objectives" in database_user[ce_id]['Owned Games'][game] :

            # go through all of their objectives
            for obj in database_user[ce_id]['Owned Games'][game]['Primary Objectives'] :

                # add up all of their points
                points_in_game += database_user[ce_id]['Owned Games'][game]['Primary Objectives'][obj]
        
        if points_in_game != 0 :
            groups[database_name[game]['Genre']].append(points_in_game)
        else : continue


    # now that we have all the values, 
    # go through each category and actually calculate the CR
    total_cr = 0.0
    for genre in groups :
        genre_value = 0.0
        for index, value in enumerate(groups[genre]) :
            genre_value += (0.85**index)*(float(value))
        groups[genre] = round(genre_value, 2)
        total_cr += genre_value
    
    embed = discord.Embed(title="CR Values", description="The calculation of all of your (<@{}>'s) CRs!".format(interaction.user.id), timestamp=datetime.datetime.now(), color=0x000000)
    embed.add_field(name="Total CR", value=str(round(total_cr, 2)), inline=False)

    for genre in groups :
        embed.add_field(name=str(genre) + " CR", value=str(groups[genre]), inline=True)
    
    del database_name
    del database_user
    

    return await interaction.followup.send(embed=embed)
"""




"""


@tree.command(name='startup_sched', description='hoping this is outdated by now!!!!', guild=discord.Object(id=guild_ID))
async def startup(interaction: discord.Interaction):
    await interaction.response.defer()
    print('starting up')
    await startup_sched()
    print('started up')
    await interaction.followup.send('i love blob the log')

"""


# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------- REASON COMMAND----------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
@tree.command(name="add-notes", description="Add note to game-additions embed", guild=discord.Object(id=guild_ID))
@app_commands.describe(reason="The string you'd like to add under the 'Notes' banner on a site-addition embed")
@app_commands.describe(embed_id="The message ID of the embed you'd like to change the note of")
async def reason(interaction : discord.Interaction, reason : str, embed_id : str) :

    # defer and make ephemeral
    await interaction.response.defer(ephemeral=True)

    # grab the site additions channel
    site_additions_channel = client.get_channel(game_additions_id)

    # try to get the message
    try :
        message = await site_additions_channel.fetch_message(int(embed_id))

    # if it errors, message is not in the site-additions channel
    except :
        return await interaction.followup.send("This message is not in the <#949482536726298666> channel.")
    
    if message.author.id != 1108618891040657438 : return await interaction.followup.send("This message was not sent by the bot!")

    # grab the embed
    embed = message.embeds[0]

    # try and see if the embed already has a reason field
    try :
        if(embed.fields[len(embed.fields)-1].name == "Note") :
            embed.set_field_at(index=len(embed.fields)-1, name="Note", value=reason)
    
    # if it errors, then just add a reason field
    except :
        embed.add_field(name="Note", value=reason, inline=False)

    # edit the message
    await message.edit(embed=embed, attachments="")

    # and send a response to the original interaction
    await interaction.followup.send("worked", ephemeral=True)


def get_points(user_api_data) :
    # get the unix timecode of the first of the month
    year1 = int(time.strftime('%Y'))
    month1 = int(time.strftime('%m'))
    date_time = datetime.datetime(year=year1, month=month1, day=1, hour=0, minute=0, second=0)
    date_limit = int(time.mktime(date_time.timetuple()))
    del date_time


    if month1 != 1 : date_time_2 = datetime.datetime(year=year1, month=month1 - 1, day=1, hour=0, minute=0, second=0)
    else : date_time_2 = datetime.datetime(year=year1 - 1, month=12, day=1, hour=0, minute=0, second=0)
    date_limit_2 = int(time.mktime(date_time_2.timetuple()))
    del date_time_2

    # iterate through the objectives
    points = 0
    points_old = 0
    total_points = 0
    three : dict[int, str] = {}
    for item in user_api_data['userObjectives'] :
        if timestamp_to_unix(item['updatedAt']) > date_limit :
            if item['partial'] :
                points += item['objective']['pointsPartial']
            else :
                points += item['objective']['points']
        elif timestamp_to_unix(item['updatedAt']) > date_limit_2 :
            if item['partial'] :
                points_old += item['objective']['pointsPartial']
            else:
                points_old += item['objective']['points']
        if item['partial'] : total_points += item['objective']['pointsPartial']
        else : total_points += item['objective']['points']

        # put all objectives in a dictionary
        silly_str = item['objective']['name'] + " ("
        if item['partial'] : silly_str += str(item['objective']['pointsPartial'])
        else : silly_str += str(item['objective']['points'])
        silly_str += icons['Points'] + ") - " + item['objective']['game']['name']

        three[timestamp_to_unix(item['updatedAt'])] = silly_str

    sorted_dict = dict(sorted(three.items(), key=lambda x: x[0], reverse=True))
    final_dict = dict(list(sorted_dict.items())[:3:])

    del three
    del sorted_dict
    
    
    
    return [points, points_old, date_limit, date_limit_2, total_points, final_dict]


"""
@tree.command(name="most-recent-points", description="See the points you (or a friend) have accumulated since the start of the month", guild=discord.Object(id=guild_ID))
async def most_recent_points(interaction : discord.Interaction, user: discord.User = None) :
    # defer the message
    await interaction.response.defer()
    
    # if no user is provided, use the sender's
    if user == None : user = interaction.user.id
    else : user = user.id

    # grab their ce_id, and return if they're not registered
    ce_id = await get_ce_id(user)
    if ce_id == None : return await interaction.followup.send(f"<@{user}> isn't registered in the CE Assistant database!")

    # grab their most recent ce data
    user_api_data = get_api("user", ce_id)

    array = get_points(user_api_data)
    points = array[0]
    points_old = array[1]
    date_limit = array[2]
    date_limit_2 = array[3]
    total_points = array[4]

    del user_api_data

    return await interaction.followup.send(f"<@{user}> has achieved {points} points since <t:{date_limit}>, and {points_old} points last month.")
"""



@tree.command(name="profile", description="Get general info about anyone in CE!", guild=discord.Object(id=guild_ID))
async def profile(interaction : discord.Interaction, user : discord.Member = None):
    await interaction.response.defer()

    if user == None : user = interaction.user

    ce_id = await get_ce_id(user.id)
    if ce_id == None : return await interaction.followup.send(f"<@{user.id}> is not registered in the CE Assistant database. Please run `/register` with the link to your CE page!")

    # pull data
    user_api_data = get_api("user", ce_id)
    database_user = await get_mongo('user')
    database_name = await get_mongo('name')

    # get stuff
    array = get_points(user_api_data)
    points = array[0]
    points_old = array[1]
    date_limit = array[2]
    date_limit_2 = array[3]
    total_points = array[4]
    recents = array[5]

    # get cr
    array2 = calculate_cr(ce_id, database_user, database_name)
    total_cr = array2[0]
    groups = array2[1]

    # tier and genre stuff
    stupid_horribleness = {
        "3c3fd562-525c-4e24-a1fa-5b5eda85ebbd" : "Platformer",
        "4d43349a-43a8-4755-9d52-41ece63ec5b1" : "Action",
        "7f8676fe-4900-400b-9284-c073388d88f7" : "Bullet Hell",
        "a6d00cc0-9481-47cb-bb52-a7011041915a" : "First-Person",
        "ec499226-0913-4db1-890e-093b366bcb3c" : "Arcade",
        "ffb558c1-5a45-4b8c-856c-e9622ce54f00" : "Strategy",
        "00000000-0000-0000-0000-000000000000" : None
    }
    genres_local = {}
    tiers_local = {}
    tiergenrestr = ""
    for item in user_api_data['userTierSummaries'] :
        if item['genreId'] == "00000000-0000-0000-0000-000000000000" : 
            total = item['total']
            for i in range(1,6) :
                tiers_local['Tier ' + str(i)] = item['tier' + str(i)]
        else:
            genreName = stupid_horribleness[item['genreId']]
            genres_local[genreName] = item['total']

    for i in range(1, 7) :
        tiergenrestr += f"{icons[all_genres[i-1]]}: {genres_local[all_genres[i-1]]}\t　\t"
        if i != 6: tiergenrestr += f"{icons['Tier ' + str(i)]}: {tiers_local['Tier ' + str(i)]}\n"
        else : tiergenrestr += f"Total: {total}"
    
    # get recent string
    recentsstr = ""
    for item in recents:
        recentsstr += recents[item] + "\n"

    # get month names
    curr_month = datetime.datetime.now().month
    if curr_month != 1 : past_month = curr_month - 1
    else : past_month = 12  

    # make the embed
    main_embed = discord.Embed(
        title="Profile",
        timestamp=datetime.datetime.now(),
        color=0xff9494
    )
    main_embed.add_field(name="User", value=f"<@{user.id}> {icons[database_user[ce_id]['Rank']]}", inline=True)
    main_embed.add_field(name="Current Points", value=f"{total_points} {icons['Points']} - CR: {str(total_cr)}", inline=True)
    main_embed.add_field(name="Recent Completions", value=recentsstr, inline=False)
    main_embed.add_field(name="Points", value=f"Points this month ({calendar.month_name[curr_month]}) : {points} {icons['Points']}\nPoints last month ({calendar.month_name[past_month]}) : {points_old} {icons['Points']}", inline=False)
    main_embed.add_field(name="Completions", value=tiergenrestr, inline=True)
    #embed.set_image(url=user.avatar.url)
    main_embed.set_author(name="Challenge Enthusiasts", url=f"https://cedb.me/user/{ce_id}", icon_url=user.avatar.url)
    main_embed.set_footer(text="CE Assistant", icon_url=final_ce_icon)

    # make roll embed
    roll_embed = checkRollsEmbed(user, database_name, database_user, ce_id)

    # make cr embed
    cr_embed = discord.Embed(title="CR Values", description="The calculation of all of <@{}>'s CRs!".format(user.id), timestamp=datetime.datetime.now(), color=0xff9494)
    cr_embed.add_field(name="Total CR", value=str(round(total_cr, 2)), inline=False)
    for genre in groups :
        cr_embed.add_field(name=str(genre) + " CR", value=str(groups[genre]), inline=True)

    # make discord.ui.view
    view = discord.ui.View(timeout=600)
    mainButton = discord.ui.Button(label="Main", disabled=True)
    rollButton = discord.ui.Button(label="Rolls", disabled=False)
    crButton = discord.ui.Button(label="CR", disabled=False)
    async def mainCallback(interaction : discord.Interaction):
        rollButton.disabled = False
        crButton.disabled = False
        mainButton.disabled = True
        await interaction.response.edit_message(embed=main_embed, view=view)
    async def rollCallback(interaction : discord.Interaction):
        mainButton.disabled = False
        rollButton.disabled = True
        crButton.disabled = False
        await interaction.response.edit_message(embed=roll_embed, view=view)
    async def crCallback(interaction : discord.Interaction):
        mainButton.disabled = False
        rollButton.disabled = False
        crButton.disabled = True
        await interaction.response.edit_message(embed=cr_embed, view=view)
    mainButton.callback = mainCallback
    rollButton.callback = rollCallback
    crButton.callback = crCallback
    view.add_item(mainButton)
    view.add_item(rollButton)
    view.add_item(crButton)

    # and send the message
    return await interaction.followup.send(embed=main_embed, view=view)


@tree.command(name='stop-scrape', description='stop scrape (ADMIN ONLY!!!)', guild=discord.Object(id=guild_ID)) 
async def stop_scrape(interaction : discord.Interaction) :
    await interaction.response.defer()
    await interaction.followup.send('stopping...')
    raise ValueError










# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------- Operational Restart -------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
@tree.command(name="manual-restart", description="Will restart the computer the bot is currently hosted on", guild=discord.Object(id=guild_ID))
async def manual_restart(interaction : discord.Interaction):
    await interaction.response.send_message('rebooting...')
    await restart(__file__)


@tree.command(name="add-to-boot", description="Will add the bot to startup on boot", guild=discord.Object(id=guild_ID))
async def add_to_boot(interaction : discord.Interaction):
    await interaction.response.send_message('adding directories...')
    await add_to_windows_startup(__file__)









# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------- Operational Restart -------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
@tree.command(name="steal-schmoles-schmeat", description="Will restart the computer the bot is currently hosted on", guild=discord.Object(id=guild_ID))
async def steal_schmoles_schmeat(interaction):
    await interaction.response.send_message('stealing schmoles schmeat')
    await csv_conversion()



# ----------------------------------- LOG IN ----------------------------
@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=guild_ID))
    
    test_log = client.get_channel(private_log_id)
    await test_log.send("The bot has now been restarted.")    #get_tasks(client)
    if _in_ce:
        await master_loop.start(client)
    #await check_roll_status.start()


client.run(discord_token)