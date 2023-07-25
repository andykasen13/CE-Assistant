from asyncio import to_thread
import json
from datetime import datetime
import re
import time
# import screenshot
from .Screenshot import Screenshot
from bs4 import BeautifulSoup
import discord
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from PIL import Image
from deepdiff import DeepDiff
from pprint import pprint
from selenium.webdriver.support.color import Color
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC




# Grab information from json file
with open('Jasons/secret_info.json') as f :
    localJSONData = json.load(f)

steam_api_key = localJSONData['steam_API_key']


def get_games():
    fin = game_list()
    get_by_tier()
    return fin

    



def game_list():
    options = Options()
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(width=1440, height=2000)

    api_response = requests.get('https://cedb.me/api/games')
    json_response = json.loads(api_response.text)

    current_dict = json.loads(open("./Jasons/curator_count.json").read())
    current_newest = current_dict['Updated Time']
    current_dict['Updated Time'] = int(time.mktime(datetime.now().timetuple()))
    
    new_data = json.loads(open("./Jasons/database_name.json").read())
    number = 0

    for game in json_response:
        updated_time = time.mktime(datetime.strptime(str(game['updatedAt'][:-5:]), "%Y-%m-%dT%H:%M:%S").timetuple())
        if updated_time > current_newest:
            update(game, current_dict[game['name']], driver, number)
            number += 1
            new_data[game['name']] = get_game(game)


    # with open('Jasons/curator_count.json', 'w') as f:
    #     json.dump(current_dict, f, indent=4)
    # with open('./Jasons/database_name.json', 'w') as f :
    #     json.dump(new_data, f, indent=4)

    print('done')
    return new_data


def update(game, old_game, driver, number):
    icons = {
        "Tier 0" : ':zero:',
        "Tier 1" : ':one:',
        "Tier 2" : ':two:',
        "Tier 3" : ':three:',
        "Tier 4" : ':four:',
        "Tier 5" : ':five:',

        "Action" : ':magnet:',
        "Arcade" : ':video_game:',
        "Bullet Hell" : ':gun:',
        "First-Person" : ':person_bald:',
        "Platformer" : ':runner:',
        "Strategy" : ':chess_pawn:'
    }
        
    new_game = get_game(game)
    get_image(game, number, new_game, driver)
    embed = {
        'Embed' : discord.Embed(
            title=game,
            colour= 0xefd839,
            timestamp=datetime.now()
        ),
        'Image' : discord.File("Web_Interaction/ss{}.png".format(number), filename="image.png")
    }
    embed.set_image(url='attachment://image.png')
    update = ""
    
    #check tier
    if new_game['Tier'] != old_game['Tier']:
        update += "\n{} ➡ {}".format(icons[old_game['Tier']], icons[new_game['Tier']])

    #check Genre
    if new_game['Genre'] != old_game['Genre']:
        update += "\n{} ➡ {}".format(icons[old_game['Tier']], icons[new_game['Tier']])

    #check primary objectives
    if new_game['Primary Objectives'] != old_game['Primary Objectives']:
        for objective in new_game['Primary Objectives']:
            if list(old_game['Primary Objectives'].keys()).contains(objective) and old_game['Primary Objectives'] != new_game['Primary Objectives']:
                # check description
                if new_game['Primary Objectives']['Description'] != old_game['Primary Objectives']['Description']:
                    update += "\nDescription Updated"
                if new_game['Primary Objectives']['Point Value'] != old_game['Primary Objectives']['Point Value']:
                    update += "\n{} :star: ➡ {} :star:".format(old_game['Point Value'], new_game['Point Value'])

    return

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


def get_update():
    new = game_list()
    old = json.loads(open("./Jasons/database_name.json").read())
    
    if new != old:
        options = Options()
        options.add_argument('headless')
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(width=1440, height=2000)

        differences = DeepDiff(old, new, verbose_level=2)
        keys = list(differences.keys())

        image_number = 0
        updated_games = {}
        # added_games = {}
        # removed_games = {}
        

        if keys.count('values_changed') > 0:
            for change in differences['values_changed']:
                location = get_title(change)
                if location[1] == 'Total Owners' or location[1] == 'Full Completions':
                    continue
                updated_games = values_changed(driver, location, differences['values_changed'][change], image_number, updated_games, new)
                image_number+=1

        if keys.count('dictionary_item_added') > 0:
            for addition in differences['dictionary_item_added']:
                location = get_title(addition)
                updated_games = added(driver, location, differences['dictionary_item_added'][addition], image_number, updated_games, new)
                image_number+=1
        
        if keys.count('dictionary_item_removed') > 0:
            for removed in differences['dictionary_item_removed']:
                location = get_title(removed)
                updated_games = removal(location, differences['dictionary_item_removed'][removed], updated_games)
                image_number+=1
        
        games = [updated_games, updated_games, updated_games]

        # with open('./Jasons/database_name.json', 'w') as f :
        #     json.dump(new, f, indent=4)

        return games
    else:
        print('Up to date!')
        return []


def values_changed(driver, location, values, number, updated_games, new):
    
    icons = {
        "Tier 0" : ':zero:',
        "Tier 1" : ':one:',
        "Tier 2" : ':two:',
        "Tier 3" : ':three:',
        "Tier 4" : ':four:',
        "Tier 5" : ':five:',

        "Action" : ':magnet:',
        "Arcade" : ':video_game:',
        "Bullet Hell" : ':gun:',
        "First-Person" : ':person_bald:',
        "Platformer" : ':runner:',
        "Strategy" : ':chess_pawn:'
    }

    if list(icons.keys()).count(values['new_value']) > 0:
        new_value = icons[values['new_value']]
    else:
        new_value = values['new_value']

    if list(icons.keys()).count(values['old_value']) > 0:
        old_value = icons[values['old_value']]
    else:
        old_value = values['old_value']

    game = location.pop(0)
    title = ''
    while len(location) > 0:
        if location[0] == 'Achievements':
            title = title + " : " + " Achievement Name"
            break
        title = title + " : " + location.pop(0)
    title += " changed"


    if list(updated_games.keys()).count(game) < 1:
        get_image(game, number, new, driver)
        updated_games[game] = {
            'Embed' : discord.Embed(
                title=game,
                colour= 0xefd839,
                timestamp=datetime.now()
            ),
            'Image' : discord.File("Web_Interaction/ss{}.png".format(number), filename="image.png")
        }
        updated_games[game]['Embed'].set_image(url='attachment://image.png')
        
    updated_games[game]['Embed'].add_field(name=title, value="{} ➡ {}".format(old_value, new_value))
    return updated_games


def removal(location, value, updated_games):
    game = location.pop(0)
    title = ''
    while len(location) > 0:
        if location[0] == 'Achievements':
            title = title + " : " + "Achievement"
            break
        title = title + " : " + location.pop(0)
    title += " Removed"

    if list(updated_games.keys()).count(game) < 1:
        updated_games[game] = {
            'Embed' : discord.Embed(
                title=game,
                colour= 0xce502c,
                timestamp=datetime.now()
            ),
            'Image' : discord.File("Web_Interaction/removed.png", filename="image.png")
        }
        updated_games[game]['Embed'].set_image(url='attachment://image.png')
        
    updated_games[game]['Embed'].add_field(name=title, value="{} was removed".format(value))
    return updated_games


def added(driver, location, value, number, updated_games, new):
    game = location.pop(0)
    title = ''
    while len(location) > 0:
        if location[0] == 'Achievements':
            title = title + " : " + "Achievement"
            break
        title = title + " : " + location.pop(0)
    title += " added"

    if list(updated_games.keys()).count(game) < 1:
        get_image(game, number, new, driver)
        updated_games[game] = {
            'Embed' : discord.Embed(
                title=game,
                colour= 0x48b474,
                timestamp=datetime.now()
            ),
            'Image' : discord.File("Web_Interaction/ss{}.png".format(number), filename="image.png")
        }
        updated_games[game]['Embed'].set_image(url='attachment://image.png')
        
    updated_games[game]['Embed'].add_field(name=title, value="{} was added".format(value))
    return updated_games


def get_title(root):
    address = []
    if len(root) > 2:
        next = root[root.find("['")+2:root.find("']"):]
        new_root = root[root.find("']")+2::]
        address.append(next)
        address.extend(get_title(new_root))
        
    return address
    


def get_by_tier():
    games = json.loads(open("./Jasons/database_name.json").read())
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

    with open('./Jasons/database_tier.json', 'w') as f :
        json.dump(tier_based_data, f, indent=4)


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
                    time = 0
                else :
                    end = str(a.parent)[1::].find('h')+1
                    time = str(a.parent)[56:end:]
        except:
            continue

    return time


def get_image(game_name, number, new_data, driver):
    CE_ID = new_data[game_name]['CE ID']
    url = 'https://cedb.me/game/' + CE_ID
    driver.get(url)

    objective_lst = []
    while(len(objective_lst) < 1 or not objective_lst[0].is_displayed()):
        objective_lst = driver.find_elements(By.CLASS_NAME, "bp4-html-table-striped")

    top_left = driver.find_element(By.CLASS_NAME, "GamePage-Header-Image").location
    bottom_right = objective_lst[len(objective_lst)-2].location
    size = objective_lst[len(objective_lst)-2].size

    header_elements = [
        'bp4-navbar',
        'tr-fadein'
    ]
    border_width = 15
    ob = Screenshot(bottom_right['y']+size['height']+border_width)
    im = ob.full_screenshot(driver, save_path=r'Web_Interaction/', image_name="ss{}.png".format(number), is_load_at_runtime=True, load_wait_time=3, hide_elements=header_elements)

    
    im = Image.open('Web_Interaction/ss{}.png'.format(number))
    im = im.crop((top_left['x']-border_width, top_left['y']-border_width, bottom_right['x']+size['width']+border_width, bottom_right['y']+size['height']+border_width)) # defines crop points
    im.save('Web_Interaction/ss{}.png'.format(number))