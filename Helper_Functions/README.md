# Helper Function Files

This folder is filled with helper functions that `main.py` uses. Here's a brief description of all of them.

### Scheduler.py
This file is no longer used, but it previously held functions for getting code to run at certain times.

### buttons.py
This file held functions relating to `discord.ui.Button`s. The function `get_buttons()` takes in a list of `discord.Embed`s and a `discord.ui.View` and attaches buttons to the `View` that act as scrolling through the `Embed`s.
Additionally, the function `get_genre_buttons()` takes in a lot of parameters and works with the backend to select a game in the genre that was clicked by the user.

### create_embed.py
This file holds all the functions for setting up `discord.Embed`s. `getEmbed()` takes in a CE ID and returns an `Embed` with information on it. `create_multi_embed()` uses this function to return a list of `Embed`s for all the rolled games for a casino event.

### end_time.py
Even we aren't sure what we thought was gonna happen here, but it is now a whole lot of commented out code, with one additional function `months_to_days()` that, accurately, takes in a number of months and returns the number of days between now and that-many-months months away. Thank you Schmole for writing this!

### mongo_silly.py
This file serves as the hub for all MongoDB related interaction. The main functions, `get_mongo()` and `dump_mongo()` do exactly what they say - retrieve data, or set data. It also houses a lot of random functions, like `get_unix()` (used for getting the unix timestamp), `timestamp_to_unix()` (converts the CE timestamp to a unix timestamp), and more.

### os.py
This file holds the restart function, which restarts whatever computer the bot is running on and restarts the program.

### roll_string.py
This file holds only one function, and its to get the string that goes in an `Embed` detailing all of the user's completed and current rolls.

### rollable_games.py
This one is pretty self explanatory. Two functions live here - `get_rollable_game()`, which takes in a lot of parameters and returns a rollable game, and `get_rollable_game_from_list()`, which of course gets a rollable game from a list.

### site_achievements.py
This unfinished function would have returned a dictionary with a list of all the site achievements and which ones a user had earned. Never got around to finishing this.

### spreadsheet.py
This file retrieves data from a Google Sheet and stores it locally. This is used to retrieve [Schmole's SteamHunters data](https://docs.google.com/spreadsheets/d/1oAUw5dZdqZa1FWqrBV9MQQTr8Eq8g33zwEb49vk3hrk/edit?usp=sharing) or the [Discord role information](https://docs.google.com/spreadsheets/d/1BIxKr3vqiQ909u1xCZbJR-RgDdPBocoMafy0Ov7ep04/edit?usp=sharing).

### update.py
The ugliest function written for this project, this file goes through a user's data on CE and compares it with its corresponding local MongoDB data. It assembles a list of messages to be sent to a log channel, and goes through all of their roll events to determine if they've expired, been won, or are still in progress.
