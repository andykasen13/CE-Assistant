# import discord
# import json
# from Helper_Functions.rollable_games import *
import datetime
# from datetime import timedelta
import calendar
# import time

# from Helper_Functions.update import update_p

# async def roll_completed(ended_roll_name : str, casino_channel : discord.channel, user_name : str, collection) :

#     with open('Jasons/users2.json', 'r') as dbU:
#         database_user = json.load(dbU)
    
#     roll_num = 0
#     for roll in database_user[user_name]['Current Rolls'] :
#         if roll['Event Name'] == ended_roll_name : break
#         roll_num += 1
    


#     # FOURWARD THINKING
#     if(ended_roll_name == "Fourward Thinking") :
#         if(len(database_user[user_name]['Current Rolls'][roll_num]['Games']) == 1) :
#             await casino_channel.send(f"<@{database_user[user_name]['Discord ID']}>, you can now roll for your T2 in Fourward Thinking.")
#             # roll a t2
#         elif(len(database_user[user_name]['Current Rolls'][roll_num]['Games']) == 2) :
#             await casino_channel.send(f"<@{database_user[user_name]['Discord ID']}>, you can now roll for your T3 in Fourward Thinking.")
#             # roll a t3
#         elif(len(database_user[user_name]['Current Rolls'][roll_num]['Games']) == 3) :
#             await casino_channel.send(f"<@{database_user[user_name]['Discord ID']}>, you can now roll for your T4 in Fourward Thinking.")
#             #roll a t4
#         elif(len(database_user[user_name]['Current Rolls'][roll_num]['Games']) == 4) :
#             return await casino_channel.send(f"<@{database_user[user_name]['Discord ID']}>, you have completed Fourward Thinking!"
#                                              + " Please let an admin know so you can recieve the Community Objective on the site.")
#             # be done
        
#         del database_user[user_name]['Current Rolls'][roll_num]['End Time']


    
#     else :
#         await casino_channel.send(f"<@{database_user[user_name]['Discord ID']}>, you have completed {ended_roll_name}!"
#                                   + " Please let an admin know so you can recieve the Community Objective on the site.")
#         database_user[user_name]['Current Rolls'][roll_num]['End Time'] = int(time.mktime(datetime.datetime.now().timetuple()))
#         database_user[user_name]['Completed Rolls'].append(database_user[user_name]['Current Rolls'][roll_num])
#         del database_user[user_name]['Current Rolls'][roll_num]

#     with open('Jasons/users2.json', 'w') as f :
#         json.dump(database_user, f, indent=4)

# async def roll_failed(ended_roll_name : str, casino_channel : discord.channel, user_name : str, log_channel : discord.TextChannel) :


#     #TODO: if the game is 'pending...', then don't report it. it just means that they can rewrite the command again.

#     # Set up the cooldowns
#     cooldowns = {
#         "One Hell of a Day" : timedelta(14),
#         "One Hell of a Week" : timedelta(28),
#         "One Hell of a Month" : timedelta(28*3),
#         "Two Week T2 Streak" : 0,
#         "Two 'Two Week T2 Streak' Streak" : timedelta(7),
#         "Never Lucky" : timedelta(28),
#         "Triple Threat" : timedelta(28*3),
#         "Let Fate Decide" : timedelta(28*3),
#         "Fourward Thinking" : 0,
#         "Russian Roulette" : timedelta(28*6)
#     }
#     cooldowns_str = {
#         "One Hell of a Day" : "two weeks",
#         "One Hell of a Week" : "one month",
#         "One Hell of a Month" : "three months",
#         "Two Week T2 Streak" : 0,
#         "Two 'Two Week T2 Streak' Streak" : "one week",
#         "Never Lucky" : "one month",
#         "Triple Threat" : "three months",
#         "Let Fate Decide" : "three months",
#         "Fourward Thinking" : 0,
#         "Russian Roulette" : "six months"
#     }

#     # Open the database
#     with open('Jasons/users2.json', 'r') as dbU:
#         database_user = json.load(dbU)
    
#     # Find the roll in the user's database
#     roll_num = 0
#     for roll in database_user[user_name]['Current Rolls'] :
#         if roll['Event Name'] == ended_roll_name : break
#         roll_num += 1

#     # TODO: update the user's information. if they still have failed the roll, continue on. 
#     # if it turns out that they actually did complete the roll but just forgot to update their profile, 
#     # run the function above.

#     # - - - - - The roll is 'pending...' - - - - - 
#     if database_user[user_name]['Current Rolls'][roll_num]['Games'] == ['pending...'] :
#         print('pending... was removed. ')
#         del database_user[user_name]['Current Rolls'][roll_num]
#         await casino_channel.send('you can now roll {} again. sorry if your message got deltelhfjdsl lol'.format(ended_roll_name))
#         await log_channel.send('{} can now roll {} again.'.format(database_user[user_name]['Discord ID'], ended_roll_name))

#         with open('Jasons/users2.json', 'w') as f :
#             json.dump(database_user, f, indent=4)

#         return
    
#     # Update the user's database to see if the roll was completed or not
#     silly = await update_p(user_name)
#     print(silly)
    
#     # - - - - - The user completed the roll - - - - -

#     # - - - - - The user has failed the roll - - - - - 
#     await casino_channel.send(f"<@{database_user[user_name]['Discord ID']}>, you have failed {ended_roll_name}."
#                               + f" Your cooldown will end in {cooldowns_str[ended_roll_name]}" 
#                               + f" (<t:{int(time.mktime((datetime.datetime.now()+cooldowns[ended_roll_name]).timetuple()))}>).")
    
#     database_user[user_name]['Cooldowns'][ended_roll_name] = int(time.mktime((datetime.datetime.now()+cooldowns[ended_roll_name]).timetuple()))

#     del database_user[user_name]['Current Rolls'][roll_num]

#     with open('Jasons/users2.json', 'w') as f :
#         json.dump(database_user, f, indent=4)


# async def check_if_done(user_name : str) :
#     with open('Jasons/users2.json', 'r') as f:
#         database_user = json.load(f)
    
#     for cu_roll in database_user[user_name]['Current Rolls'] :
#         if("End Time" not in cu_roll) : print('end ime not in roll')
#         elif(cu_roll['End Time'] > int(time.mktime((datetime.datetime.now()).timetuple()))) : print("{} is joever".format(cu_roll['Event Name']))

def months_to_days(num_months):
    # purpose -- determine number of days to 'x' months away. Required as duration will be different depending on point in the year, and get_rollable_game requires day inputs
    # function input = number of months
    # function output = number of days between now and input months away 
    now = datetime.datetime.now()
    end_year = now.year + (now.month + num_months - 1) // 12
    end_month = (now.month + num_months - 1) % 12 + 1
    end_date = datetime.date(end_year, end_month, min(calendar.monthrange(end_year, end_month)[1], now.day))
    date_delta = end_date - datetime.date(now.year, now.month, now.day)

    return date_delta.days
    
