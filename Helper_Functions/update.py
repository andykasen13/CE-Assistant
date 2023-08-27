import time
import discord
import requests
import json
import datetime
from datetime import timedelta

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
    if(user == -1) : 
        
        return "Unregistered"

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
    response = requests.get(f"https://cedb.me/api/user/{ce_id}")
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









    remove_indexes = []

    # Check if any rolls have been completed
    for index, current_roll in enumerate(user_dict[ce_id]['Current Rolls']) :
        roll_completed = True

        print("checking {}".format(current_roll["Event Name"]))

        # --------------------------------- co op rolls :sob: ---------------------------------
        # destiny alignment
        if current_roll["Event Name"] == "Destiny Alignment" : 

            for other_roll in database_user[current_roll["Partner"]]["Current Rolls"] :
                if other_roll["Event Name"] == "Destiny Alignment" : 
                    other_game = other_roll["Games"][0]
                    break
            
            # set the int user's game
            game = current_roll["Games"][0]

            # format int game
            for dbN_objective in database_name[game]["Primary Objectives"] :
                if(type(database_name[game]["Primary Objectives"][dbN_objective]) is int) : continue
                if("Achievements" in database_name[game]["Primary Objectives"][dbN_objective]) : del database_name[game]["Primary Objectives"][dbN_objective]["Achievements"]
                if("Requirements" in database_name[game]["Primary Objectives"][dbN_objective]) : del database_name[game]["Primary Objectives"][dbN_objective]["Requirements"]
                del database_name[game]["Primary Objectives"][dbN_objective]["Description"]
                database_name[game]["Primary Objectives"][dbN_objective] = database_name[game]["Primary Objectives"][dbN_objective]["Point Value"]
            
            # format part game
            for dbN_objective in database_name[other_game]["Primary Objectives"] :
                if(type(database_name[other_game]["Primary Objectives"][dbN_objective]) is int) : continue
                if("Achievements" in database_name[other_game]["Primary Objectives"][dbN_objective]) : del database_name[other_game]["Primary Objectives"][dbN_objective]["Achievements"]
                if("Requirements" in database_name[other_game]["Primary Objectives"][dbN_objective]) : del database_name[other_game]["Primary Objectives"][dbN_objective]["Requirements"]
                del database_name[other_game]["Primary Objectives"][dbN_objective]["Description"]
                database_name[other_game]["Primary Objectives"][dbN_objective] = database_name[other_game]["Primary Objectives"][dbN_objective]["Point Value"]

            # do the checking
            if ((game not in user_dict[ce_id]["Owned Games"] or "Primary Objectives" not in user_dict[ce_id]["Owned Games"][game])
                or
                (user_dict[ce_id]["Owned Games"][game]["Primary Objectives"] != database_name[game]["Primary Objectives"])
                or
                (other_game not in database_user[current_roll["Partner"]]["Owned Games"] or "Primary Objectives" not in database_user[current_roll["Partner"]]["Owned Games"][other_game])
                or
                (database_user[current_roll["Partner"]]["Owned Games"][other_game]["Primary Objectives"] != database_name[other_game]["Primary Objectives"])) : 
                
                    roll_completed = False
        # end of destiny alignment
        
        

        # soul mates
        elif current_roll["Event Name"] == "Soul Mates" :

            # format the game
            for dbN_objective in database_name[game]["Primary Objectives"] :
                if(type(database_name[game]["Primary Objectives"][dbN_objective]) is int) : continue
                if("Achievements" in database_name[game]["Primary Objectives"][dbN_objective]) : del database_name[game]["Primary Objectives"][dbN_objective]["Achievements"]
                if("Requirements" in database_name[game]["Primary Objectives"][dbN_objective]) : del database_name[game]["Primary Objectives"][dbN_objective]["Requirements"]
                del database_name[game]["Primary Objectives"][dbN_objective]["Description"]
                database_name[game]["Primary Objectives"][dbN_objective] = database_name[game]["Primary Objectives"][dbN_objective]["Point Value"]

            # do the checking
            if ((game not in user_dict[ce_id]["Owned Games"] or "Primary Objectives" not in user_dict[ce_id]["Owned Games"][game])
                    or
                    (user_dict[ce_id]["Owned Games"][game]["Primary Objectives"] != database_name[game]["Primary Objectives"])
                    or
                    (game not in database_user[current_roll["Partner"]]["Owned Games"] or "Primary Objectives" not in database_user[current_roll["Partner"]]["Owned Games"][game])
                    or
                    (database_user[current_roll["Partner"]]["Owned Games"][game]["Primary Objectives"] != database_name[game]["Primary Objectives"])) : roll_completed = False
        # end of soul mates



        # teamwork makes the dream work
        elif current_roll["Event Name"] == "Teamwork Makes the Dream Work" :
            for game in current_roll["Games"] :
                # ---------- standardize the game dictionary ----------
                # remove COs from the equation
                del database_name[game]["Community Objectives"]

                # format database_name like users2.json
                for dbN_objective in database_name[game]["Primary Objectives"] :
                    if(type(database_name[game]["Primary Objectives"][dbN_objective]) is int) : continue
                    if("Achievements" in database_name[game]["Primary Objectives"][dbN_objective]) : del database_name[game]["Primary Objectives"][dbN_objective]["Achievements"]
                    if("Requirements" in database_name[game]["Primary Objectives"][dbN_objective]) : del database_name[game]["Primary Objectives"][dbN_objective]["Requirements"]
                    del database_name[game]["Primary Objectives"][dbN_objective]["Description"]
                    database_name[game]["Primary Objectives"][dbN_objective] = database_name[game]["Primary Objectives"][dbN_objective]["Point Value"]

                if(game not in user_dict[ce_id]["Owned Games"] or "Primary Objectives" not in user_dict[ce_id]["Owned Games"][game] or user_dict[ce_id]["Owned Games"][game]["Primary Objectives"] != database_name[game]["Primary Objectives"]
                   and
                   game not in database_user[current_roll["Partner"]]["Owned Games"] or "Primary Objectives" not in database_user[current_roll["Partner"]]["Owned Games"][game] or database_user[current_roll["Partner"]]["Owned Games"][game]["Primary Objectives"] != database_name[game]["Primary Objectives"]) :
                    roll_completed = False
        # end of teamwork makes the dream work



        # winner takes all
        elif current_roll["Event Name"] == "Winner Takes All":
            # set the game
            game = current_roll["Games"][0]

            # formatting
            for dbN_objective in database_name[game]["Primary Objectives"] :
                if(type(database_name[game]["Primary Objectives"][dbN_objective]) is int) : continue
                if("Achievements" in database_name[game]["Primary Objectives"][dbN_objective]) : del database_name[game]["Primary Objectives"][dbN_objective]["Achievements"]
                if("Requirements" in database_name[game]["Primary Objectives"][dbN_objective]) : del database_name[game]["Primary Objectives"][dbN_objective]["Requirements"]
                del database_name[game]["Primary Objectives"][dbN_objective]["Description"]
                database_name[game]["Primary Objectives"][dbN_objective] = database_name[game]["Primary Objectives"][dbN_objective]["Point Value"]

            # figure out who completed what game
            winner = ""
            bool_1 = game in user_dict[ce_id]["Owned Games"] and "Primary Objectives" in user_dict[ce_id]["Owned Games"][game] and user_dict[ce_id]["Owned Games"][game]["Primary Objectives"] == database_name[game]["Primary Objectives"]
            bool_2 = game in database_user[ce_id]["Owned Games"] and "Primary Objectives" in database_user[current_roll["Partner"]]["Owned Games"][game] and database_user[current_roll["Partner"]]["Owned Games"][game]["Primary Objectives"] == database_name[game]["Primary Objectives"]
            if bool_1 and not bool_2 :
                winner = 1
                await log_channel.send("<@{}> has beaten <@{}> in Winner Takes All.".format(user_dict[ce_id]["Discord ID"], database_user[current_roll["Partner"]]["Discord ID"]))
            elif not bool_1 and bool_2 :
                winner = 2
                await log_channel.send("<@{}> has beaten <@{}> in Winner Takes All.".format(database_user[current_roll["Partner"]]["Discord ID"], user_dict[ce_id]["Discord ID"]))
            elif not bool_1 and not bool_2 :
                continue
            elif bool_1 and bool_2 :
                winner = 1
            
            # user 1 wins
            if winner == 1 :
                # update user 1 database
                current_roll["End Time"] = int(time.mktime((datetime.datetime.now()).timetuple()))
                user_dict[ce_id]["Completed Rolls"].append(current_roll)
                remove_indexes.append(index)
                # update user 2 database
                for index, other_roll in enumerate(database_user[current_roll["Partner"]]["Current Rolls"]) :
                    if other_roll["Event Name"] == "Winner Takes All" : 
                        other_location = index
                        break
                database_user[current_roll["Partner"]]["Cooldowns"]["Winner Takes All"] = int(time.mktime((datetime.datetime.now()+timedelta(28*3)).timetuple()))
                del database_user[current_roll["Partner"]]["Current Rolls"][other_location]
                continue

            # user 2 wins
            elif winner == 2:
                # update user 2 database
                for index, other_roll in enumerate(database_user[current_roll["Partner"]]["Current Rolls"]) :
                    if other_roll["Event Name"] == "Winner Takes All" : 
                        other_location = index
                        break
                database_user[current_roll["Partner"]]["Current Rolls"][other_location]["End Time"] = int(time.mktime((datetime.datetime.now()).timetuple()))
                database_user[current_roll["Partner"]]["Completed Rolls"].append(database_user[current_roll["Partner"]]["Current Rolls"][other_location])
                del database_user[current_roll["Partner"]]["Current Rolls"][other_location]
                # update user 1 database
                user_dict[ce_id]["Cooldowns"]["Winner Takes All"]  = int(time.mktime((datetime.datetime.now()+timedelta(28*3)).timetuple()))
                remove_indexes.append(index)
                continue


            else :
                print('something is wrongf')
                continue

                
                
                    

            """
            1. is the user done with the game?
            2. is their partner done with the game?
            if 1 not 2, they win
            if 2 not 1, they win
            if 1 and 1, ah man
                go through cedb.me/user/user1/game/gameID/objectives and grab the most recent updated time
                go through cedb.me/user/user2/game/gameID/objectives and grab the most recent updated time
                whoever's is later wins!
            
            move winners to completed rolls
            move losers to cooldowns
            
            """

            time.mktime(datetime.datetime.strptime(str(game['updatedAt'][:-5:]), "%Y-%m-%dT%H:%M:%S").timetuple())





        else :
        # --------------------------------- check to see if rolls that aren't weird (solo rolls) are done ---------------------------------
            for game in current_roll["Games"] :
            
                # ---------- standardize the game dictionary ----------
                # remove COs from the equation
                del database_name[game]["Community Objectives"]

                # format database_name like users2.json
                for dbN_objective in database_name[game]["Primary Objectives"] :
                    if(type(database_name[game]["Primary Objectives"][dbN_objective]) is int) : continue
                    print(dbN_objective)
                    if("Achievements" in database_name[game]["Primary Objectives"][dbN_objective]) : del database_name[game]["Primary Objectives"][dbN_objective]["Achievements"]
                    if("Requirements" in database_name[game]["Primary Objectives"][dbN_objective]) : del database_name[game]["Primary Objectives"][dbN_objective]["Requirements"]
                    del database_name[game]["Primary Objectives"][dbN_objective]["Description"]
                    database_name[game]["Primary Objectives"][dbN_objective] = database_name[game]["Primary Objectives"][dbN_objective]["Point Value"]

                # ---------- check to see if the games are equal ----------
                if (game not in user_dict[ce_id]["Owned Games"] or user_dict[ce_id]["Owned Games"][game]["Primary Objectives"] != database_name[game]["Primary Objectives"]) : roll_completed = False
                else : print('{} complete'.format(game))
            
            if not roll_completed : continue
            
            print(f'{current_roll["Event Name"]} completed')

            current_roll["End Time"] = int(time.mktime((datetime.datetime.now()).timetuple()))

            user_dict[ce_id]["Completed Rolls"].append(current_roll)

            del user_dict[ce_id]["Current Rolls"][index]

            await log_channel.send("<@{}>, you have completed {}! Congratulations!".format(user_dict[ce_id]["Discord ID"], current_roll["Event Name"]))
        
    for indexx in remove_indexes :
        del user_dict[ce_id]["Current Rolls"][indexx]

    # Add the user file to the database
    database_user.update(user_dict)

    # Dump the data
    with open('Jasons/users2.json', 'w') as f :
        json.dump(database_user, f, indent=4)

    return "Updated"

