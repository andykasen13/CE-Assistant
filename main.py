# This example requires the 'message_content' intent.
import asyncio
from asyncio import Event, wait
from datetime import datetime, timedelta
import datetime
import time
import subprocess
import discord
from discord import Button, app_commands
from discord.ext import tasks, commands

import requests
import random
import json
from steam.webapi import WebAPI
from steam.steamid import SteamID
import steamctl
from steam.client import SteamClient as SClient
steamClient = SClient()

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

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


# ------------------------------------------------------------------------------------------------------------------------------ #
# ----------------------------------------------------------VIEW CLASS---------------------------------------------------------- #
# ------------------------------------------------------------------------------------------------------------------------------ #
class SimpleView(discord.ui.View) :
    @discord.ui.button(label = "hello",
                       style=discord.ButtonStyle.success)
    async def hello(self, interaction, button: discord.ui.Button) :
        await interaction.response.send_message("World")

# ------------------------------------------------------------------------------------------------------------------------------ #
# ----------------------------------------------------------NEXT CLASS---------------------------------------------------------- #
# ------------------------------------------------------------------------------------------------------------------------------ #
# class NextView(discord.ui.View) :
#     @discord.ui.button(label="NEXT")

# ------------------------------------------------------------------------------------------------------------------------------ #
# ----------------------------------------------------------PREV CLASS---------------------------------------------------------- #
# ------------------------------------------------------------------------------------------------------------------------------ #


# ------------------------------------------------------------------------------------------------------------------------------ #
# ---------------------------------------------------------HELP COMMAND--------------------------------------------------------- #
# ------------------------------------------------------------------------------------------------------------------------------ #


@tree.command(name="help", description="help", guild=discord.Object(id=guildID))
async def help(interaction) :
    await interaction.response.defer()
    view = SimpleView()
    button = discord.ui.Button(label = "click me")
    view.add_item(button)
    #embed = discord.Embed(
    #    title="Help",
    #    color=0x000000,
    #    timestamp=datetime.datetime.now()
    #)
   # embed.add_field(name="page 1", value="pge 1")

    await interaction.followup.send(view=view)


# ------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------ROLL COMMAND --------------------------------------------------------- # 
# ------------------------------------------------------------------------------------------------------------------------------- #

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

    # -------------- One Hell of a Week ---------------
    elif event == "one hell of a week" :
        await interaction.followup.send(f"you ave week")

    # -------------- One Hell of a Month --------------
    elif event == "one hell of a month" : 
        await interaction.followup.send(f"you have month")

    # -------------- kill yourself --------------------
    else : await interaction.response.send_message(f"jfasdklfhasd")

    with open('info.json', 'r') as f :
        userInfo = json.load(f)
        
    i = 0
    while userInfo['users'][i]['ID'] != interaction.user.id :
        i += 1
        
    userInfo['users'][i]['current_rolls'].append({"event_name" : "One Hell of a Day", "games" : [{"name" : embed.title, "completed" : False}], "end_time" : "" + datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

    with open('info.json', 'w') as f :
        json.dump(userInfo, f, indent=4)

        # TODO: make sure you indicate if the game is on sale
        # TODO: think about switching the icon of 
        # the /roll command to the user's avatar

        # --------------------------------------------- 
        # ---------------- Events ---------------------
        # One Hell of a Day: random T1
        # One Hell of a Week: random T1s for each category
        # One Hell of a Month: 5 T1s from each category,
        #   and complete three of each five
        # Two Week T2 Streak: 2 random T2s
        # Two "Two Week T2 Streak" Streak: 4 random T2s
        # Never Lucky: random T3 (no time limit)
        # Triple Threat: three random T3s, complete
        #   all within a month
        # Let Fate Decide: random T4 (no time limit)
        # Fourward Thinking: bro what
        # Russian Roulette: pick six T5s, and randomly roll one of them

        # ---------------------------------------------
        # ------------------ Co-ops -------------------
        # Destiny Alignment: You and another player roll games
        #   from the other's library, and both must complete them
        # Soul Mates: You and another player agree on a tier, 
        #   and then a game is rolled (time limit based on tier)

    embed.add_field(name="Roll Requirements", value = 
        "You have one day to complete " + embed.title + "."    
        + "\nMust be completed by <t:" + str(int(time.mktime((datetime.now()+timedelta(1)).timetuple())))
        + ">\nOne Hell of a Day has two week cooldown."
        + "\nCooldown ends on <t:" + str(int(time.mktime((datetime.now()+timedelta(14)).timetuple())))
        + ">\n[insert link to cedb.me page]", inline=False)
    embed.set_author(name="ONE HELL OF A DAY", url="https://example.com")

        # Finally, send the embed
    await interaction.followup.send(embed=embed)
    print("Sent information on rolled game " + game)

    


# ----------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------MY_ROLLS COMMAND --------------------------------------------------------- # 
# ----------------------------------------------------------------------------------------------------------------------------------- #
@tree.command(name="check_rolls", description="Check the active rolls of anyone on the server", guild=discord.Object(id=guildID))
async def checkRolls(interaction, user: discord.Member=None) :
    await interaction.response.defer()

    if user is None :
        user = interaction.user

    #open the json file and get the data
    with open('info.json', 'r') as f :
        userInfo = json.load(f)

    #iterate through the json file until you find the
    #designated user
    userNum = 0
    while userInfo['users'][userNum]['ID'] != user.id :
        if(userNum + 1 == len(userInfo['users'])) : return await interaction.followup.send("This user does not exist.")
        else: userNum += 1

    currentrollstr = ""
    completedrollstr = ""

    # TODO: make sure that if the roll is empty,
    # you don't do all this or it will error a lot!

    # TODO: this is much further down the line but
    # you should debate whether or not it is worth 
    # it to include objectives in this, and if they are, 
    # how to show it.

    # (done) TODO: you forgot the end date silly

    # TODO: co-op rolls :weary: 😩

    for x in userInfo['users'][userNum]['current_rolls'] :
        end_time = time.mktime(datetime.strptime(str(x['end_time']), "%Y-%m-%d %H:%M:%S").timetuple())
        currentrollstr = currentrollstr + "- __" + x['event_name'] + "__ (complete by <t:" + str(int(end_time)) + ">):\n"
        gameNum = 1
        for y in x['games'] :
            if(y['completed']) :
                currentrollstr += (" " + str(gameNum) + ". " + y['name'] + " (completed)\n")
            else : currentrollstr += (" " + str(gameNum) + ". " + y['name'] + " (not completed)\n")
            gameNum += 1
    
    if(currentrollstr == "") :
        currentrollstr = f"{user.name} has no current rolls."

    for x in userInfo['users'][userNum]['completed_rolls'] :
        end_time = time.mktime(datetime.strptime(str(x['completed_time']), "%Y-%m-%d %H:%M:%S").timetuple())
        completedrollstr += "- __" + x['event_name'] + "__ (completed on <t:" + str(int(end_time)) + ">):\n"
        gameNum = 0
        for y in x['games'] :
            completedrollstr += (" " + str(gameNum) + ". " + y['name'] + "\n")
            gameNum += 1
    
    if(completedrollstr == "") :
        completedrollstr = f"{user.global_name} has no completed rolls."
        

        
    embed = discord.Embed(
    colour=0x000000,
    timestamp=datetime.now()
    )


    embed.add_field(name="User", value = "<@" + str(user.id) + ">", inline=False)
    embed.add_field(name="Current Rolls", value=currentrollstr, inline=False)
    embed.add_field(name="Completed Rolls", value=completedrollstr, inline=False)
    embed.set_thumbnail(url=user.avatar.url)
    embed.set_footer(text="CE Assistant",
        icon_url="https://cdn.discordapp.com/attachments/639112509445505046/891449764787408966/challent.jpg")

    await interaction.followup.send(embed=embed)




# ---------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------- GRABBING TIERS --------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
@tree.command(name="get_tier", description="dt", guild=discord.Object(id=guildID))
async def get_tier(interaction):
    # payload = {'cc': 'us', 'l' : 'english'}
    # response = requests.get('https://cedb.me/games?tier=t1', params=payload)
    # soup = BeautifulSoup(response.text)
    # print(soup.prettify())

    await interaction.response.defer()

    driver = webdriver.Chrome()
    # driver.implicitly_wait(0.5)
    #WebDriverWait(driver, timeout=10).until(document_initialised)
    driver.get("https://cedb.me/games?tier=t1")
    # access HTML source code with page_source method
    
    
    plants = WebDriverWait(driver, timeout=3000).until(lambda d: d.find_elements(By.TAG_NAME,"h2"))#driver.find_elements(By.TAG_NAME, "h2")
    #s = driver.page_source
    for plant in plants:
        print(plant.text)

    await interaction.followup.send("hj")

# -------------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------- STEAM TEST COMMAND --------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------------------------- #

@tree.command(name="steam_game", description="Get information on any steam game", guild=discord.Object(id=guildID))
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
    print("Sent information on requested game " + game_name + "\n")

# -------------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------- GET EMBED FUNCTION --------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------------------------- #
def getEmbed(game_name, authorID):

    #TODO add error exceptions
    #TODO turn this into a class with getters and setters for wider versatility

    payload = {'term': game_name, 'f': 'games', 'cc' : 'us', 'l' : 'english'}
    response = requests.get('https://store.steampowered.com/search/suggest?', params=payload)
    #print(response.text)
    correctAppID = BeautifulSoup(response.text, features="html.parser").a['data-ds-appid']

    """ # THIS IS THERONS CODE. DO NOT TOUCH ANDY
    
    prams = {'term': game_name, 'f': 'games', 'cc': 'us'}
    noodle = requests.get('https://store.steampowered.com/search/suggest?', params=prams)
    #print(noodle.text)
    soup = BeautifulSoup(noodle.text, features='html.parser')
    print("testerooni")
    print(soup.get_text)
    print("testerino")
    bowl = soup.find_all('div')
    print(bowl)
    collinder = list(bowl)
    for x in range(0, collinder.len()):
        if collinder.index(x).get_text() == "Free" or "Free To Play" or "":
            collinder.pop(x)
    print(collinder)

    """
        

    
    

# --- DOWNLOAD JSON FILE ---

    # Open and save the JSON data
    payload = {'appids': correctAppID, 'cc' : 'US'}
    response = requests.get("https://store.steampowered.com/api/appdetails?", params = payload)
    jsonData = json.loads(response.text)
    
    # Save important information
    gameTitle = jsonData[correctAppID]['data']['name']
    imageLink = jsonData[correctAppID]['data']['header_image']
    gameDescription = jsonData[correctAppID]['data']['short_description']
    if(jsonData[correctAppID]['data']['is_free']) :
        gamePrice = "Free"
    else: gamePrice = jsonData[correctAppID]['data']['price_overview']['final_formatted']
    # TODO: get discounts working
    gameNameWithLinkFormat = game_name.replace(" ", "_")

# --- CREATE EMBED ---

    # and create the embed!
    embed = discord.Embed(title=f"{gameTitle}",
        url=f"https://store.steampowered.com/app/{correctAppID}/{gameNameWithLinkFormat}/",
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

# --------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------- curator --------------------------------------------------------- #
# --------------------------------------------------------------------------------------------------------------------------- #

async def getCuratorCount():
    veggies = {'cc': 'us', 'l' : 'english'}
    broth = requests.get("https://store.steampowered.com/curator/36185934/", params=veggies)
    soup = BeautifulSoup(broth.text, features="html.parser")
    noodle = soup.find_all("span")
    for noodlet in noodle:
        try:
            if noodlet['id'] == "Recommendations_total":
                number = noodlet.string
        except:
            continue
    return number


async def checkCuratorCount():
    number = await getCuratorCount()
    if number != tree.reviewCount:
        await curator(int(tree.reviewCount)-int(number))
        return number
    else:
        return number

utc = datetime.timezone.utc
times = [
    datetime.time(hour=3, tzinfo=utc),
    datetime.time(hour=6, tzinfo=utc),
    datetime.time(hour=9, tzinfo=utc),
    datetime.time(hour=12, tzinfo=utc),
    datetime.time(hour=15, tzinfo=utc),
    datetime.time(hour=18, tzinfo=utc),
    datetime.time(hour=21, tzinfo=utc),
    datetime.time(hour=0, tzinfo=utc),
    datetime.time(hour=13, minute= 40, tzinfo=utc)
]


@tasks.loop(time = times)
async def loop():
    tree.reviewCount = await checkCuratorCount()


async def curator(num: int) :
    payload = {'cc': 'us', 'l' : 'english'}
    response = requests.get("https://store.steampowered.com/curator/36185934/", params=payload)
    html = BeautifulSoup(response.text, features="html.parser")

    descriptions = []
    app_ids = []
    links = []

    divs = html.find_all('div')
    for div in divs:
        try:
            if div["class"][0] == "recommendation_desc":
                descriptions.append(div.string.replace('\t', '').replace('\r', '').replace('\n', ''))
            if div["class"][0] == "recommendation_readmore":
                links.append(div.contents[0]["href"][43:])
        except:
            continue
    del descriptions[num:]

    onlyAs = html.find_all('a')
    for a in onlyAs:
        try:
            app_ids.append(a["data-ds-appid"])
        except:
            continue
    del app_ids[num:]

    # print(descriptions)
    # print(app_ids)
    # print(links)

    embed = discord.Embed(
        title="Help",
        color=0x000000,
        timestamp=datetime.datetime.now()
    )


    x = 0
    print(len(descriptions))
    while x < len(descriptions):
    #TODO: once you get multi-page embeds working get this to change pls
        correctAppID = app_ids[x]

# Open and save the JSON data
        payload = {'appids': correctAppID, 'cc' : 'US'}
        response = requests.get("https://store.steampowered.com/api/appdetails?", params = payload)
        jsonData = json.loads(response.text)
    
    # Save important information
        gameTitle = jsonData[correctAppID]['data']['name']
        imageLink = jsonData[correctAppID]['data']['header_image']
        gameDescription = jsonData[correctAppID]['data']['short_description']
        if(jsonData[correctAppID]['data']['is_free']) :
            gamePrice = "Free"
        else: gamePrice = jsonData[correctAppID]['data']['price_overview']['final_formatted']
        # TODO: get discounts working
        gameNameWithLinkFormat = gameTitle.replace(" ", "_")
        correctChannel = client.get_channel(788158122907926611)

        embed = discord.Embed(
            title = gameTitle,
            url=f"https://store.steampowered.com/app/{correctAppID}/{gameNameWithLinkFormat}/",
            colour = 0x000000,
            timestamp=datetime.datetime.now()
        )

        embed.add_field(name="Review", value=descriptions[x], inline=False)
        embed.add_field(name="Price", value=gamePrice, inline=False)
        embed.set_image(url=imageLink)
        embed.set_footer(text="CE Assistant",
            icon_url="https://cdn.discordapp.com/attachments/639112509445505046/891449764787408966/challent.jpg")
        embed.set_author(name="New game added to curator!", url="https://store.steampowered.com/curator/36185934/")
    
        await correctChannel.send(embed=embed)
        x+=1

# --------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------TEST COMMAND------------------------------------------------------------- #
# --------------------------------------------------------------------------------------------------------------------------- #


@tree.command(name="test_command", description="test", guild=discord.Object(id=guildID))
async def test(interaction) :
    await interaction.response.send_message("uselsess command")

# ----------------------------------- LOG IN ----------------------------
@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=guildID))
    print("Ready!")
    tree.reviewCount = await getCuratorCount()
    await loop.start()
client.run(discordToken)
