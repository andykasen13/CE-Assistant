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
from Web_Interaction.scraping import all_game_data, get_achievements, get_games, get_completion_data


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

    view = discord.ui.View(timeout=600)
    games = []
    embeds = []
    genres = ["Action", "Arcade", "Bullet Hell", "First-Person", "Platformer", "Strategy"]

    # find the location of the user
    with open('Jasons/users2.json', 'r') as u2:
        userInfo = json.load(u2)
    i = 0
    target_user = ""
    for current_user in userInfo :
        if(userInfo[current_user]["discord_ID"] == interaction.user.id) :
            target_user = current_user
            break
    
    if(target_user == "") :
        return await interaction.followup.send("You are not registered in the CE Assistant database. Please contact Andy for support.")

    with open('Jasons/database_tier.json', 'r') as dB :
        database_tier = json.load(dB)
    
    with open('Jasons/database_name.json', 'r') as dBN :
        database_name = json.load(dBN)
    
    # if(event in list(users[target_user]['cooldowns'])) :
    #     return await interaction.response.followup(embed=discord.Embed(title="you are on cooldown"))

    for eventInfo in userInfo[target_user]['current_rolls'] :
        if(eventInfo['event_name'] == event) : return await interaction.followup.send(embed=discord.Embed(title="You are already participating in this event!"))
    


    def get_rollable_game(avg_completion_time_limit, price_limit, tier_number, specific_genre = "any") :
        returned_game = ""
        rollable = False
        while not rollable :
            # ----- Grab random game -----
            # (Genre not given)
            if(specific_genre == "any") :
                print("No genre specified.")
                # ----- Pick a random number -----
                random_num = -1
                for genre in genres :
                    random_num += len(database_tier[tier_number][genre]) 
                random_num = random.randint(0, random_num)

                # ----- Determine genre based on number -----
                for genre in genres :
                    if(random_num < len(database_tier[tier_number][genre])) :
                        # ----- Pick the game -----
                        returned_game = database_tier[tier_number][genre][random_num]
                        print("Chosen genre: " + genre)
                        break
                    # ----- Move to the next genre -----
                    else : random_num -= len(database_tier[tier_number][genre])
            # (Genre given)
            elif type(specific_genre) == str:
                print(f"Specified genre: {specific_genre}.")
                random_num = random.randint(0,len(database_tier[tier_number][specific_genre]))
                returned_game = database_tier[tier_number][specific_genre][random_num]
            # (Genres given)
            elif type(specific_genre) == list :
                print(f"Genres specified: {str(specific_genre)}")
                # ----- Pick a random number -----
                random_num = -1
                for genre in specific_genre :
                    random_num += len(database_tier[tier_number][genre])
                random_num = random.randint(0, random_num)

                # ----- Determine genre based on number -----
                for genre in specific_genre :
                    if(random_num < len(database_tier[tier_number][genre])) :
                        # ----- Pick the game -----
                        returned_game = database_tier[tier_number][genre][random_num]
                        print("Chosen genre: " + genre)
                        break
                    # ----- Move to the next genre -----
                    else : random_num -= len(database_tier[tier_number][genre])

            # ----- Log it in the console -----
            print(f"Seeing if {returned_game} is rollable...")
            gameID = int(database_name[returned_game]["Steam ID"])

            # ----- Grab Steam JSON file -----
            payload = {'appids': gameID, 'cc' : 'US'}
            response = requests.get("https://store.steampowered.com/api/appdetails?", params = payload)
            jsonData = json.loads(response.text)

            # ----- Determine game price -----
            if(jsonData[str(gameID)]['data']['is_free']) : 
                gamePrice = 0
            else: 
                gamePrice = float(str(jsonData[str(gameID)]['data']['price_overview']['final_formatted'])[1::])
            
            # ----- Grab SteamHunters completion time -----
            completion_time = get_completion_data(gameID)
            if(completion_time == "none") : continue
            else : completion_time = int(completion_time)

            print(f"Game price is {gamePrice}... {gamePrice < price_limit}")
            print(f"Game completion time is {completion_time}... {completion_time < avg_completion_time_limit}")

            # ----- Check to see if rollable -----
            if(gamePrice < price_limit and completion_time < avg_completion_time_limit) :
                rollable = True
            print("\n")

        print(f"{returned_game} is rollable.")
        print("\n")
        return returned_game

    def create_multi_embed(event_name, time_limit, game_list, cooldown_time) :
        # ----- Set up initial embed -----
        embeds = []
        embeds.append(discord.Embed(
            color = 0x000000,
            title=event_name,
            timestamp=datetime.datetime.now()
        ))
        embeds[0].set_footer(text=f"Page 1 of {str(len(game_list) + 1)}")
        embeds[0].set_author(name="Challenge Enthusiasts")

        # ----- Add all games to the embed -----
        games_value = ""
        i = 1
        for selected_game in games:
            games_value += "\n" + str(i) + ". " + selected_game
            i+=1
        embeds[0].add_field(name="Rolled Games", value = games_value)

        # ----- Display Roll Requirements -----
        embeds[0].add_field(name="Roll Requirements", value =
            f"You have two weeks to complete " + embeds[0].title + "."
            + "\nMust be completed by <t:" + str(int(time.mktime((datetime.datetime.now()+timedelta(time_limit)).timetuple())))
            + f">\n{event_name} has a cooldown time of {cooldown_time} days.", inline=False)
        embeds[0].timestamp = datetime.datetime.now()
        embeds[0].set_thumbnail(url = interaction.user.avatar)
        
        # ----- Create the embeds for each game -----
        page_limit = len(game_list) + 1
        i=0
        for selected_game in games :
            total_points = 0
            embeds.append(getEmbed(selected_game, interaction.user.id))
            embeds[i+1].add_field(name="Rolled by", value = "<@" + str(interaction.user.id) + ">", inline=True)
            embeds[i+1].set_footer(text=(f"Page {i+2} of {page_limit}"),
                                   icon_url="https://cdn.discordapp.com/attachments/639112509445505046/891449764787408966/challent.jpg")
            embeds[i+1].set_author(name="Challenge Enthusiasts")
            embeds[i+1].set_thumbnail(url=interaction.user.avatar)
            for objective in database_name[selected_game]["Primary Objectives"] :
                total_points += int(database_name[selected_game]["Primary Objectives"][objective]["Point Value"])
            embeds[i+1].add_field(name="CE Status", value=f"{total_points} Points", inline=True)
            embeds[i+1].add_field(name="CE Owners", value="[insert]", inline=True)
            embeds[i+1].add_field(name="CE Completions", value="[insert]", inline=True)
            i+=1
        
        return embeds # Set the embed to send as the first one

    #  -------------------------------------------- One Hell of a Day  --------------------------------------------
    if event == "One Hell of a Day" :
        # Get one random (rollable) game in Tier 1, non-genre specific
        games.append(get_rollable_game(10, 10, "Tier 1"))

        # Create the embed
        embed = getEmbed(games[0], interaction.user.id)
        embed.add_field(name="Roll Requirements", value = 
            "You have one day to complete " + embed.title + "."    
            + "\nMust be completed by <t:" + str(int(time.mktime((datetime.datetime.now()+timedelta(1)).timetuple())))
            + ">\nOne Hell of a Day has a two week cooldown."
            + "\nCooldown ends on <t:" + str(int(time.mktime((datetime.datetime.now()+timedelta(14)).timetuple())))
            + ">\n[insert link to cedb.me page]", inline=False)
        embed.set_author(name="ONE HELL OF A DAY", url="https://example.com")

    # -------------------------------------------- Two Week T2 Streak --------------------------------------------
    elif event == "Two Week T2 Streak" :
        # two random t2s
        print("received two week t2 streak")

        # ----- Grab two random games -----
        games.append(get_rollable_game(40, 20, "Tier 2"))
        genres.remove(database_name[games[0]]["Genre"])
        games.append(get_rollable_game(40, 20, "Tier 2", genres))
        
        # ----- Get all the embeds -----s
        embeds = create_multi_embed("Two Week T2 Streak", 14, games, 0)
        embed = embeds[0]

        await get_buttons(view, embeds) # Create buttons

    # -------------------------------------------- One Hell of a Week --------------------------------------------
    elif event == "One Hell of a Week" : 
        # t1s from each category
        print("Recieved request for One Hell of a Week")

        # ----- Grab all the games -----
        genres.remove("Strategy")
        i = 0
        while i < 5:
            games.append(get_rollable_game(10, 10, "Tier 1", genres))
            genres.remove(database_name[games[i]]["Genre"])
            i+=1

        # ----- Get all the embeds -----
        embeds = create_multi_embed("One Hell of a Week", 7, games, 28)       
        embed = embeds[0] # Set the embed to send as the first one
        await get_buttons(view, embeds) # Create buttons

    # -------------------------------------------- One Hell of a Month --------------------------------------------
    elif event == "One Hell of a Month" : 
        # five t1s from each category
        embed = discord.Embed(title=f"you have month")

    # -------------------------------------------- Two "Two Week T2 Streak" Streak --------------------------------------------
    elif event == "Two 'Two Week T2 Streak' Streak" :
        # four t2s
        print("Recieved request for Two 'Two Week T2 Streak' Streak")

        # ----- Grab all the games -----
        genres.remove("Strategy")
        i=0
        while i < 4:
            games.append(get_rollable_game(40, 20, "Tier 2", genres))
            genres.remove(database_name[games[i]]["Genre"])
            i+=1
        
        # ----- Get all the embeds -----
        embeds = create_multi_embed("Two 'Two Week T2 Streak' Streak", 28, games, 7)
        embed = embeds[0]
        await get_buttons(view, embeds)

    # -------------------------------------------- Never Lucky --------------------------------------------
    elif event == "Never Lucky" :
        # one t3
        games.append(get_rollable_game(40, 20, "Tier 3"))

        # Create the embed
        embed = getEmbed(games[0], interaction.user.id)
        embed.add_field(name="Roll Requirements", value = 
            "There is no time limit on " + embed.title + "."
            + "\nNever Lucky has a one week cooldown."
            + "\nCooldown ends on <t:" + str(int(time.mktime((datetime.datetime.now()+timedelta(7)).timetuple())))
            + f">\nhttps://cedb.me/game/{database_name[embed.title]['CE ID']}/", inline=False)
        embed.set_author(name="Never Lucky", url="https://example.com")

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

    # append the roll to the user's current rolls array
    userInfo[target_user]["current_rolls"].append({"event_name" : event, 
                                                  "end_time" : "" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                  "games" : games})

    # dump the info
    with open('Jasons/users2.json', 'w') as f :
        json.dump(userInfo, f, indent=4)
    # ---------------------------------------------
    # ------------------ Co-ops -------------------
    # Destiny Alignment: You and another player roll games
    #   from the other's library, and both must complete them
    # Soul Mates: You and another player agree on a tier, 
    #   and then a game is rolled (time limit based on tier)

    

    # Finally, send the embed
    await interaction.followup.send(embed=embed, view=view)
    print("Sent information on rolled game: " + str(games) + "\n")


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
def scrape_thread_call(client):
    get_games(client)

@tree.command(name="scrape", description="run through each game in the CE database and grab the corresponding data", guild=discord.Object(id=guild_ID))
async def scrape(interaction):
    await interaction.response.send_message("scraping...")
    await scrape_thread_call(client) #all_game_data(client)
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
    embed.set_author(name="Requested Steam info on '" + game_name + "'")
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

    with open('Jasons/database_name.json', 'r') as dB :
        database_name = json.load(dB)
    
    if(game_name in list(database_name)) : 
        correct_app_id = database_name[game_name]["Steam ID"]
        print(f"found {game_name} with app id {correct_app_id} in local json file :)")
    else :
        print(f"couldn't find {game_name} in local json file, searching steam :(")
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
    
    embed.set_author(name="Challenge Enthusiasts", url="https://example.com")
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
    await interaction.response.defer(ephemeral=True)

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
    await interaction.followup.send(embed=embed, view=view, ephemeral=True)


# --------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------TEST COMMAND------------------------------------------------------------- #
# --------------------------------------------------------------------------------------------------------------------------- #

@tree.command(name="test", description="test", guild=discord.Object(id=guild_ID))
async def test(interaction) :
    return

# ----------------------------------- LOG IN ----------------------------
@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=guild_ID))
    print("Ready!")
    await loop.start(client)

client.run(discord_token)