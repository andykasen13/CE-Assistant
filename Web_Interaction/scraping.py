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


ce_hex_icon = "https://media.discordapp.net/attachments/643158133673295898/1133596132551966730/image.png?width=778&height=778"




# Grab information from json file
with open('Jasons/secret_info.json') as f :
    localJSONData = json.load(f)

steam_api_key = localJSONData['steam_API_key']


def get_games():
    fin = game_list()
    get_by_tier()
    return fin

    



def game_list():
    # Set selenium driver and preferences
    options = Options()
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(width=1440, height=2000)

    # grab first game to get color on the rest of them
    url = 'https://cedb.me/game/1e8565aa-b9f2-4b41-9578-22e4c2a5436b'
    driver.get(url)
    objective_lst = []
    while(len(objective_lst) < 1 or not objective_lst[0].is_displayed()):
        objective_lst = driver.find_elements(By.CLASS_NAME, "bp4-html-table-striped")


    # set up API requests
    api_response = requests.get('https://cedb.me/api/games')
    json_response = json.loads(api_response.text)

    # grab last updated time
    current_dict = json.loads(open("./Jasons/curator_count.json").read())
    current_newest = current_dict['Updated Time']
    current_dict['Updated Time'] = int(time.mktime(datetime.now().timetuple()))
    
    # grab the new data and initialize trackers
    new_data = json.loads(open("./Jasons/database_name.json").read())
    number = 0
    updated_games = []
    game_tracker = list(new_data.keys())


    # game loop adding updated parts
    for game in json_response:

        # check if updated since last check
        updated_time = time.mktime(datetime.strptime(str(game['updatedAt'][:-5:]), "%Y-%m-%dT%H:%M:%S").timetuple())
        
        # if game is updated
        if updated_time > current_newest and game['name'] in list(new_data.keys()):
            game_tracker.remove(game['name'])
            test_old = new_data[game['name']]
            test_new = get_game(game)
            del test_new['Full Completions']
            del test_new['Total Owners']
            del test_old['Full Completions']
            del test_old['Total Owners']
            if test_old != test_new:
                updated_games.append(update(game, new_data[game['name']], driver, number))
                number += 1
            new_data[game['name']] = get_game(game)

        # if game is new
        elif not game['name'] in list(new_data.keys()):
            get_image(number, game['id'], driver)
            new_data[game['name']] = get_game(game)
            
            embed = {
                'Embed' : discord.Embed(
                    title="__" + game['name'] + "__ added to the site", # TODO make it fill out more info (tier, genre, num of objectives for _ points)
                    colour= 0x48b474,
                    timestamp=datetime.now()
                ),
                'Image' : discord.File("Pictures/ss{}.png".format(number), filename="image.png")
            }
            embed['Embed'].set_image(url='attachment://image.png')
            embed['Embed'].set_author(name="Challenge Enthusiasts", url="https://example.com", icon_url=ce_hex_icon)
            embed['Embed'].set_thumbnail(url=ce_hex_icon)
            embed['Embed'].set_footer(text="CE Assistant",
                icon_url=ce_hex_icon)
           
            updated_games.append(embed)
            number += 1

        # game is neither new nor updated
        else:
            game_tracker.remove(game['name'])


    # games removed
    for game in game_tracker:
        embed = {
            'Embed' : discord.Embed(
                title=game,
                colour= 0xce4e2c,
                timestamp=datetime.now()
            ),
            'Image' : discord.File("Pictures/removed.png".format(number), filename="image.png")
        }
        embed['Embed'].set_image(url='attachment://image.png')
        updated_games.append(embed)
        del new_data[game]

    # with open('Jasons/curator_count.json', 'w') as f:
    #     json.dump(current_dict, f, indent=4)
    # with open('./Jasons/database_name.json', 'w') as f :
    #     json.dump(new_data, f, indent=4)

    print('done')
    return updated_games


# updates for games
def update(game, old_game, driver, number):

    # icons for CE emoji
    icons = {   #TODO change these to CE emojis
        "Tier 0" : '<:tier0:1133560874464985139>', #<:tier0:1126268390605070426>',
        "Tier 1" : '<:tier1:1133560876381773846>', #'<:tier1:1126268393725644810>',
        "Tier 2" : '<:tier2:1133560878294372432>', #'<:tier2:1126268395483037776>',
        "Tier 3" : '<:tier3:1133560879544291469>', #'<:tier3:1126268398561677364>',
        "Tier 4" : '<:tier4:1133560881356226650>', #'<:tier4:1126268402596585524>',
        "Tier 5" : '<:tier5:1133560882291548323>', #'<:tier5:1126268404781809756>',
        "Tier 6" : '<:tier6:1133540654983688324>', #'<:tier6:1126268408116285541>',
        "Tier 7" : '<:tier7:1133540655981920347>', #'<:tier7:1126268411220074547>',

        "Action" : '<:CE_action:1133558549990088734>', #'<:CE_action:1126326215356198942>',
        "Arcade" : '<:CE_arcade:1133558574287683635>', #'<:CE_arcade:1126326209983291473>',
        "Bullet Hell" : '<:CE_bullethell:1133558610530676757>', #'<:CE_bullethell:1126326205642190848>',
        "First-Person" : '<:CE_firstperson:1133558611898015855>', #'<:CE_firstperson:1126326202102186034>',
        "Platformer" : '<:CE_platformer:1133558613705769020>', #'<:CE_platformer:1126326197983383604>',
        "Strategy" : '<:CE_strategy:1133558616536915988>', #'<:CE_strategy:1126326195915591690>'
    }
        
    # get game info and image
    new_game = get_game(game)
    get_image(number, new_game['CE ID'], driver, new_data=new_game)

    # initialize the embed description
    update = ""
    
    # ------------------- check tier -------------------
    if new_game['Tier'] != old_game['Tier']:
        update += "\n- {} ➡ {}".format(icons[old_game['Tier']], icons[new_game['Tier']])


    # ------------------- check Genre -------------------
    if new_game['Genre'] != old_game['Genre']:
        update += "\n- {} ➡ {}".format(icons[old_game['Tier']], icons[new_game['Tier']])


    # ------------------- check primary objectives -------------------
    if new_game['Primary Objectives'] != old_game['Primary Objectives']:

        # primary objective loop
        for objective in new_game['Primary Objectives']:

            # if objective is new
            if objective in list(new_game['Primary Objectives'].keys()) and not objective in list(old_game['Primary Objectives'].keys()):
                update += "\n- New Primary Objective '**{}**' added:\n\t- {} points <:CE_points:1133558614867587162>\n  - {}".format(objective, new_game['Primary Objectives'][objective]['Point Value'], new_game['Primary Objectives'][objective]['Description'])
            
            # if objective is updated
            elif objective in list(old_game['Primary Objectives'].keys()) and old_game['Primary Objectives'] != new_game['Primary Objectives']:
                
                # initialize some shit
                new = new_game['Primary Objectives'][objective]
                old = old_game['Primary Objectives'][objective]


                # ------------------- check points -------------------
                # points increased
                if new['Point Value'] > old['Point Value']:
                    update += "\n- '**{}**' increased from {} <:CE_points:1133558614867587162> ➡ {} <:CE_points:1133558614867587162> points:".format(objective, old['Point Value'], new['Point Value'])
                                       #<:CE_points:1128420207329816597>

                # points decreased
                elif new['Point Value'] < old['Point Value']:
                    update += "\n- '**{}**' decreased from {} <:CE_points:1133558614867587162> ➡ {} <:CE_points:1133558614867587162> points:".format(objective, old['Point Value'], new['Point Value'])
                
                # points unchanged
                else:
                    update += "\n- '**{}**' updated".format(objective)


                # ------------------- check description -------------------
                if new['Description'] != old['Description']:
                    update += "\n\t- Description Updated"


                # ------------------- check requirements -------------------
                # requirements are new
                if 'Requirements' in list(new.keys()) and not 'Requirements' in list(old.keys()):
                    update += "\n\t- Requirement '{}' added".format(new['Requirements'])
                
                # requirements deleted
                elif 'Requirements' in list(old.keys()) and not 'Requirements' in list(new.keys()):
                    update += "\n\t- Requirements removed"
                
                # requirements changed
                elif 'Requirements' in list(new.keys()) and new['Requirements'] != old['Requirements']:
                    update += "\n\t- Requirements updated from '{}' ➡ '{}'".format(old['Requirements'], new['Requirements'])
                

                # ------------------- check achievements -------------------
                # if achievements are a new requirement
                if 'Achievements' in list(new.keys()) and not 'Achievements' in list(old.keys()):

                    # initialize added achievement message
                    stand_in = "\n\t- "

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
                    update += "\n\t- All achievements removed"
                

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

                    # loop through achievements
                    for achievement in new['Achievements']:
                        
                        # new and not last achievement
                        if new['Achievements'][achievement] != new['Achievements'][list(new['Achievements'].keys())[-1]]:
                            stand_in += "'{}', ".format(new['Achievements'][achievement])

                        # the last achievement
                        else:
                            stand_in += "and '{}'".format(achievement)

                    # add to message if pertinent
                    if len(stand_in) > 17:
                        update += stand_in


                    # anything left over has been removed
                    if len(old_achievements) > 0:

                        # initialize
                        stand_in = "\n\t- Achievements "

                        # loop through each removed game
                        for achievement in old_achievements:
                            print(old_achievements[list(old_achievements.keys())[-1]])
                            # if no the last one
                            if old['Achievements'][achievement] != old_achievements[list(old_achievements.keys())[-1]]:
                                stand_in += "'{}', ".format(old['Achievements'][achievement])

                            # if it is the last one
                            else:
                                stand_in += "and '{}' removed".format(old['Achievements'][achievement])
                    
                    # add to message if pertinent
                    if len(stand_in) > 17:
                        update += stand_in


    # ------------------- make final embed -------------------
    embed = {
        'Embed' : discord.Embed(
            title="__" + game['name'] + "__ updated on the site:",
            colour= 0xefd839,
            timestamp=datetime.now(),
            description=update.strip()
        ),
        'Image' : discord.File("Pictures/ss{}.png".format(number), filename="image.png")
    }
    embed['Embed'].set_image(url='attachment://image.png')
    embed['Embed'].set_author(name="Challenge Enthusiasts", url="https://example.com", icon_url=ce_hex_icon)
    embed['Embed'].set_thumbnail(url=ce_hex_icon)
    embed['Embed'].set_footer(text="CE Assistant",
        icon_url=ce_hex_icon)

    # return :)
    return embed


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


def get_image(number, CE_ID, driver, new_data={}):

    if 'Tier' in new_data and new_data['Tier'] == 'Tier 0':
        pic = Image.open('Pictures/fix_later.png')
        pic.save('Pictures/ss{}.png'.format(number))
    else:
        try:
            url = 'https://cedb.me/game/' + CE_ID
            driver.get(url)
            objective_lst = []
            while(len(objective_lst) < 1 or not objective_lst[0].is_displayed()):
                objective_lst = []
                objective_lst = driver.find_elements(By.CLASS_NAME, "bp4-html-table-striped")
        except :
            print("I'm a doodoo head")
            get_image(number, CE_ID, driver, new_data)
        top_left = driver.find_element(By.CLASS_NAME, "GamePage-Header-Image").location
        bottom_right = objective_lst[len(objective_lst)-2].location
        size = objective_lst[len(objective_lst)-2].size

        header_elements = [
            'bp4-navbar',
            'tr-fadein'
        ]
        border_width = 15
        ob = Screenshot(bottom_right['y']+size['height']+border_width)
        im = ob.full_screenshot(driver, save_path=r'Pictures/', image_name="ss{}.png".format(number), is_load_at_runtime=True, load_wait_time=3, hide_elements=header_elements)

        
        im = Image.open('Pictures/ss{}.png'.format(number))
        im = im.crop((top_left['x']-border_width, top_left['y']-border_width, bottom_right['x']+size['width']+border_width, bottom_right['y']+size['height']+border_width)) # defines crop points
        im.save('Pictures/ss{}.png'.format(number))