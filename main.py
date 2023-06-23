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

# ------------------------- Test Commands -----------------------

@tree.command(name = "commandname", description = "My first application Command", guild=discord.Object(id=788158122907926608)) 
async def first_command(interaction):
    await interaction.response.send_message("Hello!")

@tree.command(name = "balls", description = "more balls", guild=discord.Object(id=788158122907926608))
async def second_command(interaction):
    await interaction.response.send_message("suck my balls")

@tree.command(name="test_argument", description = "help", guild=discord.Object(id=788158122907926608))
async def sub_command(interaction, argument: str) -> None:
    await interaction.response.send_message(f"Hello, you sent {argument}!")

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
        game = random.choice(data_into_list)
        print("game: " + game)

        # Write the name of the game into the HelloWorld.txt file
        with open('HelloWorld.txt', 'w') as f:
            await interaction.response.defer()
            f.write(f"{game}") 

        # Open and run jsfile.js to get the AppID       
        p2 = subprocess.Popen(['/Program Files/nodejs/node.exe', '/Users/andre/Desktop/better-ce-bot/jsfile.js', 'andre'], stdout=subprocess.PIPE)
        out2 = p2.stdout.read()

        print(out2)

        # Read the HelloWorld.txt file (will be rewritten with the appID of the game we supplied earlier)
        with open('HelloWorld.txt', 'r') as f: 
            correctAppID = f.read()

        # Formulate the correct API link to download JSON file
        correctURL = "https://store.steampowered.com/api/appdetails?appids=" + correctAppID

        # Open and save the JSON data
        payload = {'appids': correctAppID, 'cc' : 'US'}
        response = requests.get("https://store.steampowered.com/api/appdetails?", params = payload)
        jsonData = json.loads(response.text)
    
        # Save important information
        imageLink = jsonData[correctAppID]['data']['header_image']
        gameDescription = jsonData[correctAppID]['data']['short_description']
        gamePrice = jsonData[correctAppID]['data']['price_overview']['final_formatted']
        gameNameWithLinkFormat = game.replace(" ", "_")

        # and create the embed!
        embed = discord.Embed(title=f"{game}",
            url=f"https://store.steampowered.com/app/{correctAppID}/{gameNameWithLinkFormat}/",
            description=(f"{gameDescription}"),
            colour=0x000000,
            timestamp=datetime.now())

        embed.add_field(name="Price", value = gamePrice, inline=True)
        embed.add_field(name="User", value = "<@" + str(interaction.user.id) + ">", inline=True)
        embed.add_field(name="Roll Requirements", value = "**you have this much time to  complete it!**" 
            + "\ndate and time of completion\ndate and time of cooldown end" 
            + "\n[insert link to cedb.me page]", inline=False)
    

        embed.set_author(name="[INSERT ROLL EVENT NAME HERE]",
                 url="https://example.com")

        embed.set_image(url=imageLink)

        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/639112509445505046/891449764787408966/challent.jpg")

        embed.set_footer(text="CE Assistant",
                     icon_url="https://cdn.discordapp.com/attachments/639112509445505046/891449764787408966/challent.jpg")

        # Finally, send the embed
        await interaction.followup.send(embed=embed)

    # -------------- One Hell of a Week ---------------
    elif argument == "one hell of a week" :
        await interaction.response.send_message(f"you ave week")

    # -------------- One Hell of a Month --------------
    elif argument == "one hell of a month" : 
        await interaction.response.send_message(f"you have month")

    # -------------- kill yourself --------------------
    else : await interaction.response.send_message(f"jfasdklfhasd")

# --------------------------------------------------- #
# ------------- STEAM TEST COMMAND ------------------ #
# --------------------------------------------------- #

@tree.command(name="steam_test", description="fhjskdla", guild=discord.Object(id=788158122907926608))
async def steam_command(interaction, game_name: str):

    # Log the command
    print("Recieved steam_game command with parameter: " + game_name + ".")

    # Write the name of the game into the HelloWorld.txt file
    with open('HelloWorld.txt', 'w') as f:
        await interaction.response.defer()
        f.write(f"{game_name}") 

    # Open and run jsfile.js to get the AppID       
    p = subprocess.Popen(['/Program Files/nodejs/node.exe', '/Users/andre/Desktop/better-ce-bot/jsfile.js', 'andre'], stdout=subprocess.PIPE)
    out = p.stdout.read()

    print(out)

    # Read the HelloWorld.txt file (will be rewritten with the appID of the game we supplied earlier)
    with open('HelloWorld.txt', 'r') as f: 
        correctAppID = f.read()

    # Formulate the correct API link to download JSON file
    correctURL = "https://store.steampowered.com/api/appdetails?appids=" + correctAppID

    # Open and save the JSON data
    payload = {'appids': correctAppID, 'cc' : 'US'}
    response = requests.get("https://store.steampowered.com/api/appdetails?", params = payload)
    jsonData = json.loads(response.text)
    
    # Save important information
    imageLink = jsonData[correctAppID]['data']['header_image']
    gameDescription = jsonData[correctAppID]['data']['short_description']
    if(jsonData[correctAppID]['data']['is_free'] == "true") : gamePrice = "Free"
    else: gamePrice = jsonData[correctAppID]['data']['price_overview']['final_formatted']
    gameNameWithLinkFormat = game_name.replace(" ", "_")

    # and create the embed!
    embed = discord.Embed(title=f"{game_name}",
        url=f"https://store.steampowered.com/app/{correctAppID}/{gameNameWithLinkFormat}/",
        description=(f"{gameDescription}"),
        colour=0x000000,
        timestamp=datetime.now())

    embed.add_field(name="Price", value = gamePrice, inline=True)
    embed.add_field(name="User", value = "<@" + str(interaction.user.id) + ">", inline=True)
    embed.add_field(name="Roll Requirements", value = "**you have this much time to  complete it!**" 
            + "\ndate and time of completion\ndate and time of cooldown end" 
            + "\n[insert link to cedb.me page]", inline=False)
    

    embed.set_author(name="[INSERT ROLL EVENT NAME HERE]",
                 url="https://example.com")

    embed.set_image(url=imageLink)

    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/639112509445505046/891449764787408966/challent.jpg")

    embed.set_footer(text="CE Assistant",
                 icon_url="https://cdn.discordapp.com/attachments/639112509445505046/891449764787408966/challent.jpg")

    # Finally, send the embed
    await interaction.followup.send(embed=embed)
    
# ----------------------------------- LOG IN ----------------------------

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=788158122907926608))
    print("Ready!")

client.run(discordToken)
