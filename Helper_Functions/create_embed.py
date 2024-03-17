import json
import discord
import time
import datetime
from datetime import timedelta
from bs4 import BeautifulSoup
import requests
from Helper_Functions.mongo_silly import *


# ------------------------------------------------ CREATE MULTI EMBED ------------------------------------------------------------ #
def create_multi_embed(event_name, time_limit, game_list, cooldown_time, interaction, database_name) :

    # ----- Set up initial embed -----
    embeds = []
    embeds.append(discord.Embed(
        color = 0x000000,
        title=event_name,
        timestamp=datetime.datetime.now()
    ))
    embeds[0].set_footer(text=f"Page 1 of {str(len(game_list) + 1)}", icon_url = final_ce_icon)
    embeds[0].set_author(name="Challenge Enthusiasts")

    # ----- Add all games to the embed -----
    games_value = ""
    i = 1
    for selected_game in game_list:
        games_value += "\n" + str(i) + ". " + database_name[selected_game]['Name']
        i+=1
    embeds[0].add_field(name="Rolled Games", value = games_value)

    # ----- Display Roll Requirements -----
    embeds[0].add_field(name="Roll Requirements", value =
        "\nYou must complete " + str(event_name) + " by <t:" + str(get_unix(time_limit))
        + f">.\n{event_name} has a cooldown time of {cooldown_time} days.", inline=False)
    embeds[0].timestamp = datetime.datetime.now()
    embeds[0].set_thumbnail(url = interaction.user.avatar)
    
    # ----- Create the embeds for each game -----
    page_limit = len(game_list) + 1
    i=0
    for selected_game in game_list :
        total_points = 0
        embeds.append(getEmbed(selected_game, interaction.user.id, database_name))
        embeds[i+1].set_footer(text=(f"Page {i+2} of {page_limit}"),
                                icon_url=final_ce_icon)
        embeds[i+1].set_thumbnail(url=interaction.user.avatar)
        for objective in database_name[selected_game]['Primary Objectives'] :
            total_points += int(database_name[selected_game]['Primary Objectives'][objective]['Point Value'])
        i+=1
    
    return embeds # Set the embed to send as the first one



# ----------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------- GET EMBED FUNCTION ------------------------------------------------------ #
# ----------------------------------------------------------------------------------------------------------------------------------- #
def getEmbed(game_name, authorID, database_name) -> discord.Embed:

    total_points = 0
    #TODO add error exceptions
    #TODO turn this into a class with getters and setters for wider versatility
    if(len(game_name) == 36 and game_name[8:9] == game_name[13:14] == game_name[18:19] == game_name[23:24] == "-") : 
        game_id = game_name
        game_name = database_name[game_name]['Name']
        print(True)
    else :
        game_id = game_name
    
    
    if(game_id in (database_name)) : 
        correct_app_id = database_name[game_id]['Steam ID']
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
                if div['class'][0] == "match_name":
                    options.append(div.text)
            except:
                continue

            correct_app_id = ass[0]['data-ds-appid']

        for i in range(0, len(options)):
            if game_name == options[i]:
                correct_app_id = ass[i]['data-ds-appid']
        
        if correct_app_id == None : return discord.Embed(title=f"Could not find game \"{game_name}\".")

# --- DOWNLOAD JSON FILE ---

    # Open and save the JSON data
    payload = {'appids': correct_app_id, 'cc' : 'US'}
    response = requests.get("https://store.steampowered.com/api/appdetails?", params = payload) #TODO: possible error here
    jsonData = json.loads(response.text)
    
    # Save important information
    imageLink = jsonData[correct_app_id]['data']['header_image']
    gameDescription = str(jsonData[correct_app_id]['data']['short_description']).replace('&amp;', '&').replace('&quot;', '\"')
    if(jsonData[correct_app_id]['data']['is_free']) : 
        gamePrice = "Free"
    
    elif('price_overview' in list(jsonData[correct_app_id]['data'].keys())) :
        gamePrice = jsonData[correct_app_id]['data']['price_overview']['final_formatted']
    else :
        gamePrice = "No price listed."
    gameNameWithLinkFormat = game_name.replace(" ", "_")

# --- CREATE EMBED ---

    # and create the embed!
    embed = discord.Embed(title=f"{game_name}",
        url=f"https://store.steampowered.com/app/{correct_app_id}/{gameNameWithLinkFormat}/",
        description=(f"{gameDescription}"),
        colour=0x000000,
        timestamp=datetime.datetime.now())

    embed.add_field(name="Price", value = gamePrice, inline=True)
    if game_name in database_name :
        embed.set_author(name="Challenge Enthusiasts", url=f"https://cedb.me/game/{database_name[game_name]['CE ID']}/")
    else:
        embed.set_author(name="Challenge Enthusiasts")
    embed.set_image(url=imageLink)
    embed.set_thumbnail(url=ce_mountain_icon)
    embed.set_footer(text="CE Assistant",
        icon_url=final_ce_icon)
    embed.add_field(name="Rolled by", value = "<@" + str(authorID) + ">", inline=True)
    if game_id in database_name.keys() :
        for objective in database_name[game_id]['Primary Objectives'] :
            total_points += int(database_name[game_id]['Primary Objectives'][objective]['Point Value'])
        embed.add_field(name="CE Status", 
                        value=icons[database_name[game_id]['Tier']] + icons[database_name[game_id]['Genre']] + f" - {total_points} Points" + icons['Points'], 
                        inline=True)
        try:
            embed.add_field(name="CE Owners", value= database_name[game_id]['Total Owners'], inline=True)
            embed.add_field(name="CE Completions", value= database_name[game_id]['Full Completions'], inline=True)
        except:""
    else : embed.add_field(name="CE Status", value="Not on Challenge Enthusiasts", inline=True)

    return embed
