# ---------- time imports -----------
import asyncio
from datetime import datetime, timedelta
import datetime
import functools
import time
import typing

# ----------- discord imports ---------
import discord
from discord import app_commands
import random
from typing import Literal

# ----------- json imports ------------
import json
import psutil

# --------- web imports ---------
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# --------- other file imports ---------
from Web_Interaction.curator import loop
from Web_Interaction.scraping import get_achievements, get_games

# --------------------------------------------------- ok back to the normal bot ----------------------------------------------
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

intents.message_content = True

# Grab information from json file
with open('Jasons/secret_info.json') as f :
    localJSONData = json.load(f)

discord_token = localJSONData['discord_token']
guild_ID = localJSONData['guild_ID']

# Add the guild ids in which the slash command will appear. 
# If it should be in all, remove the argument, but note that 
# it will take some time (up to an hour) to register the command 
# if it's for all guilds.
    

# ------------------------------------------------------------------------------------------------------------------------------ #
# ---------------------------------------------------------HELP COMMAND--------------------------------------------------------- #
# ------------------------------------------------------------------------------------------------------------------------------ #
@tree.command(name="help", description="help", guild=discord.Object(id=guild_ID))
async def help(interaction) :
    # Defer the message
    await interaction.response.defer()

    # Create the view (will be used for buttons later)
    view = discord.ui.View(timeout=600)

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


# ------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------ROLL COMMAND --------------------------------------------------------- # 
# ------------------------------------------------------------------------------------------------------------------------------- #
events = Literal["One Hell of a Day", "One Hell of a Week", "One Hell of a Month", "Two Week T2 Streak", 
          "Two 'Two Week T2 Streak' Streak", "Never Lucky", "Triple Threat", "Let Fate Decide", "Fourward Thinking",
          "Russian Roulette"]

@tree.command(name="roll", description="Participate in Challenge Enthusiast roll events!", guild=discord.Object(id=guild_ID))
async def roll_command(interaction, event: events) -> None:
    await interaction.response.defer()

    # Open file
    tier_one_file = open("faket1list.txt", "r")
    data = tier_one_file.read()
    data_into_list = data.split("\n")
    tier_one_file.close()

    view = discord.ui.View(timeout=600)
    game = "error"

    #  -------------------------------------------- One Hell of a Day  --------------------------------------------
    if event == "One Hell of a Day" :
        # Pick a random game from the list
        game = random.choice(data_into_list)
        print("Rolled game: " + game)

        # Create the embed
        embed = getEmbed(game, interaction.user.id)
        embed.add_field(name="Roll Requirements", value = 
            "You have one day to complete " + embed.title + "."    
            + "\nMust be completed by <t:" + str(int(time.mktime((datetime.datetime.now()+timedelta(1)).timetuple())))
            + ">\nOne Hell of a Day has a two week cooldown."
            + "\nCooldown ends on <t:" + str(int(time.mktime((datetime.datetime.now()+timedelta(14)).timetuple())))
            + ">\n[insert link to cedb.me page]", inline=False)
        embed.set_author(name="ONE HELL OF A DAY", url="https://example.com")

    # -------------------------------------------- Two week t2 streak --------------------------------------------
    elif event == "Two Week T2 Streak" :
        # two random t2s
        print("received two week t2 streak")
        games = []
        embeds = []

        # ----- Grab two random games -----
        i=0
        while(i != 2) :
            games.append(random.choice(data_into_list))
            i += 1
        game = games[0] + " and " + games[1]

        # ----- Create opening embed -----
        embeds.append(discord.Embed(
            color=0x000000,
            title="Two Week T2 Streak",
            description="games lol"))
        embeds[0].set_footer(text="Page 1 of 3")
        i=1
        for gamer in games:
            embeds[0].description += "\n" + str(i) + ". " + gamer
            i+=1
        embeds[0].add_field(name="Roll Requirements", value =
            "You have two weeks to complete " + embeds[0].title + "."
            + "\nMust be completed by <t:" + str(int(time.mktime((datetime.datetime.now()+timedelta(14)).timetuple())))
            + ">\nTwo Week T2 Streak has no cooldown."
            + "\n[insert link to cedb.me page]", inline=False)
        embeds[0].set_author(name = "TWO WEEK T2 STREAK", url="https://example.com")

        # ----- Create the embeds for each game -----
        #currentPage = 1
        page_limit = 3
        i=0
        for gamer in games :
            embeds.append(getEmbed(gamer, interaction.user.id))
            embeds[i+1].set_footer(text=(f"Page {i+2} of {page_limit}"))
            embeds[i+1].set_author(name="TWO WEEK T2 STREAK")
            i+=1

        # ----- Set the embed to send as the first one ------
        embed = embeds[0]
       
        # ----- Create buttons -----
        await get_buttons(view, embeds)



    # -------------------------------------------- One Hell of a Week --------------------------------------------
    elif event == "One Hell of a Week" :
        # t1s from each category
        embed = discord.Embed(title=f"you ave week")

    # -------------------------------------------- One Hell of a Month --------------------------------------------
    elif event == "One Hell of a Month" : 
        # five t1s from each category
        embed = discord.Embed(title=f"you have month")

    # -------------------------------------------- Two "Two Week T2 Streak" Streak --------------------------------------------
    elif event == "Two 'Two Week T2 Streak' Streak" :
        # four t2s
        embed = discord.Embed(title=("two two week t2 streak streak"))

    # -------------------------------------------- Never Lucky --------------------------------------------
    elif event == "Never Lucky" :
        # one t3
        embed = discord.Embed(title=("never lucky"))

    # -------------------------------------------- Triple Threat --------------------------------------------
    elif event == "Triple Threat" :
        # three t3s
        embed = discord.Embed(title=("triple threat"))
         
    # -------------------------------------------- Let Fate Decide --------------------------------------------
    elif event == "Let Fate Decide" :
        # one t4
        embed = discord.Embed(title=("let fate decide"))

    # -------------------------------------------- Fourward Thinking --------------------------------------------
    elif event == "Fourward Thinking" :
        # idk
        embed = discord.Embed(title=("fourward thinking"))

    # -------------------------------------------- Russian Roulette --------------------------------------------
    elif event == "Russian Roulette" :
        # choose six t5s and get one at random
        embed = discord.Embed(title=("russian roulette"))

    # -------------------------------------------- kill yourself --------------------------------------------
    else : embed=discord.Embed(title=(f"'{event}' is not a valid event."))

    # open the json file
    with open('Jasons/users.json', 'r') as f :
        userInfo = json.load(f)
    
    # find the location of the user
    i = 0
    while userInfo['users'][i]['ID'] != interaction.user.id :
        i += 1
        
    # append the roll to the user's current rolls array
    # userInfo['users'][i]['current_rolls'].append({"event_name" : "One Hell of a Day", 
    #                                               "games" : [{"name" : embed.title, "completed" : False}], 
    #                                               "end_time" : "" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

    # dump the info
    with open('Jasosns/users.json', 'w') as f :
        json.dump(userInfo, f, indent=4)
    # ---------------------------------------------
    # ------------------ Co-ops -------------------
    # Destiny Alignment: You and another player roll games
    #   from the other's library, and both must complete them
    # Soul Mates: You and another player agree on a tier, 
    #   and then a game is rolled (time limit based on tier)

    # Finally, send the embed
    await interaction.followup.send(embed=embed, view=view)
    print("Sent information on rolled game: " + game)


# -------------------------------------------------------------------------------------------------- #
# -------------------------------------------- BUTTONS --------------------------------------------- #
# -------------------------------------------------------------------------------------------------- #

async def get_buttons(view, embeds):
    currentPage = 1
    page_limit = len(embeds)
    buttons = [discord.ui.Button(label=">", style=discord.ButtonStyle.green, disabled=False), discord.ui.Button(label="<", style=discord.ButtonStyle.red, disabled=True)]
    view.add_item(buttons[1])
    view.add_item(buttons[0])

    async def hehe(interaction):
        return await callback(interaction, num=1)

    async def haha(interaction):
        return await callback(interaction, num=-1)

    async def callback(interaction, num):
        nonlocal currentPage, view, embeds, page_limit, buttons
        currentPage+=num
        if(currentPage >= page_limit) :
            buttons[0].disabled = True
        else : buttons[0].disabled = False
        if(currentPage <= 1) :
            buttons[1].disabled = True
        else : buttons[1].disabled = False
        await interaction.response.edit_message(embed=embeds[currentPage-1], view=view)

    buttons[0].callback = hehe
    buttons[1].callback = haha


# ----------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------- CHECK_ROLLS COMMAND ------------------------------------------------------ # 
# ----------------------------------------------------------------------------------------------------------------------------------- #
@tree.command(name="check_rolls", description="Check the active rolls of anyone on the server", guild=discord.Object(id=guild_ID))
async def checkRolls(interaction, user: discord.Member=None) :
    # defer the message
    await interaction.response.defer()

    # if no user is provided default to sender
    if user is None :
        target_user = interaction.user

    #open the json file and get the data
    with open('Jasons/users2.json', 'r') as f :
        userInfo = json.load(f)

    with open('Jasons/database_name.json', 'r') as g :
        database_name_info = json.load(g)

    # iterate through the json file until you find the
    # designated user
    steam_user_name = ""
    for user_name in list(userInfo) :
        if(userInfo[user_name]["discord_ID"] == target_user.id) :
            steam_user_name = user_name
            break
    
    if(steam_user_name == "") : return await interaction.response.followup("This user does not exist.")
    print(steam_user_name)

    current_roll_str = get_roll_string(userInfo, steam_user_name, database_name_info, target_user, 'current_rolls')
    completed_roll_str = get_roll_string(userInfo, steam_user_name, database_name_info, target_user, 'completed_rolls')
    
    # make the embed that you're going to send
    embed = discord.Embed(colour=0x000000, timestamp=datetime.datetime.now())
    embed.add_field(name="User", value = "<@" + str(target_user.id) + ">", inline=False)
    embed.add_field(name="Current Rolls", value=current_roll_str, inline=False)
    embed.add_field(name="Completed Rolls", value=completed_roll_str, inline=False)
    embed.set_thumbnail(url=target_user.avatar.url)
    embed.set_footer(text="CE Assistant",
        icon_url="https://cdn.discordapp.com/attachments/639112509445505046/891449764787408966/challent.jpg")

    # send the embed
    await interaction.followup.send(embed=embed)

# ---------------------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------------- ROLL STRING ---------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
def get_roll_string(userInfo, steam_user_name, database_name_info, target_user, x) :
    # set up this bullshit
    roll_string = ""

    # grab all current rolls
    for x in userInfo[steam_user_name][x] :
        end_time = time.mktime(datetime.datetime.strptime(str(x['end_time']), "%Y-%m-%d %H:%M:%S").timetuple())
        roll_string = roll_string + "- __" + x['event_name'] + "__ (complete by <t:" + str(int(end_time)) + ">):\n"
        gameNum = 1
        for game in x['games'] : # Iterate through all games in the roll event
            game_info = database_name_info[game] # Grab the dictionary containing all info about that game
            game_title = game # Set the game title
            roll_string += "  " + str(gameNum) + ". "+ str(game_title) + "\n" # Add the game number and the game title to the string
            for objective_title in game_info["Primary Objectives"] : # Iterate through all of the games' objectives
                objective_info = (game_info["Primary Objectives"][objective_title]) # Grab the dictionary containing all info about that objective
                objective_point_value = objective_info["Point Value"] # Set the point value
                roll_string += "    - " + str(objective_title) + " (" + str(objective_point_value) + ")\n" # Update the roll string
            gameNum += 1 # Add to the gameNum
    
    # account for no current rolls
    if(roll_string == "") :
        if(x == 'current_rolls') : roll_string = f"{target_user.name} has no current rolls."
        elif(x == 'completed_rolls') : roll_string = f"{target_user.name} has no completed rolls."

    return roll_string

# ---------------------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------------- THREADING ------------------------------------------------------------ #
# ---------------------------------------------------------------------------------------------------------------------------------- #

def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper


# ---------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------- SCRAPING --------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #

@to_thread
def scrape_thread_call():
    get_games()

@tree.command(name="scrape", description="run through each game in the CE database and grab the corresponding data", guild=discord.Object(id=guild_ID))
async def scrape(interaction):
    await interaction.response.send_message("scraping...")
    await scrape_thread_call()
    await interaction.channel.send("scraped")


# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------- COMMAND RESOURCE TESTING ---------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #

@tree.command(name="resource_testing", description="runs function while recording ram and time", guild=discord.Object(id=guild_ID))
async def resource_testing(function):
    ram_usage = []
    time = []
    ram_before = psutil.virtual_memory()[3]/1000000000
    time_before = datetime.datetime.now()
    await function
    ram_after = psutil.virtual_memory()[3]/1000000000
    time_after = datetime.datetime.now()
    ram_usage.append(ram_after-ram_before)
    time.append((time_after-time_before).total_seconds())

    print('ram usage (GB): ' + str(sum(ram_usage)/len(ram_usage)))
    print('time taken (s):' + str(sum(time)/len(time)))


# ----------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------- STEAM TEST COMMAND ------------------------------------------------------ #
# ----------------------------------------------------------------------------------------------------------------------------------- #

@tree.command(name="steam_game", description="Get information on any steam game", guild=discord.Object(id=guild_ID))
async def steam_command(interaction, game_name: str):

    # Log the command
    print("Recieved steam_game command with parameter: " + game_name + ".")

    # Defer the interaction
    await interaction.response.defer()

    # Get the embed
    embed = getEmbed(game_name, interaction.user.id)
    embed.set_author(name="REQUESTED STEAM GAME INFO ON '" + game_name + "'")
    embed.remove_field(1)
    embed.add_field(name="Requested by", value="<@" + str(interaction.user.id) + ">", inline=True)
    embed.add_field(name="CE Status", value="Not on CE / x Points", inline=True)
    embed.add_field(name="CE Owners", value="[insert]", inline=True)
    embed.add_field(name="CE Completions", value="[insert]", inline=True)

    # Finally, send the embed
    await interaction.followup.send(embed=embed)

    # And log it
    print("Sent information on requested game " + game_name + "\n")


# ----------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------- GET EMBED FUNCTION ------------------------------------------------------ #
# ----------------------------------------------------------------------------------------------------------------------------------- #
def getEmbed(game_name, authorID):

    #TODO add error exceptions
    #TODO turn this into a class with getters and setters for wider versatility

    game_word_lst = game_name.split(" ")
    for name in game_word_lst:
        if len(name) != len(name.encode()):
            game_word_lst.pop(game_word_lst.index(name))


    searchable_game_name = " ".join(game_word_lst)

    payload = {'term': searchable_game_name, 'f': 'games', 'cc' : 'us', 'l' : 'english'}
    response = requests.get('https://store.steampowered.com/search/suggest?', params=payload)

    divs = BeautifulSoup(response.text, features="html.parser").find_all('div')
    ass = BeautifulSoup(response.text, features="html.parser").find_all('a')
    options = []
    for div in divs:
        try:
            if div["class"][0] == "match_name":
                options.append(div.text)
        except:
            continue
    

        correct_app_id = ass[0]['data-ds-appid']

    for i in range(0, len(options)):
        if game_name == options[i]:
            correct_app_id = ass[i]['data-ds-appid']

# --- DOWNLOAD JSON FILE ---

    # Open and save the JSON data
    payload = {'appids': correct_app_id, 'cc' : 'US'}
    response = requests.get("https://store.steampowered.com/api/appdetails?", params = payload)
    jsonData = json.loads(response.text)
    
    # Save important information
    gameTitle = jsonData[correct_app_id]['data']['name']
    imageLink = jsonData[correct_app_id]['data']['header_image']
    gameDescription = jsonData[correct_app_id]['data']['short_description']
    if(jsonData[correct_app_id]['data']['is_free']) : 
        gamePrice = "Free"
    else: gamePrice = jsonData[correct_app_id]['data']['price_overview']['final_formatted']
    gameNameWithLinkFormat = game_name.replace(" ", "_")

# --- CREATE EMBED ---

    # and create the embed!
    embed = discord.Embed(title=f"{gameTitle}",
        url=f"https://store.steampowered.com/app/{correct_app_id}/{gameNameWithLinkFormat}/",
        description=(f"{gameDescription}"),
        colour=0x000000,
        timestamp=datetime.datetime.now())

    embed.add_field(name="Price", value = gamePrice, inline=True)
    embed.add_field(name="User", value = "<@" + str(authorID) + ">", inline=True)
    
    embed.set_author(name="[INSERT ROLL EVENT NAME HERE]", url="https://example.com")
    embed.set_image(url=imageLink)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/639112509445505046/891449764787408966/challent.jpg")
    embed.set_footer(text="CE Assistant",
        icon_url="https://cdn.discordapp.com/attachments/639112509445505046/891449764787408966/challent.jpg")
    return embed


# ---------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------- COLORS ----------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
@tree.command(name="set_color", description="Set your name color to any color you've unlocked!", guild=discord.Object(id=guild_ID))
async def color(interaction) :
    await interaction.response.defer()

    ex_rank_role = discord.utils.get(interaction.guild.roles, name = "EX RANK")
    sss_rank_role = discord.utils.get(interaction.guild.roles, name = "SSS RANK")
    ss_rank_role = discord.utils.get(interaction.guild.roles, name = "SS RANK")
    s_rank_role = discord.utils.get(interaction.guild.roles, name = "S RANK")
    a_rank_role = discord.utils.get(interaction.guild.roles, name = "A RANK")
    b_rank_role = discord.utils.get(interaction.guild.roles, name = "B RANK")
    c_rank_role = discord.utils.get(interaction.guild.roles, name = "C RANK")
    d_rank_role = discord.utils.get(interaction.guild.roles, name = "D RANK")

    black_role = discord.utils.get(interaction.guild.roles, name = "Black")
    red_role = discord.utils.get(interaction.guild.roles, name = "Red")
    yellow_role = discord.utils.get(interaction.guild.roles, name = "Yellow")
    orange_role = discord.utils.get(interaction.guild.roles, name = "Orange")
    purple_role = discord.utils.get(interaction.guild.roles, name = "Purple")
    blue_role = discord.utils.get(interaction.guild.roles, name = "Blue")
    green_role = discord.utils.get(interaction.guild.roles, name = "Green")
    brown_role = discord.utils.get(interaction.guild.roles, name = "Brown")  


    view = discord.ui.View(timeout=60)

    black_button = (discord.ui.Button(label="⚫", disabled=(not ex_rank_role in interaction.user.roles)))
    red_button = discord.ui.Button(label = "🔴", disabled = (not sss_rank_role in interaction.user.roles
                                                             and not ex_rank_role in interaction.user.roles))
    yellow_button = (discord.ui.Button(label="🟡", style=discord.ButtonStyle.gray, disabled=(not ss_rank_role in interaction.user.roles
                                                                                              and not sss_rank_role in interaction.user.roles
                                                                                              and not ex_rank_role in interaction.user.roles)))  
    orange_button = (discord.ui.Button(label="🟠", style=discord.ButtonStyle.gray, disabled=(not s_rank_role in interaction.user.roles
                                                                                              and not ss_rank_role in interaction.user.roles
                                                                                              and not sss_rank_role in interaction.user.roles
                                                                                              and not ex_rank_role in interaction.user.roles)))
    purple_button = (discord.ui.Button(label="🟣", style=discord.ButtonStyle.gray, disabled=(not a_rank_role in interaction.user.roles
                                                                                              and not s_rank_role in interaction.user.roles
                                                                                              and not ss_rank_role in interaction.user.roles
                                                                                              and not sss_rank_role in interaction.user.roles
                                                                                              and not ex_rank_role in interaction.user.roles)))
    blue_button = (discord.ui.Button(label="🔵", style=discord.ButtonStyle.gray, disabled=(not b_rank_role in interaction.user.roles
                                                                                               and not a_rank_role in interaction.user.roles
                                                                                               and not s_rank_role in interaction.user.roles
                                                                                               and not ss_rank_role in interaction.user.roles
                                                                                               and not sss_rank_role in interaction.user.roles
                                                                                               and not ex_rank_role in interaction.user.roles)))
    green_button = (discord.ui.Button(label="🟢", style=discord.ButtonStyle.gray, disabled=(not c_rank_role in interaction.user.roles
                                                                                              and not b_rank_role in interaction.user.roles
                                                                                              and not a_rank_role in interaction.user.roles
                                                                                              and not s_rank_role in interaction.user.roles
                                                                                              and not ss_rank_role in interaction.user.roles
                                                                                              and not sss_rank_role in interaction.user.roles
                                                                                              and not ex_rank_role in interaction.user.roles)))
    brown_button = (discord.ui.Button(label="🟤", style=discord.ButtonStyle.gray, disabled=(not d_rank_role in interaction.user.roles
                                                                                             and not c_rank_role in interaction.user.roles
                                                                                             and not b_rank_role in interaction.user.roles
                                                                                             and not a_rank_role in interaction.user.roles
                                                                                             and not s_rank_role in interaction.user.roles
                                                                                             and not ss_rank_role in interaction.user.roles
                                                                                             and not sss_rank_role in interaction.user.roles
                                                                                             and not ex_rank_role in interaction.user.roles)))

    
    async def black_callback(interaction) : return await assign_role(interaction, black_role)
    async def red_callback(interaction) : return await assign_role(interaction, red_role)
    async def yellow_callback(interaction) : return await assign_role(interaction, yellow_role)
    async def orange_callback(interaction) : return await assign_role(interaction, orange_role)
    async def purple_callback(interaction) : return await assign_role(interaction, purple_role)
    async def blue_callback(interaction) : return await assign_role(interaction, blue_role)
    async def green_callback(interaction) : return await assign_role(interaction, green_role)
    async def brown_callback(interaction) : return await assign_role(interaction, brown_role)

    black_button.callback = black_callback
    red_button.callback = red_callback
    yellow_button.callback = yellow_callback
    orange_button.callback = orange_callback
    purple_button.callback = purple_callback
    blue_button.callback = blue_callback
    green_button.callback = green_callback
    brown_button.callback = brown_callback

    view.add_item(black_button)
    view.add_item(red_button)
    view.add_item(yellow_button)
    view.add_item(orange_button)
    view.add_item(purple_button)
    view.add_item(blue_button)
    view.add_item(green_button)
    view.add_item(brown_button)

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
        if(brown_role in interaction.user.roles and not(role == brown_button)) : await interaction.user.remove_roles(brown_role)


        return await interaction.response.edit_message(embed=discord.Embed(title = f"You have recieved the {role.name} role!", color=role.color))
        
    

    embed = discord.Embed(title="COLORS", description="choose your colors wisely.")

    await interaction.followup.send(embed=embed, view=view)

# --------------------------------------------------- ASSIGN ROLE COMMAND -------------------------------------------------- #




# --------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------TEST COMMAND------------------------------------------------------------- #
# --------------------------------------------------------------------------------------------------------------------------- #

@tree.command(name="open", description="test", guild=discord.Object(id=guild_ID))
async def test(interaction) :
    return

# ----------------------------------- LOG IN ----------------------------
@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=guild_ID))
    print("Ready!")
    await loop.start(client)

client.run(discord_token)