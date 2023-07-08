import asyncio
import json
from selenium import webdriver
from selenium.webdriver.common.by import By


async def get_games():
    driver = webdriver.Chrome()
    driver.get("https://cedb.me/games")
    games = await asyncio.wait_for(tag(driver), timeout=10)
    with open('database.json', 'w') as f :
        json.dump(games, f, indent=4)



async def tag(driver):
    please = True
    games = {}
    while(please):
        names = driver.find_elements(By.TAG_NAME, "h2")

        if len(names)<32:
            continue
        for plant in names:
            if not (plant.text and plant.text.strip()):
                continue
        please = False


    id = driver.find_elements(By.CSS_SELECTOR, ":link")
    tier_and_genre = driver.find_elements(By.CLASS_NAME, "bp4-text-overflow-ellipsis")
    buttons = driver.findelements(By.TAG_NAME, "button")


    id = id[7::2]
    names = names[::2]
    tiers = tier_and_genre[14::5]
    genres = tier_and_genre[15::5]
    
    for i in range(0, len(id)):
        games[names[i].text] = {
            "CE ID" : id[i].get_attribute("href")[21::],
            "tier" : tiers[i].text,
            "genre" : genres[i].text
        }

    return games