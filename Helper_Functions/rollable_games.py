import json
import random
from bson import ObjectId
import requests

from Web_Interaction.scraping import get_completion_data

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

def get_rollable_game(avg_completion_time_limit, price_limit, tier_number, user_info = -1, specific_genre = "any", games : list = [], database_tier = "", database_name = "") :
        returned_game = ""
        rollable = False
        genres = ["Action", "Arcade", "Bullet Hell", "First-Person", "Platformer", "Strategy"] 

        if avg_completion_time_limit == "nope" : avg_completion_time_limit = 9999999
        
    
        while not rollable :
            # ----- Grab random game -----
            # (Genre not given)
            if(specific_genre == "any") :
                print("No genre specified.")
                # ----- Pick a random number -----
                random_num = -1
                for genre in genres :
                    random_num += len(database_tier[tier_number][genre]) 
                random_num = random.randint(0, random_num)

                # ----- Determine genre based on number -----
                for genre in genres :
                    if(random_num < len(database_tier[tier_number][genre])) :
                        # ----- Pick the game -----
                        returned_game = database_tier[tier_number][genre][random_num]
                        print("Chosen genre: " + genre)
                        break
                    # ----- Move to the next genre -----
                    else : random_num -= len(database_tier[tier_number][genre])
            # (Genre given)
            elif type(specific_genre) == str:
                print(f"Specified genre: {specific_genre}.")
                random_num = random.randint(0,len(database_tier[tier_number][specific_genre])-1)
                returned_game = database_tier[tier_number][specific_genre][random_num]
            # (Genres given)
            elif type(specific_genre) == list :
                print(f"Genres specified: {str(specific_genre)}")
                # ----- Pick a random number -----
                random_num = -1
                for genre in specific_genre :
                    random_num += len(database_tier[tier_number][genre])
                random_num = random.randint(0, random_num)

                # ----- Determine genre based on number -----
                for genre in specific_genre :
                    if(random_num < len(database_tier[tier_number][genre])) :
                        # ----- Pick the game -----
                        returned_game = database_tier[tier_number][genre][random_num]
                        print("Chosen genre: " + genre)
                        break
                    # ----- Move to the next genre -----
                    else : random_num -= len(database_tier[tier_number][genre])

            # ----- Log it in the console -----
            print(f"Seeing if {returned_game} is rollable...")
            if returned_game in banned_games :
                print(f"{returned_game} is banned.\n")
                continue
                
            # ----- Check if the game has already been rolled -----
            if returned_game in games :
                print("{} already rolled! Continuing...".format(returned_game))
                continue

            # ---- Check to see if the user has already completed the game -----
            if(user_info != -1) :
                if((returned_game in list(user_info["Owned Games"].keys())) 
                and "Primary Objectives" in list(user_info["Owned Games"][returned_game].keys())
                and user_info["Owned Games"][returned_game]["Primary Objectives"].keys() == database_name[returned_game]["Primary Objectives"].keys()) :
                    print("User has completed game. Moving on...\n")
                    continue

            for obj in database_name[returned_game]["Primary Objectives"]:
                if database_name[returned_game]["Primary Objective"][obj]["Point Value"] % 5 != 0:
                    print('uncleared game. continuing...')
                    continue
            
            # ----- Grab the Game ID -----
            gameID = int(database_name[returned_game]["Steam ID"])

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

            print(f"Game price is {gamePrice}... {gamePrice < price_limit}" + f"Game completion time is {completion_time}... {completion_time < avg_completion_time_limit}")

            # ----- Check to see if rollable -----
            if(gamePrice < price_limit and completion_time < avg_completion_time_limit) :
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
    from Helper_Functions.mongo_silly import get_mongo, dump_mongo, get_unix

    database_name = await get_mongo('name')
    rollable = False
    while not rollable :
        random_num = random.randint(0, len(games)-1)
        random_game = games[random_num]

        print(f"Seeing if {random_game} is rollable...")

        # check for price and avg completion time
        game_id = database_name[random_game]["Steam ID"]
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

