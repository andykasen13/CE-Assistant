import time
import datetime

# ---------------------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------------- ROLL STRING ---------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
def get_roll_string(database_user, ce_id, database_name, target_user, roll_type) :
    # set up this bullshit
    roll_string = ""

    """
    for obj in database_user[ce_id][roll_type]:
        if "End Time" in obj : end_time = obj['End Time']
        else : end_time = None
        if "Games" in obj : games = obj['Games']
        else: games = None
        if "Partner" in obj : partner = obj['Partner']
        else : partner = None
        if "Rerolls" in obj : rerolls = obj['Rerolls']
        else : rerolls = None


    return
    """
    # grab all current rolls
    for x in database_user[ce_id][roll_type] :

        # get all the values (if they exist!)
        if("End Time" in list(x.keys())) : end_time = x['End Time']
        else : end_time = None
        if("Games" in list(x.keys())) : games = x['Games']
        else : games = None
        if("Partner" in list(x.keys())) : partner = x['Partner']
        else : partner = None
        if("Rerolls" in list(x.keys())) : rerolls = x['Rerolls']
        else : rerolls = None

        roll_string = roll_string + "- __" + x['Event Name'] + "__"

        if(end_time != None) : 
            if(roll_type == "Current Rolls") : roll_string += " (complete by "
            elif(roll_type == "Completed Rolls") : roll_string += " (completed on "
            roll_string += "<t:" + str(end_time) + ">)"

        if(partner != None) :
            roll_string += " (Partner: <@" + str(database_user[partner]['Discord ID']) +">)"

        if(x['Event Name'] == "One Hell of a Month") and games != None:
            roll_string += "\t\t- Just DM me <@413427677522034727> for details. This will be updated in v1.1.\n"
            continue

        if end_time == None and games == None and partner == None : 
            roll_string += "\n"
            continue
        
        roll_string += ":\n"

        gameNum = 1

        # if no games are listed, do not continue
        if(games != None) :
        
            for game in x['Games'] : # Iterate through all games in the roll event
                game_info = database_name[game] # Grab the dictionary containing all info about that game
                game_title = database_name[game]['Name'] # Set the game title
                roll_string += "  " + str(gameNum) + ". "+ str(game_title) # Add the game number and the game title to the string
                
                # set up points
                total_default_points = 0
                total_user_points = 0

                # get points
                for objective_title in game_info['Primary Objectives'] : # Iterate through all of the games' objectives
                    total_default_points += game_info['Primary Objectives'][objective_title]['Point Value']

                    if(game_title in list(database_user[ce_id]['Owned Games'].keys())
                    and
                    "Primary Objectives" in list(database_user[ce_id]['Owned Games'][game_title].keys())
                    and
                    objective_title in list(database_user[ce_id]['Owned Games'][game_title]['Primary Objectives'].keys())) : 
                            total_user_points += database_user[ce_id]['Owned Games'][game_title]['Primary Objectives'][objective_title]

                roll_string += " (" + str(total_user_points) + "/" + str(total_default_points) +")\n"
                gameNum += 1 # Add to the gameNum
    
    # account for no current rolls
    if(roll_string == "") :
        if(roll_type == 'Current Rolls') : roll_string = f"{target_user.name} has no current rolls."
        elif(roll_type == 'Completed Rolls') : roll_string = f"{target_user.name} has no completed rolls."

    return roll_string
