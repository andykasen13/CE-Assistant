# ---------- time imports -----------
import asyncio
from datetime import datetime, timedelta
import datetime
import functools
import os
import time
import typing
from monthdelta import monthdelta

# ----------- discord imports ---------
import discord
from discord import app_commands
import random
from typing import Literal

# ----------- json imports ------------
import json
import psutil

# --------- web imports ---------
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# --------- other file imports ---------
from Web_Interaction.curator import loop, single_run
from Web_Interaction.scraping import get_games, get_completion_data
from Helper_Functions.rollable_games import get_rollable_game, get_rollable_game_from_list
from Helper_Functions.create_embed import create_multi_embed, getEmbed
from Helper_Functions.roll_string import get_roll_string
from Helper_Functions.buttons import get_buttons, get_genre_buttons
from Helper_Functions.end_time import roll_completed, roll_failed
from Helper_Functions.update import update_p

# --------------------------------------------------- ok back to the normal bot ----------------------------------------------
intents = discord.Intents.default()
intents.reactions = True
intents.members = True
intents.guilds = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

intents.message_content = True

# Grab information from json file
with open('Jasons/secret_info.json') as f :
    localJSONData = json.load(f)

discord_token = localJSONData['discord_token']
guild_ID = localJSONData['other_guild_ID']
ce_mountain_icon = "https://cdn.discordapp.com/attachments/639112509445505046/891449764787408966/challent.jpg"
ce_hex_icon = "https://media.discordapp.net/attachments/643158133673295898/1133596132551966730/image.png?width=778&height=778"
ce_james_icon = "https://cdn.discordapp.com/attachments/1028404246279888937/1136056766514339910/CE_Logo_M3.png"


# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------HELP COMMAND------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
@tree.command(name="help", description="help", guild=discord.Object(id=guild_ID))
async def help(interaction) :
    # Defer the message
    await interaction.response.defer()

    # Create the view (will be used for buttons later)
    view = discord.ui.View(timeout=600)

    helpInfo = {
        "Rolls" : "This bot has the ability to roll random games for any event in the Challenge Enthusiast server. P.S. andy reminder to get autofill to work!",
        "/get_rolls" : "Use this command to see your current (and past) rolls, or the rolls of any other user in the server.",
        "steam_test" : "Get general information about any STEAM game.",
        "Curator" : "The bot will automatically check to see if any new entries have been added to the CE curator (within three hours)."
    }

    embeds=[]
    pageNum = 1
    
    for page in list(helpInfo):
        embed=discord.Embed(color=0x000000, title=page, description=helpInfo[page])
        embed.set_footer(text=(f"Page {pageNum} of {len(list(helpInfo))}"))
        embed.timestamp=datetime.datetime.now()
        embeds.append(embed)
        pageNum+=1

    await get_buttons(view, embeds)

    await interaction.followup.send(embed=embeds[0], view=view)





# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------- SOLO ROLL COMMAND ------------------------------------------------------------ # 
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
events_solo = Literal["One Hell of a Day", "One Hell of a Week", "One Hell of a Month", "Two Week T2 Streak", 
          "Two 'Two Week T2 Streak' Streak", "Never Lucky", "Triple Threat", "Let Fate Decide", "Fourward Thinking",
          "Russian Roulette"]
@tree.command(name="solo-roll", description="Participate in Challenge Enthusiast roll events!", guild=discord.Object(id=guild_ID))
@app_commands.describe(event="The event you'd like to participate in")
async def roll_solo_command(interaction : discord.Interaction, event: events_solo) -> None:   
    await interaction.response.defer()

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

    # find the location of the user
    with open('Jasons/users2.json', 'r') as u2:
        userInfo = json.load(u2)
    i = 0
    target_user = ""
    for current_user in userInfo :
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
        if(eventInfo['Event Name'] == event and eventInfo['Games'] == ['pending...']) : return await interaction.followup.send('uh uh uh!')
        if((eventInfo['Event Name'] == event) and event != "Fourward Thinking") : return await interaction.followup.send(embed=discord.Embed(title=f"You are already participating in {event}!"))
    
    # Open the databases.
    with open('Jasons/database_tier.json', 'r') as dB :
        database_tier = json.load(dB)
    with open('Jasons/database_name.json', 'r') as dBN :
        database_name = json.load(dBN)

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
        embed = discord.Embed(title=f"⚠️Roll still under construction!⚠️")
        dont_save = True

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
        embed.add_field(name="Rolled by", value = "<@" + str(interaction.user.id) + ">", inline=True)
        embed.set_thumbnail(url=interaction.user.avatar)
        embed.add_field(name="Roll Requirements", value = 
            "There is no time limit on " + embed.title + "."
            + "\nNever Lucky has a one week cooldown."
            + "\nCooldown ends on <t:" + str(int(time.mktime((datetime.datetime.now()+monthdelta(1)).timetuple())))
            + f">\nhttps://cedb.me/game/{database_name[embed.title]['CE ID']}/", inline=False)

    # -------------------------------------------- Triple Threat --------------------------------------------
    elif event == "Triple Threat" :
        # three t3s
        print("Recieved request for Triple Threat")
        
        for x_roll in userInfo[target_user]['Current Rolls'] :
            if(x_roll['Event Name'] == event and x_roll['Games'] == ['pending...']) :
                return await interaction.followup.send('hang on their buster')
        
        userInfo[target_user]['Current Rolls'].append({"Event Name" : event, "End Time" : int(time.mktime((datetime.datetime.now()+timedelta(minutes=10)).timetuple())), "Games" : ["pending..."]})
        print(userInfo[target_user])

        with open('Jasons/users2.json', 'w') as f :
            json.dump(userInfo, f, indent=4)

        with open('Jasons/users2.json', 'r') as f :
            userInfo = json.load(f)

        # ----- Grab all the games -----
        embed = discord.Embed(title=("⚠️Roll still under construction...⚠️"), description="Please select your genre.")

        await get_genre_buttons(view, 40, 20, "Tier 3", "Triple Threat", 28, 84, 3, interaction.user.id)

        dont_save = True
         
    # -------------------------------------------- Let Fate Decide --------------------------------------------
    elif event == "Let Fate Decide" :
        # one t4
        print("Recieved request for Let Fate Decide")

        embed = discord.Embed(title=("let fate decide"))
        await get_genre_buttons(view, 40, 20, "Tier 4", event, 1, 84, 1, interaction.user.id)
        dont_save = True
        ends = False

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
            embed = discord.Embed(title=("fourward thinking"))
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
                game = get_rollable_game(40, 20, "Tier 2", userInfo[current_user])

                embeds[0].add_field(name="Roll Status", value="You have rolled your T2. You have two weeks to complete.")

            elif(num_of_games == 2):              
                # get a game
                game = get_rollable_game(40, 20, "Tier 3", userInfo[current_user])

                embeds[0].add_field(name="Roll Status", value = "You have rolled your T3. You have three weeks to complete.")
            elif(num_of_games == 3):
                # get a game
                game = get_rollable_game(40, 20, "Tier 4", userInfo[current_user])
                
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

    if dont_save is False :
        # append the roll to the user's current rolls array
        userInfo[target_user]["Current Rolls"].append({"Event Name" : event, 
                                                    "End Time" :  int(time.mktime((datetime.datetime.now()+times[event]).timetuple())),
                                                    "Games" : games})

    # dump the info
    with open('Jasons/users2.json', 'w') as f :
        json.dump(userInfo, f, indent=4)

    # Finally, send the embed
    await interaction.followup.send(embed=embed, view=view)
    print("Sent information on rolled game: " + str(games) + "\n")



# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------- CO-OP ROLL COMMAND ------------------------------------------------------------ # 
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
events_co_op = Literal["Destiny Alignment", "Soul Mates", "Teamwork Makes the Dream Work", 
                       "Winner Takes All", "Game Theory"]

@tree.command(name="co-op-roll", description="Participate in Challenge Enthusiast Co-Op or PvP roll events!", guild=discord.Object(id=guild_ID))
@app_commands.describe(event="The event you'd like to participate in")
@app_commands.describe(partner="The user you'd like to enter the roll with")
async def roll_co_op_command(interaction : discord.Interaction, event : events_co_op, partner : discord.Member) :
    await interaction.response.defer()

    # Open the user database
    with open('Jasons/users2.json', 'r') as dbU:
        database_user = json.load(dbU)
    with open('Jasons/database_name.json', 'r') as dbN :
        database_name = json.load(dbN)
    
    # Set up variables
    interaction_user_data = ""
    target_user_data = ""
    view = discord.ui.View(timeout=600)
    user_a_avatar = interaction.user.avatar
    user_b_avatar = partner.avatar
    genres = ["Action", "Arcade", "Bullet Hell", "First-Person", "Platformer", "Strategy"]

    # Make sure the user doesn't select themselves
    #if interaction.user.id == partner.id : return await interaction.followup.send("You cannot enter a co-op roll with yourself.")

    # Grab the information for both users
    for user in database_user :
        if database_user[user]["Discord ID"] == interaction.user.id : 
            interaction_user_data = database_user[user]
            username_interaction = user
        if database_user[user]["Discord ID"] == partner.id : 
            target_user_data = database_user[user]
            username_target = user
    
    # Make sure both users are registered in the database
    if interaction_user_data == "" : return await interaction.followup.send("You are not registered in the CE Assistant database.")
    if target_user_data == "" : return await interaction.followup.send(f"<@{partner.id}> is not registered in the CE Assistant database.")

    # Make sure both users aren't currently participating in the event
    for roll in interaction_user_data['Current Rolls'] :
        if(roll['Event Name'] == event) : return await interaction.followup.send("You are currently participating in {}!".format(event))
    for roll in target_user_data['Current Rolls'] :
        if(roll['Event Name'] == event) : return await interaction.followup.send("Your partner is currently participating in {}!".format(event))

    # ----------------------------------------------- Destiny Alignment ---------------------------------------------------
    if(event == "Destiny Alignment") :

        # Make sure both users are the same rank
        if(interaction_user_data["Rank"] != target_user_data["Rank"]) : return await interaction.followup.send("You are not the same rank!")

        # Send confirmation embed
        embed = discord.Embed(title="Destiny Alignment", timestamp=datetime.datetime.now())
        embed.add_field(name="Roll Information", value="You will each roll a game that the other has completed." 
                        + " You must both complete all Primary Objectives for your rolled game."
                        + " Cooldown is one month.")
        embed.add_field(name="Confirmation", value=f"<@{partner.id}>, do you agree to participate with <@{interaction.user.id}>?")

        # ----- Set up buttons... -----
        agree_button = discord.ui.Button(label="Agree", style=discord.ButtonStyle.success)
        deny_button = discord.ui.Button(label="Deny", style=discord.ButtonStyle.danger)
        view.add_item(deny_button)
        view.add_item(agree_button)
        async def agree_callback(interaction) :
            await interaction.response.defer()
            if interaction.user.id != target_user_data["Discord ID"] : return
            
            interaction_user_completed_games = []
            target_user_completed_games = []

            # -------------------------------------------------------- Grab games ----------------------------------------------------

            # Grab all completed games from interaction user 
            for interaction_user_game in interaction_user_data["Owned Games"] :
                print(interaction_user_game)
                # Grab all objectives completed by User A
                try : interaction_user_obj_list = list(interaction_user_data["Owned Games"][interaction_user_game]["Primary Objectives"])
                except : interaction_user_obj_list = []

                # Grab all objectives for the game
                database_obj_list = list(database_name[interaction_user_game]["Primary Objectives"])

                # If they're the same, add the game to the list of possibilities.
                if interaction_user_obj_list == database_obj_list : interaction_user_completed_games.append(interaction_user_game)

            #  Grab all completed games from target user 
            for target_user_game in target_user_data["Owned Games"] :
                # Grab all objectives completed by User B
                try: target_user_obj_list = list(target_user_data["Owned Games"][target_user_game]["Primary Objectives"])
                except : target_user_obj_list = []

                # Grab all objectives for the game
                database_obj_list = list(database_name[target_user_game]["Primary Objectives"])

                # If they're the same, add the game to the list of possibilities.
                if target_user_obj_list == database_obj_list : target_user_completed_games.append(target_user_game)

            # ----- Make sure the other user doesn't have any points in the game they rolled -----
            target_user_owns_game = True
            target_user_has_points_in_game = True

            while target_user_owns_game and target_user_has_points_in_game :
                # grab a rollable game
                interaction_user_selected_game = await get_rollable_game_from_list(interaction_user_completed_games)
                # check to see if they own the game and if they have points in the game
                target_user_owns_game = list(target_user_data["Owned Games"].keys()).count(interaction_user_selected_game) > 0
                if(target_user_owns_game) : 
                    target_user_has_points_in_game = list(target_user_data["Owned Games"][interaction_user_selected_game].keys()).count("Primary Objectives") > 0
                else : target_user_has_points_in_game = False

            interaction_user_owns_game = True
            interaction_user_has_points_in_game = True

            while interaction_user_owns_game and interaction_user_has_points_in_game :
                # grab a rollable game
                target_user_selected_game = await get_rollable_game_from_list(target_user_completed_games)
                # check to see if they own the game and if they have points in the game
                interaction_user_owns_game = list(interaction_user_data["Owned Games"].keys()).count(target_user_selected_game) > 0
                if(interaction_user_owns_game) :
                    interaction_user_has_points_in_game = list(interaction_user_data["Owned Games"][target_user_selected_game].keys()).count("Primary Objectives") > 0
                else : interaction_user_has_points_in_game = False

            games = [interaction_user_selected_game, target_user_selected_game]

            # ------------------------------------------- Return to other things ----------------------------------------------

            # Clear the "agree" and "deny" buttons
            view.clear_items()

            # Grab the embeds you'll need
            embeds = create_multi_embed("Destiny Alignment", 0, games, 28, interaction)

            # Make adjustments to embeds
            embeds[0].set_field_at(index=0, name="Rolled Games",
                                  value=f"<@{target_user_data['Discord ID']}>: {interaction_user_selected_game}"
                                  + f"\n<@{interaction_user_data['Discord ID']}>: {target_user_selected_game}")
            embeds[0].set_thumbnail(url = ce_mountain_icon)
            embeds[2].set_field_at(index = 1, name = "Rolled by", value = f"<@{interaction_user_data['Discord ID']}>")
            embeds[2].set_thumbnail(url = user_a_avatar)

            # Get page buttons
            await get_buttons(view, embeds)

            
            database_user[username_interaction]["Current Rolls"].append({"Event Name" : event, 
                                                                         "Games" : [target_user_selected_game],
                                                                         "Partner": username_target})
            database_user[username_target]["Current Rolls"].append({"Event Name" : event,
                                                                    "Games" : [interaction_user_selected_game],
                                                                    "Partner" : username_interaction})
        
            with open('Jasons/users2.json', 'w') as f:
                json.dump(database_user, f, indent=4)

            # and edit the message.
            return await interaction.followup.edit_message(embed=embeds[0], view=view, message_id=interaction.message.id)
        
        async def deny_callback(interaction) :
            await interaction.response.defer()
            if interaction.user.id != target_user_data["Discord ID"] : return

            # Set up denial embed
            embed = discord.Embed(
                title="Roll Denied",
                description=f"<@{partner.id}> has denied the roll.",
                timestamp=datetime.datetime.now()
            )

            view.clear_items()
            return await interaction.followup.edit_message(embed=embed, view=view, message_id=interaction.message.id)
        agree_button.callback = agree_callback
        deny_button.callback = deny_callback
    
    # --------------------------------------------- Soul Mates ---------------------------------------------------------
    elif(event == "Soul Mates") :
        embed = discord.Embed(title="Soul Mates", timestamp=datetime.datetime.now())
        embed.add_field(name="Roll Requirements", value="You and your partner must agree on a tier. A game will be rolled for both of you," 
                                                        + "and you must **both** complete it in the time constraint listed below.")
        embed.add_field(name="Tier Choices",
                        value=":one: : 48 Hours\n:two: : 10 Days\n:three: : One Month\n:four: : Two Months\n:five: : Forever")
        embed.set_thumbnail(url = ce_mountain_icon)
        embed.set_author(name="Challenge Enthusiasts")
        embed.set_footer(text="CE Assistant", icon_url=ce_james_icon)

        buttons = []
        i = 1
        while i < 6 :
            buttons.append(discord.ui.Button(label=f"Tier {i}"))
            view.add_item(buttons[i-1])
            i+=1
    
        async def t1_callback(interaction) : return await soulmate_callback(interaction, "Tier 1")
        async def t2_callback(interaction) : return await soulmate_callback(interaction, "Tier 2")
        async def t3_callback(interaction) : return await soulmate_callback(interaction, "Tier 3")
        async def t4_callback(interaction) : return await soulmate_callback(interaction, "Tier 4")
        async def t5_callback(interaction) : return await soulmate_callback(interaction, "Tier 5")

        async def soulmate_callback(interaction : discord.Interaction, tier_num) :
            await interaction.response.defer()
            if interaction.user.id != interaction_user_data['Discord ID'] : return

            view.clear_items()
            await interaction.followup.edit_message(embed=discord.Embed(title="Working..."), message_id=interaction.message.id, view=view)

            # ----- Make sure the other user doesn't have any points in the game they rolled -----
            target_user_owns_game = True
            target_user_has_points_in_game = True
            interaction_user_owns_game = True
            interaction_user_has_points_in_game = True
            while (target_user_owns_game and target_user_has_points_in_game) or (interaction_user_owns_game and interaction_user_has_points_in_game) :
                # grab a rollable game
                game = get_rollable_game(40, 20, tier_num)
                
                # check to see if user B owns the game and if they have points in the game
                target_user_owns_game = list(target_user_data["Owned Games"].keys()).count(game) > 0
                if(target_user_owns_game) : 
                    target_user_has_points_in_game = list(target_user_data["Owned Games"][game].keys()).count("Primary Objectives") > 0
                else : target_user_has_points_in_game = False

                # check to see if user A owns the game and if they have points in the game
                interaction_user_owns_game = list(interaction_user_data["Owned Games"].keys()).count(game) > 0
                if(interaction_user_owns_game) :
                    interaction_user_has_points_in_game = list(interaction_user_data["Owned Games"][game].keys()).count("Primary Objectives") > 0
                else : interaction_user_has_points_in_game = False

            # ----- Set up agreement buttons for User B -----
            agree_button = discord.ui.Button(label="Agree", style=discord.ButtonStyle.success)
            deny_button = discord.ui.Button(label ="Deny", style=discord.ButtonStyle.danger)
            view.add_item(agree_button)
            view.add_item(deny_button)
            async def agree_callback(interaction) :
                await interaction.response.defer()
                if interaction.user.id != target_user_data['Discord ID'] : return

                view.clear_items()
                embed = getEmbed(game, interaction.user.id)
                embed.set_field_at(index=1, name="Rolled by", value=f"<@{interaction_user_data['Discord ID']}> and <@{target_user_data['Discord ID']}>")
                embed.add_field(name="Tier", value=database_name[game]["Tier"])

                times = {"Tier 1" : timedelta(days=2),
                         "Tier 2" : timedelta(10),
                         "Tier 3" : timedelta(30),
                         "Tier 4" : timedelta(60)}

            
                # fake dict 1
                fake_dict_1 = {
                    "Event Name" : event
                }
                if(tier_num != "Tier 5") : fake_dict_1.update({"End Time" : int(time.mktime((datetime.datetime.now()+times[tier_num]).timetuple()))})
                fake_dict_1.update({"Games" : [game],
                                    "Partner": username_target})

                # fake dict 2
                fake_dict_2 = {
                    "Event Name" : event
                }
                if(tier_num != "Tier 5") : fake_dict_2.update({"End Time" : int(time.mktime((datetime.datetime.now()+times[tier_num]).timetuple()))})
                fake_dict_2.update({"Games" : [game],
                                    "Partner": username_target})
                         

                database_user[username_interaction]["Current Rolls"].append(fake_dict_1)
                database_user[username_target]["Current Rolls"].append(fake_dict_2)
                
                with open('Jasons/users2.json', 'w') as f:
                    json.dump(database_user, f, indent=4)

                return await interaction.followup.edit_message(embed=embed, view=view, message_id=interaction.message.id)
            async def deny_callback(interaction) :
                await interaction.response.defer()
                if interaction.user.id != target_user_data['Discord ID'] : return
                view.clear_items()
                return await interaction.followup.edit_message(message_id=interaction.message.id, embed=discord.Embed(title="Roll denied."))
            agree_button.callback = agree_callback
            deny_button.callback = deny_callback


            # Set up embed for user B
            embed = discord.Embed(title="Do you accept?", description='{} chosen by <@{}>.'.format(tier_num, interaction_user_data['Discord ID']), timestamp=datetime.datetime.now())
            await interaction.followup.edit_message(message_id=interaction.message.id, embed=embed, view=view)

        buttons[0].callback = t1_callback
        buttons[1].callback = t2_callback
        buttons[2].callback = t3_callback
        buttons[3].callback = t4_callback
        buttons[4].callback = t5_callback
        """
        - send a message asking what tier should be picked from
            - only user A should be able to respond
            - this should include notes on how long each tier would have to complete the roll
        - send another confirmation message 
            - only user B should be allowed to respond
        - get rollable games for whatever tier they asked for
            - game must be rerolled if either user has any points in the game

        """
    
    # -------------------------------------------- Teamwork Makes the Dream Work -------------------------------------------
    elif(event == "Teamwork Makes the Dream Work") :
        # Send confirmation embed
        embed = discord.Embed(title = "Teamwork Makes the Dream Work", timestamp = datetime.datetime.now())
        embed.add_field(name = "Roll Information", value = "Four Tier 3 games will be rolled. Between the two of you,"
                        + " you must complete all four games. This roll has no time limit, and the cooldown is three months.")
        embed.add_field(name = "Confirmation", value = f"<@{partner.id}>, do you agree to participate with <@{interaction.user.id}>?")

        # ----- Set up buttons -----
        agree_button = discord.ui.Button(label = "Agree", style = discord.ButtonStyle.success)
        deny_button = discord.ui.Button(label = "Deny", style = discord.ButtonStyle.danger)
        view.add_item(agree_button)
        view.add_item(deny_button)

        async def agree_callback(interaction) :
            await interaction.response.defer()
            # make sure only target can use button
            if interaction.user.id != target_user_data["Discord ID"] : return

            # clear the agree and deny buttons
            view.clear_items()
            games = []

            await interaction.followup.edit_message(embed=discord.Embed(title="Working..."), view=view, message_id=interaction.message.id)


            i = 0
            while (i < 4) :
                # ----- Make sure neither player has any points in any game -----
                target_user_owns_game = True
                target_user_has_points_in_game = True
                interaction_user_owns_game = True
                interaction_user_has_points_in_game = True
                while (target_user_owns_game and target_user_has_points_in_game) or (interaction_user_owns_game and interaction_user_has_points_in_game) :
                    # grab a rollable game
                    game = get_rollable_game(40, 20, "Tier 3")
                    
                    # check to see if user B owns the game and if they have points in the game
                    target_user_owns_game = list(target_user_data["Owned Games"].keys()).count(game) > 0
                    if(target_user_owns_game) : 
                        target_user_has_points_in_game = list(target_user_data["Owned Games"][game].keys()).count("Primary Objectives") > 0
                    else : target_user_has_points_in_game = False

                    # check to see if user A owns the game and if they have points in the game
                    interaction_user_owns_game = list(interaction_user_data["Owned Games"].keys()).count(game) > 0
                    if(interaction_user_owns_game) :
                        interaction_user_has_points_in_game = list(interaction_user_data["Owned Games"][game].keys()).count("Primary Objectives") > 0
                    else : interaction_user_has_points_in_game = False
                # append the game 
                games.append(game)
                i+=1

            # Get embeds
            embeds = create_multi_embed("Teamwork Makes the Dream Work", 28, games, (28*3), interaction)

            i = 1
            while i < 5 :
                embeds[i].set_field_at(index=1, name="Rolled by", value="<@{}> and <@{}>".format(interaction_user_data['Discord ID'], target_user_data['Discord ID']))
                i+=1

            # Get page buttons
            await get_buttons(view, embeds)

            database_user[username_interaction]["Current Rolls"].append({"Event Name" : event, 
                                                                        "End Time" : int(time.mktime((datetime.datetime.now()+timedelta(30)).timetuple())),
                                                                         "Games" : games,
                                                                         "Partner": username_target})
            database_user[username_target]["Current Rolls"].append({"Event Name" : event,
                                                                        "End Time" : int(time.mktime((datetime.datetime.now()+timedelta(30)).timetuple())),
                                                                    "Games" : games,
                                                                    "Partner" : username_interaction})
            
            with open('Jasons/users2.json', 'w') as f :
                json.dump(database_user, f, indent=4)

            # and edit the message.
            return await interaction.followup.edit_message(embed=embeds[0], view=view, message_id=interaction.message.id)
        async def deny_callback(interaction) :
            await interaction.response.defer()
            if interaction.user.id != target_user_data['Discord ID'] : return
            view.clear_items()
            return await interaction.followup.edit_message(message_id=interaction.message.id, embed=discord.Embed(title="Roll denied."))
        agree_button.callback = agree_callback
        deny_button.callback = deny_callback
        """
        - send confirmation message
            - only user B should be allowed to respond
        - roll them four tier 3 games
            - game must be rerolled if either user has any points in the game
        """
    
    # -------------------------------------------------- Winner Takes All --------------------------------------------------
    elif(event == "Winner Takes All") :
        embed = discord.Embed(title="Winner Takes All", timestamp=datetime.datetime.now())
        embed.add_field(name="Roll Requirements", value="You and your partner must agree on a tier. A game will be rolled for both of you." 
                                                        + " The first to complete all Primary Objectives will win.")
        embed.set_thumbnail(url = ce_mountain_icon)
        embed.set_author(name="Challenge Enthusiasts")
        embed.set_footer(text="CE Assistant", icon_url=ce_james_icon)

        buttons = []
        i = 1
        while i < 6 :
            buttons.append(discord.ui.Button(label=f"Tier {i}"))
            view.add_item(buttons[i-1])
            i+=1
    
        async def t1_callback(interaction) : return await soulmate_callback(interaction, "Tier 1")
        async def t2_callback(interaction) : return await soulmate_callback(interaction, "Tier 2")
        async def t3_callback(interaction) : return await soulmate_callback(interaction, "Tier 3")
        async def t4_callback(interaction) : return await soulmate_callback(interaction, "Tier 4")
        async def t5_callback(interaction) : return await soulmate_callback(interaction, "Tier 5")

        async def soulmate_callback(interaction, tier_num) :
            await interaction.response.defer()
            if interaction.user.id != interaction_user_data['Discord ID'] : return
            view.clear_items()

            # ----- Make sure the other user doesn't have any points in the game they rolled -----
            target_user_owns_game = True
            target_user_has_points_in_game = True
            interaction_user_owns_game = True
            interaction_user_has_points_in_game = True
            while (target_user_owns_game and target_user_has_points_in_game) or (interaction_user_owns_game and interaction_user_has_points_in_game) :
                # grab a rollable game
                game = get_rollable_game(40, 20, tier_num)
                
                # check to see if user B owns the game and if they have points in the game
                target_user_owns_game = list(target_user_data["Owned Games"].keys()).count(game) > 0
                if(target_user_owns_game) : 
                    target_user_has_points_in_game = list(target_user_data["Owned Games"][game].keys()).count("Primary Objectives") > 0
                else : target_user_has_points_in_game = False

                # check to see if user A owns the game and if they have points in the game
                interaction_user_owns_game = list(interaction_user_data["Owned Games"].keys()).count(game) > 0
                if(interaction_user_owns_game) :
                    interaction_user_has_points_in_game = list(interaction_user_data["Owned Games"][game].keys()).count("Primary Objectives") > 0
                else : interaction_user_has_points_in_game = False

            # ----- Set up agreement buttons for User B -----
            agree_button = discord.ui.Button(label="Agree", style=discord.ButtonStyle.success)
            deny_button = discord.ui.Button(label ="Deny", style=discord.ButtonStyle.danger)
            view.add_item(agree_button)
            view.add_item(deny_button)
            async def agree_callback(interaction) :
                await interaction.response.defer()
                if interaction.user.id != target_user_data['Discord ID'] : return
                view.clear_items()
                embed = getEmbed(game, interaction.user.id)
                embed.add_field(name="Rolled by", value=f"<@{interaction_user_data['Discord ID']}> and <@{target_user_data['Discord ID']}>")
                embed.add_field(name="Tier", value=database_name[game]["Tier"])
                embed.add_field(name="Completion", value="When you have completed, submit your proof to <#747384873320448082>. The first to do so wins.")

                database_user[username_interaction]["Current Rolls"].append({"Event Name" : event, 
                                                                         "Games" : [game],
                                                                         "Partner": username_target})
                database_user[username_target]["Current Rolls"].append({"Event Name" : event,
                                                                    "Games" : [game],
                                                                    "Partner" : username_interaction})
            
                with open('Jasons/users2.json', 'w') as f :
                    json.dump(database_user, f, indent=4)

                return await interaction.followup.edit_message(embed=embed, view=view, message_id=interaction.message.id)
            async def deny_callback(interaction) :
                await interaction.response.defer()
                if interaction.user.id != target_user_data['Discord ID'] : return
                view.clear_items()
                return await interaction.followup.edit_message(message_id=interaction.message.id, embed=discord.Embed(title="Roll denied."))
            agree_button.callback = agree_callback
            deny_button.callback = deny_callback


            # Set up embed for user B
            embed = discord.Embed(title="Do you accept?", timestamp=datetime.datetime.now())
            await interaction.followup.edit_message(message_id=interaction.message.id, embed=embed, view=view)

        buttons[0].callback = t1_callback
        buttons[1].callback = t2_callback
        buttons[2].callback = t3_callback
        buttons[3].callback = t4_callback
        buttons[4].callback = t5_callback
        """
        - send a message asking what tier should be picked from
            - only user A should be able to respond
        - send a confirmation message for user B
            - only user B should be allowed to respond
        - roll a random game in that tier
            - neither user can have completed any objectives in the game
        """

    # ---------------------------------------------------- Game Theory -----------------------------------------------------
    elif(event == "Game Theory") :
        embed = discord.Embed(title="Game Theory", timestamp=datetime.datetime.now())
        embed.add_field(name="Roll Requirements", value="You and your partner must agree on a tier. A game will be rolled for both of you," 
                                                        + "and you must **both** complete it in the time constraint listed below.")
        embed.add_field(name="Tier Choices",
                        value=f"<@{interaction.user.id}>, please select the genre for the other user.")
        embed.set_thumbnail(url = ce_mountain_icon)
        embed.set_author(name="Challenge Enthusiasts")
        embed.set_footer(text="CE Assistant", icon_url=ce_james_icon)

        buttons = []
        i = 0

        async def action_callback(interaction) : return await game_theory_callback_1(interaction, "Action")        
        async def arcade_callback(interaction) : return await game_theory_callback_1(interaction, "Arcade")
        async def bullet_hell_callback(interaction) : return await game_theory_callback_1(interaction, "Bullet Hell")
        async def fps_callback(interaction) : return await game_theory_callback_1(interaction, "First-Person")
        async def platformer_callback(interaction) : return await game_theory_callback_1(interaction, "Platformer")
        async def strategy_callback(interaction) : return await game_theory_callback_1(interaction, "Strategy")


        while i < 6 :
            buttons.append(discord.ui.Button(label=genres[i]))
            view.add_item(buttons[i])
            i+=1
        
        buttons[0].callback = action_callback
        buttons[1].callback = arcade_callback
        buttons[2].callback = bullet_hell_callback
        buttons[3].callback = fps_callback
        buttons[4].callback = platformer_callback
        buttons[5].callback = strategy_callback

        buttons[5].disabled = True

        async def game_theory_callback_1(interaction : discord.Interaction, targets_genre) :
            await interaction.response.defer()
            if(interaction.user.id != interaction_user_data["Discord ID"]) : return

            view.clear_items()
            embed.set_field_at(index=1, name="Tier Choices", 
                               value=f"Tier chosen. <@{target_user_data['Discord ID']}>, please select the genre for the other user.")

            buttons = []

            i = 0
            while i < 6 :
                buttons.append(discord.ui.Button(label=genres[i]))
                view.add_item(buttons[i])
                i+=1
            
            async def action_callback1(interaction) : return await game_theory_callback_2(interaction, "Action")        
            async def arcade_callback1(interaction) : return await game_theory_callback_2(interaction, "Arcade")
            async def bullet_hell_callback1(interaction) : return await  game_theory_callback_2(interaction, "Bullet Hell")
            async def fps_callback1(interaction) : return await game_theory_callback_2(interaction, "First-Person")
            async def platformer_callback1(interaction) : return await game_theory_callback_2(interaction, "Platformer")
            async def strategy_callback1(interaction) : return await game_theory_callback_2(interaction, "Strategy")

            buttons[0].callback = action_callback1
            buttons[1].callback = arcade_callback1
            buttons[2].callback = bullet_hell_callback1
            buttons[3].callback = fps_callback1
            buttons[4].callback = platformer_callback1
            buttons[5].callback = strategy_callback1

            buttons[5].disabled = True

            async def game_theory_callback_2(interaction : discord.Interaction, interactions_genre) :
                await interaction.response.defer()
                if interaction.user.id != target_user_data["Discord ID"] : return

                view.clear_items()

                await interaction.followup.edit_message(message_id=interaction.message.id, view=view, embed=discord.Embed(title="Working..."))
                

                # ----- Make sure the target user doesn't have any points in the game they rolled -----
                target_user_owns_game = True
                target_user_has_points_in_game = True

                while target_user_owns_game and target_user_has_points_in_game :
                    # grab a rollable game
                    target_user_selected_game = get_rollable_game(40, 20, "Tier 3", specific_genre=targets_genre)
                    # check to see if they own the game and if they have points in the game
                    target_user_owns_game = list(target_user_data["Owned Games"].keys()).count(target_user_selected_game) > 0
                    if(target_user_owns_game) : 
                        target_user_has_points_in_game = list(target_user_data["Owned Games"][target_user_selected_game].keys()).count("Primary Objectives") > 0
                    else : target_user_has_points_in_game = False

                # ----- Make sure the interaction user doesn't have any points in the game they rolled -----
                interaction_user_owns_game = True
                interaction_user_has_points_in_game = True

                while interaction_user_owns_game and interaction_user_has_points_in_game :
                    # grab a rollable game
                    interaction_user_selected_game = get_rollable_game(40, 20, "Tier 3", specific_genre=interactions_genre)
                    # check to see if they own the game and if they have points in the game
                    interaction_user_owns_game = list(interaction_user_data["Owned Games"].keys()).count(interaction_user_selected_game) > 0
                    if(interaction_user_owns_game) :
                        interaction_user_has_points_in_game = list(interaction_user_data["Owned Games"][interaction_user_selected_game].keys()).count("Primary Objectives") > 0
                    else : interaction_user_has_points_in_game = False
                
                games = [interaction_user_selected_game, target_user_selected_game]

                # Get the embeds
                embeds = create_multi_embed("Game Theory", 0, games, 28, interaction)

                # Edit the embeds to Game Theory's specific needs
                embeds[0].set_field_at(index=0, name="Rolled Games",
                                      value=f"<@{interaction_user_data['Discord ID']}>: {interaction_user_selected_game} ({interactions_genre})"
                                      + f"\n<@{target_user_data['Discord ID']}>: {target_user_selected_game} ({targets_genre})")
                embeds[0].set_field_at(index=0, name="Roll Requirements",
                                       value="Whoever completes their roll first will win Game Theory."
                                       + "\nGame Theory has a cooldown of one month.")
                embeds[2].set_field_at(index=1, name="Rolled by", value=f"<@{target_user_data['Discord ID']}>")
                embeds[2].set_thumbnail(url=user_b_avatar)

                embed = embeds[0]
                # Get the buttons
                await get_buttons(view, embeds)

                database_user[username_interaction]["Current Rolls"].append({"Event Name" : event, 
                                                                         "Games" : interaction_user_selected_game,
                                                                         "Partner": username_target})
                database_user[username_target]["Current Rolls"].append({"Event Name" : event,
                                                                    "Games" : target_user_selected_game,
                                                                    "Partner" : username_interaction})
            
                with open('Jasons/users2.json', 'w') as f :
                    json.dump(database_user, f, indent=4)

                # Edit the message
                await interaction.followup.edit_message(message_id=interaction.message.id, view=view, embed=embed)
            
            # ------------- END OF CALLBACK ----------------------
            
            # Edit the message
            await interaction.followup.edit_message(message_id=interaction.message.id, view=view, embed=embed)

        # ---------- END OF CALLBACK --------------
                
        # append the roll to the user's current rolls array



    return await interaction.followup.send(view=view, embed=embed)




# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------- CHECK_ROLLS COMMAND ----------------------------------------------------- # 
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
@tree.command(name="check-rolls", description="Check the active rolls of anyone on the server", guild=discord.Object(id=guild_ID))
@app_commands.describe(user="The user you'd like to check the rolls of")
async def checkRolls(interaction, user: discord.Member=None) :
    # defer the message
    print('balls')
    await interaction.response.defer()

    # if no user is provided default to sender
    if user is None :
        user = interaction.user

    #open the json file and get the data
    with open('Jasons/users2.json', 'r') as f :
        userInfo = json.load(f)

    with open('Jasons/database_name.json', 'r') as g :
        database_name_info = json.load(g)

    # iterate through the json file until you find the
    # designated user
    steam_user_name = ""
    for user_name in list(userInfo) :
        if(userInfo[user_name]["Discord ID"] == user.id) :
            steam_user_name = user_name
            break
    
    if(steam_user_name == "") : return await interaction.response.followup("This user does not exist.")
    print(steam_user_name)

    current_roll_str = get_roll_string(userInfo, steam_user_name, database_name_info, user, 'Current Rolls')
    completed_roll_str = get_roll_string(userInfo, steam_user_name, database_name_info, user, 'Completed Rolls')
    
    # make the embed that you're going to send
    embed = discord.Embed(colour=0x000000, timestamp=datetime.datetime.now())
    embed.add_field(name="User", value = "<@" + str(user.id) + ">", inline=False)
    embed.add_field(name="Current Rolls", value=current_roll_str, inline=False)
    embed.add_field(name="Completed Rolls", value=completed_roll_str, inline=False)
    embed.set_thumbnail(url=user.avatar.url)
    embed.set_footer(text="CE Assistant",
        icon_url=ce_james_icon)

    # send the embed
    await interaction.followup.send(embed=embed)




# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------------- THREADING ------------------------------------------------------------ #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper




# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------- SCRAPING --------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
@to_thread
def scrape_thread_call():
    return get_games()

@tree.command(name="scrape", description="run through each game in the CE database and grab the corresponding data", guild=discord.Object(id=guild_ID))
async def scrape(interaction):
    await interaction.response.send_message("scraping...")
    updates = await scrape_thread_call() #all_game_data(client)
    await interaction.channel.send("scraped")

    correctChannel = client.get_channel(1128742486416834570) #1135993275162050690
    await correctChannel.send('----------------------------------------- begin things --------------------------------------------')
    for dict in updates[0]:
            await correctChannel.send(file=dict['Image'], embed=dict['Embed'])

    for i in range(0, updates[1]):
        os.remove('Pictures/ss{}.png'.format(i))



# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------- CURATE ---------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
@tree.command(name="curate", description="manually activate the curator check", guild=discord.Object(id=guild_ID))
@app_commands.describe(num="Number of previous curator entries to pull")
async def curate(interaction, num : int = 0):
    await interaction.response.defer()
    await single_run(client, num)

    if num > 0:
        await interaction.followup.send('Those are the last {} curator reviews!'.format(num))
    else:
        await interaction.followup.send('There are no new curator reviews.')




# ----------------------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------- STEAM TEST COMMAND ------------------------------------------------------ #
# ----------------------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------------------------------------------------------------------------------------- #
@tree.command(name="steam-game", description="Get information on any steam game", guild=discord.Object(id=guild_ID))
async def steam_command(interaction : discord.Interaction, game_name: str):

    # Log the command
    print("Recieved steam_game command with parameter: " + game_name + ".")

    # Defer the interaction
    await interaction.response.defer(ephemeral=True)

    # Get the embed
    embed = getEmbed(game_name, interaction.user.id)
    embed.set_author(name="Requested Steam info on '" + game_name + "'")
    

    # Finally, send the embed
    await interaction.followup.send(embed=embed)

    # And log it
    print("Sent information on requested game " + game_name + ": " + embed.title +"\n")




# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------- COLORS ----------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
@tree.command(name="set-color", description="Set your name color to any color you've unlocked!", guild=discord.Object(id=guild_ID))
async def color(interaction) :
    await interaction.response.defer(ephemeral=True)

    ex_rank_role = discord.utils.get(interaction.guild.roles, name = "EX Rank")
    sss_rank_role = discord.utils.get(interaction.guild.roles, name = "SSS Rank")
    ss_rank_role = discord.utils.get(interaction.guild.roles, name = "SS Rank")
    s_rank_role = discord.utils.get(interaction.guild.roles, name = "S Rank")
    a_rank_role = discord.utils.get(interaction.guild.roles, name = "A Rank")
    b_rank_role = discord.utils.get(interaction.guild.roles, name = "B Rank")
    c_rank_role = discord.utils.get(interaction.guild.roles, name = "C Rank")
    d_rank_role = discord.utils.get(interaction.guild.roles, name = "D Rank")

    black_role = discord.utils.get(interaction.guild.roles, name = "Black")
    red_role = discord.utils.get(interaction.guild.roles, name = "Red")
    yellow_role = discord.utils.get(interaction.guild.roles, name = "Yellow")
    orange_role = discord.utils.get(interaction.guild.roles, name = "Orange")
    purple_role = discord.utils.get(interaction.guild.roles, name = "Purple")
    blue_role = discord.utils.get(interaction.guild.roles, name = "Blue")
    green_role = discord.utils.get(interaction.guild.roles, name = "Green")
    brown_role = discord.utils.get(interaction.guild.roles, name = "Brown")  
    grey_role = discord.utils.get(interaction.guild.roles, name = "Gray")


    view = discord.ui.View(timeout=60)

    black_button = (discord.ui.Button(label="⚫", disabled=(not ex_rank_role in interaction.user.roles)))
    red_button = discord.ui.Button(label = "🔴", disabled = (not sss_rank_role in interaction.user.roles
                                                             and not ex_rank_role in interaction.user.roles))
    yellow_button = (discord.ui.Button(label="🟡", disabled=(not ss_rank_role in interaction.user.roles
                                                            and not sss_rank_role in interaction.user.roles
                                                            and not ex_rank_role in interaction.user.roles)))  
    orange_button = (discord.ui.Button(label="🟠", disabled=(not s_rank_role in interaction.user.roles
                                                            and not ss_rank_role in interaction.user.roles
                                                            and not sss_rank_role in interaction.user.roles
                                                            and not ex_rank_role in interaction.user.roles)))
    purple_button = (discord.ui.Button(label="🟣", disabled=(not a_rank_role in interaction.user.roles
                                                            and not s_rank_role in interaction.user.roles
                                                            and not ss_rank_role in interaction.user.roles
                                                            and not sss_rank_role in interaction.user.roles
                                                            and not ex_rank_role in interaction.user.roles)))
    blue_button = (discord.ui.Button(label="🔵", disabled=(not b_rank_role in interaction.user.roles
                                                            and not a_rank_role in interaction.user.roles
                                                            and not s_rank_role in interaction.user.roles
                                                            and not ss_rank_role in interaction.user.roles
                                                            and not sss_rank_role in interaction.user.roles
                                                            and not ex_rank_role in interaction.user.roles)))
    green_button = (discord.ui.Button(label="🟢", disabled=(not c_rank_role in interaction.user.roles
                                                            and not b_rank_role in interaction.user.roles
                                                            and not a_rank_role in interaction.user.roles
                                                            and not s_rank_role in interaction.user.roles
                                                            and not ss_rank_role in interaction.user.roles
                                                            and not sss_rank_role in interaction.user.roles
                                                            and not ex_rank_role in interaction.user.roles)))
    brown_button = (discord.ui.Button(label="🟤", disabled=(not d_rank_role in interaction.user.roles
                                                            and not c_rank_role in interaction.user.roles
                                                            and not b_rank_role in interaction.user.roles
                                                            and not a_rank_role in interaction.user.roles
                                                            and not s_rank_role in interaction.user.roles
                                                            and not ss_rank_role in interaction.user.roles
                                                            and not sss_rank_role in interaction.user.roles
                                                            and not ex_rank_role in interaction.user.roles)))
    grey_button = discord.ui.Button(label="⚪")
    
    async def black_callback(interaction) : return await assign_role(interaction, black_role)
    async def red_callback(interaction) : return await assign_role(interaction, red_role)
    async def yellow_callback(interaction) : return await assign_role(interaction, yellow_role)
    async def orange_callback(interaction) : return await assign_role(interaction, orange_role)
    async def purple_callback(interaction) : return await assign_role(interaction, purple_role)
    async def blue_callback(interaction) : return await assign_role(interaction, blue_role)
    async def green_callback(interaction) : return await assign_role(interaction, green_role)
    async def brown_callback(interaction) : return await assign_role(interaction, brown_role)
    async def grey_callback(interaction) : return await assign_role(interaction, grey_role)

    black_button.callback = black_callback
    red_button.callback = red_callback
    yellow_button.callback = yellow_callback
    orange_button.callback = orange_callback
    purple_button.callback = purple_callback
    blue_button.callback = blue_callback
    green_button.callback = green_callback
    brown_button.callback = brown_callback
    grey_button.callback = grey_callback

    view.add_item(black_button)
    view.add_item(red_button)
    view.add_item(yellow_button)
    view.add_item(orange_button)
    view.add_item(purple_button)
    view.add_item(blue_button)
    view.add_item(green_button)
    view.add_item(brown_button)
    view.add_item(grey_button)

    async def assign_role(interaction, role) :
        if(role in interaction.user.roles) : return await interaction.response.edit_message(embed=discord.Embed(title = f"You already have the {role.name} role!", color = role.color))
        
        await (interaction.user.add_roles(role))

        if(black_role in interaction.user.roles and not(role == black_role)) : await interaction.user.remove_roles(black_role)
        if(red_role in interaction.user.roles and not(role == red_role)) : await interaction.user.remove_roles(red_role)
        if(yellow_role in interaction.user.roles and not(role == yellow_role)) : await interaction.user.remove_roles(yellow_role)
        if(orange_role in interaction.user.roles and not(role == orange_role)) : await interaction.user.remove_roles(orange_role)
        if(purple_role in interaction.user.roles and not(role == purple_role)) : await interaction.user.remove_roles(purple_role)
        if(blue_role in interaction.user.roles and not(role == blue_role)) : await interaction.user.remove_roles(blue_role)
        if(green_role in interaction.user.roles and not(role == green_role)) : await interaction.user.remove_roles(green_role)
        if(brown_role in interaction.user.roles and not(role == brown_role)) : await interaction.user.remove_roles(brown_role)
        if(grey_role in interaction.user.roles and not(role == grey_role)) : await interaction.user.remove_roles(grey_role)

        return await interaction.response.edit_message(embed=discord.Embed(title = f"You have recieved the {role.name} role!", color=role.color))
        
    embed = discord.Embed(title="COLORS", description="choose your colors wisely.")
    await interaction.followup.send(embed=embed, view=view, ephemeral=True)





# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------TEST COMMAND-------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
@tree.command(name="test", description="test", guild=discord.Object(id=guild_ID))
async def test(interaction : discord.Interaction, role : discord.Role) :
    await interaction.response.defer()

    casino_channel = client.get_channel(811286469251039333)
    
    await roll_failed(ended_roll_name='Triple Threat', casino_channel=casino_channel, user_name='d7cb0869-5ed9-465c-87bf-0fb95aaebbd5')


    return await interaction.followup.send(embed=discord.Embed(title="this is the test command"))
    print(role.id)
    
    embed = discord.Embed(title="__Celeste__ has been updadted on the site", description="' ∀MAZING' increased from 120 :CE_points: ➡ 125 :CE_points: points: Achievements '∀NOTHER ONE', and '∀DVENTED' removed New Primary Objective '∀WOKEN' added: 30 points :CE_points: Clear the Pandemonic Nightmare stage, and clear Hymeno Striker on AKASCHIC+RM difficulty.")
    embed.set_thumbnail(url=ce_hex_icon)
    embed.set_image(url="https://media.discordapp.net/attachments/1128742486416834570/1133903990090895440/image.png?width=1083&height=542")
    embed.set_author(name="Challenge Enthusiasts", icon_url="https://cdn.akamai.steamstatic.com/steamcommunity/public/images/apps/504230/04cb7aa0b497a3962e6b1655b7fd81a2cc95d18b.jpg")

    return await interaction.followup.send(embed=embed)





# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------- REGISTRATION COMMAND----------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
@tree.command(name="register", description="Register yourself in the CE Assistant database to unlock rolls.", guild=discord.Object(id=guild_ID))
@app_commands.describe(ce_id="Please use the link to your personal CE user page!")
async def register(interaction : discord.Interaction, ce_id: str) :
    await interaction.response.defer(ephemeral=True) # defer the message
    
    #Open the user database
    with open('Jasons/users2.json', 'r') as dbU :
        database_user = json.load(dbU)

    # Set up total_points to calculate rank
    total_points = 0

    # Make sure the input is a valid CE-ID
    print(f"Input = {ce_id}")
    if(ce_id[:20:] == "https://cedb.me/user" and len(ce_id) >= 29 and (ce_id[29] == '-')) :
        if(ce_id[(len(ce_id)-5)::] == "games") : ce_id = ce_id[21:(len(ce_id)-6):]
        else : ce_id = ce_id[21::]
    else: return await interaction.followup.send(f"'{ce_id}' is not a valid user link. Please try again or contact <@413427677522034727> for assistance.")
    print(f"Working ID = {ce_id}")

    # Make sure user isn't already registered
    for user in database_user :
        if(database_user[user]["Discord ID"] == interaction.user.id) : return await interaction.followup.send("You are already registered in the database!")
        elif(database_user[user]["CE ID"] == ce_id) : return await interaction.followup.send(f"This CE-ID is already registered to <@{database_user[user]['Discord ID']}>, silly!")
    
    # Grab user info from CE API
    response = requests.get(f"https://cedb.me/api/user/{ce_id}")
    user_ce_data = json.loads(response.text)

    # Set up the user's JSON file
    user_dict = {
        ce_id : {
            "CE ID" : ce_id,
            "Discord ID" : interaction.user.id,
            "Rank" : "",
            "Reroll Tickets" : 0,
            "Casino Score" : 0,
            "Owned Games" : {},
            "Cooldowns" : {},
            "Current Rolls" : [],
            "Completed Rolls" : []
        }
    }

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
    if total_points < 50 : rank = "Rank E"
    elif total_points < 250 : rank = "Rank D"
    elif total_points < 500 : rank = "Rank C"
    elif total_points < 1000 : rank = "Rank B"
    elif total_points < 2500 : rank = "Rank A"
    elif total_points < 5000 : rank = "Rank S"
    elif total_points < 7500 : rank = "Rank SS"
    elif total_points < 10000 : rank = "Rank SSS"
    else : rank = "Rank EX"

    user_dict[ce_id]["Rank"] = rank

    all_events = ["One Hell of a Day", "One Hell of a Week", "One Hell of a Month", "Two Week T2 Streak", "Two 'Two Week T2 Streak' Streak",
                  "Never Lucky", "Triple Threat", "Let Fate Decide", "Fourward Thinking", "Russian Roulette", "Destiny Alignment",
                  "Soul Mates", "Teamwork Makes the Dream Work", "Winner Takes All", "Game Theory"]

    # Check and see if the user has any completed rolls
    if(list(user_dict[ce_id]["Owned Games"].keys()).count("- Challenge Enthusiasts -") > 0) :
        x=0
        
        for event_name in all_events :
            if(list(user_dict[ce_id]["Owned Games"]["- Challenge Enthusiasts -"]["Community Objectives"].keys()).count(event_name) > 0) :
                x=0
                user_dict[ce_id]["Completed Rolls"].append({"Event Name" : event_name})

    # Add the user file to the database
    database_user.update(user_dict)

    # Dump the data
    with open('Jasons/users2.json', 'w') as f :
        json.dump(database_user, f, indent=4)

    # Create confirmation embed
    embed = discord.Embed(
        title="Registered!",
        color=0x000000,
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="Information", value=f"You have been registered in the CE Assistant database. Your CE-ID is {ce_id}"
                    + f". You may now use all aspects of this bot.")
    embed.set_author(name="Challenge Enthusiasts", url="https://example.com")
    embed.set_footer(text="CE Assistant",
        icon_url=ce_james_icon)
    embed.set_thumbnail(url=interaction.user.avatar)

    registered_role = discord.utils.get(interaction.guild.roles, name = "registered")
    #await interaction.user.add_roles(registered_role)

    # Send a confirmation message
    await interaction.followup.send(embed=embed)




@tree.command(name="update", description="Update your stats in the CE Assistant database.", guild=discord.Object(id=guild_ID))
async def update(interaction : discord.Interaction) :

    # Defer the message
    await interaction.response.defer()

    str = update_p(interaction.user.id)

    if str == "Unregistered" : return await interaction.followup.send("You have not registered. Please use /register with the link to your CE page.")
    elif(str == "Updated") :
        # Create confirmation embed
        embed = discord.Embed(
            title="Updated!",
            color=0x000000,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="Information", value=f"Your information has been updated in the CE Assistant database.")
        embed.set_author(name="Challenge Enthusiasts", url="https://example.com")
        embed.set_footer(text="CE Assistant",
            icon_url=ce_james_icon)
        embed.set_thumbnail(url=interaction.user.avatar)

        # Send a confirmation message
        await interaction.followup.send(embed=embed)


# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------- REASON COMMAND----------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
@tree.command(name="add-reason", description="Add reason to embed", guild=discord.Object(id=guild_ID))
@app_commands.describe(reason="The string you'd like to add under the 'Reason' banner on a site-addition embed")
@app_commands.describe(embed_id="The message ID of the embed you'd like to change the reason of")
async def reason(interaction : discord.Interaction, reason : str, embed_id : str) :

    # grab the site additions channel
    # TODO: update this in the CE server
    site_additions_channel = client.get_channel(1128742486416834570)

    # try to get the message
    try :
        message = await site_additions_channel.fetch_message(int(embed_id))

    # if it errors, message is not in the site-additions channel
    except :
        return await interaction.response.send_message("This message is not in the <#1128742486416834570> channel.")
    
    # grab the embed
    embed = message.embeds[0]

    # try and see if the embed already has a reason field
    try :
        if(embed.fields[len(embed.fields)-1].name == "Reason") :
            embed.set_field_at(index=len(embed.fields)-1, name="Reason", value=reason)
    
    # if it errors, then just add a reason field
    except :
        embed.add_field(name="Reason", value=reason, inline=False)

    # edit the message
    await message.edit(embed=embed)

    # and send a response to the original interaction
    await interaction.response.send_message("worked", ephemeral=True)



# ----------------------------------- LOG IN ----------------------------
@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=guild_ID))
    print("Ready!")
    await loop.start(client)

client.run(discord_token)