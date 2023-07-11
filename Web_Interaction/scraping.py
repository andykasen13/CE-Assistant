import json
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import psutil

# Grab information from json file
with open('Jasons/secret_info.json') as f :
    localJSONData = json.load(f)

steam_api_key = localJSONData['steam_API_key']


def get_games():

    ram_before = psutil.virtual_memory()[3]/1000000000
    time_before = datetime.now()
    driver = webdriver.Chrome()
    driver.get("https://cedb.me/games")
    # game_list(driver)
    game_data(driver)
    # print(get_achievements("999990"))
    # print(get_objectives("021b06b7-a5b5-4a54-bf45-36ed9037ee1d", driver))
    ram_after = psutil.virtual_memory()[3]/1000000000
    time_after = datetime.now()
    print('ram usage (GB): ' + str(ram_after-ram_before))
    print('time taken (s):' + str(time_after-time_before))
    



def game_list(driver):
    button_enabled = True
    games = {}

    
    while(button_enabled):
        names = driver.find_elements(By.TAG_NAME, "h2")[::2]
        while(len(names) < 1 or not names[0].is_displayed()):
            names = driver.find_elements(By.TAG_NAME, "h2")[::2]

        ids = driver.find_elements(By.CSS_SELECTOR, ":link")[7::2]
        button = driver.find_elements(By.TAG_NAME, "button")[30]

        ignore = [
            "- Challenge Enthusiasts -",
            "- Puzzle Games -",
            "clown town 1443"
        ]

        for i in range(0, len(names)):
            if ignore.count(names[i].text) > 0:
                continue
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
        data = get_objectives(games[game]["CE ID"], driver)
        for dat in data:
            games[game][dat] = data[dat]

    with open('./Jasons/database_name.json', 'w') as f :
        json.dump(games, f, indent=4)


def get_objectives(id, driver):
    url = "https://cedb.me/game/" + id
    driver.get(url)
    
    objectives_string = None
    while(objectives_string == None):
        try:
            objectives_string = driver.find_element(By.CLASS_NAME, "bp4-html-table").text
        except:
            continue
    tier_and_genre = driver.find_elements(By.CLASS_NAME, "bp4-fill")
    app_id = driver.find_element(By.CLASS_NAME, 'no-decoration').get_attribute("href")[34::]
    tier = tier_and_genre[0].text
    genre = tier_and_genre[1].text


    objectives_lst = objectives_string.split("\n")
    primary_objectives = {}
    all_achievements = get_achievements(app_id)
    while(len(objectives_lst) > 0):
        achievements = []
        intermediate = {}

        title = objectives_lst.pop(0)
        intermediate["Point Value"] = objectives_lst.pop(0)
        intermediate["Description"] = objectives_lst.pop(0)
        if(len(objectives_lst) > 0 and objectives_lst[0] == "Achievements:"):
            objectives_lst.pop(0)
            while(len(objectives_lst) > 0 and all_achievements.count(objectives_lst[0].strip()) > 0):
                if (not (len(objectives_lst) > 3 and (objectives_lst[3] == "Achievements:" or objectives_lst[3] == "Requirements:"))):
                    achievements.append(objectives_lst.pop(0))
                else:
                    break
            intermediate["Achievements"] = achievements
        if(len(objectives_lst) > 0 and objectives_lst[0] == "Requirements:"):
            objectives_lst.pop(0)

            intermediate["Requirements"] = objectives_lst.pop(0)
        primary_objectives[title] = intermediate

    full_game_info = {
        "Steam ID" : app_id,
        "Tier" : tier,
        "Genre" : genre,
        "Objectives" : primary_objectives
    }

    return full_game_info




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