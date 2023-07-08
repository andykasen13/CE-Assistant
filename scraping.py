import asyncio
import json
from selenium import webdriver
from selenium.webdriver.common.by import By


async def get_games():
    driver = webdriver.Chrome()
    driver.get("https://cedb.me/games")
    games = await asyncio.wait_for(tag(driver), timeout=10)
    with open('database.json', 'w') as f :
        json.dump(games, f, indent=1)



async def tag(driver):
    please = True
    games = {}
    while(please):
        names = driver.find_elements(By.TAG_NAME, "h2")
        id = driver.find_elements(By.CSS_SELECTOR, ":link")
        
        if len(names)<32:
            continue
        for plant in names:
            if not (plant.text and plant.text.strip()):
                continue
        please = False
    
    id = id[7::2]
    names = names[::2]
    
    for i in range(0, len(id)):
        print(id[i].get_attribute("href")[21::] + " " + names[i].text)
        games[names[i].text] = {
            "CE ID" : id[i].get_attribute("href")[21::]
        }


    return games