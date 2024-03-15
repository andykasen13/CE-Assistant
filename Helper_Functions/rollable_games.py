import asyncio
import functools
import json
import random
import typing
from bson import ObjectId
import requests

from Web_Interaction.scraping import get_completion_data
from Helper_Functions.mongo_silly import *

# --------------------------------------------------------- banned games -------------------------------------------------------- #
banned_games = ["Serious Sam HD: The Second Encounter", 
                        "Infinite Air with Mark McMorris", 
                        "A Bastard's Tale",
                        "A Most Extraordinary Gnome",
                        "Bot Vice",
                        "Curvatron",
                        "Dark Souls III",
                        "Destructivator 2",
                        "DSY",
                        "Geballer",
                        "Gravity Den",
                        "Gridform",
                        "Heck Deck",
                        "ITTA",
                        "Just Arms",
                        "LaserBoy",
                        "Little Nightmares",
                        "MO:Astray",
                        "MOONPONG",
                        "Mortal Shell",
                        "Overture",
                        "Project Rhombus",
                        "Satryn Deluxe",
                        "SEUM",
                        "Squidlit",
                        "Super Cable Boy",
                        "The King's Bird",
                        "you have to win the game",
                        "Heavy Bullets",
                        "Barrier X",
                        "Elasto Mania Remastered"]


# -------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------- GET ROLLABLE GAME ------------------------------------------------------ #
# -------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------------------- #
def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper

@to_thread
def get_rollable_game(avg_completion_time_limit, price_limit, tier_number, user_info = -1, specific_genre = "any", games : list = [], database_tier = "", database_name = "") :
        returned_game = ""
        rollable = False
        genres = ["Action", "Arcade", "Bullet Hell", "First-Person", "Platformer", "Strategy"] 

        if avg_completion_time_limit == "nope" : avg_completion_time_limit = 9999999
        
        if tier_number == 'Tier 5+':
            database_tier['Tier 5+'] = {
                "Action" : 0,
                "Arcade" : 0,
                "Bullet Hell" : 0,
                "First-Person" : 0,
                "Platformer" : 0,
                "Strategy" : 0
            }

            for g in genres :
                database_tier["Tier 5+"][g] = database_tier['Tier 5'][g] + database_tier['Tier 6'][g]
    
        while not rollable :
            # ----- Grab random game -----
            # (Genre not given)
            if(specific_genre == "any") :
                # Pick a random number
                random_num = -1
                for genre in genres :
                    random_num += len(database_tier[tier_number][genre]) 
                random_num = random.randint(0, random_num)

                # Determine genre
                for genre in genres :
                    if(random_num < len(database_tier[tier_number][genre])) :
                        # Correct genre, pick game
                        returned_game = database_tier[tier_number][genre][random_num]
                        print("Chosen genre: " + genre)
                        break
                    # Next genre
                    else : random_num -= len(database_tier[tier_number][genre])

            # (Genre given)
            elif type(specific_genre) == str:
                if (len(database_tier[tier_number][specific_genre]) - 1 == 0) :
                    print(tier_number)
                    print(specific_genre)
                    print('you are fucked buddy')
                    return "NO ROLLABLE GAMES IN CATEGORY"
                random_num = random.randint(0,len(database_tier[tier_number][specific_genre])-1)
                returned_game = database_tier[tier_number][specific_genre][random_num]
                genre = specific_genre

            # (Genres given)
            elif type(specific_genre) == list :
                # Pick a random number
                random_num = -1
                for genre in specific_genre :
                    random_num += len(database_tier[tier_number][genre])
                random_num = random.randint(0, random_num)

                # Determine genre
                for genre in specific_genre :
                    if(random_num < len(database_tier[tier_number][genre])) :
                        # Correct genre, pick game
                        returned_game = database_tier[tier_number][genre][random_num]
                        print("Chosen genre: " + genre)
                        break
                    # Next genre
                    else : random_num -= len(database_tier[tier_number][genre])

            # ----- Check to see if it's banned -----
            print(f"Seeing if {returned_game} is rollable...")
            if returned_game in banned_games :
                del database_tier[tier_number][genre][random_num]
                print(f"{returned_game} is banned.\n")
                continue
                
            # ----- Check if the game has already been rolled -----
            if returned_game in games :
                del database_tier[tier_number][genre][random_num]
                print("{} already rolled! Continuing...".format(returned_game))
                continue

            # ---- Check to see if the user has already completed the game -----
            if(user_info != -1) :
                if((returned_game in user_info['Owned Games'].keys()) 
                and "Primary Objectives" in user_info['Owned Games'][returned_game]
                # TODO: this is so so cheating because if someone has partial points in some and finished all others this says theyre done. lets fix that
                and set(user_info['Owned Games'][returned_game]['Primary Objectives'].keys()) == set(database_name[returned_game]['Primary Objectives'].keys())) :
                    del database_tier[tier_number][genre][random_num]
                    print("User has completed game. Moving on...\n")
                    continue

            # ---- Check to see if it's uncleared ----
            uncleared = False
            for obj in database_name[returned_game]['Primary Objectives']:
                if database_name[returned_game]['Primary Objectives'][obj]['Point Value'] % 5 != 0:
                    del database_tier[tier_number][genre][random_num]
                    print('uncleared game. continuing...')
                    uncleared = True
            if uncleared : continue
            
            # ----- Grab the Game ID -----
            gameID = int(database_name[returned_game]['Steam ID'])

            # ----- Grab Steam JSON file -----
            payload = {'appids': gameID, 'cc' : 'US'}
            response = requests.get("https://store.steampowered.com/api/appdetails?", params = payload)
            jsonData = json.loads(response.text)

            # ----- Determine game price -----
            if(jsonData[str(gameID)]['data']['is_free']) : 
                gamePrice = 0
            elif('price_overview' in list(jsonData[str(gameID)]['data'].keys())): 
                gamePrice = float(str(jsonData[str(gameID)]['data']['price_overview']['final_formatted'])[1::])
            else :
                gamePrice = 999999
            
            # ----- Grab SteamHunters completion time -----
            completion_time = get_completion_data(gameID)
            if(completion_time == "none") :
                print(f"No completion data for {returned_game}.") 
                continue

            # ---- Check price ----
            if (gamePrice > price_limit) :
                del database_tier[tier_number][genre][random_num]
                print("Too pricey.")
                continue
            
            # ----- Check SteamHunters completion time ----
            if completion_time > avg_completion_time_limit :
                del database_tier[tier_number][genre][random_num]
                print("Completion time too high.")
                continue

            # ----- Check to see if rollable -----
            if(gamePrice <= price_limit and completion_time <= avg_completion_time_limit) :
                rollable = True
            print("\n")

        # ----- We now have a rollable game. Return it. -----
        print(f"{returned_game} is rollable.")
        print("\n")
        return returned_game

# -------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------- GET ROLLABLE GAME FROM LIST ----------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------------------- #

async def get_rollable_game_from_list(games, collection) :
    database_name = await get_mongo('name')
    rollable = False
    while not rollable :
        random_num = random.randint(0, len(games)-1)
        random_game = games[random_num]

        print(f"Seeing if {random_game} is rollable...")

        # check for price and avg completion time
        game_id = database_name[random_game]['Steam ID']
        # ----- Grab Steam JSON file -----
        payload = {'appids': game_id, 'cc' : 'US'}
        response = requests.get("https://store.steampowered.com/api/appdetails?", params = payload)
        jsonData = json.loads(response.text)

        # ----- Determine game price -----
        if(jsonData[str(game_id)]['data']['is_free']) : 
            gamePrice = 0
        else: 
            gamePrice = float(str(jsonData[str(game_id)]['data']['price_overview']['final_formatted'])[1::])
        
        # ----- Grab SteamHunters completion time -----
        completion_time = get_completion_data(game_id)
        if(completion_time == "none") : continue
        else : completion_time = int(completion_time)

        print(f"Game price is {gamePrice}... {gamePrice < 20}")
        print(f"Game completion time is {completion_time}... {completion_time < 40}")

        # ----- Check to see if rollable -----
        if(gamePrice < 20 and completion_time < 40) :
            rollable = True
            return random_game
        print(' ')

