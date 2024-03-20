import discord
import datetime
from mongo_silly import *

def check_site_achievements(interaction : discord.Interaction, database_name, database_user, database_tier) :
    # grab ce-id
    ce_id = get_ce_id_normal(interaction.user.id, database_user)

    # grab the user's api page
    user_api = get_api("user", ce_id)
    if user_api == None : return Literal["api failed"]

    # set up the actual dictionary
    achievements : dict[str, bool] = {
        "\"I'll add it to the backlog\"" : False,
        "Chase the Rainbow" : False,
        "Happy Anniversary" : False,
        "Insert Tired Old Meme Here" : False,
        "Supporter" : False,
        "Veteran" : False,
        "As God Intended" : False,
        "Challenge Sequence" : False,
        "Female Empowerment" : False, #star
        "Flash of Nostalgia" : False, #star
        "Follow the Masses" : False, #star
        "Free Advertising" : False, #star
        "Free, As In It Costs No Money" : False, #star
        "Immersive Difficulty" : False, #star
        "Number One Fan" : False, #star
        "Objectively Cracked" : False
    }
    # set up stupid horrible variables
    _made_ofs : int = 0
    _objectively_crackeds : int = 0
    _reach_for_the_stars : bool = False

    for objective in user_api['userObjectives']:
        objective_name = objective['objective']['name']
        objective_id = objective['objectiveId']
        points = objective['objective'] = objective['objective']['points'] if not objective['partial'] else objective['objective']['pointsPartial']
        if objective_name[0:7] == "Made of" : _made_ofs += 1
        if points > 10 : _objectively_crackeds += 1
    
    for game in user_api['userGames']:
        game_name = game['game']['name']
        game_id = game['gameId']
        if game['points'] >= 500 : _reach_for_the_stars = True

        

    achievements["\"I'll add it to the backlog\""] = len(user_api['userGames']) >= 365
    achievements["Chase the Rainbow"] = False
    achievements["Happy Anniversary"] = (datetime.datetime.now() - interaction.user.joined_at) > datetime.timedelta(days=365)
    achievements["Insert Tired Old Meme Here"] = False
    achievements["Supporter"] = False
    achievements["Veteran"] = (datetime.datetime.now() - interaction.user.joined_at) > datetime.timedelta(days=(365*3))
    achievements["As God Intended"] = _made_ofs >= 5
    achievements["Objectively Cracked"] = _objectively_crackeds >= 140



