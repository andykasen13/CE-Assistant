# CE-Bot
This discord bot, using `discord.py` and made by myself and @TheronBoozer, handles automation in the Challenge Enthusiasts Discord Server.

## Random Rolls
The Challenge Enthusiasts host events that involved randomly rolling games on Steam for bonuses outside of their normal point values.

For example, if you roll One Hell of a Day, the bot will return an easy game - and you have 24 hours to complete it. If you succeed, you will be awarded a Community Objective on your profile.

### `/roll`
`/roll` takes in one parameter: the name of the event. This will return a (multi-page) embed detailing the game(s) and event you've rolled in.

### `/check_rolls`
`/check_rolls` takes in one parameter: a discord user. If no parameter is provided, the sender is chosen as the user. This sends back an embed detailing all current (and completed) rolls for that user.

### DM Reminders
Users can ask the bot to send them reminders on their rolls.

### Cooldowns
Each event has a specific cooldown (only if the roll is failed) and the bot will ping users when their cooldown ends.

