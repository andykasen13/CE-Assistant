import time
import datetime

# ---------------------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------------- ROLL STRING ---------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
def get_roll_string(userInfo, steam_user_name, database_name_info, target_user, x) :
    # set up this bullshit
    roll_string = ""

    # grab all current rolls
    for x in userInfo[steam_user_name][x] :
        end_time = time.mktime(datetime.datetime.strptime(str(x['end_time']), "%Y-%m-%d %H:%M:%S").timetuple())
        roll_string = roll_string + "- __" + x['event_name'] + "__ (complete by <t:" + str(int(end_time)) + ">):\n"
        gameNum = 1
        for game in x['Games'] : # Iterate through all games in the roll event
            game_info = database_name_info[game] # Grab the dictionary containing all info about that game
            game_title = game # Set the game title
            roll_string += "  " + str(gameNum) + ". "+ str(game_title) + "\n" # Add the game number and the game title to the string
            for objective_title in game_info["Primary Objectives"] : # Iterate through all of the games' objectives
                objective_info = (game_info["Primary Objectives"][objective_title]) # Grab the dictionary containing all info about that objective
                objective_point_value = objective_info["Point Value"] # Set the point value
                roll_string += "    - " + str(objective_title) + " (" + str(objective_point_value) + ")\n" # Update the roll string
            gameNum += 1 # Add to the gameNum
    
    # account for no current rolls
    if(roll_string == "") :
        if(x == 'Current Rolls') : roll_string = f"{target_user.name} has no current rolls."
        elif(x == 'Completed Rolls') : roll_string = f"{target_user.name} has no completed rolls."

    return roll_string
