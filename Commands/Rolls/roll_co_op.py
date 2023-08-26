import discord
import json

from Helper_Functions.rollable_games import *
from Helper_Functions.create_embed import *
from Helper_Functions.buttons import *


async def co_op_command(interaction : discord.Interaction, event, partner : discord.User, reroll : bool) :

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

    # Make sure the user doesn't select themselves
    if interaction.user.id == partner.id : return await interaction.followup.send("You cannot enter a co-op roll with yourself.")

    # Grab the information for both users
    for user in database_user :
        if database_user[user]["Discord ID"] == interaction.user.id : 
            interaction_user_data = database_user[user]
            int_user_id = user
        if database_user[user]["Discord ID"] == partner.id : 
            target_user_data = database_user[user]
            part_user_id = user

    # Make sure both users are registered in the database,
    # and return a message if they're not
    if interaction_user_data == "" : return await interaction.followup.send("You are not registered in the CE Assistant database.")
    if target_user_data == "" : return await interaction.followup.send(f"<@{partner.id}> is not registered in the CE Assistant database.")
    
    # check to see if either are pending or if either are currently participating...
    for eventInfo in database_user[int_user_id]['Current Rolls'] :
        #TODO: have different errors if someone tries to go again during pending and if someone tries to reroll while pending
        if(eventInfo['Event Name'] == event and eventInfo['Games'] == ['pending...']) : return await interaction.followup.send('Please wait 10 minutes in between rolling for the same event!')
        if((eventInfo['Event Name'] == event) and event != "Fourward Thinking" and not reroll) : return await interaction.followup.send(embed=discord.Embed(title=f"You are already participating in {event}!"))
    
    for eventInfo in database_user[part_user_id]['Current Rolls'] :
        #TODO: have different errors if someone tries to go again during pending and if someone tries to reroll while pending
        if(eventInfo['Event Name'] == event and eventInfo['Games'] == ['pending...']) : return await interaction.followup.send('Please wait 10 minutes in between rolling for the same event!')
        if((eventInfo['Event Name'] == event) and event != "Fourward Thinking" and not reroll) : return await interaction.followup.send(embed=discord.Embed(title=f"You are already participating in {event}!"))

    database_user[int_user_id]['Current Rolls'].append({"Event Name" : event, "End Time" : int(time.mktime((datetime.datetime.now()+timedelta(minutes=10)).timetuple())), "Games" : ["pending..."]})
    database_user[part_user_id]['Current Rolls'].append({"Event Name" : event, "End Time" : int(time.mktime((datetime.datetime.now()+timedelta(minutes=10)).timetuple())), "Games" : ["pending..."]})

    with open('Jasons/users2.json', 'w') as f :
        json.dump(database_user, f, indent=4)

    with open('Jasons/users2.json', 'r') as f :
        database_user = json.load(f)

    # Make sure both users are registered in the database
    if interaction_user_data == "" : return await interaction.followup.send("You are not registered in the CE Assistant database.")
    if target_user_data == "" : return await interaction.followup.send(f"<@{partner.id}> is not registered in the CE Assistant database.")
    
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------- Destiny Alignment ---------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #

    if(event == "Destiny Alignment") :

        # Make sure both users are the same rank
        if(interaction_user_data["Rank"] != target_user_data["Rank"]) : return await interaction.followup.send("You are not the same tier!")

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

            i_num = 0
            for roll_i in database_user[int_user_id]["Current Rolls"] :
                if(roll_i["Games"] == ['pending...']) : break
                i_num += 1
            
            t_num = 0
            for roll_t in database_user[int_user_id]["Current Rolls"] :
                if(roll_t["Games"] == ['pending...']) : break
                t_num += 1
            
            database_user[int_user_id]["Current Rolls"][i_num] = ({
                "Event Name" : event,
                "Partner" : target_user_data["CE ID"],
                "Games" : [target_user_selected_game]
            })

            database_user[part_user_id]["Current Rolls"][t_num] = ({
                "Event Name" : event,
                "Partner" : interaction_user_data["CE ID"],
                "Games" : [interaction_user_selected_game]
            })

            with open('Jasons/users2.json', 'w') as dbU :
                json.dump(database_user, dbU, indent=4)

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
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------- Soul Mates ------------------------------------------------------------ #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #

    elif(event == "Soul Mates") :
        embed = discord.Embed(title="Soul Mates", timestamp=datetime.datetime.now())
        embed.add_field(name="Roll Requirements", value="You and your partner must agree on a tier. A game will be rolled for both of you," 
                                                        + "and you must **both** complete it in the time constraint listed below.")
        embed.add_field(name="Tier Choices",
                        value=":one: : 48 Hours\n:two: : 10 Days\n:three: : One Month\n:four: : Two Months\n:five: : Forever")
        embed.set_thumbnail(url = ce_mountain_icon)
        embed.set_author(name="Challenge Enthusiasts")
        embed.set_footer(text="CE Assistant", icon_url=ce_mountain_icon)

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

                end_db = {
                    "Tier 1" : timedelta(2),
                    "Tier 2" : timedelta(10),
                    "Tier 3" : timedelta(28),
                    "Tier 4" : timedelta(56)
                }

                i_num = 0
                for roll_i in database_user[int_user_id]["Current Rolls"] :
                    if(roll_i["Games"] == ['pending...']) : break
                    i_num += 1
                
                t_num = 0
                for roll_t in database_user[int_user_id]["Current Rolls"] :
                    if(roll_t["Games"] == ['pending...']) : break
                    t_num += 1

                if(tier_num == "Tier 5") : 

                    database_user[int_user_id]["Current Rolls"][i_num] = ({
                        "Event Name" : event,
                        "Partner" : target_user_data["CE ID"],
                        "Games" : [game]
                    })

                    database_user[part_user_id]["Current Rolls"][t_num] = ({
                        "Event Name" : event,
                        "Partner" : interaction_user_data["CE ID"],
                        "Games" : [game]
                    })

                
                else :
                
                    database_user[int_user_id]["Current Rolls"][i_num] = ({
                        "Event Name" : event,
                        "Partner" : target_user_data["CE ID"],
                        "End Time" : int(time.mktime((datetime.datetime.now()+end_db[tier_num]).timetuple())),
                        "Games" : [game]
                    })

                    database_user[part_user_id]["Current Rolls"][t_num] = ({
                        "Event Name" : event,
                        "Partner" : interaction_user_data["CE ID"],
                        "End Time" : int(time.mktime((datetime.datetime.now()+end_db[tier_num]).timetuple())),
                        "Games" : [game]
                    })

                with open('Jasons/users2.json', 'w') as dbU :
                    json.dump(database_user, dbU, indent=4)

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
            - this should include notes on how long each tier would have to complete the roll
        - send another confirmation message 
            - only user B should be allowed to respond
        - get rollable games for whatever tier they asked for
            - game must be rerolled if either user has any points in the game

        """
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------- Teamwork Makes the Dream Work -------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
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


        # --------------------------------------- Agree Button --------------------------------
        async def agree_callback(interaction) :
            await interaction.response.defer()
            # make sure only target can use button
            if interaction.user.id != target_user_data["Discord ID"] : return

            # clear the agree and deny buttons
            view.clear_items()
            
            games = []
            # Let the user know the function is working...
            await interaction.followup.edit_message(embed=discord.Embed(title="Working..."), view=view, message_id=interaction.message.id)

            # -------------- Grab the games --------------
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


                # ----- Append the game -----
                games.append(game)
                
                # Increase the count
                i+=1
            #}


            # ----------- Get embeds ---------------------
            embeds = create_multi_embed("Teamwork Makes the Dream Work", 28, games, (28*3), interaction)

            # ------ Get page buttons -------
            await get_buttons(view, embeds)

            i_num = 0
            for roll_i in database_user[int_user_id]["Current Rolls"] :
                if(roll_i["Games"] == ['pending...']) : break
                i_num += 1
            
            t_num = 0
            for roll_t in database_user[int_user_id]["Current Rolls"] :
                if(roll_t["Games"] == ['pending...']) : break
                t_num += 1

            database_user[int_user_id]["Current Rolls"][i_num] = ({
                "Event Name" : event,
                "Partner" : target_user_data["CE ID"],
                "Games" : games
            })

            database_user[part_user_id]["Current Rolls"][t_num] = ({
                "Event Name" : event,
                "Partner" : interaction_user_data["CE ID"],
                "Games" : games
            })

            with open('Jasons/users2.json', 'w') as dbU :
                json.dump(database_user, dbU, indent=4)

            # ------ and edit the message. ------
            return await interaction.followup.edit_message(embed=embeds[0], view=view, message_id=interaction.message.id)
        
        # ---------------------------------------- Deny Button ----------------------------------
        async def deny_callback(interaction) :
            await interaction.response.defer()
            if interaction.user.id != target_user_data['Discord ID'] : return
            view.clear_items()
            return await interaction.followup.edit_message(message_id=interaction.message.id, embed=discord.Embed(title="Roll denied."))
        
        # ---------------------------------------- Set the callbacks ------------------------------
        agree_button.callback = agree_callback
        deny_button.callback = deny_callback
        
        
    
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------ Winner Takes All ------------------------------------------------------------ #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
    elif(event == "Winner Takes All") :
        embed = discord.Embed(title="Winner Takes All", timestamp=datetime.datetime.now())
        embed.add_field(name="Roll Requirements", value="You and your partner must agree on a tier. A game will be rolled for both of you." 
                                                        + " The first to complete all Primary Objectives will win.")
        embed.set_thumbnail(url = ce_mountain_icon)
        embed.set_author(name="Challenge Enthusiasts")
        embed.set_footer(text="CE Assistant", icon_url=ce_mountain_icon)

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
                embed.set_field_at(index=1, name="Rolled by", value=f"<@{interaction_user_data['Discord ID']}> and <@{target_user_data['Discord ID']}>")
                embed.add_field(name="Tier", value=database_name[game]["Tier"])
                embed.add_field(name="Completion", value="When you have completed, submit your proof to <#811286469251039333>. The first to do so wins.")

                i_num = 0
                for roll_i in database_user[int_user_id]["Current Rolls"] :
                    if(roll_i["Games"] == ['pending...']) : break
                    i_num += 1
                
                t_num = 0
                for roll_t in database_user[int_user_id]["Current Rolls"] :
                    if(roll_t["Games"] == ['pending...']) : break
                    t_num += 1

                database_user[int_user_id]["Current Rolls"][i_num] = ({
                    "Event Name" : event,
                    "Partner" : target_user_data["CE ID"],
                    "Games" : [game]
                })

                database_user[part_user_id]["Current Rolls"][t_num] = ({
                    "Event Name" : event,
                    "Partner" : interaction_user_data["CE ID"],
                    "Games" : [game]
                })

                with open('Jasons/users2.json', 'w') as dbU :
                    json.dump(database_user, dbU, indent=4)

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

# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------- Game Theory ------------------------------------------------------------ #
# ---------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #
    elif(event == "Game Theory") :
        embed = discord.Embed(title="Game Theory", timestamp=datetime.datetime.now())
        embed.add_field(name="Roll Requirements", value="You and your partner will secretly select a genre for the other person. " 
                                                        + "A T3 in your selected genre will be rolled for your partner. The first to complete theirs wins!")
        embed.add_field(name="Genre Choices",
                        value=f"<@{interaction.user.id}>, please select the genre for the other user.")
        embed.set_thumbnail(url = ce_mountain_icon)
        embed.set_author(name="Challenge Enthusiasts")
        embed.set_footer(text="CE Assistant", icon_url=ce_mountain_icon)

        buttons = []
        i = 0

        genres = ["Action", "Arcade", "Bullet Hell", "First-Person", "Platformer", "Strategy"]

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

            async def game_theory_callback_2(interaction : discord.Interaction, interactions_genre) :
                await interaction.response.defer()
                if interaction.user.id != target_user_data["Discord ID"] : return

                view.clear_items()
                

                # ----- Make sure the target user doesn't have any points in the game they rolled -----
                target_user_owns_game = True
                target_user_has_points_in_game = True

                while target_user_owns_game and target_user_has_points_in_game :
                    # grab a rollable game
                    target_user_selected_game = get_rollable_game(40, 20, "Tier 3", specific_genre=targets_genre)

                    # check to see if they own the game and if they have points in the game
                    target_user_owns_game = list(target_user_data["Owned Games"].keys()).count(target_user_selected_game) > 0
                    if(target_user_owns_game) : target_user_has_points_in_game = list(target_user_data["Owned Games"][target_user_selected_game].keys()).count("Primary Objectives") > 0
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
                embeds[2].set_thumbnail(url=partner.display_avatar)

                embed = embeds[0]
                # Get the buttons
                await get_buttons(view, embeds)

                database_user[int_user_id]["Current Rolls"].append({
                    "Event Name" : event,
                    "Partner" : target_user_data["CE ID"],
                    "Games" : [interaction_user_selected_game]
                })

                database_user[part_user_id]["Current Rolls"].append({
                    "Event Name" : event,
                    "Partner" : interaction_user_data["CE ID"],
                    "Games" : [target_user_selected_game]
                })

                with open('Jasons/users2.json', 'w') as dbU :
                    json.dump(database_user, dbU, indent=4)

                # Edit the message
                await interaction.followup.edit_message(message_id=interaction.message.id, view=view, embed=embed)
            
            # Edit the message
            await interaction.followup.edit_message(message_id=interaction.message.id, view=view, embed=embed)
                


    return await interaction.followup.send(view=view, embed=embed)