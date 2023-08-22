import time
import discord
import requests
import json
import datetime

async def update_p(user_id : int, log_channel : discord.TextChannel, casino_channel : discord.TextChannel) :
    # Open the database
    with open('Jasons/users2.json', 'r') as dbU :
        database_user = json.load(dbU)

    # Set up total-points
    total_points = 0

    # Find the users data
    user = -1
    for for_user in database_user :
        if(database_user[for_user]['Discord ID'] == user_id) : 
            user = for_user
            break

    # If the user has no data, tell them to register
    if(user == -1) : return "Unregistered"

    # Grab the CE-ID
    ce_id = user

    # Set up the new user-dict
    user_dict = {
        ce_id : {
            "CE ID" : ce_id,
            "Discord ID" : user_id,
            "Rank" : "",
            "Reroll Tickets" : 0,
            "Casino Score" : 0,
            "Owned Games" : {},
            "Cooldowns" : {},
            "Current Rolls" : [],
            "Completed Rolls" : []
        }
    }

    # Grab user info from CE API
    response = requests.get(f"https://cedb.me/api/user/{database_user[user]['CE ID']}")
    user_ce_data = json.loads(response.text)

    # Go through owned games in CE JSON
    for game in user_ce_data["userGames"] :
        game_name = game["game"]["name"]
        
        # Add the games to the local JSON
        user_dict[ce_id]["Owned Games"][game_name] = {}

    # Go through all objectives 
    for objective in user_ce_data["userObjectives"] :
        game_name = objective["objective"]["game"]["name"]
        obj_name = objective["objective"]["name"]
        
        # If the objective is community, set the value to true
        if objective["objective"]["community"] : 
            if(list(user_dict[ce_id]["Owned Games"][game_name].keys()).count("Community Objectives") == 0) :
                user_dict[ce_id]["Owned Games"][game_name]["Community Objectives"] = {}
            user_dict[ce_id]["Owned Games"][game_name]["Community Objectives"][obj_name] = True

        # If the objective is primary...
        else : 
            # ... and there are partial points AND no one has assigned requirements...
            if(objective["objective"]["pointsPartial"] != 0 and objective["assignerId"] == None) :
                # ... set the points earned to the partial points value.
                points = objective["objective"]["pointsPartial"]
            # ... and there are no partial points, set the points earned to the total points value.
            else : points = objective["objective"]["points"]

            # Add the points to user's total points
            total_points += points

            # Now actually update the value in the user's dictionary.
            if(list(user_dict[ce_id]["Owned Games"][game_name].keys()).count("Primary Objectives") == 0) :
                user_dict[ce_id]["Owned Games"][game_name]["Primary Objectives"] = {}
            user_dict[ce_id]["Owned Games"][game_name]["Primary Objectives"][obj_name] = points


    # Get the user's rank
    rank = ""
    if total_points < 50 : rank = "Rank E"
    elif total_points < 250 : rank = "Rank D"
    elif total_points < 500 : rank = "Rank C"
    elif total_points < 1000 : rank = "Rank B"
    elif total_points < 2500 : rank = "Rank A"
    elif total_points < 5000 : rank = "Rank S"
    elif total_points < 7500 : rank = "Rank SS"
    elif total_points < 10000 : rank = "Rank SSS"
    else : rank = "Rank EX"

    user_dict[ce_id]["Rank"] = rank

    user_dict[ce_id]["Current Rolls"] = database_user[user]["Current Rolls"]
    user_dict[ce_id]["Completed Rolls"] = database_user[user]["Completed Rolls"]
    user_dict[ce_id]["Cooldowns"] = database_user[user]["Cooldowns"]
    user_dict[ce_id]["Casino Score"] = database_user[user]["Casino Score"]

    with open('Jasons/database_name.json', 'r') as ff :
        database_name = json.load(ff)

    # Check if any rolls have been completed
    for index, current_roll in enumerate(user_dict[ce_id]['Current Rolls']) :
        roll_completed = True

        for game in current_roll["Games"] :
            # remove COs from the equation
            del database_name[game]["Community Objectives"]

            # format database_name like users2.json
            for dbN_objective in database_name[game]["Primary Objectives"] :
               if("Achievements" in database_name[game]["Primary Objectives"][dbN_objective]) : del database_name[game]["Primary Objectives"][dbN_objective]["Achievements"]
               if("Requirements" in database_name[game]["Primary Objectives"][dbN_objective]) : del database_name[game]["Primary Objectives"][dbN_objective]["Requirements"]
               del database_name[game]["Primary Objectives"][dbN_objective]["Description"]
               database_name[game]["Primary Objectives"][dbN_objective] = database_name[game]["Primary Objectives"][dbN_objective]["Point Value"]
            

            if (game not in user_dict[ce_id]["Owned Games"] or user_dict[ce_id]["Owned Games"][game]["Primary Objectives"] != database_name[game]["Primary Objectives"]) : roll_completed = False
            else : print('{} complete'.format(game))
        
        if not roll_completed : continue
        
        print(f'{current_roll["Event Name"]} completed')

        current_roll["End Time"] = int(time.mktime((datetime.datetime.now()).timetuple()))

        user_dict[ce_id]["Completed Rolls"].append(current_roll)

        del user_dict[ce_id]["Current Rolls"][index]

        await log_channel.send("<@{}>, you have completed {}! Congratulations!".format(user_dict[ce_id]["Discord ID"], current_roll["Event Name"]))
        


    # Add the user file to the database
    database_user.update(user_dict)

    # Dump the data
    with open('Jasons/users2.json', 'w') as f :
        json.dump(database_user, f, indent=4)

    return "Updated"

