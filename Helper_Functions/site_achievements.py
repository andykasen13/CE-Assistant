import discord
import datetime
from Helper_Functions.mongo_silly import *

async def check_site_achievements(user : discord.Member) :
    """Takes in the interaction and returns """
    # grab mongos
    database_name = await get_mongo('name')
    database_tier = await get_mongo('tier')
    database_user = await get_mongo('user')

    # grab ce-id
    ce_id = get_ce_id_normal(user.id, database_user)

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
        "Objectively Cracked" : False,
        "Puzzle Grandmaster" : False,
        "Reach for the Stars" : False,
        "Reading Rainbow" : False,
        "Super Super Super Super Super Super Super Super Super Super Super Super Super Super Super Star" : False,
        "The 1%" : False,
        "Word from the Wise" : False,
        "Zookeeper" : False
    }
    
    # set up stupid horrible variables
    _made_ofs : int = 0
    _objectively_crackeds : int = 0
    _reach_for_the_stars : bool = False
    _puzzle_games_objectives : int = 0
    _alphabet : list[str] = ["a", "b", "c", "d", "e", "f", "g", "h", "i", 
                             "j", "k", "l", "m", "n", "o", "p", "q", "r", 
                             "s", "t", "u", "v", "w", "x", "y", "z"]
    _supers = 0

    # iterate through objectives
    for objective in user_api['userObjectives']:
        objective_name : str = objective['objective']['name']
        objective_id : str = objective['objectiveId']
        points = objective['objective'] = objective['objective']['points'] if not objective['partial'] else objective['objective']['pointsPartial']
        if objective_name[0:7] == "Made of" : _made_ofs += 1
        if points > 10 : _objectively_crackeds += 1
        if objective_id == "27578157-10b2-4f29-acee-452c2dc59477" : _puzzle_games_objectives += 1
    
    # iterate through games
    for game in user_api['userGames']:
        game_name : str = game['game']['name']
        game_id : str = game['gameId']
        completed : bool = game['points'] == game['game']['points']
        if game['points'] >= 500 : _reach_for_the_stars = True
        if completed and game_name[0:1].lower() in _alphabet : _alphabet.remove(game_name[0:1].lower())
        if completed and "super" in game_name.lower() : _supers += 1


    # set values
    achievements["\"I'll add it to the backlog\""] = len(user_api['userGames']) >= 365
    #achievements["Chase the Rainbow"] = False
    achievements["Happy Anniversary"] = (datetime.datetime.now(datetime.timezone.utc) - user.joined_at) > datetime.timedelta(days=365)
    #achievements["Insert Tired Old Meme Here"] = False
    #achievements["Supporter"] = False
    achievements["Veteran"] = (datetime.datetime.now(datetime.timezone.utc) - user.joined_at) > datetime.timedelta(days=(365*3))
    achievements["As God Intended"] = _made_ofs >= 5
    achievements["Objectively Cracked"] = _objectively_crackeds >= 140
    achievements["Puzzle Grandmaster"] = _puzzle_games_objectives >= 10
    achievements["Reach for the Stars"] = _reach_for_the_stars
    achievements["Reading Rainbow"] = len(_alphabet) == 0
    achievements['Super Super Super Super Super Super Super Super Super Super Super Super Super Super Super Star'] = _supers >= 15

    # make the message
    description = ""
    for site_achievement in achievements :
        description += site_achievement + " "
        description += "✅" if achievements[site_achievement] else "🚫"
        description += "\n"
    
    # make the embed
    embed = discord.Embed(
        title="Site Achievement Progress",
        description=description,
        timestamp=datetime.datetime.now(),
        color=0x000000
    )
    return embed

