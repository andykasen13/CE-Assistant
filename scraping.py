import asyncio
import functools
import json
from datetime import datetime
import typing
from selenium import webdriver
from selenium.webdriver.common.by import By
import psutil




def get_games():
    # print('RAM Used (GB):', psutil.virtual_memory()[3]/1000000000)
    # now = datetime.now()
    # current_time = now.strftime("%H:%M:%S")
    # print(current_time)
    driver = webdriver.Chrome()
    driver.get("https://cedb.me/games")
    tag(driver)




def tag(driver):
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

    # print('RAM Used (GB):', psutil.virtual_memory()[3]/1000000000)
    # now = datetime.now()
    # current_time = now.strftime("%H:%M:%S")
    # print(current_time)
    with open('database.json', 'w') as f :
        json.dump(games, f, indent=4)
    games=None
    