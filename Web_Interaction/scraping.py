import json
from datetime import datetime
from Screenshot import Screenshot
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from PIL import Image


# Grab information from json file
with open('Jasons/secret_info.json') as f :
    localJSONData = json.load(f)

steam_api_key = localJSONData['steam_API_key']


def get_games():

    # driver = webdriver.Chrome()
    # game_list(driver)
    # game_data(driver)
    # get_image('21144d8d-c943-4130-8349-6e768220cfc9')
    get_by_tier()
    



def game_list(driver):
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
    


def game_data(driver):
    games = json.loads(open("./Jasons/database_name.json").read())
    for game in games:
        print(game)
        games[game] = get_data(games[game]["CE ID"], driver)

    with open('./Jasons/database_name.json', 'w') as f :
        json.dump(games, f, indent=4)


def get_data(id, driver):
    url = "https://cedb.me/game/" + id
    driver.get(url)
    
    table_list = []
    while(len(table_list) < 1 or not table_list[0].is_displayed()):
        table_list = driver.find_elements(By.CLASS_NAME, "bp4-html-table-striped")

    primary_objectives_string = table_list[0].text
    community_objectives_string = table_list[1].text

    tier_and_genre = driver.find_elements(By.CLASS_NAME, "bp4-fill")
    app_id = driver.find_element(By.CLASS_NAME, 'no-decoration').get_attribute("href")[34::]
    tier = tier_and_genre[0].text
    genre = tier_and_genre[1].text
    headings = driver.find_elements(By.TAG_NAME, "h2")
    community_objectives_exist = headings[1].text == "Community Objectives"


    primary_objectives_list = primary_objectives_string.split("\n")
    community_objectives_list = community_objectives_string.split("\n")
    primary_objectives = {}
    community_objectives = {}
    all_achievements = get_achievements(app_id)

    exceptions = [
        "Nonviolentist", "TOUGH RERUN"
    ] #Cosmodreamer, The Next Penelope

    while(len(primary_objectives_list) > 0):
        achievements = []
        intermediate = {}
        title = primary_objectives_list.pop(0)
        intermediate["Point Value"] = primary_objectives_list.pop(0)
        intermediate["Description"] = primary_objectives_list.pop(0)
        if(len(primary_objectives_list) > 0 and primary_objectives_list[0] == "Achievements:"):
            primary_objectives_list.pop(0)
            while(len(primary_objectives_list) > 0 and ((all_achievements.count(primary_objectives_list[0].strip()) > 0) or (exceptions.count(primary_objectives_list[0]) > 0))):
                if (not (len(primary_objectives_list) > 3 and (primary_objectives_list[3] == "Achievements:" or primary_objectives_list[3] == "Requirements:"))):
                    achievements.append(primary_objectives_list.pop(0))
                else:
                    break
            intermediate["Achievements"] = achievements
        if(len(primary_objectives_list) > 0 and primary_objectives_list[0] == "Requirements:"):
            primary_objectives_list.pop(0)

            intermediate["Requirements"] = primary_objectives_list.pop(0)
        primary_objectives[title] = intermediate


    while(len(community_objectives_list) > 0 and community_objectives_exist):
        achievements = []
        intermediate = {}
        title = community_objectives_list.pop(0)
        intermediate["Description"] = community_objectives_list.pop(0)
        if(len(community_objectives_list) > 0 and community_objectives_list[0] == "Achievements:"):
            community_objectives_list.pop(0)
            while(len(community_objectives_list) > 0 and (all_achievements.count(community_objectives_list[0].strip()) > 0 or exceptions.count(community_objectives_list[0]) > 0)):
                if (not (len(community_objectives_list) > 2 and (community_objectives_list[2] == "Achievements:" or community_objectives_list[2] == "Requirements:"))):
                    achievements.append(community_objectives_list.pop(0))
                else:
                    break
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












def get_achievements(steam_id) :

    # Open and save the JSON data
    payload = {'key' : steam_api_key, 'appid': steam_id, 'cc' : 'US'}
    response = requests.get("https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?", params = payload)
    jsonData = json.loads(response.text)

    all_achievements = []
    if 'availableGameStats' in jsonData['game'].keys() and 'achievements' in jsonData['game']['availableGameStats'].keys():
        for achievement in jsonData['game']['availableGameStats']['achievements'] :
            all_achievements.append(achievement['displayName'].strip())
    
    return all_achievements



def get_image(CE_ID):
    options = Options()
    options.add_argument('headless')
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

    ob = Screenshot.Screenshot()
    ob.full_screenshot(driver, save_path=r'.', image_name="ss.png", is_load_at_runtime=True, load_wait_time=3, hide_elements=header_elements)

    border_width = 15
    im = Image.open('ss.png')
    im = im.crop((top_left['x']-border_width, top_left['y']-border_width, bottom_right['x']+size['width']+border_width, bottom_right['y']+size['height']+border_width)) # defines crop points
    im.save('Web_Interaction/ss.png')

    # return(discord.file('ss.png'))