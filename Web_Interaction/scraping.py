

#-----------------------------------------------------------------------------------------#
#                                                                                         #
"                                    DATA SCRAPER                                         "
#                                                                                         #
#               updates both databases (tier and name) every 15 minutes                   #      
#                    and sends update logs to the desired channel                         #
#                                                                                         #
#-----------------------------------------------------------------------------------------#


# the basics
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


# set basic icons
ce_hex_icon = "https://cdn.discordapp.com/attachments/639112509445505046/891449764787408966/challent.jpg"
ce_james_icon = "https://cdn.discordapp.com/attachments/1028404246279888937/1136056766514339910/CE_Logo_M3.png"
final_ce_icon = "https://cdn.discordapp.com/attachments/1135993275162050690/1144289627612655796/image.png"



# Grab information from json file
# with open('Jasons/secret_info.json') as f :
#     localJSONData = json.load(f)

# steam_api_key = localJSONData['steam_API_key']


def get_games(database_name, curator_count):

    # create our returnable and update database_name
    fin = game_list(database_name, curator_count)
    # use database_name to update database_tier
    database_tier = get_by_tier(database_name)
    fin.append(database_tier)
    # return embeds
    return fin


def single_scrape(curator_count):
    api_response = requests.get('https://cedb.me/api/games')
    json_response = json.loads(api_response.text)

    curator_count['Updated Time'] = int(time.mktime(datetime.now().timetuple()))

    database_name = {}

    for game in json_response:
        if(game['genre'] == None or game['genre']['name'] == None) : continue
        print(game['name'])
        database_name[game['name']] = get_game(game)

    database_tier = get_by_tier(database_name)

    return [database_name, curator_count, database_tier]

    

def game_list(new_data, current_dict):
    # Set selenium driver and preferences
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)
    print(driver)
    driver.set_window_size(width=1440, height=8000)

    # grab first game to get color on the rest of them
    url = 'https://cedb.me/game/1e8565aa-b9f2-4b41-9578-22e4c2a5436b'
    driver.get(url)
    print(driver.page_source)
    objective_lst = []
    while(len(objective_lst) < 1 or not objective_lst[0].is_displayed()):
        objective_lst = driver.find_elements(By.CLASS_NAME, "bp4-html-table-striped")
        print(objective_lst)


    # set up API requests
    api_response = requests.get('https://cedb.me/api/games')
    json_response = json.loads(api_response.text)

    # grab last updated time
    current_newest = current_dict['Updated Time']
    current_dict['Updated Time'] = int(time.mktime(datetime.now().timetuple()))
    
    # grab the new data and initialize trackers
    number = 0
    updated_games = []
    game_tracker = list(new_data.keys())
    game_tracker.remove('_id')


    # icons for CE emoji
    icons = {
        "Tier 0" : '<:tier0:1126268390605070426>',
        "Tier 1" : '<:tier1:1126268393725644810>',
        "Tier 2" : '<:tier2:1126268395483037776>',
        "Tier 3" : '<:tier3:1126268398561677364>',
        "Tier 4" : '<:tier4:1126268402596585524>',
        "Tier 5" : '<:tier5:1126268404781809756>',
        "Tier 6" : '<:tier6:1126268408116285541>',
        "Tier 7" : '<:tier7:1126268411220074547>',

        "Action" : '<:CE_action:1126326215356198942>',
        "Arcade" : '<:CE_arcade:1126326209983291473>',
        "Bullet Hell" : '<:CE_bullethell:1126326205642190848>',
        "First-Person" : '<:CE_firstperson:1126326202102186034>',
        "Platformer" : '<:CE_platformer:1126326197983383604>',
        "Strategy" : '<:CE_strategy:1126326195915591690>'
    }

    get_image(0, "1e866995-6fec-452e-81ba-1e8f8594f4ea", driver)

    # game loop adding updated parts
    for game in json_response:
        print(game['name'])

        # check if updated since last check
        updated_time = time.mktime(datetime.strptime(str(game['updatedAt'][:-5:]), "%Y-%m-%dT%H:%M:%S").timetuple())
        created_time = time.mktime(datetime.strptime(str(game['createdAt'][:-5:]), "%Y-%m-%dT%H:%M:%S").timetuple())
        icon = game['icon']

        # if game is a T0 and updated
        if updated_time > current_newest and game['tier'] == 0 and game['name'] in list(new_data.keys()):
            # update game tracker
            game_tracker.remove(game['name'])

            # get old data
            test_old = new_data[game['name']]

            # get new data that wont be mutated
            to_keep = get_game(game)

            # create maluable data
            test_new = to_keep

            # remove completion data for comparisons
            test_new['Full Completions'] = None
            test_new['Total Owners'] = None
            test_old['Full Completions'] = None
            test_old['Total Owners'] = None

            # compare old and new data excluding completion data
            if test_old != test_new:
                updated_games.extend(special_update(to_keep, new_data[game['name']], driver, number, icon, icons, game['name']))
                number += 1

            # update data
            new_data[game['name']] = get_game(game)

        # if game is updated
        elif updated_time > current_newest and game['name'] in list(new_data.keys()):
            print("UPDATED: " + game["name"])
            game_tracker.remove(game['name'])
            test_old = new_data[game['name']]
            to_keep = get_game(game)
            test_new = to_keep
            test_new['Full Completions'] = None
            test_new['Total Owners'] = None
            test_old['Full Completions'] = None
            test_old['Total Owners'] = None
            if test_old != test_new:
                updated_games.append(update(to_keep, new_data[game['name']], driver, number, icon, icons, game['name']))
                number += 1
            new_data[game['name']] = get_game(game)

        # if game is new
        # elif not game['name'] in list(new_data.keys()) and game['genreId'] != None:
        elif created_time > current_newest:
            print("NEW: " + game['name'])
            if game['tier'] == 0 : 
                print('tier 0')
                continue
            get_image(number, game['id'], driver)
            new_game = get_game(game)
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
            embed = {
                'Embed' : discord.Embed(
                    title="__" + game['name'] + "__ added to the site", 
                    colour= 0x48b474,
                    timestamp=datetime.now(),
                    description="\n- {} {}\n- {} Primary Objective{} worth {} points{}".format(icons[new_game['Tier']], icons[new_game['Genre']], len(list(new_game['Primary Objectives'])), second_part, points, third_part)
                ),
                'Image' : discord.File("/CE-Assistant/Pictures/ss{}.png".format(number), filename="image.png")
            }
            embed['Embed'].set_image(url='attachment://image.png')
            embed['Embed'].set_author(name="Challenge Enthusiasts", url="https://cedb.me", icon_url=icon)
            embed['Embed'].set_thumbnail(url=ce_hex_icon)
            embed['Embed'].set_footer(text="CE Assistant",
                icon_url=final_ce_icon)
           
            updated_games.append(embed)
            number += 1

        # game is neither new nor updated
        elif game['name'] in game_tracker:
            game_tracker.remove(game['name'])
        elif not game['name'] in list(new_data.keys()) and game['genreId'] != None:
            for other_game in json_response:
                if game['id'] == other_game['id']:
                    game_tracker.remove(other_game['name'])
                    del(new_data[other_game['name']])
                    new_data[game['name']] = get_game(game)


    # games removed
    for game in game_tracker:
        embed = {
            'Embed' : discord.Embed(
                title=game,
                colour= 0xce4e2c,
                timestamp=datetime.now()
            ),
            'Image' : discord.File("Web_Interaction/removed.png", filename="image.png")
        }
        embed['Embed'].set_image(url='attachment://image.png')
        updated_games.append(embed)
        del new_data[game]

    return [updated_games, number, new_data, current_dict]


# updates for games
def update(new_game, old_game, driver, number, icon, icons, name):
    # get game info and image
    #new_game = get_game(game)
    get_image(number, new_game['CE ID'], driver)

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

    if new_points != old_points:
        update += "\n- {} ➡ {}".format(old_points, new_points)

    # ------------------- check Genre -------------------
    if new_game['Genre'] != old_game['Genre']:
        update += "\n- {} ➡ {}".format(icons[old_game['Genre']], icons[new_game['Genre']])


    # ------------------- check objectives -------------------
    update += objective_update('Primary', new_game, old_game).replace('🧑‍🦲😼💀😩🥵', '')
    update += objective_update('Community', new_game, old_game).replace('🧑‍🦲😼💀😩🥵', '')

    # ------------------- make final embed -------------------
    embed = {
        'Embed' : discord.Embed(
            title="__" + name + "__ updated on the site:",
            colour= 0xefd839,
            timestamp=datetime.now(),
            description=update.strip()
        ),
        'Image' : discord.File("/CE-Assistant/Pictures/ss{}.png".format(number), filename="image.png")
    }
    embed['Embed'].set_image(url='attachment://image.png')
    embed['Embed'].set_author(name="Challenge Enthusiasts", url="https://cedb.me", icon_url=icon)
    embed['Embed'].set_thumbnail(url=ce_hex_icon)
    embed['Embed'].set_footer(text="CE Assistant",
        icon_url=final_ce_icon)

    # return :)
    return embed


def special_update(new_game, old_game, driver, number, icon, icons, name):
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
        special_image(number, decimal, new_game['CE ID'], driver, objective)

        embed = {
        'Embed' : discord.Embed(
            title="__" + name + "__ updated on the site:",
            colour= 0xefd839,
            timestamp=datetime.now(),
            description=objective_info.strip()
        ),
        'Image' : discord.File("/CE-Assistant/Pictures/ss{}.png".format(str(number) + '-' + str(decimal)), filename="image.png")
        }
        embed['Embed'].set_image(url='attachment://image.png')
        embed['Embed'].set_author(name="Challenge Enthusiasts", url="https://cedb.me", icon_url=icon)
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

            # if objective is removed
            elif objective in list(old_game['{} Objectives'.format(type)].keys()) and not objective in list(new_game['{} Objectives'.format(type)].keys()):
                update += "🧑‍🦲😼💀😩🥵"
                update += "'**{}**' was removed from the site".format(objective)
    

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
        update += "\n\t- Description Updated"


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
        stand_in = "\n- Achievements "
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
                    stand_in +=  " '{}'".format(new['Achievements'][achievement])
                elif grammar_check == 2:
                    stand_in = stand_in[:-2:] + " and '{}'".format(new['Achievements'][achievement])
                else:
                    stand_in += "and '{}'".format(new['Achievements'][achievement])

        # add to message if pertinent
        if len(stand_in) > 17:
            update += stand_in


        # anything left over has been removed
        if len(old_achievements) > 0:

            # checking how long the list will be for grammatical reasons
            grammar_check = len(old_achievements)

            # initialize
            stand_in = "\n\t- Achievements "

            # loop through each removed game
            for achievement in old_achievements:

                # if no the last one
                if old['Achievements'][achievement] != old_achievements[list(old_achievements.keys())[-1]]:
                    stand_in += "'{}', ".format(old['Achievements'][achievement])

                # if it is the last one
                else:
                    if grammar_check == 1:
                        stand_in +=  " '{}'".format(old['Achievements'][achievement])
                    elif grammar_check == 2:
                        stand_in = stand_in[:-1:] + "and '{}'".format(old['Achievements'][achievement])
                    else:
                        stand_in += "and '{}'".format(old['Achievements'][achievement])

        # add to message if pertinent
        if len(stand_in) > 17:
            update += stand_in

    return update


# get the game info
def get_game(game):
    objectives = get_objectives(game['id'])
    returnable = {
        "CE ID" : game['id'],
        'Steam ID' : game['platformId'],
        'Tier' : 'Tier ' + str(game['tier']),
        'Genre' : game['genre']['name'],
        'Full Completions' : game['completion']['completed'],
        'Total Owners' : game['completion']['total'],
        'Primary Objectives' : objectives[0],
        'Community Objectives' : objectives[1]
        }
    
    return returnable


# get objective info
def get_objectives(CE_ID):
    api_response = requests.get('https://cedb.me/api/game/{}'.format(CE_ID))
    json_response = json.loads(api_response.text)

    objectives = [{}, {}]
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
        }
    }
    
    for game in games:
            tier_based_data[games[game]["Tier"]][games[game]["Genre"]].append(game)

    return tier_based_data



def get_completion_data(steam_id):
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
    print('test 5')

    print('Pictures/ss{}.png'.format(number))
    print('/CE-Assistant/Pictures/ss{}.png'.format(number))

    im = Image.open('/CE-Assistant/Pictures/ss{}.png'.format(number))
    print('test 6')
    im = im.crop((top_left_x, top_left_y, bottom_right_x, bottom_right_y)) # defines crop points
    print('test 7')
    im.save('/CE-Assistant/Pictures/ss{}.png'.format(number))
    print('test 8')




def special_image(number, decimal, CE_ID, driver, objective_name):
    try:
        url = 'https://cedb.me/game/' + CE_ID
        driver.get(url)
        objective_lst = []
        while(len(objective_lst) < 1 or not objective_lst[0].is_displayed()):
            objective_lst = []
            objective_lst = driver.find_elements(By.TAG_NAME, "tr")

        
    except :
        print("I'm a doodoo head")
        special_image(number, decimal, CE_ID, driver, objective_name)


    for objective in objective_lst:
        if objective_name == objective.find_element(By.TAG_NAME, "h3").text:
            target_objective = objective
            break
    
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
    im = ob.full_screenshot(driver, save_path=r'Pictures/', image_name="ss{}.png".format(str(number) + '-' + str(decimal)), is_load_at_runtime=True, load_wait_time=3, hide_elements=header_elements)
    im = Image.open('/CE-Assistant/Pictures/ss{}.png'.format(str(number) + '-' + str(decimal)))
    im = im.crop((top_left_x, top_left_y, bottom_right_x, bottom_right_y)) # defines crop points
    im.save('/CE-Assistant/Pictures/ss{}.png'.format(str(number) + '-' + str(decimal)))

    return