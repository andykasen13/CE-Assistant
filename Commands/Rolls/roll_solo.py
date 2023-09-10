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
from Helper_Functions.end_time import roll_completed, roll_failed
from Helper_Functions.update import update_p

final_ce_icon = "https://cdn.discordapp.com/attachments/1135993275162050690/1144289627612655796/image.png"

async def solo_command(interaction : discord.Interaction, event : str, reroll : bool, collection) :
    

    # Set up variables
    view = discord.ui.View(timeout=600)
    games = []
    embeds = []
    genres = ["Action", "Arcade", "Bullet Hell", "First-Person", "Platformer", "Strategy"]
    times = {
        "One Hell of a Day" : timedelta(1),
        "One Hell of a Week" : timedelta(7),
        "One Hell of a Month" : timedelta(28),
        "Two Week T2 Streak" : timedelta(14),
        "Two 'Two Week T2 Streak' Streak" : timedelta(28),
        "Never Lucky" : timedelta(0),
        "Triple Threat" : timedelta(28),
        "Let Fate Decide" : timedelta(0),
        "Fourward Thinking" : timedelta(0),
        "Russian Roulette" :timedelta(0)
    }
    dont_save = False
    ends = True

    userInfo = await collection.find_one({'_id' : ObjectId('64f8bd1b094bdbfc3f7d0051')})
    
    i = 0
    target_user = ""
    for current_user in userInfo :
        if current_user == '_id' : continue
        print(current_user)
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
        if((eventInfo['Event Name'] == event) and event != "Fourward Thinking" and not reroll) : return await interaction.followup.send(embed=discord.Embed(title=f"You are already participating in {event}!"))

    database_name = await collection.find_one({'_id' : ObjectId('64f8d47f827cce7b4ac9d35b')})

    #  -------------------------------------------- One Hell of a Day  --------------------------------------------
    if event == "One Hell of a Day" :
        # Get one random (rollable) game in Tier 1, non-genre specific
        games.append(get_rollable_game(10, 10, "Tier 1", userInfo[current_user]))

        # Create the embed
        embed = getEmbed(games[0], interaction.user.id)
        embed.add_field(name="Roll Requirements", value = 
            "You have one day to complete " + embed.title + "."    
            + "\nMust be completed by <t:" + str(int(time.mktime((datetime.datetime.now()+timedelta(1)).timetuple())))
            + ">\nOne Hell of a Day has a two week cooldown."
            + "\nCooldown ends on <t:" + str(int(time.mktime((datetime.datetime.now()+timedelta(14)).timetuple())))
            + ">\n[insert link to cedb.me page]", inline=False)
        embed.set_author(name="ONE HELL OF A DAY", url="https://example.com")

    # -------------------------------------------- Two Week T2 Streak --------------------------------------------
    elif event == "Two Week T2 Streak" :
        # two random t2s
        print("received two week t2 streak")

        # ----- Grab two random games -----
        games.append(get_rollable_game(40, 20, "Tier 2", userInfo[current_user]))
        genres.remove(database_name[games[0]]["Genre"])
        games.append(get_rollable_game(40, 20, "Tier 2", userInfo[current_user], genres))
        
        # ----- Get all the embeds -----s
        embeds = create_multi_embed("Two Week T2 Streak", 14, games, 0, interaction,)
        embed = embeds[0]

        await get_buttons(view, embeds) # Create buttons

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
            games.append(get_rollable_game(10, 10, "Tier 1", userInfo[current_user], genres))
            genres.remove(database_name[games[i]]["Genre"])
            i+=1

        # ----- Get all the embeds -----
        embeds = create_multi_embed("One Hell of a Week", 7, games, 28, interaction)       
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
                games.append(get_rollable_game(10, 10, "Tier 1", specific_genre=ggenre, games=games))
                i+=1
        embeds = create_multi_embed("One Hell of a Month", 28, games, 28*3, interaction)
        embed = embeds[0]
        await get_buttons(view, embeds)


    # -------------------------------------------- Two "Two Week T2 Streak" Streak ---------------------------------------------
    elif event == "Two 'Two Week T2 Streak' Streak" :
        # four t2s
        print("Recieved request for Two 'Two Week T2 Streak' Streak")

        eligible = False
        for roll in userInfo[target_user]["Completed Rolls"] :
            if(roll["Event Name"] == "Two Week T2 Streak") : eligible = True

        if not eligible : return await interaction.followup.send(f"You must complete 'Two Week T2 Streak' to be eligible for {event}.")

        # ----- Grab all the games -----
        genres.remove("Strategy")
        i=0
        while i < 4:
            games.append(get_rollable_game(40, 20, "Tier 2", userInfo[current_user], genres))
            genres.remove(database_name[games[i]]["Genre"])
            i+=1
        
        # ----- Get all the embeds -----
        embeds = create_multi_embed("Two 'Two Week T2 Streak' Streak", 28, games, 7, interaction)
        embed = embeds[0]
        await get_buttons(view, embeds)

    # -------------------------------------------- Never Lucky --------------------------------------------
    elif event == "Never Lucky" :
        # one t3
        games.append(get_rollable_game(40, 20, "Tier 3", userInfo[current_user]))

        ends = False

        # Create the embed
        total_points = 0
        embed = getEmbed(games[0], interaction.user.id)
        embed.set_author(name="Never Lucky", url="https://example.com")
        embed.add_field(name="Roll Requirements", value = 
            "There is no time limit on " + embed.title + "."
            + "\nNever Lucky has a one week cooldown."
            + "\nCooldown ends on <t:" + str(int(time.mktime((datetime.datetime.now()+timedelta(28)).timetuple())))
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
        userInfo[target_user]['Current Rolls'].append({"Event Name" : event, "End Time" : int(time.mktime((datetime.datetime.now()+timedelta(minutes=10)).timetuple())), "Games" : ["pending..."]})

        # close and reopen users2.json
        dump = await collection.replace_one({'_id' : ObjectId('64f8bd1b094bdbfc3f7d0051')}, userInfo)
        userInfo = await collection.find_one({'_id' : ObjectId('64f8bd1b094bdbfc3f7d0051')})

        # ----- Grab all the games -----
        embed = discord.Embed(title=("Triple Threat"), description="Please select your genre.")
            
        await get_genre_buttons(view, 40, 20, "Tier 3", "Triple Threat", 28, 84, 3, interaction.user.id, reroll=reroll)

        dont_save = True
         
    # -------------------------------------------- Let Fate Decide --------------------------------------------
    elif event == "Let Fate Decide" :
        # one t4

        # add pending...
        userInfo[target_user]['Current Rolls'].append({"Event Name" : event, "End Time" : int(time.mktime((datetime.datetime.now()+timedelta(minutes=10)).timetuple())), "Games" : ["pending..."]})

        # close and reopen users2.json
        dump = await collection.replace_one({'_id' : ObjectId('64f8bd1b094bdbfc3f7d0051')}, userInfo)
        userInfo = await collection.find_one({'_id' : ObjectId('64f8bd1b094bdbfc3f7d0051')})

        embed = discord.Embed(title=("Let Fate Decide"), description="A random T4 in a genre of you choosing will be rolled. There is no time limit for Let Fate Decide. You win once you complete all Primary Objectives in your rolled game!")
        await get_genre_buttons(view, 1000, 20, "Tier 4", event, 1, 84, 1, interaction.user.id, reroll=reroll)
        dont_save = True

    # -------------------------------------------- Fourward Thinking --------------------------------------------
    elif event == "Fourward Thinking" :
        # idk
        
        # See if the user has already rolled Fourward Thinking
        has_roll = False
        roll_num = 0
        for roll in userInfo[target_user]["Current Rolls"] :
            if roll["Event Name"] == "Fourward Thinking" : 
                has_roll = True
                break
            roll_num += 1


        if(not has_roll) : 
            # Has not rolled Fourward Thinking before
            embed = discord.Embed(title=("Fourward Thinking"),
                                  description="You are about to roll Fourward Thinking. This is the most confusing roll event, so buckle in."
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
            embed.set_footer(text="CE Assistant", icon_url=final_ce_icon)
            embed.set_author(name="Challenge Enthusiasts")

            dont_save=True


        elif (has_roll and "End Time" in list(userInfo[target_user]["Current Rolls"][roll_num].keys())) :
            # Has rolled Fourward Thinking but isn't done with the roll yet.
            embed = discord.Embed(title="You are currently participating in Fourward Thinking!")
            dont_save = True

        else : 
            # Has rolled Fourward Thinking and is ready for the next roll
            # OR OR OR is done!
            num_of_games = len(userInfo[target_user]["Current Rolls"][roll_num]["Games"])
            print(num_of_games)

            # set up the starting embed
            embeds.append(discord.Embed(title=event, timestamp=datetime.datetime.now()))
            if(num_of_games == 1) :
                # get a game
                game = get_rollable_game(80, 20, "Tier 2", userInfo[current_user])

                embeds[0].add_field(name="Roll Status", value="You have rolled your T2. You have two weeks to complete.")

            elif(num_of_games == 2):              
                # get a game
                game = get_rollable_game(120, 20, "Tier 3", userInfo[current_user])

                embeds[0].add_field(name="Roll Status", value = "You have rolled your T3. You have three weeks to complete.")
            elif(num_of_games == 3):
                # get a game
                game = get_rollable_game(160, 20, "Tier 4", userInfo[current_user])
                
                embeds[0].add_field(name="Roll Status", value = "You have rolled your T4. You have four weeks to complete.")
                #roll a t4
            
            # get the embed for the new game
            embeds.append(getEmbed(game, interaction.user.id))

            # get buttons
            await get_buttons(view, embeds)
            embed = embeds[0]

            # update users2.json
            userInfo[target_user]["Current Rolls"][roll_num]["Games"].append(game)
            userInfo[target_user]["Current Rolls"][roll_num]["End Time"] = int(time.mktime((datetime.datetime.now()+timedelta(7*(num_of_games+1))).timetuple()))
            
            # dont add the thing to users2.json AGAIN!
            dont_save = True


    # -------------------------------------------- Russian Roulette --------------------------------------------
    elif event == "Russian Roulette" :
        # choose six t5s and get one at random
        embed = discord.Embed(title=("⚠️Roll still under construction!⚠️"))

        dont_save = True

        ends = False

    # ------------------------------------ CONTINUE ON ---------------------------------------------------

    if (dont_save is False) and (not reroll) :
        # append the roll to the user's current rolls array
        userInfo[target_user]["Current Rolls"].append({"Event Name" : event, 
                                                    "End Time" :  int(time.mktime((datetime.datetime.now()+times[event]).timetuple())),
                                                    "Games" : games})

    elif (dont_save is False) and (reroll) :
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


    # dump the info
    dump = await collection.replace_one({'_id' : ObjectId('64f8bd1b094bdbfc3f7d0051')}, userInfo)

    # Finally, send the embed
    await interaction.followup.send(embed=embed, view=view)
    print("Sent information on rolled game: " + str(games) + "\n")