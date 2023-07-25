import discord
import json
from Helper_Functions.rollable_games import *
import datetime
from datetime import timedelta
import monthdelta

async def roll_completed(ended_roll_name : str, casino_channel : discord.channel, user_name : str) :
    x=0

    with open('Jasons/users2.json', 'r') as dbU:
        database_user = json.load(dbU)
    
    roll_num = 0
    for roll in database_user[user_name]["Current Rolls"] :
        if roll["Event Name"] == ended_roll_name : break
        roll_num += 1
    


    # FOURWARD THINKING
    if(ended_roll_name == "Fourward Thinking") :
        x=0
        if(len(database_user[user_name]["Current Rolls"][roll_num]["Games"]) == 1) :
            await casino_channel.send(f"<@{database_user[user_name]['Discord ID']}>, you can now roll for your T2 in Fourward Thinking.")
            # roll a t2
        elif(len(database_user[user_name]["Current Rolls"][roll_num]["Games"]) == 2) :
            await casino_channel.send(f"<@{database_user[user_name]['Discord ID']}>, you can now roll for your T3 in Fourward Thinking.")
            # roll a t3
        elif(len(database_user[user_name]["Current Rolls"][roll_num]["Games"]) == 3) :
            await casino_channel.send(f"<@{database_user[user_name]['Discord ID']}>, you can now roll for your T4 in Fourward Thinking.")
            #roll a t4
        elif(len(database_user[user_name]["Current Rolls"][roll_num]["Games"]) == 4) :
            return await casino_channel.send(f"<@{database_user[user_name]['Discord ID']}>, you have completed Fourward Thinking!"
                                             + " Please let an admin know so you can recieve the Community Objective on the site.")
            # be done
        
        del database_user[user_name]["Current Rolls"][roll_num]["End Time"]

        with open('Jasons/users2.json', 'w') as f :
            json.dump(database_user, f, indent=4)

async def roll_failed(ended_roll : dict) :
    x=0

    cooldowns = {
        "One Hell of a Day" : timedelta(14),
        "One Hell of a Week" : monthdelta(1),
        "One Hell of a Month" : monthdelta(3),
        "Two Week T2 Streak" : 0,
        "Two 'Two Week T2 Streak' Streak" : timedelta(7),
        "Never Lucky" : monthdelta(1),
        "Triple Threat" : monthdelta(3),
        "Let Fate Decide" : monthdelta(3),
        "Fourward Thinking" : 0,
        "Russian Roulette" : monthdelta(6)
    }