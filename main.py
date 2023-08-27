# ---------- time imports -----------
import asyncio
from datetime import datetime, timedelta
import datetime
import functools
import time
import typing
from monthdelta import monthdelta

# ----------- discord imports ---------
import discord
from discord import app_commands
import random
from typing import Literal

# ----------- json imports ------------
import json

# --------- web imports ---------
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from Helper_Functions.Scheduler import create_schedule, get_tasks

# --------- other file imports ---------
from Web_Interaction.loopty_loop import master_loop, thread_curate
from Web_Interaction.curator import single_run
from Web_Interaction.scraping import single_scrape
from Helper_Functions.rollable_games import get_rollable_game, get_rollable_game_from_list
from Helper_Functions.create_embed import create_multi_embed, getEmbed
from Helper_Functions.roll_string import get_roll_string
from Helper_Functions.buttons import get_buttons, get_genre_buttons
from Helper_Functions.end_time import roll_completed, roll_failed
from Helper_Functions.update import update_p

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

# Grab information from json file
with open('Jasons/secret_info.json') as f :
    localJSONData = json.load(f)

discord_token = localJSONData['discord_token']  
guild_ID = localJSONData['test_guild_ID']
ce_mountain_icon = "https://cdn.discordapp.com/attachments/639112509445505046/891449764787408966/challent.jpg"
ce_hex_icon = "https://media.discordapp.net/attachments/643158133673295898/1133596132551966730/image.png?width=778&height=778"
ce_james_icon = "https://cdn.discordapp.com/attachments/1028404246279888937/1136056766514339910/CE_Logo_M3.png"


# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------HELP COMMAND------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
@tree.command(name="help", description="help", guild=discord.Object(id=guild_ID))
async def help(interaction : discord.Interaction) :
    # Defer the message
    await interaction.response.defer()

    class HelpSelect(discord.ui.Select):
        def __init__(self):
            options=[
                discord.SelectOption(label="Rolls",emoji="🎲",description="This is option 1!"),
                discord.SelectOption(label="Check Rolls",emoji="📖",description="This is option 2!"),
                discord.SelectOption(label="Site Additions",emoji="🤭",description="This is option 3!"),
                discord.SelectOption(label="Curator", emoji="🤓", description="This is option 4!")
            ]
            super().__init__(placeholder="Select an option",max_values=1,min_values=1,options=options)
        async def callback(self, interaction: discord.Interaction):
            await interaction.response.edit_message(content=f"Your choice is {self.values[0]}!",ephemeral=True)

    class HelpSelectView(discord.ui.View):
        def __init__(self, *, timeout = 180):
            super().__init__(timeout=timeout)
            self.add_item(HelpSelect())

    # Create the view (will be used for buttons later)
    view = discord.ui.View(timeout=600)

    return await interaction.followup.send('Help command coming soon!', view=HelpSelectView(), ephemeral=True)

    helpInfo = {
        "Rolls" : "This bot has the ability to roll random games for any event in the Challenge Enthusiast server. P.S. andy reminder to get autofill to work!",
        "/get_rolls" : "Use this command to see your current (and past) rolls, or the rolls of any other user in the server.",
        "steam_test" : "Get general information about any STEAM game.",
        "Curator" : "The bot will automatically check to see if any new entries have been added to the CE curator (within three hours)."
    }

    embeds=[]
    pageNum = 1
    
    for page in list(helpInfo):
        embed=discord.Embed(color=0x000000, title=page, description=helpInfo[page])
        embed.set_footer(text=(f"Page {pageNum} of {len(list(helpInfo))}"))
        embed.timestamp=datetime.datetime.now()
        embeds.append(embed)
        pageNum+=1

    await get_buttons(view, embeds)

    await interaction.followup.send(embed=embeds[0], view=view)





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

    await solo_command(interaction, event, reroll = False)
    



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

    await co_op_command(interaction, event, partner, reroll = False)



# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------- CHECK_ROLLS COMMAND ----------------------------------------------------- # 
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
@tree.command(name="check-rolls", description="Check the active rolls of anyone on the server", guild=discord.Object(id=guild_ID))
@app_commands.describe(user="The user you'd like to check the rolls of")
async def checkRolls(interaction, user: discord.Member=None) :
    # defer the message
    print('balls')
    await interaction.response.defer()

    # if no user is provided default to sender
    if user is None :
        user = interaction.user

    #open the json file and get the data
    with open('Jasons/users2.json', 'r') as f :
        userInfo = json.load(f)

    with open('Jasons/database_name.json', 'r') as g :
        database_name_info = json.load(g)

    # iterate through the json file until you find the
    # designated user
    steam_user_name = ""
    for user_name in list(userInfo) :
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
        icon_url=ce_james_icon)

    # send the embed
    await interaction.followup.send(embed=embed)




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



# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------- SCRAPING --------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
@to_thread
def scrape_thread_call():
    single_scrape()


@tree.command(name="scrape", description="Force update every game without creating embeds. DO NOT RUN UNLESS NECESSARY.", guild=discord.Object(id=guild_ID))
async def scrape(interaction):
    await interaction.response.send_message('scraping...')
    await scrape_thread_call()
    await interaction.channel.send('scraped')

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
    await single_run(client, num)

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

    # Defer the interaction
    await interaction.response.defer(ephemeral=True)

    # Get the embed
    embed = getEmbed(game_name, interaction.user.id)
    embed.set_author(name="Requested Steam info on '" + game_name + "'")
    

    # Finally, send the embed
    await interaction.followup.send(embed=embed)

    # And log it
    print("Sent information on requested game " + game_name + ": " + embed.title +"\n")




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
@tree.command(name="test", description="test", guild=discord.Object(id=guild_ID))
async def test(interaction : discord.Interaction, role : discord.Role) :
    await interaction.response.defer()

    await interaction.followup.send("Menus!")

    return

    casino_channel = client.get_channel(811286469251039333)
    
    await roll_failed(ended_roll_name='Triple Threat', casino_channel=casino_channel, user_name='d7cb0869-5ed9-465c-87bf-0fb95aaebbd5')


    return await interaction.followup.send(embed=discord.Embed(title="this is the test command"))
    print(role.id)
    
    embed = discord.Embed(title="__Celeste__ has been updadted on the site", description="' ∀MAZING' increased from 120 :CE_points: ➡ 125 :CE_points: points: Achievements '∀NOTHER ONE', and '∀DVENTED' removed New Primary Objective '∀WOKEN' added: 30 points :CE_points: Clear the Pandemonic Nightmare stage, and clear Hymeno Striker on AKASCHIC+RM difficulty.")
    embed.set_thumbnail(url=ce_hex_icon)
    embed.set_image(url="https://media.discordapp.net/attachments/1128742486416834570/1133903990090895440/image.png?width=1083&height=542")
    embed.set_author(name="Challenge Enthusiasts", icon_url="https://cdn.akamai.steamstatic.com/steamcommunity/public/images/apps/504230/04cb7aa0b497a3962e6b1655b7fd81a2cc95d18b.jpg")

    return await interaction.followup.send(embed=embed)





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
    with open('Jasons/users2.json', 'r') as dbU :
        database_user = json.load(dbU)

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
    with open('Jasons/users2.json', 'w') as f :
        json.dump(database_user, f, indent=4)

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
        icon_url=ce_james_icon)
    embed.set_thumbnail(url=interaction.user.avatar)

    registered_role = discord.utils.get(interaction.guild.roles, name = "registered")
    #await interaction.user.add_roles(registered_role)

    # Send a confirmation message
    await interaction.followup.send(embed=embed)




@tree.command(name="update", description="Update your stats in the CE Assistant database.", guild=discord.Object(id=guild_ID))
async def update(interaction : discord.Interaction) :

    # Defer the message
    await interaction.response.defer()

    log_channel = client.get_channel(1141886539157221457)
    casino_channel = client.get_channel(811286469251039333)

    str = await update_p(interaction.user.id, log_channel, casino_channel)

    if str == "Unregistered" : return await interaction.followup.send("You have not registered. Please use /register with the link to your CE page.")
    elif(str == "Updated") :
        # Create confirmation embed
        embed = discord.Embed(
            title="Updated!",
            color=0x000000,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="Information", value=f"Your information has been updated in the CE Assistant database.")
        embed.set_author(name="Challenge Enthusiasts", url="https://example.com")
        embed.set_footer(text="CE Assistant",
            icon_url=ce_james_icon)
        embed.set_thumbnail(url=interaction.user.avatar)

        # Send a confirmation message
        await interaction.followup.send(embed=embed)


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
    await message.edit(embed=embed)

    # and send a response to the original interaction
    await interaction.followup.send("worked", ephemeral=True)

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
    with open('Jasons/users2.json', 'r') as f:
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
    await interaction.followup.send('You are eligible to reroll {}.'.format(event))

    # set up confirmation embed
    confirm_embed = discord.Embed(
        title="Are you sure?",
        timestamp=datetime.datetime.now(),
        description="You are asking to reroll {}. Your game(s) will switch from {} to other game(s).".format(event, database_user[user_name]["Current Rolls"][roll_num]["Games"])
        + " You will not recieve any additional time to complete this roll - and your deadline is still <t:{}>.".format(database_user[user_name]["Current Rolls"][roll_num]["End Time"])
    )

    # add buttons


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

    

# ----------------------------------- LOG IN ----------------------------
@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=guild_ID))
    print("Ready!")
    get_tasks(client)
    await master_loop.start(client)

client.run(discord_token)
