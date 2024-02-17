import random
from bson import ObjectId
import discord
import datetime
from datetime import timedelta
import json
import time
# --------- other file imports ---------
from Helper_Functions.rollable_games import get_rollable_game, get_rollable_game_from_list
from Helper_Functions.create_embed import create_multi_embed, getEmbed
from Helper_Functions.roll_string import get_roll_string
from Helper_Functions.buttons import get_buttons, get_genre_buttons
from Helper_Functions.update import update_p
from Helper_Functions.Scheduler import add_task
from Helper_Functions.mongo_silly import get_mongo, dump_mongo, get_unix

final_ce_icon = "https://cdn.discordapp.com/attachments/1135993275162050690/1144289627612655796/image.png"

async def solo_command(interaction : discord.Interaction, event : str, reroll : bool, collection) :


    # Set up variables
    view = discord.ui.View(timeout=600)
    games = []
    embeds = []
    genres = ["Action", "Arcade", "Bullet Hell", "First-Person", "Platformer", "Strategy"]
    times = {
        "One Hell of a Day" : (1),
        "One Hell of a Week" : (7),
        "One Hell of a Month" : (28),
        "Two Week T2 Streak" : (14),
        "Two 'Two Week T2 Streak' Streak" : (28),
        "Never Lucky" : (0),
        "Triple Threat" : (28),
        "Let Fate Decide" : (0),
        "Fourward Thinking" : (0),
        "Russian Roulette" :(0)
    }
    dont_save = False
    ends = True

    # grab user info
    userInfo = await get_mongo('user')
    
    i = 0
    target_user = ""
    for current_user in userInfo :
        if current_user == '_id' : continue
        if(userInfo[current_user]["Discord ID"] == interaction.user.id) :
            target_user = current_user
            break
    
    # Inform the user that they are not registered.
    if(target_user == "") :
        return await interaction.followup.send("You are not registered in the CE Assistant database. Please try /register with your CE link.")

    # Check if the event is on cooldown...
    if(event in list(userInfo[target_user]['Cooldowns'])) :
        return await interaction.followup.send(embed=discord.Embed(title="Cooldown", description=f"You are currently on cooldown for {event}."))

    # ...or if the event is currently active.
    for eventInfo in userInfo[target_user]['Current Rolls'] :
        #TODO: have different errors if someone tries to go again during pending and if someone tries to reroll while pending
        if(eventInfo['Event Name'] == event and eventInfo['Games'] == ['pending...']) : return await interaction.followup.send('Please wait 10 minutes in between rolling for the same event!')
        if((eventInfo['Event Name'] == event) and event != "Fourward Thinking" and event != "Two Week T2 Streak"
           and event != "Two 'Two Week T2 Streak' Streak" and not reroll) : 
            return await interaction.followup.send(embed=discord.Embed(title=f"You are already participating in {event}!"))

    # grab both databases (tier needs to be passed to get_rollable_game())
    database_name = await get_mongo('name')
    database_tier = await get_mongo('tier')

    #  -------------------------------------------- One Hell of a Day  --------------------------------------------
    if event == "One Hell of a Day" :
        # Get one random (rollable) game in Tier 1, non-genre specific
        games.append(get_rollable_game(10, 10, "Tier 1", userInfo[current_user], database_name=database_name, database_tier=database_tier))

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
        for i, roll in enumerate(userInfo[target_user]["Completed Rolls"]):
            if roll["Event Name"] == "Two Week T2 Streak" : 
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
            game = get_rollable_game(40, 20, "Tier 2", userInfo[target_user], database_name=database_name, database_tier=database_tier)
            embeds.append(getEmbed(game, interaction.user.id, database_name))

            await get_buttons(view, embeds)
            userInfo[target_user]["Current Rolls"].append({
                "Event Name" : "Two Week T2 Streak",
                "End Time" : get_unix(7),
                "Games" : [game]
            })

            dump = await dump_mongo("user", userInfo)
            return await interaction.followup.send(embed=embeds[0], view=view)
        
        # has roll and ready for second game
        elif "End Time" not in userInfo[target_user]["Current Rolls"][roll_num]:
            embed = discord.Embed(title = "Two Week T2 Streak",
                                  description="You have one week to complete this T2.",
                                  timestamp=datetime.datetime.now(),
                                  color =0x000000)
            embed.add_field(name="Roll", value="Click to the next message to see your second T2!")

            view = discord.ui.View(timeout=600)
            embeds = [embed]
            
            # take out the genre that's been rolled already
            existing_games = userInfo[target_user]["Current Rolls"][roll_num]["Games"]
            genres.remove(database_name[existing_games[0]]["Genre"])

            # get the game and embed
            game = get_rollable_game(40, 20, "Tier 2", userInfo[target_user], genres, database_name=database_name, database_tier=database_tier)
            embeds.append(getEmbed(game, interaction.user.id, database_name))
            await get_buttons(view, embeds)
            
            # update database_user
            userInfo[target_user]["Current Rolls"][roll_num] = {
                "Event Name" : "Two Week T2 Streak",
                "End Time" : get_unix(7),
                "Games" : existing_games + [game]
            }

            # dump and send
            await dump_mongo("user", userInfo)
            return await interaction.followup.send(embed=embeds[0], view = view)
    
        # has roll and is not ready
        elif "End Time" in userInfo[target_user]["Current Rolls"][roll_num]:
            return await interaction.followup.send("You need to finish your current T2 first before you can roll the next one!")
        
        #something is wrong
        else:
            return await interaction.followup.send("Something has gone wrong with the bot. Please ping andy for support!!")

        # old method
        """
        # ----- Grab two random games -----
        games.append(get_rollable_game(40, 20, "Tier 2", userInfo[current_user], database_name=database_name, database_tier=database_tier))
        genres.remove(database_name[games[0]]["Genre"])
        games.append(get_rollable_game(40, 20, "Tier 2", userInfo[current_user], genres, database_name=database_name, database_tier=database_tier))
        
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
        for completed_roll in userInfo[target_user]["Completed Rolls"] :
            if completed_roll["Event Name"] == "One Hell of a Day": can_continue = True
        
        if not can_continue : return await interaction.followup.send("You must complete One Hell of a Day in order to roll One Hell of a Week!")
                

        # ----- Grab all the games -----
        genres.remove("Strategy")
        i = 0
        while i < 5:
            games.append(get_rollable_game(10, 10, "Tier 1", userInfo[current_user], genres, database_name=database_name, database_tier=database_tier))
            genres.remove(database_name[games[i]]["Genre"])
            i+=1

        # ----- Get all the embeds -----
        embeds = create_multi_embed("One Hell of a Week", 7, games, 28, interaction, database_name)       
        embed = embeds[0] # Set the embed to send as the first one
        await get_buttons(view, embeds) # Create buttons

    # -------------------------------------------- One Hell of a Month --------------------------------------------
    elif event == "One Hell of a Month" : 
        # five t1s from each category
        print("One Hell of a Month")

        can_continue = False
        for completed_roll in userInfo[target_user]["Completed Rolls"] :
            if completed_roll["Event Name"] == "One Hell of a Week": can_continue = True
        
        if not can_continue : return await interaction.followup.send("You must complete One Hell of a Week in order to roll One Hell of a Month!")
             

        # select a random genre to remove
        random_num = random.randint(0, 5)
        genres.remove(genres[random_num])

        for ggenre in genres :
            i=0
            while(i < 5) :
                games.append(get_rollable_game(10, 10, "Tier 1", specific_genre=ggenre, games=games, database_name=database_name, database_tier=database_tier))
                i+=1
        embeds = create_multi_embed("One Hell of a Month", 28, games, 28*3, interaction, database_name)
        embed = embeds[0]
        await get_buttons(view, embeds)


    # -------------------------------------------- Two "Two Week T2 Streak" Streak ---------------------------------------------
    elif event == "Two 'Two Week T2 Streak' Streak" :
        # four t2s
        print("Recieved request for Two 'Two Week T2 Streak' Streak")

        # check if they've done prerequisite
        eligible = False
        for r in userInfo[target_user]["Current Rolls"]:
            if r["Event Name"] == "Two Week T2 Streak" : eligible = True
        if not eligible : return await interaction.followup.send("You need to complete Two Week T2 Streak first!!!")

        roll_num = -1
        for i, roll in enumerate(userInfo[target_user]["Current Rolls"]) :
            if roll["Event Name"] == "Two 'Two Week T2 Streak' Streak":
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
            game = get_rollable_game(40, 20, "Tier 2", userInfo[target_user], database_name=database_name, database_tier=database_tier)
            embeds.append(getEmbed(game, interaction.user.id, database_name))
            await get_buttons(view, embeds)

            # update database_user
            userInfo[target_user]["Current Rolls"].append({
                "Event Name" : "Two 'Two Week T2 Streak' Streak",
                "End Time" : get_unix(7),
                "Games" : [game]
            })

            # dump and send
            dump = await dump_mongo("user", userInfo)
            return await interaction.followup.send(embed=embeds[0], view=view)
        
        # has roll and ready for next game
        elif "End Time" not in userInfo[target_user]["Current Rolls"][roll_num]:
            embed = discord.Embed(title = "Two 'Two Week T2 Streak' Streak",
                        description="You have one week to complete this T2.",
                        timestamp=datetime.datetime.now(),
                        color =0x000000)
            embed.add_field(name="Roll", value="Click to the next message to see your next T2!")

            # set up view and o.g. embed
            view = discord.ui.View(timeout=600)
            embeds = [embed]

            # take out genres that have been rolled already
            existing_games = userInfo[target_user]["Current Rolls"][roll_num]["Games"]
            for g in existing_games:
                genres.remove(database_name[g]["Genre"])
            
            game = get_rollable_game(40, 20, "Tier 2", userInfo[target_user], genres, database_name=database_name, database_tier=database_tier)
            embeds.append(getEmbed(game, interaction.user.id, database_name))
            await get_buttons(view, embeds)

            # update database user
            userInfo[target_user]["Current Rolls"][roll_num] = {
                "Event Name" : "Two 'Two Week T2 Streak' Streak",
                "End Time" : get_unix(7),
                "Games" : existing_games + [game]
            }

            # dump and send
            await dump_mongo('user', userInfo)
            return await interaction.followup.send(embed = embeds[0], view = view)
            
            # get games and embeds

        elif "End Time" in userInfo[target_user]["Current Rolls"][roll_num]:
            return await interaction.followup.send("You need to finish your current T2 before rolling the next one!")
        
        else:
            return await interaction.followup.send("Something has gone wrong with the bot. Please ping andy for support!")

        # old method
        """
        return
        eligible = False
        for roll in userInfo[target_user]["Completed Rolls"] :
            if(roll["Event Name"] == "Two Week T2 Streak") : eligible = True

        if not eligible : return await interaction.followup.send(f"You must complete 'Two Week T2 Streak' to be eligible for {event}.")

        # ----- Grab all the games -----
        genres.remove("Strategy")
        i=0
        while i < 4:
            games.append(get_rollable_game(40, 20, "Tier 2", userInfo[current_user], genres, database_name=database_name, database_tier=database_tier))
            genres.remove(database_name[games[i]]["Genre"])
            i+=1
        
        # ----- Get all the embeds -----
        embeds = create_multi_embed("Two 'Two Week T2 Streak' Streak", 28, games, 7, interaction, database_name)
        embed = embeds[0]
        await get_buttons(view, embeds)
        """

    # -------------------------------------------- Never Lucky --------------------------------------------
    elif event == "Never Lucky" :
        # one t3
        games.append(get_rollable_game(40, 20, "Tier 3", userInfo[current_user], database_name=database_name, database_tier=database_tier))

        ends = False

        # Create the embed
        total_points = 0
        embed = getEmbed(games[0], interaction.user.id, database_name)
        embed.set_author(name="Never Lucky", url="https://example.com")
        embed.add_field(name="Roll Requirements", value = 
            "There is no time limit on " + embed.title + "."
            + "\nNever Lucky has a one week cooldown."
            + "\nCooldown ends on <t:" + str(get_unix(28))
            + f">\nhttps://cedb.me/game/{database_name[embed.title]['CE ID']}/", inline=False)

    # -------------------------------------------- Triple Threat --------------------------------------------
    elif event == "Triple Threat" :
        # three t3s

        # check if pending... and also make sure Never Lucky has been completed
        can_continue = False
        for x_roll in userInfo[target_user]['Current Rolls'] :
            if(x_roll['Event Name'] == event and x_roll['Games'] == ['pending...']) :
                return await interaction.followup.send('hang on their buster')
        
        for roll in userInfo[target_user]['Completed Rolls'] :
            if(roll["Event Name"] == "Never Lucky") : can_continue = True
        
        # Never lucky hasn't been completed
        if not can_continue : return await interaction.followup.send("You must complete Never Lucky to roll Triple Threat!")
        
        # add the pending...
        userInfo[target_user]['Current Rolls'].append({"Event Name" : event, "End Time" : get_unix(minutes=10), "Games" : ["pending..."]})

        # close and reopen users2.json
        dump = await dump_mongo('user', userInfo)
        userInfo = await get_mongo('user')

        # ----- Grab all the games -----
        embed = discord.Embed(title=("Triple Threat"), description="Please select your genre.")
            
        await get_genre_buttons(view, 40, 20, "Tier 3", "Triple Threat", 28, 84, 3, interaction.user.id, reroll=reroll, collection=collection)

        dont_save = True
         
    # -------------------------------------------- Let Fate Decide --------------------------------------------
    elif event == "Let Fate Decide" :
        # one t4

        # add pending...
        userInfo[target_user]['Current Rolls'].append({"Event Name" : event, "End Time" : get_unix(minutes=10), "Games" : ["pending..."]})

        # close and reopen users2.json
        dump = await dump_mongo('user', userInfo)
        userInfo = await get_mongo('user')

        embed = discord.Embed(title=("Let Fate Decide"), description="A random T4 in a genre of you choosing will be rolled. There is no time limit for Let Fate Decide. You win once you complete all Primary Objectives in your rolled game!")
        await get_genre_buttons(view, 1000, 20, "Tier 4", event, 1, 84, 1, interaction.user.id, reroll=reroll, collection=collection)
        dont_save = True

    # -------------------------------------------- Fourward Thinking --------------------------------------------
    elif event == "Fourward Thinking" :
        # idk
        print('hahahaha')

        # eligibility
        eligible = False
        for r in database_name[target_user]["Completed Rolls"]:
            if r["Event Name"] == "Let Fate Decide":
                eligible = True
                break
        if not eligible : return await interaction.followup.send("You need to complete Let Fate Decide to roll Fourward Thinking!")
        
        # See if the user has already rolled Fourward Thinking
        has_roll = False
        roll_num = 0
        for roll in userInfo[target_user]["Current Rolls"] :
            if roll["Event Name"] == "Fourward Thinking" : 
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
            userInfo[target_user]["Current Rolls"].append({
                "Event Name" : "Fourward Thinking",
                "End Time" : get_unix(minutes=10),
                "Games" : ["pending..."],
                "Rerolls" : 0
            })

            dump = await dump_mongo('user', userInfo)
            return await interaction.followup.send(embed=embed, view=view)


            # old method
            """
            game2 = get_rollable_game(40, 20, "Tier 1", database_tier=database_tier, database_name=database_name)
            embed2 = getEmbed(game2, interaction.user.id, database_name)

            embeds = [embed, embed2]

            view = discord.ui.View(timeout=600)
            await get_buttons(view, embeds)

            userInfo[target_user]["Current Rolls"].append({
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
        elif (has_roll and "End Time" in list(userInfo[target_user]["Current Rolls"][roll_num].keys())) :
            if userInfo[target_user]["Current Rolls"][roll_num]["Games"][0] == "pending...":
                return await interaction.followup.send("Please wait 10 minutes in between requests.")
            if userInfo[target_user]["Current Rolls"][roll_num]["Rerolls"] == 0:
                return await interaction.followup.send("You are currently participating in Fourward Thinking and have no reroll tickets. Beat it.")
            else:
                view = discord.ui.View(timeout=600)
                agree_button = discord.ui.Button(label="Agree", style=discord.ButtonStyle.success)
                deny_button = discord.ui.Button(label ="Deny", style=discord.ButtonStyle.danger)
                view.add_item(deny_button)
                view.add_item(agree_button)
                return await interaction.followup.send(f"You have {userInfo[target_user]["Current Rolls"][roll_num]["Rerolls"]} reroll ticket(s). Would you like to use one?", 
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
            num_of_games = len(userInfo[target_user]["Current Rolls"][roll_num]["Games"])
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
            
            for game in (userInfo[target_user]["Current Rolls"][roll_num]["Games"]):
                genre = database_name[game]["Genre"]
                for i, g in enumerate(genres):
                    if g == genre: view.children[i].disabled = True
            
            userInfo[target_user]["Current Rolls"][roll_num] = {
                "Event Name" : "Fourward Thinking",
                "End Time" : get_unix(minutes=10),
                "Games" : ["pending..."] + userInfo[target_user]["Current Rolls"][roll_num]["Games"],
                "Rerolls" : userInfo[target_user]["Current Rolls"][roll_num]["Rerolls"]
            }
            
            dump = await dump_mongo('user', userInfo)
            return await interaction.followup.send(view=view, embed=embed)


            # update users2.json
            """
            userInfo[target_user]["Current Rolls"][roll_num]["Games"].append(game)
            userInfo[target_user]["Current Rolls"][roll_num]["End Time"] = get_unix(7*(num_of_games+1))
            userInfo[target_user]["Current Rolls"][roll_num]["Rerolls"] += 1

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
        userInfo[target_user]["Current Rolls"].append({"Event Name" : event, 
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
        for index, c_roll in enumerate(userInfo[target_user]["Current Rolls"]) :
            if c_roll["Event Name"] == event :
                c_num = index
                break
        
        if c_num == -1 : return await interaction.followup.send('you havent rolled this game. except i should have cleared that already. something is wrong')

        userInfo[target_user]['Current Rolls'][c_num] = ({
            "Event Name" : event,
            "End Time" : userInfo[target_user]["Current Rolls"][c_num]["End Time"],
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
    del dump#
