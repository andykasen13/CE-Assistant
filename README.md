# CE-Assistant
i'm gonna try and make a discord bot for challenge enthusiasts
this is version two, using discord.py

things i want to try and get working


## rolls
i want to be able to handle rolls of all kind - single and co-op, but co-op might be rough - and store them under the user

this way, you can see all the rolls you have active

the issue with this is it requires access to all rollable games - and laura has built an incredible system that i have no idea how to even begin to understand

but i will try!

the idea is that you can do `/roll` and then select the events to choose from (including monthly rolls for the 2023 event, we shall see if i can get that working)

example: `/roll two week t2 streak`, and this should give you a random game (within the limits jarvis (rip) created), and store it under the user.

and you should also be able to dm the bot and ask it which rolls you have active 

example: `/roll my rolls`, this should output a numbered list of the rolls you have active, the start date and end date, and how much time you have left

it should also dm you at certain intervals, like one week left, three days, one day.

ideally this should link to the site page for each game and oh man it would be cool to have it send you the objectives and if you've completed the objective have it in green and otherwise keep it white

obviously it should also tell you how much longer you have left for each roll

idk how this would look but it should also show you the cooldowns

if somehow i become a coding god in the next month it would be great if i could get it to have a website, like a google sheet or something that just displays this all in one place so you can see other people's stats but that is quite likely not to happen. if this could automate that google sheet tho, that would be so sick

this would be the greatest thing this bot can do i think. it would take a lot of strain off of mods (rip jarvis)

## announcements

i also want this bot to send whenever there is an update to the site, whether it be a game addition, game edit, or removal altogether.

obviously mods like folkius (ily folkius) should still be able to send announcemenets whenever necessary, but this would hopefully take one step off of mods

## other silly little things

- it should store and be able to return the site image, both jpg and gif form
- music implementation would be sick but this is not an ideal for now
- it should be able to open and close recommendations for the first week of every month (this may not be a good idea)
- maybe you could be able to tell it that you are looking for a partner for a co-op achievement?
- should be able to change color to any color you've already unlocked. this is already possible manually but should be automated. should also change tier role based on current tier.
- check on female empowerment or zookeeper status

## housekeeping reminders
- ~~reminder to myself that t0 games must have separate announcements~~
- reminder to myself that upon booting up the bot, it should go through all of the users in the server and update their information in my `users.json` file
- also reminder to myself to fix the price to check if it's on sale right now
- reminder to try and incorporate buttons to ask if they want to use a reroll ticket
- ~~once an hour, i need to parse through the website and determine if there are any new games to add to my list of rollable games - and also check to see if all info i have currently checks out, in case i need to take something off the rollable games list~~
- ~~reminder that if someone tries to roll an event that they have running already~~ or are on cooldown for, DON'T LET THEM.
- ~~reminder to use beautifulsoup to check steamhunters.com for eligibility!~~
- ~~reminder to also use beautifulsoup to get the curator thing to work :)~~
- ~~make buttons work~~
- ~~create JSON modules for all users in server~~
- ~~if the user does not exist, don't try and send them the `/check_rolls` or shit will error a lot~~
- ~~decide if you want to include objectives in the initial roll message (current me thinks no but should be included in the `/check_rolls` command)~~
- co-op rolls 😩
- indicate if the game is on sale
- think about switching the icon of the `/roll` command to the user's avatar
- make sure that you don't roll the same game for any multi-game rolls
- add error checking. this will be so so annoying but will be great for preventing the bot from just shutting down
- ~~currently the bot keeps track of if someone has completed a game in the `users.json` file but will eventually do that on its own in an 'owned_games' section in the same file. make sure that when that happens you switch it.~~

## checking on rolls
### if the user completes the roll:
- user uses /update
- runs command to go through each game in "current rolls"
- if they are all completed, send a message saying they've completed the roll (and alert an admin)
- and also move the roll out of "current rolls" and into "completed rolls"
- unless of course it is fourward thinking

### if the user fails the roll:
- have a command that logs all times to check
- at that designated time, if the user has not completed the roll, update their local database for them. if they've completed the game, see above. if they haven't, send a message saying they failed the roll (probably ephemeral), add the game to cooldown if necessary, and delete it from their "current rolls"

## imports

You will need to `pip install` the following:

- `discord` (discord)
- `selenium` (web interaction)
- `pillow` (picture taking)
- `requests` (steam and CE api access)
- `bs4` (html sorting)
- `apscheduler` (scheduling roll-ends)
- `pymongo` and `motor` (accessing databases)
- `chromedriver_binary` (don't ask bruh i have no idea)
- `webdriver_manager` (sets correct webdriver for selenium)

`pip install discord selenium pillow requests bs4 apscheduler pymongo motor chromedriver_binary webdriver_manager`


# CE-Assistant
This discord bot, using `discord.py` and made by myself and @TheronBoozer, handles automation in the Challenge Enthusiasts Discord Server.

## Random Rolls
The Challenge Enthusiasts host events that involved randomly rolling games on Steam for bonuses outside of their normal point values.

For example, if you roll One Hell of a Day, the bot will return an easy game - and you have 24 hours to complete it. If you succeed, you will be awarded a Community Objective on your profile.

### `/solo-roll`
`/solo-roll` takes in one parameter: the name of the event. This will return a (multi-page) embed detailing the game(s) and event you've rolled in.

### `/co-op-roll`
`/co-op-roll` takes in two parameters: the name of the event and the person you'd like 

### `/check_rolls`
`/check_rolls` takes in one parameter: a discord user. If no parameter is provided, the sender is chosen as the user. This sends back an embed detailing all current (and completed) rolls for that user.