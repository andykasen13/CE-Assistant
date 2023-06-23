# This example requires the 'message_content' intent.

from asyncio import Event, wait
from datetime import datetime
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
    data = json.load(f)

discordToken = data['discordToken']


# Add the guild ids in which the slash command will appear. 
# If it should be in all, remove the argument, but note that 
# it will take some time (up to an hour) to register the command 
# if it's for all guilds.

 # -------------------------------------------------------- #
 # --------------------ROLL COMMAND ----------------------- # 
 # -------------------------------------------------------- #

@tree.command(name="roll", description="Participate in Challenge Enthusiast roll events!", guild=discord.Object(id=788158122907926608))
async def roll_command(interaction, argument: str) -> None:

    # Open file
    tier_one_file = open("faket1list.txt", "r")
    data = tier_one_file.read()
    data_into_list = data.split("\n")
    print(data_into_list)
    tier_one_file.close()

    # -------------- One Hell of a Day ----------------
    if argument == "one hell of a day" :
        # Pick a random game from the list
        getTier(1)
        game = random.choice(data_into_list)
        print("Rolled game: " + game)

        await interaction.response.defer()

        embed = getEmbed(game, interaction.user.id)

        # Finally, send the embed
        await interaction.followup.send(embed=embed)
        print("Sent information on rolled game " + game)

    # -------------- One Hell of a Week ---------------
    elif argument == "one hell of a week" :
        await interaction.response.send_message(f"you ave week")

    # -------------- One Hell of a Month --------------
    elif argument == "one hell of a month" : 
        await interaction.response.send_message(f"you have month")

    # -------------- kill yourself --------------------
    else : await interaction.response.send_message(f"jfasdklfhasd")


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

@tree.command(name="steam_game", description="Get information on any steam game", guild=discord.Object(id=788158122907926608))
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

# ---------------------------- GET APP ID FUNCTION ------------------------
def getEmbed(game_name, authorID):

    payload = {'term': game_name, 'f': 'games', 'cc' : 'us', 'l' : 'english'}
    response = requests.get('https://store.steampowered.com/search/suggest?', params=payload)
    correctAppID = BeautifulSoup(response.text, features="html.parser").a['data-ds-appid']
    

# ----------------------------- DOWNLOAD JSON FILE --------------------------

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

# ------------------------------- CREATE EMBED ----------------------------------------
    # and create the embed!
    embed = discord.Embed(title=f"{gameTitle}",
        url=f"https://store.steampowered.com/app/{correctAppID}/{gameNameWithLinkFormat}/",
        description=(f"{gameDescription}"),
        colour=0x000000,
        timestamp=datetime.now())

    embed.add_field(name="Price", value = gamePrice, inline=True)
    embed.add_field(name="User", value = "<@" + str(authorID) + ">", inline=True)
    embed.add_field(name="Roll Requirements", value = "**you have this much time to  complete it!**" 
            + "\ndate and time of completion\ndate and time of cooldown end" 
            + "\n[insert link to cedb.me page]", inline=False)
    

    embed.set_author(name="[INSERT ROLL EVENT NAME HERE]",
                 url="https://example.com")

    embed.set_image(url=imageLink)

    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/639112509445505046/891449764787408966/challent.jpg")

    embed.set_footer(text="CE Assistant",
                 icon_url="https://cdn.discordapp.com/attachments/639112509445505046/891449764787408966/challent.jpg")
    return embed

@tree.command(name="test_stupid_thing", description="i will be so mad if this works", guild=discord.Object(id=788158122907926608))
async def tryCommand(interaction, game_name: str) :
    print("try command on game " + game_name)

    await interaction.response.defer()
    payload = {'term': game_name, 'f': 'games', 'cc' : 'us', 'l' : 'english'}
    response = requests.get('https://store.steampowered.com/search/suggest?', params=payload)

    soup = BeautifulSoup(response.text, features="html.parser").a['data-ds-appid']

    await interaction.followup.send("balls")

# ----------------------------------- LOG IN ----------------------------

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=788158122907926608))
    print("Ready!")

client.run(discordToken)
