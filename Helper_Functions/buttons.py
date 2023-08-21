import time
import discord
from Helper_Functions.create_embed import create_multi_embed
from Helper_Functions.rollable_games import get_rollable_game
import json
import datetime
from datetime import timedelta

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

    view.on_timeout = disable()

async def get_genre_buttons(view : discord.ui.View, completion_time, price_limit, tier_number, event_name, time_limit, cooldown_time, num_of_games, user_id, reroll : bool) :
    games = []
    genres = ["Action", "Arcade", "Bullet Hell", "First-Person", "Platformer", "Strategy"]
    buttons = []
    i=0
    for genre in genres :
        print(genre)
        buttons.append(discord.ui.Button(label=genre, style=discord.ButtonStyle.gray))
        view.add_item(buttons[i])
        i+=1

    async def AC_callback(interaction) : return await callback(interaction, "Action")
    async def AR_callback(interaction) : return await callback(interaction, "Arcade")
    async def BH_callback(interaction) : return await callback(interaction, "Bullet Hell")
    async def FP_callback(interaction) : return await callback(interaction, "First-Person")
    async def PF_callback(interaction) : return await callback(interaction, "Platformer")
    async def ST_callback(interaction) : return await callback(interaction, "Strategy")

    async def callback(interaction : discord.Interaction, genre_name):
        await interaction.response.defer()
        
        if interaction.user.id != user_id : return

        view.clear_items()
        
        await interaction.followup.edit_message(embed=discord.Embed(title="working..."), view=view, message_id=interaction.message.id)

        i=0
        while i < num_of_games :
            games.append(get_rollable_game(completion_time, price_limit, tier_number, specific_genre =genre_name))
            i+=1
       

        embeds = create_multi_embed(event_name, time_limit, games, cooldown_time, interaction)
        await get_buttons(view, embeds)
        await interaction.followup.edit_message(embed=embeds[0], view=view, message_id=interaction.message.id)

        with open("Jasons/users2.json", "r") as u :
            database_user = json.load(u)
        
        for user in database_user :
            if(database_user[user]['Discord ID'] == user_id) : 
                target_user = user
                break
        
        roll_num = 0
        
        for current_roll in database_user[target_user]["Current Rolls"] :
            if current_roll["Event Name"] == event_name : break
            roll_num +=1

        if not reroll : 
            database_user[target_user]["Current Rolls"][roll_num] = ({"Event Name" : event_name, 
                                                    "End Time" : int(time.mktime((datetime.datetime.now()+timedelta(time_limit)).timetuple())),
                                                    "Games" : games})
        
        elif reroll :
            c_nums = []
            for index, c_roll in enumerate(database_user[target_user]["Current Rolls"]) :
                if c_roll["Event Name"] == event_name :
                    c_nums.append(index)
                    

            print(c_nums)
            
            if c_nums == [] : return await interaction.followup.send('you havent rolled this game. except i should have cleared that already. something is wrong')

            if len(c_nums) > 1 : 
                del database_user[target_user]["Current Rolls"][c_nums[1]]

            c_num = c_nums[0]

            database_user[target_user]['Current Rolls'][c_num] = ({
                "Event Name" : event_name,
                "End Time" : database_user[target_user]["Current Rolls"][c_num]["End Time"],
                "Games" : games
            })

        # dump the info
        with open('Jasons/users2.json', 'w') as f :
            json.dump(database_user, f, indent=4)

    buttons[0].callback = AC_callback
    buttons[1].callback = AR_callback
    buttons[2].callback = BH_callback
    buttons[3].callback = FP_callback
    buttons[4].callback = PF_callback
    buttons[5].callback = ST_callback        

