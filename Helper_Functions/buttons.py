import discord
from Helper_Functions.create_embed import create_multi_embed
from Helper_Functions.rollable_games import get_rollable_game


# -------------------------------------------------------------------------------------------------- #
# -------------------------------------------- BUTTONS --------------------------------------------- #
# -------------------------------------------------------------------------------------------------- #

async def get_buttons(view, embeds):
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

async def get_genre_buttons(view, completion_time, price_limit, tier_number, event_name, time_limit, cooldown_time, num_of_games) :
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

    async def callback(interaction, genre_name):
        await interaction.response.defer()
        print(interaction)
        i=0
        while i < num_of_games :
            games.append(get_rollable_game(completion_time, price_limit, tier_number, genre_name))
            i+=1
        view.clear_items()
        embeds = create_multi_embed(event_name, time_limit, games, cooldown_time, interaction)
        await get_buttons(view, embeds)
        await interaction.followup.edit_message(embed=embeds[0], view=view, message_id=interaction.message.id)

    buttons[0].callback = AC_callback
    buttons[1].callback = AR_callback
    buttons[2].callback = BH_callback
    buttons[3].callback = FP_callback
    buttons[4].callback = PF_callback
    buttons[5].callback = ST_callback        

