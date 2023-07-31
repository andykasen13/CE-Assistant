import json
import discord
import time
import datetime
from datetime import timedelta
from bs4 import BeautifulSoup
import requests



ce_mountain_icon = "https://cdn.discordapp.com/attachments/639112509445505046/891449764787408966/challent.jpg"


# ------------------------------------------------ CREATE MULTI EMBED ------------------------------------------------------------ #
def create_multi_embed(event_name, time_limit, game_list, cooldown_time, interaction) :
    with open('Jasons/database_tier.json', 'r') as dB :
        database_tier = json.load(dB)
        
    with open('Jasons/database_name.json', 'r') as dBN :
        database_name = json.load(dBN)
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
    for selected_game in game_list:
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
    for selected_game in game_list :
        total_points = 0
        embeds.append(getEmbed(selected_game, interaction.user.id))
        embeds[i+1].set_footer(text=(f"Page {i+2} of {page_limit}"),
                                icon_url=ce_mountain_icon)
        embeds[i+1].set_author(name="Challenge Enthusiasts")
        embeds[i+1].set_thumbnail(url=interaction.user.avatar)
        for objective in database_name[selected_game]["Primary Objectives"] :
            total_points += int(database_name[selected_game]["Primary Objectives"][objective]["Point Value"])
        i+=1
    
    return embeds # Set the embed to send as the first one



# ----------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------- GET EMBED FUNCTION ------------------------------------------------------ #
# ----------------------------------------------------------------------------------------------------------------------------------- #
def getEmbed(game_name, authorID):

    total_points = 0
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
    response = requests.get("https://store.steampowered.com/api/appdetails?", params = payload) #TODO: possible error here
    jsonData = json.loads(response.text)
    
    # Save important information
    game_name = jsonData[correct_app_id]['data']['name']
    imageLink = jsonData[correct_app_id]['data']['header_image']
    gameDescription = jsonData[correct_app_id]['data']['short_description']
    if(jsonData[correct_app_id]['data']['is_free']) : 
        gamePrice = "Free"
    else: gamePrice = jsonData[correct_app_id]['data']['price_overview']['final_formatted']
    gameNameWithLinkFormat = game_name.replace(" ", "_")

# --- CREATE EMBED ---

    # and create the embed!
    embed = discord.Embed(title=f"{game_name}",
        url=f"https://store.steampowered.com/app/{correct_app_id}/{gameNameWithLinkFormat}/",
        description=(f"{gameDescription}"),
        colour=0x000000,
        timestamp=datetime.datetime.now())

    embed.add_field(name="Price", value = gamePrice, inline=True)
    
    embed.set_author(name="Challenge Enthusiasts", url="https://example.com")
    embed.set_image(url=imageLink)
    embed.set_thumbnail(url=ce_mountain_icon)
    embed.set_footer(text="CE Assistant",
        icon_url=ce_mountain_icon)
    embed.add_field(name="Requested by", value = "<@" + str(authorID) + ">", inline=True)
    if game_name in database_name.keys() :
        for objective in database_name[game_name]["Primary Objectives"] :
            total_points += int(database_name[game_name]["Primary Objectives"][objective]["Point Value"])
        embed.add_field(name="CE Status", value=f"{total_points} Points", inline=True)
        embed.add_field(name="CE Owners", value= database_name[game_name]["Total Owners"], inline=True)
        embed.add_field(name="CE Completions", value= database_name[game_name]["Full Completions"], inline=True)
    else : embed.add_field(name="CE Status", value="Not on Challenge Enthusiasts", inline=True)

    return embed
