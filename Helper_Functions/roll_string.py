import time
import datetime

# ---------------------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------------- ROLL STRING ---------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
def get_roll_string(userInfo, ce_id, database_name, target_user, roll_type) :
    # set up this bullshit
    roll_string = ""

    # grab all current rolls
    for x in userInfo[ce_id][roll_type] :
        print(x.keys())

        # get all the values (if they exist!)
        if("End Time" in list(x.keys())) : end_time = x["End Time"]
        else : end_time = None
        if("Games" in list(x.keys())) : games = x["Games"]
        else : games = None
        if("Partner" in list(x.keys())) : partner = x["Partner"]
        else : partner = None

        print(x)



        roll_string = roll_string + "- __" + x['Event Name'] + "__"

        if(end_time != None) : 
            if(roll_type == "Current Rolls") : roll_string += " (complete by "
            elif(roll_type == "Completed Rolls") : roll_string += " (completed on "
            roll_string += "<t:" + str(end_time) + ">):\n"
        else : roll_string += "\n"

        if(partner != None) :
            roll_string += "  (Partner: <@" + str(userInfo[partner]["Discord ID"]) +">)\n"

        

        gameNum = 1

        # if no games are listed, do not continue
        if(games != None) :
        
            for game in x['Games'] : # Iterate through all games in the roll event
                game_info = database_name[game] # Grab the dictionary containing all info about that game
                game_title = game # Set the game title
                roll_string += "  " + str(gameNum) + ". "+ str(game_title) # Add the game number and the game title to the string
                
                # set up points
                total_default_points = 0
                total_user_points = 0

                # get points
                for objective_title in game_info["Primary Objectives"] : # Iterate through all of the games' objectives
                    total_default_points += game_info["Primary Objectives"][objective_title]["Point Value"]

                    if(True
                    and
                    True) : print('yay')

                    if(game_title in list(userInfo[ce_id]["Owned Games"].keys())
                    and
                    "Primary Objectives" in list(userInfo[ce_id]["Owned Games"][game_title].keys())
                    and
                    objective_title in list(userInfo[ce_id]["Owned Games"][game_title]["Primary Objectives"].keys())) : 
                            total_user_points += userInfo[ce_id]["Owned Games"][game_title]["Primary Objectives"][objective_title]

                roll_string += " (" + str(total_user_points) + "/" + str(total_default_points) +")\n"
                gameNum += 1 # Add to the gameNum
    
    # account for no current rolls
    if(roll_string == "") :
        if(roll_type == 'Current Rolls') : roll_string = f"{target_user.name} has no current rolls."
        elif(roll_type == 'Completed Rolls') : roll_string = f"{target_user.name} has no completed rolls."

    return roll_string
