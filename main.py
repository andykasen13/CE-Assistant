# ---------- time imports -----------
import asyncio
from datetime import datetime
import datetime
import functools
import io
import typing
import os
from bson import ObjectId
import time
import json
from discord.ext import tasks

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
from Web_Interaction.scraping import single_scrape, get_image
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

uri = "mongodb+srv://andrewgarcha:KUTo7dCtGRy4Nrhd@ce-cluster.inrqkb3.mongodb.net/?retryWrites=true&w=majority"
mongo_client = AsyncIOMotorClient(uri)

mongo_database = mongo_client['database_name']
collection = mongo_client['database_name']['ce-collection']

mongo_ids = {
    "name" : ObjectId('64f8d47f827cce7b4ac9d35b'),
    "tier" : ObjectId('64f8bc4d094bdbfc3f7d0050'),
    "curator" : ObjectId('64f8d63592d3fe5849c1ba35'),
    "tasks" : ObjectId('64f8d6b292d3fe5849c1ba37'),
    "user" : ObjectId('64f8bd1b094bdbfc3f7d0051'),
    "unfinished" : ObjectId('650076a9e35bbc49b06c9881')
}


# Grab information from json file
with open('Jasons/secret_info.json') as f :
    localJSONData = json.load(f)

discord_token = localJSONData['discord_token']  
guild_ID = localJSONData['test_guild_ID']

ce_mountain_icon = "https://cdn.discordapp.com/attachments/639112509445505046/891449764787408966/challent.jpg"
ce_hex_icon = "https://media.discordapp.net/attachments/643158133673295898/1133596132551966730/image.png?width=778&height=778"
ce_james_icon = "https://cdn.discordapp.com/attachments/1028404246279888937/1136056766514339910/CE_Logo_M3.png"
final_ce_icon = "https://cdn.discordapp.com/attachments/1135993275162050690/1144289627612655796/image.png"







async def aaaa_auto(interaction : discord.Interaction, current:str) -> typing.List[app_commands.Choice[str]]:
    data = []
    database_name = await collection.find_one({'_id' : mongo_ids["tier"]})
    print(database_name) 

    for game in list(database_name.keys()):
        data.append(app_commands.Choice(name=game,value=game))
    print(data)
    return data





@tree.command(name="aaaaa", description="afjdals", guild=discord.Object(id=guild_ID))
#@app_commands.autocomplete(item=aaaa_auto)
async def aaaaa(interaction : discord.Interaction, item : str):
    await interaction.response.defer()

    data = requests.get('https://cedb.me/api/user/d7cb0869-5ed9-465c-87bf-0fb95aaebbd5/')
    print(data.text)
    data_json = json.loads(data.text)
    #data_json_2 = json.load(data.text)
    await interaction.followup.send(item)












# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------HELP COMMAND------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
@tree.command(name="help", description="help", guild=discord.Object(id=guild_ID))
async def help(interaction : discord.Interaction) :
    await interaction.response.defer(ephemeral=True)

    page_data = json.loads(open("/CE-Assistant/Jasons/help_embed_data.json").read())

    basic_options = page_data['Options']
    selections = []

    roll_options = page_data['Rolls']
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
        if option == 'Admin Options' and (not mod_role in interaction.user.roles and not admin_role in interaction.user.roles):
            continue
        selections.append(discord.SelectOption(label=basic_options[option]["Name"],emoji=basic_options[option]['Emoji'],description=basic_options[option]["Description"]))

    for option in roll_options:
        rolls.append(discord.SelectOption(label=roll_options[option]["Name"],emoji=roll_options[option]['Emoji'],description=roll_options[option]["Description"]))

    for option in admin_options:
        admin.append(discord.SelectOption(label=admin_options[option]["Name"],emoji=admin_options[option]['Emoji'],description=admin_options[option]["Description"]))
  

    

    class HelpSelect(discord.ui.Select):
        def __init__(self, select, message="Select an option"):
            options=select
            super().__init__(placeholder=message, max_values=1,min_values=1,options=options)


        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer()
            embed = self.get_embed()
            if self.values[0] == 'Rolls' or self.values[0] in list(roll_options.keys()):
                await interaction.followup.edit_message(embed = embed, view=HelpSelectView(menu=rolls, message="Rolls", message_2=self.values[0]), message_id = interaction.message.id)
            if self.values[0] == 'Admin Options' or self.values[0] in list(admin_options.keys()):
                await interaction.followup.edit_message(embed = embed, view=HelpSelectView(menu=admin, message="Admin Options", message_2=self.values[0]), message_id = interaction.message.id)
            else:
                await interaction.followup.edit_message(embed=embed, view=HelpSelectView(message=self.values[0]), message_id = interaction.message.id)

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
            self.add_item(HelpSelect(selections, message))
            if menu != "" :
                if message_2 == 'Rolls':
                    message_2 = "Select an option"
                self.add_item(HelpSelect(menu, message_2))

        async def on_timeout(self):
            self.clear_items()

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
    if interaction.user.id == 359387889781571585 : return await interaction.followup.send("syrenyx you have been blocked from the bot lol")

    await solo_command(interaction, event, reroll = False, collection=collection)
    




















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

    return await interaction.followup.send("Feature under construction!! Coming soon.")

    # if no user is provided default to sender
    if user is None :
        user = interaction.user

    # get mongo data
    userInfo = await collection.find_one({'_id' : mongo_ids["user"]})
    database_name_info = await collection.find_one({'_id' : mongo_ids["name"]})


    # iterate through the json file until you find the
    # designated user
    steam_user_name = ""
    for user_name in list(userInfo) :
        if user_name == "_id" : continue
        if(userInfo[user_name]["Discord ID"] == user.id) :
            steam_user_name = user_name
            break
    
    if(steam_user_name == "") : return await interaction.response.followup("This user does not exist.")
    print(steam_user_name)

    current_roll_str = get_roll_string(userInfo, steam_user_name, database_name_info, user, 'Current Rolls')
    completed_roll_str = get_roll_string(userInfo, steam_user_name, database_name_info, user, 'Completed Rolls')
    
    # make the embed that you're going to send
    embed = discord.Embed(colour=0x000000, timestamp=datetime.datetime.now())
    embed.add_field(name="User", value = "<@" + str(user.id) + ">", inline=False)
    embed.add_field(name="Current Rolls", value=current_roll_str, inline=False)
    embed.add_field(name="Completed Rolls", value=completed_roll_str, inline=False)
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







@tasks.loop(time=datetime.time(hour=0, minute=0, tzinfo=datetime.timezone.utc))
async def check_roll_status():
    print('it ran omg it actually ran')
    # get databases
    database_user = await collection.find_one({'_id' : mongo_ids["user"]})
    database_name = await collection.find_one({"_id" : mongo_ids["name"]})

    # create a variable that holds all the messages that need to be sent
    all_returns = []

    # go through each user in database user. if they have any cooldowns or current rolls.... update their profiles.
    for user in database_user:

        # if their current rolls are empty and their cooldowns are empty keep checking
        if(database_user[user]["Current Rolls"] == [] and database_user[user]["Cooldowns"] == {}) : continue
        else:
            # update their profile.
            returns = update_p(database_user[user]["Discord ID"], "", database_user, database_name)
            
            # update database_user.
            database_user = returns[0]
            returns[0] = "NEW USER: " + str(database_user[user]["Discord ID"])
            
            # add all returned values to the array except database_user. that has been dealt with.
            for i in range(0, len(returns)):
                all_returns.append(returns[i])
            
            # make the returns array empty.
            returns = []
    
    # update the databases
    dump = await collection.replace_one({"_id" : mongo_ids["user"]}, database_user)


    # initialize the variables ##################################################################################################################
    log_channel = client.get_channel(1141886539157221457)                                                                                       #
    casino_channel = client.get_channel(811286469251039333)                                                                                     #
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

        









# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------- SCRAPING --------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
@to_thread
def scrape_thread_call(curator_count):
    return single_scrape(curator_count)


@tree.command(name="scrape", description="Force update every game without creating embeds. DO NOT RUN UNLESS NECESSARY.", guild=discord.Object(id=guild_ID))
async def scrape(interaction):
    await interaction.response.send_message('scraping...')

    namedb = mongo_client['database_name']
    col = namedb['ce-collection']
    curator_count = await col.find_one({'_id' : ObjectId('64f8d63592d3fe5849c1ba35')})

    objects = await scrape_thread_call(curator_count)

    # add the id back to database_name
    objects[0]['_id'] = ObjectId('64f8d47f827cce7b4ac9d35b')
    objects[2]['_id'] = ObjectId('64f8bc4d094bdbfc3f7d0050')
    
    # dump the databases back onto mongoDB
    dump1 = await col.replace_one({'_id' : ObjectId('64f8d63592d3fe5849c1ba35')}, objects[1])
    dump2 = await col.replace_one({'_id' : ObjectId('64f8d47f827cce7b4ac9d35b')}, objects[0])
    dump3 = await col.replace_one({'_id' : ObjectId('64f8bc4d094bdbfc3f7d0050')}, objects[2])

    await interaction.channel.send('scraped')

    del dump3
    del dump1
    del dump2
    del curator_count
    del objects
























@tree.command(name="get_times", description="Prints out a table of times fifteen minutes apart in UTC", guild=discord.Object(id=guild_ID))
async def get_times(interaction):
    await interaction.response.send_message('times...')
    fin = "times = ["
    for i in range(0, 24):
        for j in range(0, 4):
            fin += "\n  datetime.time(hour={}, minute={}, tzinfo=utc),".format(i,j*15)

    fin = fin[:-1:] + "\n]"

    print(fin)



















# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------- CURATE ---------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
@tree.command(name="curate", description="Sends as many of the latest curator messages as requested or the latest if none specified.", guild=discord.Object(id=guild_ID))
@app_commands.describe(num="Number of previous curator entries to pull")
async def curate(interaction, num : int = 0):
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
async def steam_command(interaction : discord.Interaction, game_name: str):

    # Log the command
    print("Recieved steam_game command with parameter: " + game_name + ".")

    # open database
    database_name = await collection.find_one({'_id' : mongo_ids['name']})

    # Defer the interaction
    await interaction.response.defer(ephemeral=True)

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
    
    async def black_callback(interaction) : return await assign_role(interaction, black_role)
    async def red_callback(interaction) : return await assign_role(interaction, red_role)
    async def yellow_callback(interaction) : return await assign_role(interaction, yellow_role)
    async def orange_callback(interaction) : return await assign_role(interaction, orange_role)
    async def purple_callback(interaction) : return await assign_role(interaction, purple_role)
    async def blue_callback(interaction) : return await assign_role(interaction, blue_role)
    async def green_callback(interaction) : return await assign_role(interaction, green_role)
    async def brown_callback(interaction) : return await assign_role(interaction, brown_role)
    async def grey_callback(interaction) : return await assign_role(interaction, grey_role)

    black_button.callback = black_callback
    red_button.callback = red_callback
    yellow_button.callback = yellow_callback
    orange_button.callback = orange_callback
    purple_button.callback = purple_callback
    blue_button.callback = blue_callback
    green_button.callback = green_callback
    brown_button.callback = brown_callback
    grey_button.callback = grey_callback

    view.add_item(black_button)
    view.add_item(red_button)
    view.add_item(yellow_button)
    view.add_item(orange_button)
    view.add_item(purple_button)
    view.add_item(blue_button)
    view.add_item(green_button)
    view.add_item(brown_button)
    view.add_item(grey_button)

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
async def test(interaction : discord.Interaction) :
    await interaction.response.defer(ephemeral=True)

    await interaction.followup.send('looping....')

    await master_loop(client, mongo_client)

    

    

    #casino_channel = client.get_channel(811286469251039333)
    
    #await roll_failed(ended_roll_name='Triple Threat', casino_channel=casino_channel, user_name='d7cb0869-5ed9-465c-87bf-0fb95aaebbd5')


    #return await interaction.followup.send(embed=discord.Embed(title="this is the test command"))
    #print(role.id)
    
    # embed = discord.Embed(title="__Celeste__ has been updadted on the site", description="' ∀MAZING' increased from 120 :CE_points: ➡ 125 :CE_points: points: Achievements '∀NOTHER ONE', and '∀DVENTED' removed New Primary Objective '∀WOKEN' added: 30 points :CE_points: Clear the Pandemonic Nightmare stage, and clear Hymeno Striker on AKASCHIC+RM difficulty.")
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
    
    #Open the user database
    database_user = await collection.find_one({'_id' : (mongo_ids["user"])})

    # Set up total_points to calculate rank
    total_points = 0

    # Make sure the input is a valid CE-ID
    print(f"Input = {ce_id}")
    if(ce_id[:20:] == "https://cedb.me/user" and len(ce_id) >= 29 and (ce_id[29] == '-')) :
        if(ce_id[(len(ce_id)-5)::] == "games") : ce_id = ce_id[21:(len(ce_id)-6):]
        else : ce_id = ce_id[21::]
    else: return await interaction.followup.send(f"'{ce_id}' is not a valid user link. Please try again or contact <@413427677522034727> for assistance.")
    print(f"Working ID = {ce_id}")

    # Make sure user isn't already registered
    for user in database_user :
        if user == '_id' : continue
        if(database_user[user]["Discord ID"] == interaction.user.id) : return await interaction.followup.send("You are already registered in the database!")
        elif(database_user[user]["CE ID"] == ce_id) : return await interaction.followup.send(f"This CE-ID is already registered to <@{database_user[user]['Discord ID']}>, silly!")
    
    # Grab user info from CE API
    response = requests.get(f"https://cedb.me/api/user/{ce_id}")
    user_ce_data = json.loads(response.text)

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
            "Completed Rolls" : []
        }
    }

    # Go through owned games in CE JSON
    for game in user_ce_data["userGames"] :
        game_name = game["game"]["name"]
        
        # Add the games to the local JSON
        user_dict[ce_id]["Owned Games"][game_name] = {}

    # Go through all objectives 
    for objective in user_ce_data["userObjectives"] :
        game_name = objective["objective"]["game"]["name"]
        obj_name = objective["objective"]["name"]
        
        # If the objective is community, set the value to true
        if objective["objective"]["community"] : 
            if(list(user_dict[ce_id]["Owned Games"][game_name].keys()).count("Community Objectives") == 0) :
                user_dict[ce_id]["Owned Games"][game_name]["Community Objectives"] = {}
            user_dict[ce_id]["Owned Games"][game_name]["Community Objectives"][obj_name] = True

        # If the objective is primary...
        else : 
            # ... and there are partial points AND no one has assigned requirements...
            if(objective["objective"]["pointsPartial"] != 0 and objective["assignerId"] == None) :
                # ... set the points earned to the partial points value.
                points = objective["objective"]["pointsPartial"]
            # ... and there are no partial points, set the points earned to the total points value.
            else : points = objective["objective"]["points"]

            # Add the points to user's total points
            total_points += points

            # Now actually update the value in the user's dictionary.
            if(list(user_dict[ce_id]["Owned Games"][game_name].keys()).count("Primary Objectives") == 0) :
                user_dict[ce_id]["Owned Games"][game_name]["Primary Objectives"] = {}
            user_dict[ce_id]["Owned Games"][game_name]["Primary Objectives"][obj_name] = points


    # Get the user's rank
    rank = ""
    if total_points < 50 : rank = "Rank E"
    elif total_points < 250 : rank = "Rank D"
    elif total_points < 500 : rank = "Rank C"
    elif total_points < 1000 : rank = "Rank B"
    elif total_points < 2500 : rank = "Rank A"
    elif total_points < 5000 : rank = "Rank S"
    elif total_points < 7500 : rank = "Rank SS"
    elif total_points < 10000 : rank = "Rank SSS"
    else : rank = "Rank EX"

    user_dict[ce_id]["Rank"] = rank

    all_events = ["One Hell of a Day", "One Hell of a Week", "One Hell of a Month", "Two Week T2 Streak", "Two 'Two Week T2 Streak' Streak",
                  "Never Lucky", "Triple Threat", "Let Fate Decide", "Fourward Thinking", "Russian Roulette", "Destiny Alignment",
                  "Soul Mates", "Teamwork Makes the Dream Work", "Winner Takes All", "Game Theory"]

    # Check and see if the user has any completed rolls
    if(list(user_dict[ce_id]["Owned Games"].keys()).count("- Challenge Enthusiasts -") > 0) :
        x=0
        
        for event_name in all_events :
            if(list(user_dict[ce_id]["Owned Games"]["- Challenge Enthusiasts -"]["Community Objectives"].keys()).count(event_name) > 0) :
                x=0
                user_dict[ce_id]["Completed Rolls"].append({"Event Name" : event_name})

    # Add the user file to the database
    database_user.update(user_dict)

    # Dump the data
    dump = await collection.replace_one({'_id' : mongo_ids['user']}, database_user)

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

    registered_role = discord.utils.get(interaction.guild.roles, name = "registered")
    #await interaction.user.add_roles(registered_role)

    # Send a confirmation message
    await interaction.followup.send(embed=embed)














@tree.command(name="update", description="Update your stats in the CE Assistant database.", guild=discord.Object(id=guild_ID))
async def update(interaction : discord.Interaction) :
    # Defer the message
    await interaction.response.defer(ephemeral=True)

    database_name = await collection.find_one({'_id' : mongo_ids["name"]})
    database_user = await collection.find_one({'_id' : mongo_ids["user"]})

    log_channel = client.get_channel(1141886539157221457)
    casino_channel = client.get_channel(811286469251039333)
    
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
    returns = update_p(interaction.user.id, False, database_user, database_name)

    if returns == "Unregistered" : return await interaction.followup.send("You have not registered. Please use /register with the link to your CE page.")

    dump = await collection.replace_one({'_id' : mongo_ids['user']}, returns[0])
    del returns[0]

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
                    if rankrole.name == return_value[6::] : await interaction.user.add_roles(rankrole)
        
        # log channel shit
        elif return_value[:4:] == "log:" :
            await log_channel.send(return_value[5::])

        # casino channel shit
        elif return_value[:7:] == "casino:":
            await casino_channel.send(return_value[8::])

        # else
        else :
            await log_channel.send("BOT ERROR: recieved unrecognized update code: \n'{}'".format(return_value))
            




















    
@tree.command(name="calculate-cr", description="Calculate your CR for each individual genre!", guild=discord.Object(id=guild_ID))
@app_commands.describe(ephemeral="Decide if you want the reply to be visible to you only (ephemeral) or visible to everyone.")
async def cr(interaction : discord.Interaction, ephemeral : bool) :
    await interaction.response.defer(ephemeral=ephemeral)

    database_user = await collection.find_one({'_id' : mongo_ids["user"]})
    database_name = await collection.find_one({'_id' : mongo_ids['name']})
    
    # find them in the users2.json
    ce_id = ""
    for user in database_user :
        if user == '_id' : continue
        if database_user[user]["Discord ID"] == interaction.user.id :
            ce_id = user
            break
    
    # if not found, stop
    if ce_id == "" : return await interaction.followup.send('You have not registered with CE Assistant! Please use /register with the link to your personal CE page :)')

    # set up grouping
    groups = {"Action" : [], "Arcade" : [], "Bullet Hell" : [], "First-Person" : [], "Platformer" : [], "Strategy" : []}

    # go through all of their games
    for game in database_user[ce_id]["Owned Games"] :

        points_in_game = 0

        # does the user have any points in the game?
        if "Primary Objectives" in database_user[ce_id]["Owned Games"][game] :

            # go through all of their objectives
            for obj in database_user[ce_id]["Owned Games"][game]["Primary Objectives"] :

                # add up all of their points
                points_in_game += database_user[ce_id]["Owned Games"][game]["Primary Objectives"][obj]
        
        if points_in_game != 0 :
            groups[database_name[game]["Genre"]].append(points_in_game)
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








@tree.command(name='startup_sched', description='hoping this is outdated by now!!!!', guild=discord.Object(id=guild_ID))
async def startup(interaction: discord.Interaction):
    await interaction.response.defer()
    print('starting up')
    await startup_sched()
    print('started up')
    await interaction.followup.send('i love blob the log')




# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------- REASON COMMAND----------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
@tree.command(name="add-reason", description="Add reason to embed", guild=discord.Object(id=guild_ID))
@app_commands.describe(reason="The string you'd like to add under the 'Reason' banner on a site-addition embed")
@app_commands.describe(embed_id="The message ID of the embed you'd like to change the reason of")
async def reason(interaction : discord.Interaction, reason : str, embed_id : str) :

    # defer and make ephemeral
    await interaction.response.defer(ephemeral=True)

    # grab the site additions channel
    # TODO: update this in the CE server
    site_additions_channel = client.get_channel(1128742486416834570)

    # try to get the message
    try :
        message = await site_additions_channel.fetch_message(int(embed_id))

    # if it errors, message is not in the site-additions channel
    except :
        return await interaction.followup.send("This message is not in the <#1128742486416834570> channel.")
    
    if message.author.id != 1108618891040657438 : return await interaction.followup.send("This message was not sent by the bot!")

    # grab the embed
    embed = message.embeds[0]

    # try and see if the embed already has a reason field
    try :
        if(embed.fields[len(embed.fields)-1].name == "Reason") :
            embed.set_field_at(index=len(embed.fields)-1, name="Reason", value=reason)
    
    # if it errors, then just add a reason field
    except :
        embed.add_field(name="Reason", value=reason, inline=False)

    # edit the message
    await message.edit(embed=embed, attachments="")

    # and send a response to the original interaction
    await interaction.followup.send("worked", ephemeral=True)


    #get mongo shit
    def getMongoShit(option : mongo_ids.keys()):
        return asyncio.run(collection.find_one[{'_id' : mongo_ids[option]}])

"""
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------- REROLL COMMAND----------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
events_total = Literal["One Hell of a Day", "One Hell of a Week", "One Hell of a Month", "Two Week T2 Streak", 
          "Two 'Two Week T2 Streak' Streak", "Never Lucky", "Triple Threat", "Let Fate Decide", "Fourward Thinking",
          "Russian Roulette", "Destiny Alignment", "Soul Mates", "Teamwork Makes the Dream Work", 
          "Winner Takes All", "Game Theory"]

@tree.command(name='reroll', description='Reroll any of your current rolls', guild=discord.Object(id=guild_ID))
@app_commands.describe(event="The event you'd like to re-roll")
async def reroll(interaction : discord.Interaction, event : events_total) :


    # defer the message
    await interaction.response.defer()

    local_events_solo = ["One Hell of a Day", "One Hell of a Week", "One Hell of a Month", "Two Week T2 Streak", 
          "Two 'Two Week T2 Streak' Streak", "Never Lucky", "Triple Threat", "Let Fate Decide", "Fourward Thinking",
          "Russian Roulette"]
    
    local_events_co_op = ["Destiny Alignment", "Soul Mates", "Teamwork Makes the Dream Work", 
                       "Winner Takes All", "Game Theory"]

    print(event)

    # Open the database
    with open('/CE-Assistant/Jasons/users2.json', 'r') as f:
        database_user = json.load(f)

    # Check if user is in the database
    user_name = -1
    for c_user in database_user :
        if(database_user[c_user]['Discord ID'] == interaction.user.id) :
            user_name = c_user
            break
    if user_name == -1 : return await interaction.followup.send('You are not currently in the user database! Please use /register.')

    # Check if the user is participating in the event
    roll_num = -1
    for index, c_roll in enumerate(database_user[user_name]["Current Rolls"]) :

        if(c_roll["Games"] == ['pending...']) : return await interaction.followup.send('You have recently tried to roll or reroll this event. Please wait 10 minutes to try again.')


        if(c_roll["Event Name"] == event) : 
            roll_num = index
        
    # if the user isn't participating in the event
    if roll_num == -1 : return await interaction.followup.send('You are not currently participating in {}!'.format(event))

    # the user is ready to participate in the event

    # set up confirmation embed
    confirm_embed = discord.Embed(
        title="Are you sure?",
        timestamp=datetime.datetime.now(),
        description="You are asking to reroll {}. Your game(s) will switch from {} to other game(s).".format(event, database_user[user_name]["Current Rolls"][roll_num]["Games"])
        + " You will not recieve any additional time to complete this roll - and your deadline is still <t:{}>.".format(database_user[user_name]["Current Rolls"][roll_num]["End Time"])
    )

    # add buttons
    view = discord.ui.View(timeout=600)
    yes_button = discord.ui.Button(label="Yes", style=discord.ButtonStyle.green)
    no_button = discord.ui.Button(label="No", style=discord.ButtonStyle.danger)


    # send confirmation button  
    await interaction.followup.send(embed=confirm_embed)

    # run solo command if solo event
    if event in local_events_solo :
        await solo_command(interaction, event, reroll = True)

    # run co op command if co op event
    elif event in local_events_co_op :
        return await interaction.followup.send('Co-op and PvP rerolls coming soon!')
        await roll_co_op_command(interaction, event)
    
    # what happened here
    else : await interaction.followup.send('something has gone horribly horribly wrong. please let andy know')
    

    
    # class RerollView(discord.ui.View):
    #     def __init__(self):
    #         super().__init__(timeout=3)
    #         self.value = None
    #         self.current_page = 0
    #         self.pages = 10

    #     async def on_timeout(self):
    #         print("test")
    #         self.clear_items()

    #     @discord.ui.button(label="Previous", style=discord.ButtonStyle.grey, disabled=True)
    #     async def menu1(self, interaction: discord.Interaction, button: discord.ui.Button):
    #         self.current_page -= 1
    #         if self.current_page == 0:
    #             button.disabled = True
    #             print("previous should be disabled")
    #         self.children[-1].disabled = False

    #         await interaction.response.edit_message(
    #             content=f"{self.current_page}", view=self
    #         )

    #     @discord.ui.button(label="Next", style=discord.ButtonStyle.green)
    #     async def menu2(self, interaction: discord.Interaction, button: discord.ui.Button):
    #         self.current_page += 1
    #         if self.current_page == self.pages - 1:
    #             button.disabled = True
    #         self.children[0].disabled = False
    #         await interaction.response.edit_message(
    #             content=f"{self.current_page}", view=self
    #         )
"""















    

# ----------------------------------- LOG IN ----------------------------
@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=guild_ID))
    
    test_log = client.get_channel(1141886539157221457)
    await test_log.send("The bot has now been restarted.")    #get_tasks(client)
    await master_loop.start(client, mongo_client)
    await check_roll_status.start()


client.run(discord_token)
