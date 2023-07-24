import discord
import json
from Helper_Functions.rollable_games import *

casino_channel = discord.Client.get_channel(811286469251039333)

async def roll_completed(ended_roll : dict) :
    x=0

    # FOURWARD THINKING
    if(ended_roll["Event Name"] == "Fourward Thinking") :
        x=0
        if(len(ended_roll["Games"]) is 1) :
            # roll a t2
            x=0
        elif(len(ended_roll["Games"]) is 2) :
            x=0
            # roll a t3
        elif(len(ended_roll["Games"]) is 3) :
            x=0
            #roll a t4
        elif(len(ended_roll["Games"]) is 4) :
            x=0
            # be done

async def roll_failed(ended_roll : dict) :
    x=0