import time
from bson import ObjectId
import discord
from Helper_Functions.create_embed import create_multi_embed
from Helper_Functions.rollable_games import get_rollable_game
import json
import datetime
from datetime import timedelta

from Helper_Functions.Scheduler import add_task
from Helper_Functions.mongo_silly import *

# -------------------------------------------------------------------------------------------------- #
# -------------------------------------------- BUTTONS --------------------------------------------- #
# -------------------------------------------------------------------------------------------------- #

async def get_buttons(view : discord.ui.View, embeds):
    currentPage = 1
    page_limit = len(embeds)
    buttons = [discord.ui.Button(label=">", style=discord.ButtonStyle.green, disabled=False), discord.ui.Button(label="<", style=discord.ButtonStyle.red, disabled=True)]
    view.add_item(buttons[1])
    view.add_item(buttons[0])

    async def hehe(interaction):
        return await callback(interaction, num=1)

    async def haha(interaction):
        return await callback(interaction, num=-1)

    async def callback(interaction, num):
        nonlocal currentPage, view, embeds, page_limit, buttons
        currentPage+=num
        if(currentPage >= page_limit) :
            buttons[0].disabled = True
        else : buttons[0].disabled = False
        if(currentPage <= 1) :
            buttons[1].disabled = True
        else : buttons[1].disabled = False
        await interaction.response.edit_message(embed=embeds[currentPage-1], view=view)

    buttons[0].callback = hehe
    buttons[1].callback = haha

    async def disable() :
        for button in buttons :
            button.disabled = True
        print("disabled")

    #view.on_timeout = await disable()

async def get_genre_buttons(view : discord.ui.View, completion_time : int, price_limit : int, tier_number : str, event_name : str, 
                            time_limit : int, cooldown_time : int, num_of_games : int, user_id : int, 
                            collection) :
    """
    Overview
    ----------
    Gets buttons for each genre in Challenge Enthusiasts.

    Parameters
    -----------
    view: :class:`discord.ui.View` (REQUIRED)
        The view of the message that's been sent. This is required.
    
    completion_time: :class:`int` (REQUIRED)
        The limit on SteamHunters' average completion time for the game(s) chosen.
    
    price_limit: :class:`int` (REQUIRED)
        The limit on the base price on Steam for the game(s) chosen.
    
    tier_number: :class:`str` (REQUIRED)
        The tier of the game(s) chosen. (e.g. "Tier 1")
    
    event_name: :class:`str` (REQUIRED)
        The name of the roll event.
    
    time_limit: :class:`int` (REQUIRED)
        The amount of time (in days) for the user to complete this roll event.
    
    cooldown_time: :class:`int` (REQUIRED)
        The amount of time (in days) that the cooldown will last if the user fails the roll event.
    
    num_of_games: :class:`int` (REQUIRED)
        The number of games that need to be rolled for this event.
    
    user_id: :class:`int` (REQUIRED)
        The Discord ID for the user who rolled this event.
    
    collection: :class:`MongoCollection` (REQUIRED)
        The collection to pull the MongoDB information from.

    Helpful Note (from andy :))
    ----------------------------
    To make any of these buttons disabled (like, for example, in Fourward Thinking),
    after the call to this function, write `buttons[i].disabled = True`.
    """
    

    games = []
    genres = ["Action", "Arcade", "Bullet Hell", "First-Person", "Platformer", "Strategy"]
    buttons = []
    i=0
    for genre in genres :
        print(genre)
        buttons.append(discord.ui.Button(label=genre, style=discord.ButtonStyle.gray))
        view.add_item(buttons[i])
        i+=1

    print(view.children)

    async def AC_callback(interaction) : return await callback(interaction, "Action")
    async def AR_callback(interaction) : return await callback(interaction, "Arcade")
    async def BH_callback(interaction) : return await callback(interaction, "Bullet Hell")
    async def FP_callback(interaction) : return await callback(interaction, "First-Person")
    async def PF_callback(interaction) : return await callback(interaction, "Platformer")
    async def ST_callback(interaction) : return await callback(interaction, "Strategy")

    async def callback(interaction : discord.Interaction, genre_name):
        await interaction.response.defer()
        
        # only accept buttons from interaction user
        if interaction.user.id != user_id : return

        # clear the view and send a "working" message
        view.clear_items()
        await interaction.followup.edit_message(embed=discord.Embed(title="working..."), view=view, message_id=interaction.message.id)

        # Open database name
        database_name = await get_mongo("name")
        database_tier = await get_mongo("tier")
        steamhunters = await get_mongo('steamhunters')
        database_user = await get_mongo('user')


        i=0
        while i < num_of_games :
            games.append(get_rollable_game(completion_time, price_limit, tier_number, specific_genre =genre_name, database_tier=database_tier, database_name=database_name, games=games, steamhunters=steamhunters, user_info=database_user))
            i+=1

        embeds = create_multi_embed(event_name, time_limit, games, cooldown_time, interaction, database_name)
        await get_buttons(view, embeds)
        await interaction.followup.edit_message(embed=embeds[0], view=view, message_id=interaction.message.id)

        # Open database_user
        database_user = await get_mongo("user")
        
        # grab the target user
        target_user = await get_ce_id(user_id)
        
        # find the roll to replace (if it exists)
        roll_num = -1
        for i, current_roll in enumerate(database_user[target_user]['Current Rolls']) :
            if current_roll['Event Name'] == event_name : 
                roll_num = i
                break

        # update the 
        end_time = get_unix(time_limit)

        # of course, the king of shitters, fourward thinking
        if (event_name == "Fourward Thinking"):

            # this isn't their first roll
            if (roll_num != -1) :
                r = database_user[target_user]['Current Rolls'][roll_num]['Rerolls']
                
                finished_games = database_user[target_user]['Current Rolls'][roll_num]['Games']
                r+=1
                database_user[target_user]['Current Rolls'][roll_num] = ({
                    "Event Name" : "Fourward Thinking",
                    "End Time" : end_time,
                    "Games" : finished_games + games,
                    "Rerolls" : r
                })
            
            # this is their first roll
            else :
                database_user[target_user]['Current Rolls'].append({
                    'Event Name' : 'Fourward Thinking',
                    'End Time' : end_time,
                    'Games' : games,
                    'Rerolls' : 0
                })
            del database_user[target_user]['Pending Rolls']['Fourward Thinking']

        elif (event_name == "Let Fate Decide"):
            database_user[target_user]['Cooldowns']['Let Fate Decide'] = get_unix(months=3)
            database_user[target_user]['Current Rolls'].append({
                'Event Name' : 'Let Fate Decide',
                'Games' : games
            })
        # all other rolls
        else:
            if (roll_num != -1) :
                database_user[target_user]['Current Rolls'][roll_num] = ({"Event Name" : event_name, 
                                                        "End Time" : end_time,
                                                        "Games" : games})
            else :
                database_user[target_user]['Current Rolls'].append({
                    'Event Name' : event_name,
                    'End Time' : end_time,
                    'Games' : games
                })
        
        # args = [
        #     database_user[target_user]['Discord ID'],
        #     0,
        #     0,
        #     0
        # ]
        
        #await add_task(datetime.datetime.fromtimestamp(end_time), args)
        
        """
        elif reroll :
            c_nums = []
            for index, c_roll in enumerate(database_user[target_user]['Current Rolls']) :
                if c_roll['Event Name'] == event_name :
                    c_nums.append(index)
                    

            print(c_nums)
            
            if c_nums == [] : return await interaction.followup.send('you havent rolled this game. except i should have cleared that already. something is wrong')

            if len(c_nums) > 1 : 
                del database_user[target_user]['Current Rolls'][c_nums[1]]

            c_num = c_nums[0]

            database_user[target_user]['Current Rolls'][c_num] = ({
                "Event Name" : event_name,
                "End Time" : database_user[target_user]['Current Rolls'][c_num]['End Time'],
                "Games" : games
            })
        """

        # dump the info
        dump = await dump_mongo("user", database_user)
        del dump
        return

    buttons[0].callback = AC_callback
    buttons[1].callback = AR_callback
    buttons[2].callback = BH_callback
    buttons[3].callback = FP_callback
    buttons[4].callback = PF_callback
    buttons[5].callback = ST_callback        

