import asyncio
import functools
import json
from datetime import datetime
import typing
from selenium import webdriver
from selenium.webdriver.common.by import By




def get_games():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(current_time)
    driver = webdriver.Chrome()
    driver.get("https://cedb.me/games")
    tag(driver)




def tag(driver):
    button_enabled = True
    games = {}

    
    while(button_enabled):
        # page_not_loaded = True
        names = driver.find_elements(By.TAG_NAME, "h2")
        while(len(names) < 1 or not names[0].is_displayed()):
            names = driver.find_elements(By.TAG_NAME, "h2")

            # if len(names) > 1 and names[0].is_displayed():
            #     page_not_loaded = False

        ids = driver.find_elements(By.CSS_SELECTOR, ":link")
        tier_and_genre = driver.find_elements(By.CLASS_NAME, "bp4-text-overflow-ellipsis")
        buttons = driver.find_elements(By.TAG_NAME, "button")


        names = names[::2]
        ids = ids[7::2]
        tiers = tier_and_genre[14::5]
        genres = tier_and_genre[15::5]

        for i in range(0, len(names)):
            games[names[i].text] = {
                "CE ID" : ids[i].get_attribute("href")[21::],
                "tier" : tiers[i].text,
                "genre" : genres[i].text
            }

        forward_button = buttons[len(buttons) - 2]
        if(not forward_button.is_enabled()):
            print("done")
            button_enabled=False
        else:
            forward_button.click()


    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(current_time)
    with open('database.json', 'w') as f :
        json.dump(games, f, indent=4)