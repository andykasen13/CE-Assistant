import json
import random
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
                        "Barrier X"]



# -------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------- GET ROLLABLE GAME ------------------------------------------------------ #
# -------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------------------- #

def get_rollable_game(avg_completion_time_limit, price_limit, tier_number, specific_genre = "any") :
        returned_game = ""
        rollable = False
        genres = ["Action", "Arcade", "Bullet Hell", "First-Person", "Platformer", "Strategy"]
        
        with open('Jasons/database_tier.json', 'r') as dB :
            database_tier = json.load(dB)
        
        with open('Jasons/database_name.json', 'r') as dBN :
            database_name = json.load(dBN)
    
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
                print(f"{returned_game} is banned.")
                continue

            gameID = int(database_name[returned_game]["Steam ID"])

            # ----- Grab Steam JSON file -----
            payload = {'appids': gameID, 'cc' : 'US'}
            response = requests.get("https://store.steampowered.com/api/appdetails?", params = payload)
            jsonData = json.loads(response.text)

            # ----- Determine game price -----
            if(jsonData[str(gameID)]['data']['is_free']) : 
                gamePrice = 0
            else: 
                gamePrice = float(str(jsonData[str(gameID)]['data']['price_overview']['final_formatted'])[1::])
            
            # ----- Grab SteamHunters completion time -----
            completion_time = get_completion_data(gameID)
            if(completion_time == "none") :
                print(f"No completion data for {returned_game}.") 
                continue
            else : completion_time = int(completion_time)

            print(f"Game price is {gamePrice}... {gamePrice < price_limit}")
            print(f"Game completion time is {completion_time}... {completion_time < avg_completion_time_limit}")

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

async def get_rollable_game_from_list(games) :
    with open('Jasons/database_name.json', 'r') as dbN :
        database_name = json.load(dbN)
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

