# This example requires the 'message_content' intent.

from asyncio import Event, wait
from datetime import datetime, timedelta
import subprocess
import discord
from discord import app_commands

import requests
import random
import json
from steam.webapi import WebAPI
from steam.steamid import SteamID
import steamctl
from steam.client import SteamClient as SClient
steamClient = SClient()

from selenium import webdriver
from bs4 import BeautifulSoup

import json 

# --------------------------------------------------- ok back to the normal bot ----------------------------------------------
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

intents.message_content = True

# Grab information from json file
with open('useful.json') as f :
    localJSONData = json.load(f)

discordToken = localJSONData['discordToken']
guildID = localJSONData['guildID']


# Add the guild ids in which the slash command will appear. 
# If it should be in all, remove the argument, but note that 
# it will take some time (up to an hour) to register the command 
# if it's for all guilds.

# -------------------------------------------------------- #
# --------------------ROLL COMMAND ----------------------- # 
# -------------------------------------------------------- #

@tree.command(name="roll", description="Participate in Challenge Enthusiast roll events!", guild=discord.Object(id=guildID))
async def roll_command(interaction, event: str) -> None:

    await interaction.response.defer()


    # Open file
    tier_one_file = open("faket1list.txt", "r")
    data = tier_one_file.read()
    data_into_list = data.split("\n")
    #print(data_into_list)
    tier_one_file.close()

    # -------------- One Hell of a Day ----------------
    if event == "one hell of a day" :
        # Pick a random game from the list
        # getTier(1)
        game = random.choice(data_into_list)
        print("Rolled game: " + game)

        embed = getEmbed(game, interaction.user.id)

        with open('info.json', 'r') as f :
            userInfo = json.load(f)
        
        i = 0
        while userInfo['users'][i]['ID'] != interaction.user.id :
            i += 1
        
        # userInfo['users'][i]['current_rolls'].append({"event_name" : "One Hell of a Day", "games" : [{"name" : game, "completed" : False}], "end_time" : "" + datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

        with open('info.json', 'w') as f :
            json.dump(userInfo, f, indent=4)

        embed.add_field(name="Roll Requirements", value = 
            "You have one day to complete " + game + "."    
            + "\nMust be completed by " + (datetime.now()+timedelta(1)).strftime("%B %d, %Y at %I:%M:%S %p.") 
            + "\nOne Hell of a Day has two week cooldown."
            + "\nCooldown ends on " + (datetime.now()+timedelta(14)).strftime("%B %d, %Y at %I:%M:%S %p.")
            + "\n[insert link to cedb.me page]", inline=False)
        embed.set_author(name="ONE HELL OF A DAY", url="https://example.com")

        # Finally, send the embed
        await interaction.followup.send(embed=embed)
        print("Sent information on rolled game " + game)

    # -------------- One Hell of a Week ---------------
    elif event == "one hell of a week" :
        await interaction.followup.send(f"you ave week")

    # -------------- One Hell of a Month --------------
    elif event == "one hell of a month" : 
        await interaction.followup.send(f"you have month")

    # -------------- kill yourself --------------------
    else : await interaction.response.send_message(f"jfasdklfhasd")


# -------------------------------------------------------- #
# ----------------MY_ROLLS COMMAND ----------------------- # 
# -------------------------------------------------------- #
@tree.command(name="check_rolls", description="Check the active rolls of anyone on the server", guild=discord.Object(id=guildID))
async def checkRolls(interaction, user: discord.Member) :
    await interaction.response.defer()

    #open the json file and get the data
    with open('info.json', 'r') as f :
        userInfo = json.load(f)

    #iterate through the json file until you find the
    #designated user
    i = 0
    while userInfo['users'][i]['ID'] != user.id :
        if(i + 1 == len(userInfo['users'])) : return await interaction.followup.send("This user does not exist.")
        else: i += 1

    checkrollstr = ""

    # TODO: make sure that if the roll is empty,
    # you don't do all this or it will error a lot!

    # TODO: this is much further down the line but
    # you should debate whether or not it is worth 
    # it to include objectives in this, and if they are, 
    # how to show it.

    #for x in userInfo['users'][i]['current_rolls'] :
    #    checkrollstr = checkrollstr + "-" + userInfo['users'][i]['current_rolls'][x]['event_name'] + ":\n"
    #    for y in userInfo['users'][i]['current_rolls']['games'] :
    #        checkrollstr = checkrollstr + (i+1) + ". " 
    #        + userInfo['users'][i]['current_rolls']['games'][y]['name'] 
    #        + " (completed: " + userInfo['users'][i]['current_rolls']['games'][y]['completed'] + ")\n"

    embed = discord.Embed(
    colour=0x000000,
    timestamp=datetime.now()
    )

    embed.add_field(name="Current Rolls for " + "<@" + user.id + ">", value=checkrollstr, inline=False)

    await interaction.followup.send(embed=embed)




# --------------------------------------------------- #
# --------------- GRABBING TIERS -------------------- #
# --------------------------------------------------- #

def getTier(tierLevel):
    response = requests.get('https://cedb.me/games?tier=t1')
    soup = BeautifulSoup(response.text)
    print(soup.prettify())


    driver = webdriver.Chrome()
    url ='https://cedb.me/games?tier=t1'
    driver.get(url)
    html = driver.page_source

    print(html)

# --------------------------------------------------- #
# ------------- STEAM TEST COMMAND ------------------ #
# --------------------------------------------------- #

@tree.command(name="steam_game", description="Get information on any steam game", guild=discord.Object(id=guildID))
async def steam_command(interaction, game_name: str):

    # Log the command
    print("Recieved steam_game command with parameter: " + game_name + ".")

    # Defer the interaction
    await interaction.response.defer()

    # Get the embed
    embed = getEmbed(game_name, interaction.user.id)

    # Finally, send the embed
    await interaction.followup.send(embed=embed)
    print("Sent information on requested game " + game_name + "\n")

# ---------------------------- GET EMBED FUNCTION ------------------------
def getEmbed(game_name, authorID):

    payload = {'term': game_name, 'f': 'games', 'cc' : 'us', 'l' : 'english'}
    response = requests.get('https://store.steampowered.com/search/suggest?', params=payload)
    correctAppID = BeautifulSoup(response.text, features="html.parser").a['data-ds-appid']
    

# --- DOWNLOAD JSON FILE ---

    # Open and save the JSON data
    payload = {'appids': correctAppID, 'cc' : 'US'}
    response = requests.get("https://store.steampowered.com/api/appdetails?", params = payload)
    jsonData = json.loads(response.text)
    
    # Save important information
    gameTitle = jsonData[correctAppID]['data']['name']
    imageLink = jsonData[correctAppID]['data']['header_image']
    gameDescription = jsonData[correctAppID]['data']['short_description']
    if(jsonData[correctAppID]['data']['is_free']) : gamePrice = "Free"
    else: gamePrice = jsonData[correctAppID]['data']['price_overview']['final_formatted']
    gameNameWithLinkFormat = game_name.replace(" ", "_")

# --- CREATE EMBED ---

    # and create the embed!
    embed = discord.Embed(title=f"{gameTitle}",
        url=f"https://store.steampowered.com/app/{correctAppID}/{gameNameWithLinkFormat}/",
        description=(f"{gameDescription}"),
        colour=0x000000,
        timestamp=datetime.now())

    embed.add_field(name="Price", value = gamePrice, inline=True)
    embed.add_field(name="User", value = "<@" + str(authorID) + ">", inline=True)
    
    embed.set_author(name="[INSERT ROLL EVENT NAME HERE]", url="https://example.com")
    embed.set_image(url=imageLink)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/639112509445505046/891449764787408966/challent.jpg")
    embed.set_footer(text="CE Assistant",
        icon_url="https://cdn.discordapp.com/attachments/639112509445505046/891449764787408966/challent.jpg")
    return embed


@tree.command(name="curator", description="Get the latest review from the CE curator", guild=discord.Object(id=guildID))
async def curator(interaction) :
    payload = {'cc': 'us', 'l' : 'english'}
    response = requests.get("https://store.steampowered.com/curator/36185934/", params=payload)
    html = BeautifulSoup(response.text, features="html.parser")

    # "paged_items_paging_summary ellipsis" this is where 49 is stored


    await interaction.response.send_message("this command does not work righ now. sorry!")

@tree.command(name="test_command", description="test", guild=discord.Object(id=guildID))
async def test(interaction) :
    print(interaction.guild)
    print(interaction.guild_id)
    print(interaction.guild_locale)

    print(interaction.guild.members.id)
    await interaction.response.send_message("test")


# ----------------------------------- LOG IN ----------------------------
@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=guildID))
    print("Ready!")

client.run(discordToken)
