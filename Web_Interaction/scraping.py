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

    driver = webdriver.Chrome()
    # game_list(driver)
    # game_data(driver)
    # get_completion_data('504230')
    # get_by_tier()
    game_updates = all_game_data(driver)
    # get_data('1e866995-6fec-452e-81ba-1e8f8594f4ea', driver)
    # get_name_data(driver)

    return game_updates
    



def game_list(driver):
    driver.get('https://cedb.me/games')
    button_enabled = True
    games = {}

    while(button_enabled):
        names = driver.find_elements(By.TAG_NAME, "h2")[::2]
        while(len(names) < 1 or not names[0].is_displayed()):
            names = driver.find_elements(By.TAG_NAME, "h2")[::2]

        ids = driver.find_elements(By.CSS_SELECTOR, ":link")[7::2]
        button = driver.find_elements(By.TAG_NAME, "button")[30]

        for i in range(0, len(names)):
            games[names[i].text] = {
                "CE ID" : ids[i].get_attribute("href")[21::],
            }

        # button_enabled=False
        if(not button.is_enabled()):
            print("done")
            button_enabled=False
        else:
            button.click()


    with open('./Jasons/database_name.json', 'w') as f :
        json.dump(games, f, indent=4)

    games = None
    


def all_game_data(driver):
    # driver = webdriver.Chrome()
    games = json.loads(open("./Jasons/test_database.json").read())

    game_updates = []
    i = 0
    for game in games:
        data = get_data(games[game]["CE ID"], driver)
        if (games[game] != data):
            to_send = update(games[game]["CE ID"], game, games[game], data, i)
            i+=1
            games[game] = data
            game_updates.append(to_send)
            # correctChannel = client.get_channel(1128742486416834570)
            # await correctChannel.send(file=to_send[1], embed=to_send[0])
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


def get_name_data(driver):
    games = json.loads(open("./Jasons/database_name.json").read())

    for game in games:
        games[game] = get_data(games[game]['CE ID'], driver)

    with open('./Jasons/database_name.json', 'w') as f :
        json.dump(games, f, indent=4)
    

def get_data(id, driver):
    url = "https://cedb.me/game/" + id
    driver.get(url)
    
    table_list = []
    while(len(table_list) < 1 or not table_list[0].is_displayed()):
        table_list = driver.find_elements(By.CLASS_NAME, "bp4-html-table-striped")

    primary_objectives_string = table_list[0].find_elements(By.TAG_NAME, "tr")
    community_objectives_string = table_list[1].find_elements(By.TAG_NAME, "tr")

    tier_and_genre = driver.find_elements(By.CLASS_NAME, "bp4-fill")
    app_id = driver.find_element(By.CLASS_NAME, 'no-decoration').get_attribute("href")[34::]
    tier = tier_and_genre[0].text
    genre = tier_and_genre[1].text
    headings = driver.find_elements(By.TAG_NAME, "h2")
    community_objectives_exist = headings[1].text == "Community Objectives"


    primary_objectives = {}
    community_objectives = {}


    for primary_objectives_element in primary_objectives_string:
        primary_objectives_list = primary_objectives_element.text.split('\n')
        while(len(primary_objectives_list) > 0):
            achievements = []
            intermediate = {}
            title = primary_objectives_list.pop(0)
            intermediate["Point Value"] = primary_objectives_list.pop(0)
            intermediate["Description"] = primary_objectives_list.pop(0)
            if(len(primary_objectives_list) > 0 and primary_objectives_list[0] == "Achievements:"):
                primary_objectives_list.pop(0)
                while(len(primary_objectives_list) > 0 and primary_objectives_list[0] != "Requirements:"):
                    achievements.append(primary_objectives_list.pop(0))
                intermediate["Achievements"] = achievements
            if(len(primary_objectives_list) > 0 and primary_objectives_list[0] == "Requirements:"):
                primary_objectives_list.pop(0)
                intermediate["Requirements"] = primary_objectives_list.pop(0)
            primary_objectives[title] = intermediate


    if community_objectives_exist:
        for community_objectives_element in community_objectives_string:
            community_objectives_list = community_objectives_element.text.split('\n')
            print(community_objectives_list)
            while(len(community_objectives_list) > 0 and community_objectives_exist):
                achievements = []
                intermediate = {}
                title = community_objectives_list.pop(0)
                intermediate["Description"] = community_objectives_list.pop(0)
                if(len(community_objectives_list) > 0 and community_objectives_list[0] == "Achievements:"):
                    community_objectives_list.pop(0)
                    while(len(community_objectives_list) > 0 and community_objectives_list[0] != "Requirements:"):
                        achievements.append(community_objectives_list.pop(0))
                    intermediate["Achievements"] = achievements
                if(len(community_objectives_list) > 0 and community_objectives_list[0] == "Requirements:"):
                    community_objectives_list.pop(0)
                    intermediate["Requirements"] = community_objectives_list.pop(0)
                community_objectives[title] = intermediate


    full_game_info = {
        "CE ID" : id,
        "Steam ID" : app_id,
        "Tier" : tier,
        "Genre" : genre,
        "Primary Objectives" : primary_objectives,
        "Community Objectives" : community_objectives
    }
    return full_game_info


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