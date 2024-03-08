

#-----------------------------------------------------------------------------------------#
#                                                                                         #
"                                    DATA SCRAPER                                         "
#                                                                                         #
#               updates both databases (tier and name) every 15 minutes                   #      
#                    and sends update logs to the desired channel                         #
#                                                                                         #
#-----------------------------------------------------------------------------------------#


# the basics
import io
import os
import json
from datetime import datetime
import time
import discord
import requests

# web shit (like spiderman!)
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import chromedriver_binary  # Adds chromedriver binary to path

# pictures
from .Screenshot import Screenshot
from PIL import Image
from Helper_Functions.mongo_silly import *




# Grab information from json file
# with open('Jasons/secret_info.json') as f :
#     localJSONData = json.load(f)

# steam_api_key = localJSONData['steam_API_key']


def get_games(database_name, curator_count, unfinished_games):

    # create our returnable and update database_name
    fin = game_list(database_name, curator_count, unfinished_games)
    if fin == None: return None
    # use database_name to update database_tier
    database_tier = get_by_tier(database_name)
    fin.append(database_tier)
    # return embeds
    return fin


def single_scrape(curator_count):
    api_response = requests.get('https://cedb.me/api/games')
    json_response = json.loads(api_response.text)

    curator_count['Updated Time'] = int(time.mktime(datetime.datetime.now().timetuple()))

    database_name = {}

    for game in json_response:
        if(game['genre'] == None or game['genre']['name'] == None) : continue
        print(game['name'])
        database_name[game['name']] = get_game(game)

    database_tier = get_by_tier(database_name)

    return [database_name, curator_count, database_tier]

def single_scrape_v2(curator_count) :
    api_response = requests.get('https://cedb.me/api/games/')
    json_response = json.loads(api_response.text)

    curator_count['Updated Time'] = get_unix('now')

    database_name_v2 = {}

    for game in json_response:
        if(game['genre'] == None or game['genre']['name'] == None) : continue
        print(game['name'])
        database_name_v2[game['id']] = get_game(game)
    
    database_tier = get_by_tier(database_name_v2)

    return [database_name_v2, curator_count, database_tier]

    

def game_list(new_data, current_dict, unfinished_games : dict):
    """
    Parameters
    -----------
    new_data: :class:`dict`
        database_name
    current_dict: :class:`dict`
        curator_count
    unfinished_games: :class`dict`
        unfinished_games
    """
    
    # -------------- variables ------------
    hm = True # use this if you want selenium and #game-additions stuff
    option3 = True # use this if /api/games/full/ fails
    pi = False # use this if on the pi

    # ------------- actual stuff ----------
    # Set selenium driver and preferences
    if hm:
    
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('log-level=3')
        if pi:
            service = Service('/usr/lib/chromium-browser/chromedriver')
            driver = webdriver.Chrome(service=service, options=options)
        else:
            service = Service(r"C:/Program Files/Google/Chrome Dev/Application/chrome.exe")
            driver = webdriver.Chrome(options=options, service=service)
        driver.set_window_size(width=1440, height=8000)

        # grab first game to get color on the rest of them
        url = 'https://cedb.me/game/1e8565aa-b9f2-4b41-9578-22e4c2a5436b'
        driver.get(url)
        time.sleep(5)
        objective_lst = []
        
        while(len(objective_lst) < 1 or not objective_lst[0].is_displayed()):
            objective_lst = []
            time.sleep(1)
            objective_lst = driver.find_elements(By.CLASS_NAME, "bp4-html-table-striped")
            #print(objective_lst)

    

    # set up API requests
    if option3 :
        #print('fetching /api/games/...')
        api_response = requests.get('https://cedb.me/api/games')
        try:   
            json_response = json.loads(api_response.text)
            #print('fetched.\n')
        except:
            print('fetching failed lol!!!!!!! (api/games)')
            if hm: del driver
            return
        
    else :
        #print('fetching /api/games/full/...')
        api_response = requests.get('https://cedb.me/api/games/full')
        #print('fetched.\n')
        try:
            json_response = json.loads(api_response.text)
        except:
            print('fetching failed lolW (api/games/full)!!!')
            if hm: del driver
            return

    # grab last updated time
    current_newest = current_dict['Updated Time']
    c = current_newest
    current_dict['Updated Time'] = int(time.mktime(datetime.datetime.now().timetuple()))
    
    # grab the new data and initialize trackers
    number = 0
    updated_games = []
    game_tracker = list(new_data.keys())
    game_tracker.remove('_id')

    """
    theron i love you but you did a shit ass job naming these variables so here's what they all mean
    game_tracker: 
        a list of every game's name stored in database_name BEFORE scraping.
        games that are leftover in game_tracker after scraping is done have been removed.
    current_newest:
        the most recent time BEFORE scraping that scraping took place.
        stored as an int unix-timestamp.
    current_dict:
        this is curator_count.json
    c:
        truly theron what the fuck was the point of this?
        i actually have no clue what this variable is for
    new_data:
        database_name.json from BEFORE scraping.
        this is updated throughout scraping and is eventually returned to be dumped.
    """


    # make sure the json loaded in its entirety
    try:
        #print('testing...')
        a = (json_response[0]['id'])
        #print('test passed.\n')
    except:
        print('json failed lol')
        return

    #print('scraping....')
    # game loop adding updated parts
    for i, game in enumerate(json_response):
        #print(game['name'])
        current_newest = c

        import_objective_names = []
        local_objective_names = []

        if option3:
            api_response_current = requests.get('https://cedb.me/api/game/' + game['id'])
            try:   
                json_response_current = json.loads(api_response_current.text)
            except:
                print(f"{game['name']} not pulled correctly...")
                game_tracker.remove(game['name'])
                continue

            game = json_response_current




        # determine the correct updated_at time
        updated_time = timestamp_to_unix(game['updatedAt'])
        created_time = timestamp_to_unix(game['createdAt'])

        for objective in game['objectives'] :
            # store the objective names
            import_objective_names.append(objective['name'])

            # was the objective updated
            objupdatedtime = timestamp_to_unix(objective['updatedAt'])
            if updated_time < objupdatedtime : updated_time = objupdatedtime

            # was the objective's requirement updated
            for objrequirement in objective['objectiveRequirements'] :
                objrequpdatedtime = timestamp_to_unix(objrequirement['updatedAt'])
                if updated_time < objrequpdatedtime : updated_time = objrequpdatedtime

        if(game['name'] in list(new_data.keys())) : 
            # if the game is locally stored, set current_newest to that updatedvalue
            current_newest = new_data[game['name']]['Last Updated']

            # also grab the names of objectives
            local_objective_names = list(new_data[game['name']]['Primary Objectives'].keys()) + list(new_data[game['name']]['Community Objectives'].keys())
        
        if set(import_objective_names) != set(local_objective_names): updated_time = current_newest + 1
            

       # print("updatd")



        # check if updated since last check
        icon = game['icon']

        # if game is a T0 and updated
        if updated_time > current_newest and game['tier'] == 0 and game['name'] in list(new_data.keys()):
            print("T0 UPDATED: " + game['name'])
            # update game tracker
            game_tracker.remove(game['name'])

            # get old data
            test_old = new_data[game['name']]

            # get new data that wont be mutated
            to_keep = get_game(game, json_response[i])

            # create maluable data
            test_new = to_keep

            # remove completion data for comparisons
            test_new['Full Completions'] = None
            test_new['Total Owners'] = None
            test_old['Full Completions'] = None
            test_old['Total Owners'] = None

            # compare old and new data excluding completion data
            if test_old != test_new:    
                if hm:
                    updated_games.extend(special_update(to_keep, new_data[game['name']], driver, number, icon, icons, game['name']))
                    number += 1

            # update data
            new_data[game['name']] = get_game(game, json_response[i])
        
        # game is new BUT! unfinished
        elif created_time > current_newest and (game['tier'] == 0 or game['genre'] == None or game['information'] == "WIP"):
            print('unfinished game: ' + game['name'])
            if game['id'] in unfinished_games['unfinished'] : continue
            else: unfinished_games['unfinished'].append(game['id'])

        # if game is updated
        elif updated_time > current_newest and game['name'] in list(new_data.keys()):
            print("UPDATED: " + game['name'])
            game_tracker.remove(game['name'])
            test_old = new_data[game['name']]
            to_keep = get_game(game, json_response[i])
            test_new = to_keep
            test_new['Full Completions'] = None
            test_new['Total Owners'] = None
            test_old['Full Completions'] = None
            test_old['Total Owners'] = None
            if test_old != test_new:
                if hm:
                    upppp = update(to_keep, new_data[game['name']], driver, number, icon, icons, game['name'])
                    if upppp != "hiya!":
                        updated_games.append(upppp)
                        number += 1
            new_data[game['name']] = get_game(game, json_response[i])

        # if game is new
        # elif not game['name'] in list(new_data.keys()) and game['genreId'] != None:

        # if a game is new
        # ORRRRR
        # the game is in unfininshed games and is ready to go 
        #TODO: this might be redundant code but i'm not gonna find out so lol
        elif (created_time > current_newest) or (game['id'] in unfinished_games['unfinished'] and (game['tier'] != 0 and game['genre'] != None)):
            print("NEW: " + game['name'])
            if hm:
                ss = (get_image(number, game['id'], driver))
                ss = io.BytesIO(ss)
            new_game = get_game(game, json_response[i])
            new_data[game['name']] = new_game

            # grab total points
            points = 0
            uncleareds = 0
            for objective in new_game['Primary Objectives']:
                if new_game['Primary Objectives'][objective]['Point Value'] == 1: uncleareds +=1
                else: points += new_game['Primary Objectives'][objective]['Point Value']
            
            second_part = ""
            third_part = ""
            num_po = len(list(new_game['Primary Objectives']))
            num_co = len(list(new_game['Community Objectives']))

            # grammar police
            if num_po > 1:
                second_part = 's'

            if num_co > 1:
                third_part = "\n- {} Community Objectives".format(num_co)
            elif num_co == 1:
                third_part = "\n- 1 Community Objective"
            
            if uncleareds > 1:
                third_part += "\n- {} Uncleared Objectives"
            elif uncleareds == 1:
                third_part += "\n- 1 Uncleared Objective"
            

            # make embed
            if hm:
                embed = {
                    'Embed' : discord.Embed(
                        title="__" + game['name'] + "__ added to the site:", 
                        colour= 0x48b474,
                        timestamp=datetime.datetime.now(),
                        description="\n- {} {}\n- {} Primary Objective{} worth {} points{}".format(icons[new_game['Tier']], icons[new_game['Genre']], len(list(new_game['Primary Objectives'])), second_part, points, third_part)
                    ),
                    'Image' : discord.File(ss, filename="image.png")
                }
                embed['Embed'].set_image(url='attachment://image.png')
                embed['Embed'].set_author(name="Challenge Enthusiasts", url=("https://cedb.me/game/" + new_game['CE ID']), icon_url=icon)
                embed['Embed'].set_thumbnail(url=ce_hex_icon)
                embed['Embed'].set_footer(text="CE Assistant",
                    icon_url=final_ce_icon)
            
                updated_games.append(embed)
                number += 1

            if (game['id'] in unfinished_games['unfinished']): unfinished_games['unfinished'].remove(game['id'])
            if hm: del ss

        # game is neither new nor updated
        elif game['name'] in game_tracker:
            game_tracker.remove(game['name'])
        
        # two options: 
        # either the games name was changed 
        # - OR 
        # the game is not registered in the CE Assistant database.
        elif not game['name'] in list(new_data.keys()) and game['genreId'] != None:
            silly = False
            
            # check if the game's name was changed
            for other_game in new_data:
                if other_game == '_id' : continue
                if game['id'] == new_data[other_game]['CE ID']:
                    game_tracker.remove(other_game['name'])
                    del(new_data[other_game])
                    new_data[game['name']] = get_game(game, json_response[i])
                    silly = True

            # new game that wasn't caught above
            if not silly:
                print("NEW: " + game['name'])
                if hm:
                    ss = (get_image(number, game['id'], driver))
                    ss = io.BytesIO(ss)
                new_game = get_game(game, json_response[i])
                new_data[game['name']] = new_game

                # grab total points
                points = 0
                for objective in new_game['Primary Objectives']:
                    points += new_game['Primary Objectives'][objective]['Point Value']
                
                second_part = ""
                third_part = ""
                num_po = len(list(new_game['Primary Objectives']))
                num_co = len(list(new_game['Community Objectives']))

                # grammar police
                if num_po > 1:
                    second_part = 's'

                if num_co > 1:
                    third_part = "\n- {} Community Objectives".format(num_co)
                elif num_co == 1:
                    third_part = "\n- 1 Community Objective"
                

                # make embed
                if hm:
                    embed = {
                        'Embed' : discord.Embed(
                            title="__" + game['name'] + "__ added to the site:", 
                            colour= 0x48b474,
                            timestamp=datetime.datetime.now(),
                            description="\n- {} {}\n- {} Primary Objective{} worth {} points{}".format(icons[new_game['Tier']], icons[new_game['Genre']], len(list(new_game['Primary Objectives'])), second_part, points, third_part)
                        ),
                        'Image' : discord.File(ss, filename="image.png")
                    }
                    embed['Embed'].set_image(url='attachment://image.png')
                    embed['Embed'].set_author(name="Challenge Enthusiasts", url=("https://cedb.me/game/" + new_game['CE ID']), icon_url=icon)
                    embed['Embed'].set_thumbnail(url=ce_hex_icon)
                    embed['Embed'].set_footer(text="CE Assistant",
                        icon_url=final_ce_icon)
                
                    updated_games.append(embed)
                    number += 1

                if (game['id'] in unfinished_games['unfinished'] and (game['tier'] != 0 and game['genre'] != None)): unfinished_games['unfinished'].remove(game['id'])

                if hm: del ss



        # if the game exists in database_name
        if game['genre'] != None and game['name'] in list(new_data.keys()):
            new_data[game['name']]['Last Updated'] = updated_time


    # games removed
    for game in game_tracker:
        print("REMOVED: " + game)
        if hm:
            embed = {
                'Embed' : discord.Embed(
                    title=game,
                    colour= 0xce4e2c,
                    timestamp=datetime.datetime.now()
                ),
                'Image' : discord.File("Web_Interaction/removed.png", filename="image.png")
            }
            embed['Embed'].set_image(url='attachment://image.png')
            updated_games.append(embed)
        del new_data[game]

    del json_response
    if hm: 
        driver.close()
        del driver
    del game_tracker

    return [updated_games, number, new_data, current_dict, unfinished_games]


# updates for games
def update(new_game, old_game, driver, number, icon, icons, name):
    # get game info and image
    #new_game = get_game(game)
    ss = get_image(number, new_game['CE ID'], driver)
    ss = io.BytesIO(ss)

    # initialize the embed description
    update = ""

    # ------------------- check tier -------------------
    if new_game['Tier'] != old_game['Tier']:
        update += "\n- {} ➡ {}".format(icons[old_game['Tier']], icons[new_game['Tier']])

    # ------------------- check points -----------------
    new_points = 0
    for objective in new_game['Primary Objectives']:
        new_points += new_game['Primary Objectives'][objective]['Point Value']

    old_points = 0
    for objective in old_game['Primary Objectives']:
        old_points += old_game['Primary Objectives'][objective]['Point Value']

    if new_points != old_points and (len(old_game['Primary Objectives']) != 1 or len(new_game['Primary Objectives']) != 1):
        update += "\n- {} <:CE_points:1128420207329816597> ➡ {} points <:CE_points:1128420207329816597>".format(old_points, new_points)

    # ------------------- check Genre -------------------
    if new_game['Genre'] != old_game['Genre']:
        update += "\n- {} ➡ {}".format(icons[old_game['Genre']], icons[new_game['Genre']])


    # ------------------- check objectives -------------------
    update += objective_update('Primary', new_game, old_game).replace('🧑‍🦲😼💀😩🥵', '')
    update += objective_update('Community', new_game, old_game).replace('🧑‍🦲😼💀😩🥵', '')

    fake_update = update
    fake_update.replace('\n','')
    fake_update.replace('\t','')
    if fake_update == "" : return "hiya!"

    # ------------------- make final embed -------------------
    embed = {
        'Embed' : discord.Embed(
            title="__" + name + "__ updated on the site:",
            colour= 0xefd839,
            timestamp=datetime.datetime.now(),
            description=update.strip()
        ),
        'Image' : discord.File(ss, filename="image.png")
    }

    embed['Embed'].set_image(url='attachment://image.png')
    embed['Embed'].set_author(name="Challenge Enthusiasts", url=("https://cedb.me/game/" + new_game['CE ID']), icon_url=icon)
    embed['Embed'].set_thumbnail(url=ce_mountain_icon)
    embed['Embed'].set_footer(text="CE Assistant",
        icon_url=final_ce_icon)

    del ss

    # return :)
    return embed


def special_update(new_game, old_game, driver, number, icon, icons, name):
    removed = False
    update = ""
    decimal = 0
    embeds = []

    update += objective_update('Primary', new_game, old_game)
    update += objective_update('Community', new_game, old_game)


    objective_list = update.split("🧑‍🦲😼💀😩🥵")

    if len(objective_list) > 0:
        objective_list.pop(0)


    for objective_info in objective_list:
        objective = objective_info[objective_info.find("'")+3:objective_info.rfind("'")-2:]
        image = special_image(number, decimal, new_game['CE ID'], driver, objective)
        if(image == "none") : removed = True
        else:
            image = io.BytesIO(image)

        if(not removed):
            embed = {
                'Embed' : discord.Embed(
                    title="__" + name + "__ updated on the site:",
                    colour= 0xefd839,
                    timestamp=datetime.datetime.now(),
                    description=objective_info.strip()
                ),
                'Image' : discord.File(image, filename="image.png")
            }
        else:
            embed = {
                'Embed' : discord.Embed(
                    title="__" + name + "__ updated on the site:",
                    colour= 0xefd839,
                    timestamp=datetime.datetime.now(),
                    description=objective_info.strip()
                ),
                'Image' : discord.File("Web_Interaction/removed.png", filename="image.png")
            }
        embed['Embed'].set_image(url='attachment://image.png')
        embed['Embed'].set_author(name="Challenge Enthusiasts", url=("https://cedb.me/game/" + new_game['CE ID']), icon_url=icon)
        embed['Embed'].set_thumbnail(url=ce_hex_icon)
        embed['Embed'].set_footer(text="CE Assistant",
            icon_url=final_ce_icon)
        
        decimal += 1

        embeds.append(embed)


    return embeds


# updates for each objective
def objective_update(type, new_game, old_game):

    update = ""

    if new_game['{} Objectives'.format(type)] != old_game['{} Objectives'.format(type)]:

        objective_tracker = list(old_game['{} Objectives'.format(type)].keys())

        # primary objective loop
        for objective in new_game['{} Objectives'.format(type)]:

            # if objective is new
            if objective in list(new_game['{} Objectives'.format(type)].keys()) and not objective in list(old_game['{} Objectives'.format(type)].keys()):
                update += "🧑‍🦲😼💀😩🥵"
                if objective + " (UNCLEARED)" in list(old_game['{} Objectives'.format(type)].keys()):
                    update += update_embed(new_game, old_game, objective, type, cleared=False)
                elif type == 'Primary':
                    update += "\n- New Primary Objective '**{}**' added:\n\t- {} points <:CE_points:1128420207329816597>\n  - {}".format(objective, new_game['{} Objectives'.format(type)][objective]['Point Value'], new_game['{} Objectives'.format(type)][objective]['Description'])
                else:
                    update += "\n- New Community Objective '**{}**' added:\n\t  - {}".format(objective, new_game['{} Objectives'.format(type)][objective]['Description'])


            # if objective is updated
            elif objective in list(old_game['{} Objectives'.format(type)].keys()) and old_game['{} Objectives'.format(type)][objective] != new_game['{} Objectives'.format(type)][objective]:
                update += "🧑‍🦲😼💀😩🥵"
                update += update_embed(new_game, old_game, objective, type)
            
            # remove objective from tracker
            if objective in objective_tracker : objective_tracker.remove(objective)
            try:
                if objective[0:len(objective)-12] in objective_tracker : objective_tracker.remove(objective)
            except:
                print('hahahaha')

        for objective in objective_tracker:
            # if objective is removed
            if objective in list(old_game['{} Objectives'.format(type)].keys()) and not objective in list(new_game['{} Objectives'.format(type)].keys()):
                update += "🧑‍🦲😼💀😩🥵"
                update += "\n- '**{}**' was removed from the site".format(objective)
    

    return update


# final touches for objective updates
def update_embed(new_game, old_game, objective, type, cleared=True):
    update = ""

    # initialize some shit
    new = new_game['{} Objectives'.format(type)][objective]
    if cleared:
        old = old_game['{} Objectives'.format(type)][objective]
    else:
        old = old_game['{} Objectives'.format(type)][objective + ' (UNCLEARED)']


    # ------------------- check points -------------------
    # points increased
    if not cleared and type == 'Primary':
        update += "\n- '**{}**' cleared, valued at {} points <:CE_points:1128420207329816597>".format(objective, new['Point Value'])
    elif type == 'Primary':
        if new['Point Value'] > old['Point Value']:
            update += "\n- '**{}**' increased from {} <:CE_points:1128420207329816597> ➡ {} points <:CE_points:1128420207329816597>".format(objective, old['Point Value'], new['Point Value'])
                                #<:CE_points:1128420207329816597>

        # points decreased
        elif new['Point Value'] < old['Point Value']:
            update += "\n- '**{}**' decreased from {} <:CE_points:1128420207329816597> ➡ {} points <:CE_points:1128420207329816597>".format(objective, old['Point Value'], new['Point Value'])
        
        # points unchanged
        else:
            update += "\n- '**{}**' updated".format(objective)
    else:
        update += "\n- '**{}**' updated".format(objective)


    # ------------------- check description -------------------
    if new['Description'] != old['Description']:
        update += "\n\t- Description updated"


    # ------------------- check requirements -------------------
    # requirements are new
    if 'Requirements' in list(new.keys()) and not 'Requirements' in list(old.keys()):
        update += "\n  - Requirements added"
    
    # requirements deleted
    elif 'Requirements' in list(old.keys()) and not 'Requirements' in list(new.keys()):
        update += "\n  - Requirements removed"
    
    # requirements changed
    elif 'Requirements' in list(new.keys()) and new['Requirements'] != old['Requirements']:
        update += "\n  - Requirements updated"
    

    # ------------------- check achievements -------------------
    # if achievements are a new requirement
    if 'Achievements' in list(new.keys()) and not 'Achievements' in list(old.keys()):
        
        # initialize added achievement message
        stand_in = "\n  - "

        # achievement loop
        for achievement in new['Achievements']:

            # not the last achievement
            if achievement != new['Achievements'][list(new['Achievements'].keys())[-1]]:
                stand_in += "'{}', ".format(achievement)
            # the last achievement
            else:
                stand_in += "and '{}' added".format(achievement)
        
        # add to message
        update += stand_in
    

    # no more achievements
    elif 'Achievements' in list(old.keys()) and not 'Achievements' in list(new.keys()):
        update += "\n  - All achievements removed"
    

    # achievements changed
    elif 'Achievements' in list(new.keys()) and new['Achievements'] != old['Achievements']:
        
        # initialize new achievements and old achievement tracker
        stand_in = "\n  - Achievements "
        old_achievements = old['Achievements']
        to_delete = []

        # make sure the last achievement is new
        for achievement in new['Achievements']:
            if achievement in list(old_achievements.keys()):
                old_achievements.pop(achievement)
                to_delete.append(achievement)
                
        for achievement in to_delete:
            del new['Achievements'][achievement]

        # checking how long the list will be for grammatical reasons
        grammar_check = len(list(new['Achievements'].keys()))

        # loop through achievements
        for achievement in new['Achievements']:
            
            # new and not last achievement
            if new['Achievements'][achievement] != new['Achievements'][list(new['Achievements'].keys())[-1]]:
                stand_in += "'{}', ".format(new['Achievements'][achievement])

            # the last achievement
            else:
                if grammar_check == 1:
                    stand_in +=  "'{}'".format(new['Achievements'][achievement])
                elif grammar_check == 2:
                    stand_in = stand_in[:-2:] + " and '{}'".format(new['Achievements'][achievement])
                else:
                    stand_in += "and '{}'".format(new['Achievements'][achievement])
        
        stand_in += " added"

        # add to message if pertinent
        if len(stand_in) > 26:
            update += stand_in

        stand_in2 = ""


        # anything left over has been removed
        if len(old_achievements) > 0:

            # checking how long the list will be for grammatical reasons
            grammar_check = len(old_achievements)

            # initialize
            stand_in2 = "\n  - Achievements "

            # loop through each removed game
            for achievement in old_achievements:

                # if no the last one
                if old['Achievements'][achievement] != old_achievements[list(old_achievements.keys())[-1]]:
                    stand_in2 += "'{}', ".format(old['Achievements'][achievement])

                # if it is the last one
                else:
                    if grammar_check == 1:
                        stand_in2 +=  "'{}'".format(old['Achievements'][achievement])
                    elif grammar_check == 2:
                        stand_in2 = stand_in[:-1:] + "and '{}'".format(old['Achievements'][achievement])
                    else:
                        stand_in2 += "and '{}'".format(old['Achievements'][achievement])
        
        stand_in2 += " removed"

        # add to message if pertinent
        if len(stand_in2) > 30:
            update += stand_in2

    return update


# get the game info
def get_game(game, big_game = ""):
    objectives = get_objectives(game['id'])
    returnable = {
        'Name' : game['name'],
        "CE ID" : game['id'],
        'Steam ID' : game['platformId'],
        'Tier' : 'Tier ' + str(game['tier']),
        'Genre' : game['genre']['name'],
        #'Full Completions' : game['completion']['completed'],
        #'Total Owners' : game['completion']['total'],
        'Primary Objectives' : objectives[0],
        'Community Objectives' : objectives[1],
        'Last Updated' : objectives[2]
        }
    if big_game != "":
        returnable['Full Completions'] = big_game['completion']['completed']
        returnable['Total Owners'] = big_game['completion']['total']
    
    return returnable


# get objective info
def get_objectives(CE_ID):
    api_response = requests.get('https://cedb.me/api/game/{}'.format(CE_ID))
    json_response = json.loads(api_response.text)

    objectives = [{}, {}, ""]
    achievements = {}

    for achievement in json_response['achievements']:
        achievements[achievement['id']] = achievement['name']


    for objective in json_response['objectives']:
        index = 0
        achievement_name = {}
        requirements = ''

        if objective['community']:
            index = 1

        for requirement in objective['objectiveRequirements']:
            if requirement['type'] == 'achievement':
                achievement_name[requirement['data']] = achievements[requirement['data']]
            elif requirement['type'] == 'custom':
                requirements = requirement['data']

        objectives[index][objective['name']] = {
            'Description' : objective['description'],
        }

        if not objective['community']:
            objectives[index][objective['name']]['Point Value'] = objective['points']

        if achievement_name != {}:
            objectives[index][objective['name']]['Achievements'] = achievement_name
        if requirements != '':
            objectives[index][objective['name']]['Requirements'] = requirements
    
    updated_time = timestamp_to_unix(json_response['updatedAt'])

    for objective in json_response['objectives'] :
        # was the objective updated
        objupdatedtime = timestamp_to_unix(objective['updatedAt'])
        if updated_time < objupdatedtime : updated_time = objupdatedtime

        # was the objective's requirement updated
        for objrequirement in objective['objectiveRequirements'] :
            objrequpdatedtime = timestamp_to_unix(objrequirement['updatedAt'])
            if updated_time < objrequpdatedtime : updated_time = objrequpdatedtime
    
    objectives[2] = updated_time

    return objectives


# categorize by tier
def get_by_tier(games):
    tier_based_data = {
        'Tier 0' : {
            'Action' : [],
            'Arcade' : [],
            'Bullet Hell' : [],
            'First-Person' : [],
            'Platformer' : [],
            'Strategy' : []
        },
        'Tier 1' : {
            'Action' : [],
            'Arcade' : [],
            'Bullet Hell' : [],
            'First-Person' : [],
            'Platformer' : [],
            'Strategy' : []
        },
        'Tier 2' : {
            'Action' : [],
            'Arcade' : [],
            'Bullet Hell' : [],
            'First-Person' : [],
            'Platformer' : [],
            'Strategy' : []
        },
        'Tier 3' : {
            'Action' : [],
            'Arcade' : [],
            'Bullet Hell' : [],
            'First-Person' : [],
            'Platformer' : [],
            'Strategy' : []
        },
        'Tier 4' : {
            'Action' : [],
            'Arcade' : [],
            'Bullet Hell' : [],
            'First-Person' : [],
            'Platformer' : [],
            'Strategy' : []
        },
        'Tier 5' : {
            'Action' : [],
            'Arcade' : [],
            'Bullet Hell' : [],
            'First-Person' : [],
            'Platformer' : [],
            'Strategy' : []
        },
        'Tier 6' : {
            'Action' : [],
            'Arcade' : [],
            'Bullet Hell' : [],
            'First-Person' : [],
            'Platformer' : [],
            'Strategy' : []
        }
    }
    
    for game in games:
            if game == "_id" : continue
            if games[game]['Tier'] == "Tier 5":
                tot = 0
                for obj in games[game]['Primary Objectives']:
                    tot += games[game]['Primary Objectives'][obj]['Point Value']
                if tot > 1000: continue
                elif tot > 500 : tier_based_data['Tier 6'][games[game]['Genre']].append(game)
                else : tier_based_data[games[game]['Tier']][games[game]['Genre']].append(game)
                continue
            tier_based_data[games[game]['Tier']][games[game]['Genre']].append(game)

    return tier_based_data



def get_completion_data(steam_id):
    response = requests.get("https://steamhunters.com/api/apps/{}/".format(steam_id))
    json_response = response.json()

    if "medianCompletionTime" not in json_response.keys(): 
        return "none"
    else:
        return int(json_response['medianCompletionTime'] / 60)


    response = requests.get("https://steamhunters.com/apps/{}/achievements".format(steam_id))
    site = BeautifulSoup(response.text, features='html.parser')
    ass = site.find_all('i')
    time = "none"
    for a in ass:
        try:
            if(a['class'][2] == "fa-clock-o"):
                end = str(a.parent)[1::].find('m')+1
                time = str(a.parent)[56:end:]
                if len(time) <= 2 :
                    time = "-"
                else :
                    end = str(a.parent)[1::].find('h')+1
                    time = str(a.parent)[56:end:]
        except:
            continue
    
    time.replace(",", "")
    return time



def get_image(number, CE_ID, driver):
    try:
        url = 'https://cedb.me/game/' + CE_ID
        driver.get(url)
        time.sleep(5)
        objective_lst = []
        while(len(objective_lst) < 1 or not objective_lst[0].is_displayed()):
            print(objective_lst)
            objective_lst = []
            objective_lst = driver.find_elements(By.CLASS_NAME, "bp4-html-table-striped")

        
    except :
        print("I'm a doodoo head")
        get_image(number, CE_ID, driver)

    primary_table = driver.find_element(By.CLASS_NAME, "css-c4zdq5")
    print('test 1')
    objective_lst = primary_table.find_elements(By.CLASS_NAME, "bp4-html-table-striped")
    title = driver.find_element(By.TAG_NAME, "h1")
    top_left = driver.find_element(By.CLASS_NAME, "GamePage-Header-Image").location
    title_size = title.size['width']
    title_location = title.location['x']

    print('test 2')

    bottom_right = objective_lst[len(objective_lst)-2].location
    size = objective_lst[len(objective_lst)-2].size

    header_elements = [
        'bp4-navbar',
        'tr-fadein',
        'css-1ugviwv'
    ]

    border_width = 15

    top_left_x = top_left['x'] - border_width
    top_left_y = top_left['y'] - border_width
    bottom_right_y = bottom_right['y'] + size['height'] + border_width

    if title_location + title_size > bottom_right['x'] + size['width']:
        bottom_right_x = title_location + title_size + border_width
    else:
        bottom_right_x = bottom_right['x'] + size['width'] + border_width

    print('test 3')
    ob = Screenshot(bottom_right_y)
    print('test 4')
    im = ob.full_screenshot(driver, save_path=r'Pictures/', image_name="ss{}.png".format(number), is_load_at_runtime=True, load_wait_time=10, hide_elements=header_elements)
    im = io.BytesIO(im)
    im_image = Image.open(im)
    im_image = im_image.crop((top_left_x, top_left_y, bottom_right_x, bottom_right_y))

    imgByteArr = io.BytesIO()
    im_image.save(imgByteArr, format='PNG')
    final_im = imgByteArr.getvalue()
    
    return final_im
    
    return im
    print('test 5')

    print('Pictures/ss{}.png'.format(number))
    print('/CE-Assistant/Pictures/ss{}.png'.format(number))

    im = Image.open('/CE-Assistant/Pictures/ss{}.png'.format(number))
    print('test 6')
    im = im.crop((top_left_x, top_left_y, bottom_right_x, bottom_right_y)) # defines crop points
    print('test 7')
    im.save('/CE-Assistant/Pictures/ss{}.png'.format(number))
    print('test 8')




def special_image(number, decimal, CE_ID, driver, objective_name : str):
    try:
        url = 'https://cedb.me/game/' + CE_ID
        driver.get(url)
        time.sleep(5)
        objective_lst = []
        while(len(objective_lst) < 1 or not objective_lst[0].is_displayed()):
            objective_lst = []
            objective_lst = driver.find_elements(By.TAG_NAME, "tr")

        
    except :
        print("I'm a doodoo head")
        special_image(number, decimal, CE_ID, driver, objective_name)

    print('\nobjective looking: ' + objective_name)
    
    objective_name = objective_name.lower()
    objective_name = objective_name.replace(" ", '')
    objective_name = objective_name.replace("\n", '')
    objective_name = objective_name.replace("0", '')
    print(objective_name)
    print('objectives in objective list')
    for objective in objective_lst:
        check_name = str(objective.find_element(By.TAG_NAME, "h3").text)
        check_name = check_name.lower()
        check_name = check_name.replace(" ",'')
        check_name = check_name.replace("\n", '')
        check_name = check_name.replace("0", '')
        print(check_name)
        print(check_name == objective_name)
        if objective_name == check_name:
            print('yeayuhhhh"')
            target_objective = objective
            break
    
    try:
        target_objective
    except NameError:
        print('not found!!')
        return "none"
    
    
    top_left = target_objective.location
    bottom_right = target_objective.location
    size = target_objective.size

    header_elements = [
        'bp4-navbar',
        'tr-fadein',
        'css-1ugviwv'
    ]

    border_width = 15

    top_left_x = top_left['x'] - border_width
    top_left_y = top_left['y'] - border_width
    bottom_right_y = bottom_right['y'] + size['height'] + border_width
    bottom_right_x = bottom_right['x'] + size['width'] + border_width

    
    ob = Screenshot(bottom_right_y)
    im = ob.full_screenshot(driver, save_path=r'Pictures/', image_name="ss{}.png".format(number), is_load_at_runtime=True, load_wait_time=10, hide_elements=header_elements)
    im = io.BytesIO(im)
    im_image = Image.open(im)
    im_image = im_image.crop((top_left_x, top_left_y, bottom_right_x, bottom_right_y))

    imgByteArr = io.BytesIO()
    im_image.save(imgByteArr, format='PNG')
    final_im = imgByteArr.getvalue()
    
    return final_im

    """im = Image.open('/CE-Assistant/Pictures/ss{}.png'.format(str(number) + '-' + str(decimal)))
    im = im.crop((top_left_x, top_left_y, bottom_right_x, bottom_right_y)) # defines crop points
    im.save('/CE-Assistant/Pictures/ss{}.png'.format(str(number) + '-' + str(decimal)))

    return"""