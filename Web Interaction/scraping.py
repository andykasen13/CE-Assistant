import json
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import psutil

# Grab information from json file
with open('useful.json') as f :
    localJSONData = json.load(f)

steam_api_key = localJSONData['steam_API_key']


def get_games():
    driver = webdriver.Chrome()
    driver.get("https://cedb.me/games")
    # game_list(driver)
    # game_data(driver)
    print(get_objectives("[NINJA GAIDEN: Master Collection] NINJA GAIDEN Σ", 'f722baf5-4c1a-4fa3-9482-5ce6db203c73', driver))



def game_list(driver):
    button_enabled = True
    games = {}

    
    while(button_enabled):
        names = driver.find_elements(By.TAG_NAME, "h2")[::2]
        while(len(names) < 1 or not names[0].is_displayed()):
            names = driver.find_elements(By.TAG_NAME, "h2")[::2]

        ids = driver.find_elements(By.CSS_SELECTOR, ":link")[7::2]
        tier_and_genre = driver.find_elements(By.CLASS_NAME, "bp4-text-overflow-ellipsis")
        button = driver.find_elements(By.TAG_NAME, "button")[30]


        tiers = tier_and_genre[14::5]
        genres = tier_and_genre[15::5]
        tier_and_genre=None

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
                # "tier" : tiers[i].text,
                # "genre" : genres[i].text,
            }

        button_enabled=False
        if(not button.is_enabled()):
            print("done")
            button_enabled=False
        else:
            button.click()


    with open('database.json', 'w') as f :
        json.dump(games, f, indent=4)

    games = None
    


def game_data(driver):
    games = json.loads(open("database.json").read())
    for game in games:
        data = get_objectives(game, games[game]["CE ID"], driver)
        for dat in data:
            games[game][dat] = data[dat]

    with open('database.json', 'w') as f :
        json.dump(games, f, indent=4)


def get_objectives(name, id, driver):
    url = "https://cedb.me/game/" + id
    driver.get(url)
    
    objectives_string = None
    while(objectives_string == None):
        try:
            objectives_string = driver.find_element(By.CLASS_NAME, "bp4-html-table").text
        except:
            continue
    tier_and_genre = driver.find_elements(By.CLASS_NAME, "bp4-fill")
    tier = tier_and_genre[0].text
    genre = tier_and_genre[1].text


    objectives_lst = objectives_string.split("\n")
    primary_objectives = {}
    all_achievements = get_achievements(name)

    print(objectives_lst)
    while(len(objectives_lst) > 0):
        achievements = []
        intermediate = {}
        title = objectives_lst.pop(0)
        intermediate["Point Value"] = objectives_lst.pop(0)
        intermediate["Description"] = objectives_lst.pop(0)
        if(len(objectives_lst) > 0 and objectives_lst[0] == "Achievements:"):
            objectives_lst.pop(0)
            while(len(objectives_lst) > 0 and all_achievements.count(objectives_lst[0]) > 0):
                if not(len(objectives_lst) > 3 and objectives_lst[2] == "Achievements:" or "Requirements:"):
                    achievements.append(objectives_lst.pop(0))

            intermediate["Achievements"] = achievements
        if(len(objectives_lst) > 0 and objectives_lst[0] == "Requirements:"):
            objectives_lst.pop(0)
            intermediate["Requirements"] = objectives_lst.pop(0)
        primary_objectives[title] = intermediate

    full_game_info = {
        "Tier" : tier,
        "Genre" : genre,
        "Objectives" : primary_objectives
    }
    
    return full_game_info




def get_achievements(game_name) :
    # ---- GET APP ID ----
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

    #TODO: dap isn't working sorry theron

    # --- DOWNLOAD JSON FILE ---

    # Open and save the JSON data
    payload = {'key' : steam_api_key, 'appid': correct_app_id, 'cc' : 'US'}
    response = requests.get("https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?", params = payload)
    jsonData = json.loads(response.text)

    all_achievements = []
    for achievement in jsonData['game']['availableGameStats']['achievements'] :
        all_achievements.append(achievement['displayName'])
    
    return all_achievements