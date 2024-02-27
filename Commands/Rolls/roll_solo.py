import asyncio
import functools
from functools import wraps
import random
import typing
from bson import ObjectId
import discord
import datetime
from datetime import timedelta
import calendar
import json
import time
# --------- other file imports ---------
from Helper_Functions.rollable_games import get_rollable_game, get_rollable_game_from_list
from Helper_Functions.create_embed import create_multi_embed, getEmbed
from Helper_Functions.roll_string import get_roll_string
from Helper_Functions.buttons import get_buttons, get_genre_buttons
from Helper_Functions.update import update_p
from Helper_Functions.Scheduler import add_task
from Helper_Functions.mongo_silly import *
from Helper_Functions.end_time import months_to_days


def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper


@to_thread
async def solo_command(interaction : discord.Interaction, event : str, reroll : bool, collection) :
    # Set up variables
    view = discord.ui.View(timeout=600)
    games = []
    embeds = []
    genres = ['Action', 'Arcade', 'Bullet Hell', 'First-Person', 'Platformer', 'Strategy']
    times = {
        "One Hell of a Day" : (1),
        "One Hell of a Week" : (7),
        "One Hell of a Month" : (months_to_days(1)),
        "Two Week T2 Streak" : (14),
        "Two 'Two Week T2 Streak' Streak" : (months_to_days(1)),
        "Never Lucky" : (0),
        "Triple Threat" : (months_to_days(1)),
        "Let Fate Decide" : (0),
        "Fourward Thinking" : (0),
        "Russian Roulette" :(0)
    }
    dont_save = False
    ends = True

    # games that have more than one stage or are rerollable
    special_rolls = ["Two Week T2 Streak", "Two 'Two Week T2 Streak' Streak", "Never Lucky", "Let Fate Decide", "Fourward Thinking"]

    # grab user info
    userInfo = await get_mongo('user')
    
    i = 0
    target_user = ""
    for current_user in userInfo :
        if current_user == '_id' : continue
        if(userInfo[current_user]['Discord ID'] == interaction.user.id) :
            target_user = current_user
            break
    
    # Inform the user that they are not registered.
    if(target_user == "") :
        return await interaction.followup.send("You are not registered in the CE Assistant database. Please try /register with your CE link.")

    # Check if the event is on cooldown...
    if(event in list(userInfo[target_user]['Cooldowns'])) :
        return await interaction.followup.send(embed=discord.Embed(title="Cooldown", description=f"You are currently on cooldown for {event}."))

    # ... or if the user is on pending...
    if (event in userInfo[target_user]['Pending Rolls']) :
        return await interaction.followup.send('Please wait 10 minutes in between rolling for the same event!')

    # ... or if the event is currently active.
    for eventInfo in userInfo[target_user]['Current Rolls'] :
        #TODO: have different errors if someone tries to go again during pending and if someone tries to reroll while pending
        if((eventInfo['Event Name'] == event) and event not in special_rolls) : 
            return await interaction.followup.send(embed=discord.Embed(title=f"You are already participating in {event}!"))

    # grab both databases (tier needs to be passed to get_rollable_game())
    database_name = await get_mongo('name')
    database_tier = await get_mongo('tier')

    #  -------------------------------------------- One Hell of a Day  --------------------------------------------
    if event == "One Hell of a Day" :
        # Get one random (rollable) game in Tier 1, non-genre specific
        games.append(await get_rollable_game(10, 10, "Tier 1", userInfo[current_user], database_name=database_name, database_tier=database_tier))

        # Create the embed
        embed = getEmbed(games[0], interaction.user.id, database_name=database_name)
        embed.add_field(name="Roll Requirements", value = 
            "You have one day to complete One Hell of a Day."
            + "\nMust be completed by <t:" + str(get_unix(1))
            + ">\nOne Hell of a Day has a two week cooldown."
            + "\nCooldown ends on <t:" + str(get_unix(14)) + ">.", inline=False)
        embed.set_author(name="Challenge Enthusiasts", url="https://example.com")

    # -------------------------------------------- Two Week T2 Streak --------------------------------------------
    elif event == "Two Week T2 Streak" :
        # two random t2s
        print("received two week t2 streak")

        roll_num = -1
        for i, roll in enumerate(userInfo[target_user]['Current Rolls']):
            if roll['Event Name'] == "Two Week T2 Streak" : 
                roll_num = i
                break
        
        # doesnt have roll
        if roll_num == -1:
            embed = discord.Embed(title = "Two Week T2 Streak",
                                  description="A T2 will be rolled for you."
                                  + " If you complete this T2 within a week, another T2"
                                  + " of a different genre will be rolled for you. "
                                  + "If you complete that T2 within a"
                                  + " week of rolling it, you win.",
                                  timestamp=datetime.datetime.now(),
                                  color = 0x000000)
            embed.add_field(name="Roll", value="Click to the next message to see your first T2!")

            view = discord.ui.View(timeout=600)
            embeds = [embed]
            game = await get_rollable_game(40, 20, "Tier 2", userInfo[target_user], database_name=database_name, database_tier=database_tier)
            embeds.append(getEmbed(game, interaction.user.id, database_name))

            await get_buttons(view, embeds)
            userInfo[target_user]['Current Rolls'].append({
                "Event Name" : "Two Week T2 Streak",
                "End Time" : get_unix(7),
                "Games" : [game]
            })

            dump = await dump_mongo("user", userInfo)
            return await interaction.followup.send(embed=embeds[0], view=view)
        
        # has roll and ready for second game
        elif "End Time" not in userInfo[target_user]['Current Rolls'][roll_num]:
            embed = discord.Embed(title = "Two Week T2 Streak",
                                  description="You have one week to complete this T2.",
                                  timestamp=datetime.datetime.now(),
                                  color =0x000000)
            embed.add_field(name="Roll", value="Click to the next message to see your second T2!")

            view = discord.ui.View(timeout=600)
            embeds = [embed]
            
            # take out the genre that's been rolled already
            existing_games = userInfo[target_user]['Current Rolls'][roll_num]['Games']
            genres.remove(database_name[existing_games[0]]['Genre'])

            # get the game and embed
            game = await get_rollable_game(40, 20, "Tier 2", userInfo[target_user], genres, database_name=database_name, database_tier=database_tier)
            embeds.append(getEmbed(game, interaction.user.id, database_name))
            await get_buttons(view, embeds)
            
            # update database_user
            userInfo[target_user]['Current Rolls'][roll_num] = {
                "Event Name" : "Two Week T2 Streak",
                "End Time" : get_unix(7),
                "Games" : existing_games + [game]
            }

            # dump and send
            await dump_mongo("user", userInfo)
            return await interaction.followup.send(embed=embeds[0], view = view)
    
        # has roll and is not ready
        elif "End Time" in userInfo[target_user]['Current Rolls'][roll_num]:
            return await interaction.followup.send("You need to finish your current T2 first before you can roll the next one!")
        
        #something is wrong
        else:
            return await interaction.followup.send("Something has gone wrong with the bot. Please ping andy for support!!")

        # old method
        """
        # ----- Grab two random games -----
        games.append(await get_rollable_game(40, 20, "Tier 2", userInfo[current_user], database_name=database_name, database_tier=database_tier))
        genres.remove(database_name[games[0]]['Genre'])
        games.append(await get_rollable_game(40, 20, "Tier 2", userInfo[current_user], genres, database_name=database_name, database_tier=database_tier))
        
        # ----- Get all the embeds -----s
        embeds = create_multi_embed("Two Week T2 Streak", 14, games, 0, interaction, database_name)
        embed = embeds[0]

        await get_buttons(view, embeds) # Create buttons
        """

    # -------------------------------------------- One Hell of a Week --------------------------------------------
    elif event == "One Hell of a Week" : 
        # t1s from each category
        print("Recieved request for One Hell of a Week")

        can_continue = False
        for completed_roll in userInfo[target_user]['Completed Rolls'] :
            if completed_roll['Event Name'] == "One Hell of a Day": can_continue = True
        
        if not can_continue : return await interaction.followup.send("You must complete One Hell of a Day in order to roll One Hell of a Week!")
                

        # ----- Grab all the games -----
        genres.remove("Strategy")
        i = 0
        while i < 5:
            games.append(await get_rollable_game(10, 10, "Tier 1", userInfo[current_user], genres, database_name=database_name, database_tier=database_tier))
            genres.remove(database_name[games[i]]['Genre'])
            i+=1

        # ----- Get all the embeds -----
        embeds = create_multi_embed("One Hell of a Week", 7, games, months_to_days(1), interaction, database_name)       
        embed = embeds[0] # Set the embed to send as the first one
        await get_buttons(view, embeds) # Create buttons

    # -------------------------------------------- One Hell of a Month --------------------------------------------
    elif event == "One Hell of a Month" : 
        # five t1s from each category
        print("One Hell of a Month")

        can_continue = False
        for completed_roll in userInfo[target_user]['Completed Rolls'] :
            if completed_roll['Event Name'] == "One Hell of a Week": can_continue = True
        
        if not can_continue : return await interaction.followup.send("You must complete One Hell of a Week in order to roll One Hell of a Month!")
             

        # select a random genre to remove
        random_num = random.randint(0, 5)
        genres.remove(genres[random_num])

        for ggenre in genres :
            i=0
            while(i < 5) :
                games.append(await get_rollable_game(10, 10, "Tier 1", specific_genre=ggenre, games=games, database_name=database_name, database_tier=database_tier))
                i+=1
        embeds = create_multi_embed("One Hell of a Month", months_to_days(1), games, months_to_days(3), interaction, database_name)
        embed = embeds[0]
        await get_buttons(view, embeds)


    # -------------------------------------------- Two "Two Week T2 Streak" Streak ---------------------------------------------
    elif event == "Two 'Two Week T2 Streak' Streak" :
        # four t2s
        print("Recieved request for Two 'Two Week T2 Streak' Streak")

        # check if they've done prerequisite
        eligible = False
        for r in userInfo[target_user]['Completed Rolls']:
            if r['Event Name'] == "Two Week T2 Streak" : eligible = True
        if not eligible : return await interaction.followup.send("You need to complete Two Week T2 Streak first!!!")

        roll_num = -1
        for i, roll in enumerate(userInfo[target_user]['Current Rolls']) :
            if roll['Event Name'] == "Two 'Two Week T2 Streak' Streak":
                roll_num = i

        # doesnt have roll
        if roll_num == -1:
            embed = discord.Embed(title = "Two 'Two Week T2 Streak' Streak",
                                  description="A T2 will be rolled for you."
                                  + " If you complete this T2 within a week, another T2"
                                  + " of a different genre will be rolled for you, and "
                                  + "you will have a week to complete that. This process will "
                                  + "repeat until you have completed four T2s.",
                                  timestamp=datetime.datetime.now(),
                                  color = 0x000000)
            embed.add_field(name="Roll", value="Click to the next message to see your first T2!")

            # setup view and embeds
            view = discord.ui.View(timeout=600)
            embeds = [embed]
            game = await get_rollable_game(40, 20, "Tier 2", userInfo[target_user], database_name=database_name, database_tier=database_tier)
            embeds.append(getEmbed(game, interaction.user.id, database_name))
            await get_buttons(view, embeds)

            # update database_user
            userInfo[target_user]['Current Rolls'].append({
                "Event Name" : "Two 'Two Week T2 Streak' Streak",
                "End Time" : get_unix(7),
                "Games" : [game]
            })

            # dump and send
            dump = await dump_mongo("user", userInfo)
            return await interaction.followup.send(embed=embeds[0], view=view)
        
        # has roll and ready for next game
        elif "End Time" not in userInfo[target_user]['Current Rolls'][roll_num]:
            embed = discord.Embed(title = "Two 'Two Week T2 Streak' Streak",
                        description="You have one week to complete this T2.",
                        timestamp=datetime.datetime.now(),
                        color =0x000000)
            embed.add_field(name="Roll", value="Click to the next message to see your next T2!")

            # set up view and o.g. embed
            view = discord.ui.View(timeout=600)
            embeds = [embed]

            # take out genres that have been rolled already
            existing_games = userInfo[target_user]['Current Rolls'][roll_num]['Games']
            for g in existing_games:
                genres.remove(database_name[g]['Genre'])
            
            game = await get_rollable_game(40, 20, "Tier 2", userInfo[target_user], genres, database_name=database_name, database_tier=database_tier)
            embeds.append(getEmbed(game, interaction.user.id, database_name))
            await get_buttons(view, embeds)

            # update database user
            userInfo[target_user]['Current Rolls'][roll_num] = {
                "Event Name" : "Two 'Two Week T2 Streak' Streak",
                "End Time" : get_unix(7),
                "Games" : existing_games + [game]
            }

            # dump and send
            await dump_mongo('user', userInfo)
            return await interaction.followup.send(embed = embeds[0], view = view)
            
            # get games and embeds

        elif "End Time" in userInfo[target_user]['Current Rolls'][roll_num]:
            return await interaction.followup.send("You need to finish your current T2 before rolling the next one!")
        
        else:
            return await interaction.followup.send("Something has gone wrong with the bot. Please ping andy for support!")

        # old method
        """
        return
        eligible = False
        for roll in userInfo[target_user]['Completed Rolls'] :
            if(roll['Event Name'] == "Two Week T2 Streak") : eligible = True

        if not eligible : return await interaction.followup.send(f"You must complete 'Two Week T2 Streak' to be eligible for {event}.")

        # ----- Grab all the games -----
        genres.remove("Strategy")
        i=0
        while i < 4:
            games.append(await get_rollable_game(40, 20, "Tier 2", userInfo[current_user], genres, database_name=database_name, database_tier=database_tier))
            genres.remove(database_name[games[i]]['Genre'])
            i+=1
        
        # ----- Get all the embeds -----
        embeds = create_multi_embed("Two 'Two Week T2 Streak' Streak", months_to_days(1), games, 7, interaction, database_name)
        embed = embeds[0]
        await get_buttons(view, embeds)
        """

    # -------------------------------------------- Never Lucky --------------------------------------------
    elif event == "Never Lucky" :
        roll_num = -1
        for i, r in enumerate(userInfo[target_user]['Current Rolls']):
            if r['Event Name'] == 'Never Lucky' :
                roll_num = i
                break
        
        if(roll_num == -1) :
            # one t3
            games.append(await get_rollable_game(40, 20, "Tier 3", userInfo[current_user], database_name=database_name, database_tier=database_tier))

            ends = False

            # Create the embed
            total_points = 0
            embed = getEmbed(games[0], interaction.user.id, database_name)
            embed.set_author(name="Never Lucky", url="https://example.com")
            embed.add_field(name="Roll Requirements", value = 
                "There is no time limit on " + embed.title + "."
                + "\nNever Lucky has a one month cooldown."
                + "\nCooldown ends on <t:" + str(get_unix(months=1))
                + f">\nhttps://cedb.me/game/{database_name[embed.title]['CE ID']}/", inline=False)
            
            userInfo[target_user]['Current Rolls'].append({
                'Event Name' : 'Never Lucky',
                'Games' : games
            })
            userInfo[target_user]['Cooldowns']['Never Lucky'] = get_unix(months=1)
            d = await dump_mongo('user', userInfo)
            del d
            return await interaction.followup.send(embed=embed, view=view)
        
        # roll is currently... rolled...
        else :
            # set up view and buttons
            view = discord.ui.View(timeout=600)
            agree_button = discord.ui.Button(label="Agree", style=discord.ButtonStyle.success)
            deny_button = discord.ui.Button(label ="Deny", style=discord.ButtonStyle.danger)
            view.add_item(deny_button)
            view.add_item(agree_button)

            #TODO: make sure the previous game doesn't get rerolled
            async def agree_callback(interaction : discord.Interaction) :
                await interaction.response.defer()
                # pull mongo databases
                database_name = await get_mongo('name')
                userInfo = await get_mongo('user')

                # make sure only the o.g. guy can push buttons
                if interaction.user.id != userInfo[target_user]['Discord ID'] : return

                # get a new t3
                new_game = await get_rollable_game(40, 20, "Tier 3", userInfo[target_user], database_name=database_name, database_tier=database_tier)

                # make the embed
                embed = getEmbed(new_game, interaction.user.id, database_name)
                embed.set_author(name="Never Lucky", url="https://cedb.me/game/" + database_name[new_game]['CE ID'])
                embed.add_field(name="Roll Requirements", value =
                                f"There is no time limit on {event}."
                                + f"\nNever lucky has a one month cooldown."
                                + f"\nCooldown ends on <t:{str(get_unix(months=1))}>.", inline=False)
                
                # update database_user
                userInfo[target_user]['Current Rolls'][roll_num]['Games'] = [new_game]
                try:
                    del userInfo[target_user]['Pending Rolls']['Never Lucky']
                except: ""
                d = await dump_mongo('user', userInfo)

                # update the view and edit the message
                view.clear_items()
                return await interaction.followup.edit_message(content="", embed=embed, view=view, message_id=interaction.message.id)
            
            async def deny_callback(interaction : discord.Interaction) :
                await interaction.response.defer()
                database_name = await get_mongo('name')
                userInfo = await get_mongo('user')

                # make sure only o.g. user can push button
                if interaction.user.id != userInfo[target_user]['Discord ID'] : return

                # remove the pending
                del userInfo[target_user]['Pending Rolls']['Never Lucky']

                # update the view and edit the message
                view.clear_items()
                return await interaction.followup.edit_message(content="", embed=discord.Embed(title="Denied!"), view=view, message_id=interaction.message.id)
            
            agree_button.callback = agree_callback
            deny_button.callback = deny_callback

            # update Pending Rolls and dump
            userInfo[target_user]['Pending Rolls']['Never Lucky'] = get_unix(minutes=10)
            d = dump_mongo('user', userInfo)
            del d
            
            return await interaction.followup.send('Would you like to reroll your Never Lucky roll? You will lose your current game.', view=view)




    # -------------------------------------------- Triple Threat --------------------------------------------
    elif event == "Triple Threat" :
        # three t3s

        # check if pending.. and also make sure Never Lucky has been completed
        if event in userInfo[target_user]['Pending Rolls'] : return await interaction.followup.send(
            f"You just tried to roll {event}. Please wait 10 minutes in between requesting the same event!"
        )
        can_continue = False
        
        for roll in userInfo[target_user]['Completed Rolls'] :
            if(roll['Event Name'] == "Never Lucky") : can_continue = True
        
        # Never lucky hasn't been completed
        if not can_continue : return await interaction.followup.send("You must complete Never Lucky to roll Triple Threat!")
        
        # add the pending...
        userInfo[target_user]['Pending Rolls'][event] = get_unix(minutes=10)

        # close and reopen users2.json
        dump = await dump_mongo('user', userInfo)
        userInfo = await get_mongo('user')

        # ----- Grab all the games -----
        embed = discord.Embed(title=("Triple Threat"), description="Please select your genre.")
            
        await get_genre_buttons(view, 40, 20, "Tier 3", "Triple Threat", months_to_days(1), months_to_days(3), 3, interaction.user.id, collection=collection)

        dont_save = True
         
    # -------------------------------------------- Let Fate Decide --------------------------------------------
    elif event == "Let Fate Decide" :
        # one t4
        roll_num = -1
        for i, r in enumerate(userInfo[target_user]['Current Rolls']):
            if r['Event Name'] == 'Let Fate Decide' :
                roll_num = i
                break

        # User has not rolled before
        if roll_num == -1:
            # add pending...
            userInfo[target_user]['Pending Rolls'][event] = get_unix(minutes=10)

            # close and reopen users2.json
            dump = await dump_mongo('user', userInfo)
            userInfo = await get_mongo('user')

            # set up the embeds and buttons
            embed = discord.Embed(title=("Let Fate Decide"), description="A random T4 in a genre of you choosing will be rolled." +
                                " There is no time limit for Let Fate Decide. You win once you complete all Primary Objectives in your rolled game!")
            await get_genre_buttons(view, 1000, 20, "Tier 4", event, 1, months_to_days(3), 1, interaction.user.id, collection=collection)
            dont_save = True
        
        # User has rolled before and is ready to reroll...
        else :
            userInfo[target_user]['Pending Rolls'][event] = get_unix(minutes=10)

            # close and reopen userInfo
            d = await dump_mongo('user', userInfo)
            del d
            userInfo = await get_mongo('user')

            # set up the embed
            embed = discord.Embed(
                title = 'Let Fate Decide',
                description= 'You are requesting to reroll your Let Fate Decide roll. Your game will be overwritten by a new game of the same genre. Are you okay with this?'
            )
            embed.set_footer(text="CE Assistant", icon_url=final_ce_icon)

            # set up view and buttons
            view = discord.ui.View(timeout=600)
            agree_button = discord.ui.Button(label="Agree", style=discord.ButtonStyle.success)
            deny_button = discord.ui.Button(label ="Deny", style=discord.ButtonStyle.danger)
            view.add_item(deny_button)
            view.add_item(agree_button)

            #TODO: make sure the previous game doesn't get rerolled
            async def agree_callback(interaction : discord.Interaction) :
                await interaction.response.defer()
                # pull mongo databases
                database_name = await get_mongo('name')
                userInfo = await get_mongo('user')

                # make sure only the o.g. guy can push buttons
                if interaction.user.id != userInfo[target_user]['Discord ID'] : return

                # o.g. game
                original_game = userInfo[target_user]['Current Rolls'][roll_num]['Games'][0]

                # get a new t4
                new_game = await get_rollable_game(1000, 20, "Tier 4", userInfo[target_user], database_name=database_name, database_tier=database_tier,
                                                   specific_genre=[database_name[original_game]['Genre']])

                # make the embed
                embed = getEmbed(new_game, interaction.user.id, database_name)
                embed.set_author(name="Let Fate Decide", url="https://cedb.me/game/" + database_name[new_game]['CE ID'])
                embed.add_field(name="Roll Requirements", value =
                                f"There is no time limit on {event}."
                                + f"\nLet Fate Decide has a three month cooldown."
                                + f"\nCooldown ends on <t:{str(get_unix(months=3))}>.", inline=False)
                
                # update database_user
                userInfo[target_user]['Current Rolls'][roll_num]['Games'] = [new_game]
                userInfo[target_user]['Cooldowns']['Let Fate Decide'] = get_unix(months=3)
                del userInfo[target_user]['Pending Rolls']['Let Fate Decide']
                d = await dump_mongo('user', userInfo)

                # update the view and edit the message
                view.clear_items()
                return await interaction.followup.edit_message(content="", embed=embed, view=view, message_id=interaction.message.id)
            
            async def deny_callback(interaction : discord.Interaction) :
                await interaction.response.defer()
                userInfo = await get_mongo('user')

                # make sure only o.g. user can push button
                if interaction.user.id != userInfo[target_user]['Discord ID'] : return

                # remove the pending
                del userInfo[target_user]['Pending Rolls']['Let Fate Decide']

                # update the view and edit the message
                view.clear_items()
                return await interaction.followup.edit_message(content="",embed=discord.Embed(title="Denied!"), view=view,
                                                               message_id=interaction.message.id)
            
            agree_button.callback = agree_callback
            deny_button.callback = deny_callback

            return await interaction.followup.send(embed=embed, view=view)



    # -------------------------------------------- Fourward Thinking --------------------------------------------
    elif event == "Fourward Thinking" :
        # idk
        print('hahahaha')

        # eligibility
        eligible = False
        for r in userInfo[target_user]['Completed Rolls']:
            if r['Event Name'] == "Let Fate Decide":
                eligible = True
                break
        if not eligible : return await interaction.followup.send("You need to complete Let Fate Decide to roll Fourward Thinking!")
        
        # See if the user has already rolled Fourward Thinking
        has_roll = False
        roll_num = 0
        for roll in userInfo[target_user]['Current Rolls'] :
            if roll['Event Name'] == "Fourward Thinking" : 
                has_roll = True
                break
            roll_num += 1

        # Has not rolled Fourward Thinking before
        if(not has_roll) : 
            embed = discord.Embed(title=("Fourward Thinking"),
                                  description="You have rolled Fourward Thinking. This is the most confusing roll event, so buckle in."
                                  + "\nWhen you roll this event, a T1 in a genre of your choosing will be rolled for you, and you will have one week to do so."
                                  + "\nIf you manage to complete this T1 in one week, you will now choose a __different__ genre to roll a T2 - and you'll have two weeks."
                                  + "\nContinue this process through T4 - and if you complete that, you win!",
                                  timestamp=datetime.datetime.now(),
                                  color=0x000000)
            embed.add_field(name="Rerolls",
                            value="- You will get a reroll token for every game you complete in this event."
                            + "\n- Using a reroll token will add a month onto your cooldown time, but using one will reset your timer."
                            + " So, if you have two days left of your T1, you can use a reroll token and you'll get the full week to complete your new T1.")
            embed.add_field(name="Timing",
                            value="- Your T1 will not have an average completion time on steamhunters larger than 40. This goes up to 80 for your T2, 120 for T3, and 160 for T4."
                            + " \n- Your cooldown timer is calculated as such: (num of completed games + 1) * 2 weeks. Failing your T1 nets you a two week cooldown, T4 nets you ten weeks.")
            embed.add_field(name="Genre",
                            value="Choose the genre below to roll your T1. Remember: this genre cannot be picked again!!!",
                            inline=False)
            embed.set_footer(text="CE Assistant", icon_url=final_ce_icon)
            embed.set_author(name="Challenge Enthusiasts")

            view = discord.ui.View(timeout=600)
            
            await get_genre_buttons(view, 40, 20, "Tier 1", "Fourward Thinking", 7, 14, 1, interaction.user.id, collection)
            userInfo[target_user]['Pending Rolls']['Fourward Thinking'] = get_unix(minutes=10)

            dump = await dump_mongo('user', userInfo)
            return await interaction.followup.send(embed=embed, view=view)


            # old method
            """
            game2 = await get_rollable_game(40, 20, "Tier 1", database_tier=database_tier, database_name=database_name)
            embed2 = getEmbed(game2, interaction.user.id, database_name)

            embeds = [embed, embed2]

            view = discord.ui.View(timeout=600)
            await get_buttons(view, embeds)

            userInfo[target_user]['Current Rolls'].append({
                "Event Name" : event,
                "End Time" : get_unix(7),
                "Games" : [game2],
                "Rerolls" : 0
            })

            dump = await dump_mongo('user', userInfo)

            return await interaction.followup.send(embed=embed, view=view)
            
            dont_save=True
            """


        # Has rolled Fourward Thinking but isn't done with the roll yet.
        elif (has_roll and "End Time" in list(userInfo[target_user]['Current Rolls'][roll_num].keys())) :
            if event in userInfo[target_user]['Pending Rolls'] :
                return await interaction.followup.send("Please wait 10 minutes in between requests.")
            if userInfo[target_user]['Current Rolls'][roll_num]['Rerolls'] == 0:
                return await interaction.followup.send("You are currently participating in Fourward Thinking and have no reroll tickets. Beat it.")
            else:
                view = discord.ui.View(timeout=600)
                agree_button = discord.ui.Button(label="Agree", style=discord.ButtonStyle.success)
                deny_button = discord.ui.Button(label ="Deny", style=discord.ButtonStyle.danger)
                view.add_item(deny_button)
                view.add_item(agree_button)

                async def deny_callback(interaction : discord.Interaction) :
                    await interaction.response.defer()
                    if interaction.user.id != userInfo[target_user]['Discord ID'] : return

                    # Set up denial embed
                    embed = discord.Embed(
                        title="Roll Denied",
                        description=f"<@{interaction.user.id}> has denied the roll.",
                        timestamp=datetime.datetime.now()
                    )

                    view.clear_items()
                    return await interaction.followup.edit_message(embed=embed, view=view, message_id=interaction.message.id)
            
                async def agree_callback(interaction : discord.Interaction) :
                    # defer the message
                    await interaction.response.defer()

                    # pull database_user
                    userInfo = await get_mongo('user')

                    # don't let anyone else use the button!
                    if interaction.user.id != userInfo[target_user]['Discord ID'] : return

                    # get the current number of games
                    num_of_games = len(userInfo[target_user]['Current Rolls'][roll_num]['Games'])

                    # grab the most recently played game and its genre
                    most_recent_game = userInfo[target_user]['Current Rolls'][roll_num]['Games'][num_of_games - 1]
                    genre = database_name[most_recent_game]['Genre']

                    # get a new game of the same tier and genre
                    new_game = await get_rollable_game(40*num_of_games, 20, "Tier " + str(num_of_games), userInfo[target_user], genre, database_tier=database_tier, database_name=database_name, games=[most_recent_game])
                    
                    # create the embed for it
                    embed = getEmbed(new_game, interaction.user.id, database_name)

                    # update and dump the database
                    userInfo[target_user]['Current Rolls'][roll_num]['Games'][num_of_games - 1] = new_game
                    userInfo[target_user]['Current Rolls'][roll_num]['Rerolls'] = userInfo[target_user]['Current Rolls'][roll_num]['Rerolls'] - 1
                    d = await dump_mongo('user', userInfo)
                    del d

                    # clear the view and edit the message
                    view.clear_items()
                    return await interaction.followup.edit_message(content="", embed=embed, view=view, message_id=interaction.message.id)

                agree_button.callback = agree_callback
                deny_button.callback = deny_callback

                userInfo[target_user]['Pending Rolls'][event] = get_unix(minutes=10)
                dump = await dump_mongo("user", userInfo)

                return await interaction.followup.send(f"You have {userInfo[target_user]['Current Rolls'][roll_num]['Rerolls']} reroll ticket(s). Would you like to use one?", 
                                                       view=view)
            " make sure if someone else tries to click this they can't!!!!"
            """
            this is for my own brainstorm
            if someone has used a reroll ticket, their number of games completed will NOT equal the number of tickets they have
            for example, someone on their first game would not have used any as they wouldn't have gotten any reroll tickets yet
            someone on their second game could either have one or zero tickets
            so, used_tickets = (num_of_games - 1) - (num_of_tickets)
            
            TODO: change fourward thinking check to only check most recently added game!!!!
            """
            dont_save = True

        # Has rolled Fourward Thinking and is ready for the next roll
        # OR OR OR is done!
        # TODO: make the games[0] be [pending...], don't entirely override it 
        else : 
            num_of_games = len(userInfo[target_user]['Current Rolls'][roll_num]['Games'])
            print(num_of_games)

            # set up the starting embed
            embed = (discord.Embed(title=event, timestamp=datetime.datetime.now()))
            if(num_of_games == 1) :
                # get a game
                embed.add_field(name="Roll Status", value="You have rolled your T2. You have two weeks to complete.")

            elif(num_of_games == 2):
                # get a game
                embed.add_field(name="Roll Status", value = "You have rolled your T3. You have three weeks to complete.")
            elif(num_of_games == 3):
                # get a game
                embed.add_field(name="Roll Status", value = "You have rolled your T4. You have four weeks to complete.")
                #roll a t4
            
            view = discord.ui.View(timeout=600)

            await get_genre_buttons(view, 40*(num_of_games+1), 20, f"Tier {(num_of_games+1)}", "Fourward Thinking",
                                    7*(num_of_games+1), 14*(num_of_games+1), 1, interaction.user.id, collection)
            
            for game in (userInfo[target_user]['Current Rolls'][roll_num]['Games']):
                genre = database_name[game]['Genre']
                for i, g in enumerate(genres):
                    if g == genre: view.children[i].disabled = True
            
            userInfo[target_user]['Pending Rolls']['Fourward Thinking'] = get_unix(minutes=10)
            
            dump = await dump_mongo('user', userInfo)
            return await interaction.followup.send(view=view, embed=embed)


            # update users2.json
            """
            userInfo[target_user]['Current Rolls'][roll_num]['Games'].append(game)
            userInfo[target_user]['Current Rolls'][roll_num]['End Time'] = get_unix(7*(num_of_games+1))
            userInfo[target_user]['Current Rolls'][roll_num]['Rerolls'] += 1

            # dont add the thing to users2.json AGAIN!
            dont_save = True
            """


    # -------------------------------------------- Russian Roulette --------------------------------------------
    elif event == "Russian Roulette" :
        # choose six t5s and get one at random
        embed = discord.Embed(title=("⚠️ Russian Roulette ⚠️"))

        dont_save = True

        ends = False

    # ------------------------------------ CONTINUE ON ---------------------------------------------------

    if (dont_save is False) and (not reroll) :
        end_time = get_unix(times[event])
        # append the roll to the user's current rolls array
        userInfo[target_user]['Current Rolls'].append({"Event Name" : event, 
                                                    "End Time" : end_time,
                                                    "Games" : games})
        args = [
            interaction.user.id,
            0,
            0,
            0
        ]
        
        #await add_task(datetime.datetime.fromtimestamp(end_time), args)

    # this is reroll shit and rerolls dont exist anymore lol
    """ elif (dont_save is False) and (reroll) :
        c_num = -1
        for index, c_roll in enumerate(userInfo[target_user]['Current Rolls']) :
            if c_roll['Event Name'] == event :
                c_num = index
                break
        
        if c_num == -1 : return await interaction.followup.send('you havent rolled this game. except i should have cleared that already. something is wrong')

        userInfo[target_user]['Current Rolls'][c_num] = ({
            "Event Name" : event,
            "End Time" : userInfo[target_user]['Current Rolls'][c_num]['End Time'],
            "Games" : games
        })
    """


    # dump the info
    dump = await dump_mongo('user', userInfo)

    # Finally, send the embed
    await interaction.followup.send(embed=embed, view=view)
    print("Sent information on rolled game: " + str(games) + "\n")

    del database_name
    del database_tier
    del userInfo
    del embed
    del embeds
    del dump
