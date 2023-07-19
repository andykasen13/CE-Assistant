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
    # print(get_objectives('1e866995-6fec-452e-81ba-1e8f8594f4ea'))
    # driver = webdriver.Chrome()
    game_list()
    # game_data(driver)
    # get_completion_data('504230')
    # get_by_tier()
    # game_updates = all_game_data(driver)
    # get_data('1e866995-6fec-452e-81ba-1e8f8594f4ea', driver)
    # get_name_data(driver)
    # get_update()

    # return game_updates
    



def game_list():
    api_response = requests.get('https://cedb.me/api/games')
    json_response = json.loads(api_response.text)

    new_data = {}

    for game in json_response:
        #objectives = get_objectives(game['id'])
        new_data[game['name']] = get_game(game)

    with open('./Jasons/database_name.json', 'w') as f :
        json.dump(new_data, f, indent=4)

    print('done')
    new_data = None
    

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
        achievement_name = []
        requirements = ''
        if objective['community']:
            index = 1
        

        for requirement in objective['objectiveRequirements']:
            if requirement['type'] == 'achievement':
                achievement_name.append(achievements[requirement['data']])
            elif requirement['type'] == 'custom':
                requirements = requirement['data']


        objectives[index][objective['name']] = {
            'Description' : objective['description'],
            'Point Value' : objective['points']
        }

        if achievement_name != []:
            objectives[index][objective['name']]['Achievements'] = achievement_name
        if requirements != '':
            objectives[index][objective['name']]['Requirements'] = requirements


    return objectives


def get_update():
    new = json.loads(open("./Jasons/test_database_2.json").read()) #game_list()
    old = json.loads(open("./Jasons/test_database.json").read())
    
    if new != old:
        differences = DeepDiff(old, new, verbose_level=2)
        print(differences)
        keys = list(differences.keys())

        updated_games = {}

        if keys.count('values_changed') > 0:
            for change in differences['values_changed']:
                updated_games = values_changed(change, differences['values_changed'][change])

        if keys.count('dictionary_item_added') > 0:
            return
        
        if keys.count('dictionary_item_removed') > 0:
            return
        

    else:
        return 'Up to date!'



def values_changed(change, values):
    updated_games = {}
    game = change[change.find("['")+2:change.find("']"):]
    edit = change[change.rfind("['")+2:change.rfind("']")]
    new_value = values['new_value']
    old_value = values['old_value']

    location = get_title(change)
    print(location)

    if list(updated_games.keys()).count(game) < 1:
        updated_games[game] = discord.Embed(
            title=game,
            colour= 0xefd839,
            timestamp=datetime.now()
        )

    updated_games[game].add_field(name=edit, value="{} ➡ {}".format(old_value, new_value))
    return updated_games


def get_title(root):
    address = []
    if len(root) > 2:
        next = root[root.find("['")+2:root.find("']"):]
        new_root = root[root.find("']")+2::]
        address.append(next)
        address.extend(get_title(new_root))
        
    return address



def all_game_data():
    games = json.loads(open("./Jasons/test_database.json").read())

    game_updates = []
    i = 0
    for game in games:
        data = get_game(games[game])
        if (games[game] != data):
            to_send = update(games[game]["CE ID"], game, games[game], data, i)
            i+=1
            games[game] = data
            game_updates.append(to_send)
        else:
            data = None

    # with open('./Jasons/test_database.json', 'w') as f :
    #     json.dump(games, f, indent=4)

    return game_updates



def update(CE_ID, name, old_data, new_data, number):
    get_image(CE_ID, number)
    file = discord.File("Web_Interaction/ss{}.png".format(number), filename="image.png")
    embed = discord.Embed(
        title=name,
        url=f"https://store.steampowered.com/app/{new_data['Steam ID']}/{name.replace(' ', '_')}/",
        colour= 0xefd839,
        timestamp=datetime.now()
        )
    embed.set_image(url='attachment://image.png')


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

    ddiff = DeepDiff(old_data, new_data)

    if list(ddiff.keys()).count('values_changed'):
        for value in ddiff['values_changed']:
            if(list(icons.keys()).count(ddiff['values_changed'][value]['new_value']) > 0):
                ddiff['values_changed'][value]['new_value'] = icons[ddiff['values_changed'][value]['new_value']]
            if(list(icons.keys()).count(ddiff['values_changed'][value]['old_value']) > 0):
                ddiff['values_changed'][value]['old_value'] = icons[ddiff['values_changed'][value]['old_value']]
            embed.add_field(name=value[value.rfind('[')+2:value.rfind('\''):], value="{} ➡ {}".format(ddiff['values_changed'][value]['old_value'], ddiff['values_changed'][value]['new_value']))

    
    if list(ddiff.keys()).count('dictionary_item_added'):
        for value in ddiff['dictionary_item_added']:
            name_change = False
            if list(ddiff.keys()).count('dictionary_item_removed'):
                for other_value in ddiff['dictionary_item_removed']:
                    if(ddiff['dictionary_item_added'][value]==ddiff['dictionary_item_removed'][other_value]):
                        embed.add_field(name="Objective Name Change", value="{} ➡ {}".format(other_value[other_value.rfind('[')+2:other_value.rfind('\''):], value[value.rfind('[')+2:value.rfind('\''):]))
                        name_change = True
                    else:
                        embed.add_field(name='Objective Removed', value=other_value[other_value.rfind('[')+2:other_value.rfind('\''):])
            if not name_change:
                embed.add_field(name='New Objective', value=value[value.rfind('[')+2:value.rfind('\''):])


    for primary in old_data['Primary Objectives']:
        if list(old_data['Primary Objectives'][primary].keys()).count('Achievements') > 0 and list(new_data['Primary Objectives'][primary].keys()).count('Achievements') > 0 and old_data['Primary Objectives'][primary]['Achievements'] != new_data['Primary Objectives'][primary]['Achievements']:
            print("gets here")
            achievement_change = DeepDiff(old_data['Primary Objectives'][primary]['Achievements'], new_data['Primary Objectives'][primary]['Achievements'])
            if list(achievement_change.keys()).count('dictionary_item_added') > 0:
                for addition in achievement_change['dictionary_item_added']:
                    embed.add_field(name="Achievement Added", value=addition)
            if list(achievement_change.keys()).count('dictionary_item_removed') > 0:
                for addition in achievement_change['dictionary_item_removed']:
                    embed.add_field(name="Achievement Removed", value=addition)

    
    return [embed, file]
    


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


def get_image(CE_ID, number):
    options = Options()
    #options.add_argument('headless')
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(width=1440, height=2000)
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

    # return(discord.file('ss.png'))