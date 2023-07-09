import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
import psutil




def get_games():
    driver = webdriver.Chrome()
    driver.get("https://cedb.me/games")
    #game_list(driver)
    get_objectives('c04662d6-fdcc-4b55-918b-f1d1eb0d25de', driver)





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

        for i in range(0, len(names)):
            #objectives = get_objectives(ids[i].text, driver)
            games[names[i].text] = {
                "CE ID" : ids[i].get_attribute("href")[21::],
                "tier" : tiers[i].text,
                "genre" : genres[i].text
            }

        
        if(not button.is_enabled()):
            print("done")
            button_enabled=False
        else:
            button.click()


    with open('database.json', 'w') as f :
        json.dump(games, f, indent=4)

    games = None
    


def get_objectives(id, driver):
    url = "https://cedb.me/game/" + id
    driver.get(url)
    title = None
    while(title == None):
        try:
            title = driver.find_element(By.CLASS_NAME, "fl-gap-2")
        except:
            continue

    print(title.text + "huh")
