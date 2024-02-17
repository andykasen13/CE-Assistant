import time
import discord
import requests
import json
import datetime
from datetime import timedelta
from bson import ObjectId



def update_p(user_id : int, roll_ended_name, database_user, database_name) :
    from Helper_Functions.mongo_silly import get_unix
    
    cooldowns = {
        "One Hell of a Day" : (14),
        "One Hell of a Week" : (28),
        "One Hell of a Month" : (28*3),
        "Two Week T2 Streak" : 0, # multi-stage roll
        "Two 'Two Week T2 Streak' Streak" : (7),
        "Never Lucky" : (28),
        "Triple Threat" : (28*3),
        "Let Fate Decide" : (28*3),
        "Fourward Thinking" : 0, # multi-stage roll
        "Russian Roulette" : (28*6),
        "Destiny Alignment" : (28),
        "Soul Mates" : 0, # this depends on which tier was chosen
        "Teamwork Makes the Dream Work" : 28*3
    }


    # Set up total-points
    total_points = 0

    # Find the users data
    user = -1
    for for_user in database_user :
        if for_user == "_id" : continue
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

    # Create an array of returnable items
    returns = []

    # Grab user info from CE API
    try:
        response = requests.get(f"https://cedb.me/api/user/{ce_id}")
        user_ce_data = json.loads(response.text)
    except:
        return "failed"
    

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
    if total_points <= 50 : rank = "E Rank"
    elif total_points <= 250 : rank = "D Rank"
    elif total_points <= 500 : rank = "C Rank"
    elif total_points <= 1000 : rank = "B Rank"
    elif total_points <= 2500 : rank = "A Rank"
    elif total_points <= 5000 : rank = "S Rank"
    elif total_points <= 7500 : rank = "SS Rank"
    elif total_points <= 10000 : rank = "SSS Rank"
    else : rank = "EX Rank"

    returns.append("rank: {}".format(rank))


    user_dict[ce_id]["Rank"] = rank

    user_dict[ce_id]["Current Rolls"] = database_user[user]["Current Rolls"]
    user_dict[ce_id]["Completed Rolls"] = database_user[user]["Completed Rolls"]
    user_dict[ce_id]["Cooldowns"] = database_user[user]["Cooldowns"]
    user_dict[ce_id]["Casino Score"] = database_user[user]["Casino Score"]

    




    # Add the user file to the database
    database_user.update(user_dict)






    remove_indexes = []
    cooldown_indexes = []

    # Check if any rolls have been completed
    for m_index, current_roll in enumerate(user_dict[ce_id]['Current Rolls']) :
        roll_completed = True

        f = False
        for g in current_roll["Games"] :
            if g == "pending..." : continue
            if g not in database_name :
                if len(current_roll["Games"]) > 1: current_roll["Games"].remove(g)
                else : 
                    returns.append("log: <@{}>: unfortunately, the game(s) in your roll were removed from the site. please ping andy for support and/or reroll")
                    remove_indexes.append(m_index)
                    f = True
        if f : continue

        print("checking {}".format(current_roll["Event Name"]))

        # ------------------------------------ pending... -------------------------------------
        if current_roll["Games"] == ['pending...']:
            if current_roll["End Time"] < get_unix("now"): 
                #"delete pending..."
                #"continue"
                remove_indexes.append(m_index)
                returns.append("casino: " + "<@{}>, you can now roll {} again.".format(
                    user_dict[ce_id]["Discord ID"], current_roll["Event Name"]))

                continue
        
        elif current_roll["Games"][0] == 'pending...' and len(current_roll["Games"]) != 1:
            
            if(current_roll["End Time"] < get_unix("now")):
                del current_roll["Games"][0]
                del current_roll["End Time"]
                returns.append("casino: " + f"<@{user_dict[ce_id]["Discord ID"]}>, you can now roll {current_roll["Event Name"]} again.")
            continue

        # ---------------------------- deal with deleted games -------------------------------
        

        # --------------------------------- co op rolls :sob: ---------------------------------
        # destiny alignment
        elif current_roll["Event Name"] == "Destiny Alignment" : 

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



        # ----- winner takes all ------
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
            elif not bool_1 and bool_2 :
                winner = 2
            elif not bool_1 and not bool_2 :
                print('fail')
                continue
            elif bool_1 and bool_2 :
                winner = 1
            # user 1 wins
            if winner == 1 :
                print('andy wins')
                # update user 1 database
                current_roll["End Time"] = get_unix("now")
                user_dict[ce_id]["Completed Rolls"].append(current_roll)
                remove_indexes.append(m_index)
                # update user 2 database
                for index, other_roll in enumerate(database_user[current_roll["Partner"]]["Current Rolls"]) :
                    if other_roll["Event Name"] == "Winner Takes All" : 
                        other_location = index
                        break
                end_time = get_unix(28*3)
                database_user[current_roll["Partner"]]["Cooldowns"]["Winner Takes All"] = end_time
                
                args = [
                    database_user[current_roll["Partner"]]["Discord ID"],
                    0,
                    0,
                    0
                ]
                
            
                ##await add_task(datetime.datetime.fromtimestamp(end_time), args)
                
                
                del database_user[current_roll["Partner"]]["Current Rolls"][other_location]
                returns.append("log: " + "<@{}> has beaten <@{}> in Winner Takes All.".format(user_dict[ce_id]["Discord ID"], database_user[current_roll["Partner"]]["Discord ID"]))
                continue
            # user 2 wins
            elif winner == 2:
                print('brooks wins')
                # update user 2 database
                for index, other_roll in enumerate(database_user[current_roll["Partner"]]["Current Rolls"]) :
                    if other_roll["Event Name"] == "Winner Takes All" : 
                        other_location = index
                        break
                database_user[current_roll["Partner"]]["Current Rolls"][other_location]["End Time"] = get_unix("now")
                database_user[current_roll["Partner"]]["Completed Rolls"].append(database_user[current_roll["Partner"]]["Current Rolls"][other_location])
                del database_user[current_roll["Partner"]]["Current Rolls"][other_location]
                # update user 1 database
                user_dict[ce_id]["Cooldowns"]["Winner Takes All"]  = get_unix(28*3)
                
                
                args = [
                    database_user[ce_id]["Discord ID"],
                    0,
                    0,
                    0
                ]
                
                ##await add_task(datetime.datetime.fromtimestamp(end_time), args)
                
                
                remove_indexes.append(m_index)
                returns.append("log: " + "<@{}> has beaten <@{}> in Winner Takes All.".format(database_user[current_roll["Partner"]]["Discord ID"], user_dict[ce_id]["Discord ID"]))
                continue
            # something goes awry
            else :
                print('something is wrongf')
                returns.append("log: " + "Something went wrong with <@{}> and <@{}>'s Winner Takes All roll. Please contact andy for help :)".format(user_dict[ce_id]["Discord ID"], database_user[current_roll["Partner"]]["Discord ID"]))
                continue
            # ----- winner takes all -----



        # game theory
        elif(current_roll["Event Name"] == "Game Theory") :
            "game theory"
            int_game = current_roll["Games"][0]
            for other_roll in database_user[current_roll["Partner"]]["Current Rolls"] :
                if other_roll["Event Name"] == "Game Theory" : 
                    other_game = other_roll["Games"][0]
                    break
            if other_game == None : 
                returns.append("log: " + "Error! <@{}>'s Game Theory partner, <@{}>, does not have Game Theory registered! Please contact andy about this.".format(user_dict[ce_id]["Discord ID"], database_user[current_roll["Partner"]]["Discord ID"]))
                continue

            # formatting int game
            for dbN_objective in database_name[int_game]["Primary Objectives"] :
                if(type(database_name[int_game]["Primary Objectives"][dbN_objective]) is int) : continue
                if("Achievements" in database_name[int_game]["Primary Objectives"][dbN_objective]) : del database_name[int_game]["Primary Objectives"][dbN_objective]["Achievements"]
                if("Requirements" in database_name[int_game]["Primary Objectives"][dbN_objective]) : del database_name[int_game]["Primary Objectives"][dbN_objective]["Requirements"]
                del database_name[int_game]["Primary Objectives"][dbN_objective]["Description"]
                database_name[int_game]["Primary Objectives"][dbN_objective] = database_name[int_game]["Primary Objectives"][dbN_objective]["Point Value"]
            #print(database_name[int_game]["Primary Objectives"])
            #print(user_dict[ce_id]["Owned Games"][int_game]["Primary Objectives"])

            # formatting part game
            for dbN_objective in database_name[other_game]["Primary Objectives"] :
                if(type(database_name[other_game]["Primary Objectives"][dbN_objective]) is int) : continue
                if("Achievements" in database_name[other_game]["Primary Objectives"][dbN_objective]) : del database_name[other_game]["Primary Objectives"][dbN_objective]["Achievements"]
                if("Requirements" in database_name[other_game]["Primary Objectives"][dbN_objective]) : del database_name[other_game]["Primary Objectives"][dbN_objective]["Requirements"]
                del database_name[other_game]["Primary Objectives"][dbN_objective]["Description"]
                database_name[other_game]["Primary Objectives"][dbN_objective] = database_name[other_game]["Primary Objectives"][dbN_objective]["Point Value"]
            
            # figure out who completed what game
            winner = ""
            bool_1 = int_game in user_dict[ce_id]["Owned Games"] and "Primary Objectives" in user_dict[ce_id]["Owned Games"][int_game] and user_dict[ce_id]["Owned Games"][int_game]["Primary Objectives"] == database_name[int_game]["Primary Objectives"]
            bool_2 = other_game in database_user[current_roll["Partner"]]["Owned Games"] and "Primary Objectives" in database_user[current_roll["Partner"]]["Owned Games"][other_game] and database_user[current_roll["Partner"]]["Owned Games"][other_game]["Primary Objectives"] == database_name[other_game]["Primary Objectives"]
            if bool_1 and not bool_2 :
                winner = 1
            elif not bool_1 and bool_2 :
                winner = 2
            elif not bool_1 and not bool_2 :
                print('fail')
                if current_roll["End Time"] < get_unix("now") : returns.append("log: " + "<@{}> and <@{}> ")
                continue
            elif bool_1 and bool_2 :
                winner = 1
            # user 1 wins
            if winner == 1 :
                print('andy wins')
                # update user 1 database
                current_roll["End Time"] = get_unix("now")
                user_dict[ce_id]["Completed Rolls"].append(current_roll)
                remove_indexes.append(m_index)
                # update user 2 database
                for index, other_roll in enumerate(database_user[current_roll["Partner"]]["Current Rolls"]) :
                    if other_roll["Event Name"] == "Game Theory" : 
                        other_location = index
                        break
                end_time = get_unix(28)
                database_user[current_roll["Partner"]]["Cooldowns"]["Game Theory"] = end_time
                

                
                args = [
                    database_user[current_roll["Partner"]]["Discord ID"],
                    0,
                    0,
                    0
                ]
                
                ##await add_task(datetime.datetime.fromtimestamp(end_time), args)
                
                
                del database_user[current_roll["Partner"]]["Current Rolls"][other_location]
                returns.append("log: " + "<@{}> has beaten <@{}> in Game Theory.".format(user_dict[ce_id]["Discord ID"], database_user[current_roll["Partner"]]["Discord ID"]))
                continue
            # user 2 wins
            elif winner == 2:
                print('brooks wins')
                # update user 2 database
                for index, other_roll in enumerate(database_user[current_roll["Partner"]]["Current Rolls"]) :
                    if other_roll["Event Name"] == "Game Theory" : 
                        other_location = index
                        break
                database_user[current_roll["Partner"]]["Current Rolls"][other_location]["End Time"] = get_unix("now")
                database_user[current_roll["Partner"]]["Completed Rolls"].append(database_user[current_roll["Partner"]]["Current Rolls"][other_location])
                del database_user[current_roll["Partner"]]["Current Rolls"][other_location]
                # update user 1 database
                end_time = get_unix(28)
                user_dict[ce_id]["Cooldowns"]["Game Theory"]  = end_time
                
                
                args = [
                    database_user[ce_id]["Discord ID"],
                    0,
                    0,
                    0
                ]
                
                ##await add_task(datetime.datetime.fromtimestamp(end_time), args)
                
                
                remove_indexes.append(m_index)
                returns.append("log: " + "<@{}> has beaten <@{}> in Game Theory.".format(database_user[current_roll["Partner"]]["Discord ID"], user_dict[ce_id]["Discord ID"]))
                continue
            # something goes awry
            else :
                print('something is wrongf')
                returns.append("log: " + "Something went wrong with <@{}> and <@{}>'s Game Theory roll. Please contact andy for help :)".format(user_dict[ce_id]["Discord ID"], database_user[current_roll["Partner"]]["Discord ID"]))
                continue
        # game theory





        # one hell of a month #
        elif current_roll["Event Name"] == "One Hell of a Month" :
            "one "

            "?}{}"

            genrepoints = {
                "Action" : 0,
                "Arcade" : 0,
                "Bullet Hell" : 0,
                "First-Person" : 0,
                "Platformer" : 0,
                "Strategy" : 0
            }

            for game in current_roll["Games"] :

                del database_name[game]["Community Objectives"]
                # formatting
                for dbN_objective in database_name[game]["Primary Objectives"] :
                    if(type(database_name[game]["Primary Objectives"][dbN_objective]) is int) : continue
                    if("Achievements" in database_name[game]["Primary Objectives"][dbN_objective]) : del database_name[game]["Primary Objectives"][dbN_objective]["Achievements"]
                    if("Requirements" in database_name[game]["Primary Objectives"][dbN_objective]) : del database_name[game]["Primary Objectives"][dbN_objective]["Requirements"]
                    del database_name[game]["Primary Objectives"][dbN_objective]["Description"]
                    database_name[game]["Primary Objectives"][dbN_objective] = database_name[game]["Primary Objectives"][dbN_objective]["Point Value"]
                
                if game in user_dict[ce_id]["Owned Games"] and "Primary Objectives" in user_dict[ce_id]["Owned Games"][game] and user_dict[ce_id]["Owned Games"][game]["Primary Objectives"] == database_name[game]["Primary Objectives"]: 
                    genrepoints[database_name[game]["Genre"]] += 1
            
            # go through each genre and determine if they actually did it
            total_genre = 0
            for genr in genrepoints:
                if genrepoints[genr] >= 3 : total_genre += 1
            
            if total_genre >= 5 : roll_completed = True
            else: roll_completed = False

            

        elif current_roll["Event Name"] == "Fourward Thinking" or current_roll["Event Name"] == "Two Week T2 Streak" or current_roll["Event Name"] == "Two 'Two Week T2 Streak' Streak":
            ""
            # pending should have been dealt with by now
            # only check the most recently added game
            if "End Time" not in current_roll : continue
            game = current_roll["Games"][len(current_roll["Games"]) - 1]
            try:
                del database_name[game]["Community Objectives"]
            except:
                ""
            
            # format database_name like database_user
            for dbN_objective in database_name[game]["Primary Objectives"]:
                if(type(database_name[game]["Primary Objectives"][dbN_objective]) is int) : continue
                if("Achievements" in database_name[game]["Primary Objectives"][dbN_objective]) : del database_name[game]["Primary Objectives"][dbN_objective]["Achievements"]
                if("Requirements" in database_name[game]["Primary Objectives"][dbN_objective]) : del database_name[game]["Primary Objectives"][dbN_objective]["Requirements"]
                del database_name[game]["Primary Objectives"][dbN_objective]["Description"]
                database_name[game]["Primary Objectives"][dbN_objective] = database_name[game]["Primary Objectives"][dbN_objective]["Point Value"]
            
            print(database_name[game]["Primary Objectives"])
            if (
                (game not in user_dict[ce_id]["Owned Games"]) or 
                ("Primary Objectives" not in user_dict[ce_id]["Owned Games"][game]) or 
                (user_dict[ce_id]["Owned Games"][game]["Primary Objectives"] != database_name[game]["Primary Objectives"])
                ) : 
                    roll_completed = False




        else :
        # -------- check to see if rolls that aren't weird (solo rolls) are done ------------
            for game in current_roll["Games"] :
            
                # ---------- standardize the game dictionary ----------
                # remove COs from the equation
                try:
                    del database_name[game]["Community Objectives"]
                except:
                    "do nothing lol"

                # format database_name like users2.json
                for dbN_objective in database_name[game]["Primary Objectives"] :
                    if(type(database_name[game]["Primary Objectives"][dbN_objective]) is int) : continue
                    #print(dbN_objective)
                    if("Achievements" in database_name[game]["Primary Objectives"][dbN_objective]) : del database_name[game]["Primary Objectives"][dbN_objective]["Achievements"]
                    if("Requirements" in database_name[game]["Primary Objectives"][dbN_objective]) : del database_name[game]["Primary Objectives"][dbN_objective]["Requirements"]
                    del database_name[game]["Primary Objectives"][dbN_objective]["Description"]
                    database_name[game]["Primary Objectives"][dbN_objective] = database_name[game]["Primary Objectives"][dbN_objective]["Point Value"]

                # ---------- check to see if the games are equal ----------
                if ((game not in user_dict[ce_id]["Owned Games"]) or ("Primary Objectives" not in user_dict[ce_id]["Owned Games"][game]) or (user_dict[ce_id]["Owned Games"][game]["Primary Objectives"] != database_name[game]["Primary Objectives"])) : roll_completed = False


        # -------------------------------------------------- NO MORE CHECKING --------------------------------------------------------------
        # you;ve now gotten to the end. 
        # if roll completed is false then the roll was failed. 
        # if roll completed is true then they succeeded
        
        # we now have to determine if the roll has ended or not. 
        # it could be that this function was called because the roll has ended, 
        # or because it is just being updated.
                



        # -----------------------------  ROLL WAS FAILED -----------------------------
        if not roll_completed and ("End Time" not in current_roll or get_unix('now') > current_roll["End Time"]) : 
            # fourward thinking
            if current_roll["Event Name"] == "Fourward Thinking" :
                if "End Time" not in current_roll : continue
                returns.append("casino: <@{}>, you have failed your T{} in Fourward Thinking. You are now on cooldown.".format(user_dict[ce_id]["Discord ID"], str(len(current_roll["Games"]))))
                remove_indexes.append(m_index)

                cooldown_days = (len(current_roll["Games"]) * 14) + ((len(current_roll["Games"]) - 1) - (current_roll["Rerolls"]))*28
                database_user[ce_id]["Cooldowns"]["Fourward Thinking"] = get_unix(cooldown_days)

                continue


            # two week t2 streak
            elif current_roll["Event Name"] == "Two Week T2 Streak":
                if "End Time" not in current_roll : continue
                returns.append("casino: <@{}>, you have failed Two Week T2 Streak. There is no cooldown.".format(user_dict[ce_id]["Discord ID"]))
                remove_indexes.append(m_index)

                continue # :)

                
            
            # two "two week t2 streak" streak
            elif current_roll["Event Name"] == "Two 'Two Week T2 Streak' Streak":
                if "End Time" not in current_roll : continue
                returns.append("casino: <@{}>, you have failed Two 'Two Week T2 Streak' Streak and are now on cooldown.".format(user_dict[ce_id]["Discord ID"]))
                remove_indexes.append(m_index)

                database_user[ce_id]["Cooldowns"]["Two 'Two Week T2 Streak' Streak"] = get_unix(7)

                continue # :)

            # ----------------------- REGULAR ROLL HAS ENDED ----------------------------
            else: # if the roll was not completed AND the event name is ended_roll_name then they failed
                
                # if the game was pending... make a separate message
                if current_roll["Games"][0] == "pending..." : 
                    returns.append("casino: " + "<@{}>, you can now roll {} again.".format(user_dict[ce_id]["Discord ID"], current_roll["Event Name"]))
                
                # if this was a co-op roll
                elif "Partner" in current_roll : 
                    
                    # add the message
                    returns.append("casino: " + "<@{}> and <@{}>, you have failed your {} roll and are now on cooldown.".format(user_dict[ce_id]["Discord ID"], database_user[current_roll["Partner"]]["Discord ID"], current_roll["Event Name"]))
                    
                    # grab and delete partner's instance as well
                    myindex = ""
                    for roll, index3 in enumerate(database_user[current_roll["Partner"]]["Current Rolls"]):
                        if roll["Event Name"] == current_roll["Event Name"] : 
                            myindex = index3
                            break
                    del database_user[current_roll["Partner"]]["Current Rolls"][myindex]
                    
                    # set up cooldowns
                    database_user[ce_id]["Cooldowns"][current_roll["Event Name"]] = get_unix(cooldowns[current_roll["Event Name"]])
                    database_user[current_roll["Partner"]]["Cooldowns"][current_roll["Event Name"]] = get_unix(cooldowns[current_roll["Event Name"]])
                
                # this is a normal solo roll
                else : 
                    print('working')
                    # fourward thinking? again?
                    if current_roll["Event Name"] == "Fourward Thinking" : 
                        returns.append("casino: <@{}>, you have failed your T{} in Fourward Thinking. You are now on cooldown.".format(user_dict[ce_id]["Discord ID"], str(len(current_roll["Games"]))))
                    
                    # add the message for any normal roll
                    returns.append("casino: <@{}>, you have failed your {} roll and are now on cooldown.".format(user_dict[ce_id]["Discord ID"], current_roll["Event Name"]))
                    
                    # and add the cooldown
                    if current_roll["Event Name"] == "Fourward Thinking" :
                        cooldown_days = 0
                        database_user[ce_id]["Cooldowns"][current_roll["Event Name"]] = get_unix("now")
                    database_user[ce_id]["Cooldowns"][current_roll["Event Name"]] =  get_unix(cooldowns[current_roll["Event Name"]])
                remove_indexes.append(m_index)
            
            continue
        
        # ----------------------------- REGULAR ROLL WAS COMPLETED -----------------------------
        if roll_completed:
            # if its forward thinking, check the stage and run accordingly
            if(current_roll["Event Name"] == "Fourward Thinking") :
                if len(current_roll["Games"]) == 4 : 
                    returns.append("log: Congratulations to <@{}>! They have completed Fourward Thinking!".format(user_dict[ce_id]["Discord ID"]))
                else: 
                    del current_roll["End Time"]
                    returns.append("casino: <@{}>, you have completed the T{} in your Fourward Thinking roll. Use `/solo-roll Fourward Thinking` to move to your next stage!".format(user_dict[ce_id]["Discord ID"], str(len(current_roll["Games"]))))
                    continue
            
            elif(current_roll["Event Name"] == "Two Week T2 Streak") :
                if len(current_roll["Games"]) == 2:
                    returns.append("log: Congratulations <@{}>! You have completed Two Week T2 Streak!".format(user_dict[ce_id]["Discord ID"]))
                else:
                    del current_roll["End Time"]
                    returns.append("casino: <@{}>, you have completed your first T2. Use `/solo_roll Two Week T2 Streak` to roll your second one.".format(user_dict[ce_id]["Discord ID"]))
                    continue
            
            elif(current_roll["Event Name"] == "Two 'Two Week T2 Streak' Streak") :
                if len(current_roll["Games"]) == 4:
                    returns.append("log: Congratulations <@{}>! You have completed Two 'Two Week T2 Streak' Streak!".format(user_dict[ce_id]["Discord ID"]))
                else:
                    del current_roll["End Time"]
                    returns.append("casino: <@{}>, you have completed game {} of 4 in Two 'Two Week T2 Streak' Streak. Use `/solo_roll` Two 'Two Week T2 Streak' Streak to roll your next one.".format(
                        user_dict[ce_id]["Discord ID"], len(current_roll["Games"])
                    ))
                    continue
            
            # if it's a co-op roll, send it to the log channel
            elif(current_roll["Event Name"] in ["Destiny Alignment", "Soul Mates", "Teamwork Makes the Dream Work"]) :
                returns.append("log: " + "<@{}> and <@{}> have completed {}!".format(user_dict[ce_id]["Discord ID"], database_user[current_roll["Partner"]]["Discord ID"], current_roll["Event Name"]))
            
            # if it's a solo roll, send it to the log channel
            else:
                returns.append("log: " + "<@{}>, you have completed {}! Congratulations!".format(user_dict[ce_id]["Discord ID"], current_roll["Event Name"]))
            
            # edit the roll that was completed
            current_roll["End Time"] = get_unix("now")
            user_dict[ce_id]["Completed Rolls"].append(current_roll)

            # if it's a co-op roll, delete their instance as well
            if "Partner" in current_roll:
                myindex = ""
                for index3, roll in enumerate(database_user[current_roll["Partner"]]["Current Rolls"]):
                    if roll["Event Name"] == current_roll["Event Name"] : 
                        myindex = index3
                        break
                user_dict[current_roll["Partner"]]["Current Rolls"][myindex]["End Time"] = get_unix("now")
                user_dict[current_roll["Partner"]]["Completed Rolls"].append(user_dict[current_roll["Partner"]]["Current Rolls"][myindex])
                del database_user[current_roll["Partner"]]["Current Rolls"][myindex]

            # add this index to the ones that need to be removed
            remove_indexes.append(m_index) 
    
    # ///////////////////////////////////////////////////////////////////////////////////////////
    
    
    
    for cooldown in (user_dict[ce_id]["Cooldowns"]):
        if user_dict[ce_id]["Cooldowns"][cooldown] < get_unix("now"):
            cooldown_indexes.append(cooldown)
            returns.append("casino: <@{}>, your {} cooldown has now ended.".format(user_dict[ce_id]["Discord ID"], cooldown))
        
    remove_indexes.reverse()
    for indexx in remove_indexes :
        del user_dict[ce_id]["Current Rolls"][indexx]

    cooldown_indexes.reverse()
    for c_index in cooldown_indexes:
        del user_dict[ce_id]["Cooldowns"][c_index]
    
    # Add the user file to the database
    database_user.update(user_dict)

    # Dump the data
    returns.insert(0, database_user)
    
    returns.append("Updated")

    return returns

