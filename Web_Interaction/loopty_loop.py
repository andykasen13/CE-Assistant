

#-----------------------------------------------------------------------------------------#
#                                                                                         #
"                                    MASTER LOOP                                          "
#                                                                                         #
#               used to loop both curate and scrape every fifteen minutes                 #      
#                                                                                         #
#-----------------------------------------------------------------------------------------#


# basics
from datetime import datetime
import datetime
import functools
import json
import signal
from functools import wraps
import discord
import traceback

# file management
import os
import shutil

# thread management
import asyncio
from asyncio import timeout, CancelledError
from urllib3.exceptions import ReadTimeoutError
import typing
from bson import ObjectId
from discord.ext import tasks

from selenium.common.exceptions import StaleElementReferenceException

# other local files
from Web_Interaction.curator import checkCuratorCount
from Web_Interaction.scraping import get_games
from Helper_Functions.mongo_silly import *
from Helper_Functions.update import update_p


# dedicate times every --fifteen-- thirty minutes
utc = datetime.timezone.utc
times = [
  datetime.time(hour=0, minute=0, tzinfo=utc),
  datetime.time(hour=0, minute=30, tzinfo=utc),
  datetime.time(hour=1, minute=0, tzinfo=utc),
  datetime.time(hour=1, minute=30, tzinfo=utc),
  datetime.time(hour=2, minute=0, tzinfo=utc),
  datetime.time(hour=2, minute=30, tzinfo=utc),
  datetime.time(hour=3, minute=0, tzinfo=utc),
  datetime.time(hour=3, minute=30, tzinfo=utc),
  datetime.time(hour=4, minute=0, tzinfo=utc),
  datetime.time(hour=4, minute=30, tzinfo=utc),
  datetime.time(hour=5, minute=0, tzinfo=utc),
  datetime.time(hour=5, minute=30, tzinfo=utc),
  datetime.time(hour=6, minute=0, tzinfo=utc),
  datetime.time(hour=6, minute=30, tzinfo=utc),
  datetime.time(hour=7, minute=0, tzinfo=utc),
  datetime.time(hour=7, minute=30, tzinfo=utc),
  datetime.time(hour=8, minute=0, tzinfo=utc),
  datetime.time(hour=8, minute=30, tzinfo=utc),
  datetime.time(hour=9, minute=0, tzinfo=utc),
  datetime.time(hour=9, minute=30, tzinfo=utc),
  datetime.time(hour=10, minute=0, tzinfo=utc),
  datetime.time(hour=10, minute=30, tzinfo=utc),
  datetime.time(hour=11, minute=0, tzinfo=utc),
  datetime.time(hour=11, minute=30, tzinfo=utc),
  datetime.time(hour=12, minute=0, tzinfo=utc),
  datetime.time(hour=12, minute=30, tzinfo=utc),
  datetime.time(hour=13, minute=0, tzinfo=utc),
  datetime.time(hour=13, minute=30, tzinfo=utc),
  datetime.time(hour=14, minute=0, tzinfo=utc),
  datetime.time(hour=14, minute=30, tzinfo=utc),
  datetime.time(hour=15, minute=0, tzinfo=utc),
  datetime.time(hour=15, minute=30, tzinfo=utc),
  datetime.time(hour=16, minute=0, tzinfo=utc),
  datetime.time(hour=16, minute=30, tzinfo=utc),
  datetime.time(hour=17, minute=0, tzinfo=utc),
  datetime.time(hour=17, minute=30, tzinfo=utc),
  datetime.time(hour=18, minute=0, tzinfo=utc),
  datetime.time(hour=18, minute=30, tzinfo=utc),
  datetime.time(hour=19, minute=0, tzinfo=utc),
  datetime.time(hour=19, minute=30, tzinfo=utc),
  datetime.time(hour=20, minute=0, tzinfo=utc),
  datetime.time(hour=20, minute=30, tzinfo=utc),
  datetime.time(hour=21, minute=0, tzinfo=utc),
  datetime.time(hour=21, minute=30, tzinfo=utc),
  datetime.time(hour=22, minute=0, tzinfo=utc),
  datetime.time(hour=22, minute=30, tzinfo=utc),
  datetime.time(hour=23, minute=0, tzinfo=utc),
  datetime.time(hour=23, minute=30, tzinfo=utc),
]


# big daddy loop that runs every fifteen minutes
@tasks.loop(time=times)
async def master_loop(client : discord.Client):
    print('loop engaged...')
    print('time = ' + str(datetime.datetime.now().strftime("%H:%M:%S")))

    correct_channel = client.get_channel(game_additions_id)

    # start the curate function
    await curate(correct_channel)

    # start the scrape function
    try: # timeout the function after 15 minutes. it keeps getting stuck smh my head
        async with asyncio.timeout(900):
            scrape_message = await scrape(correct_channel)
    except TimeoutError:
        scrape_message = "function timed out!!!"
    except CancelledError:
        scrape_message = "function timed out!!!!"
    except StaleElementReferenceException as e:
        scrape_message = "stale element!!! wahoo!! please ping andy even though he will cry"
        print(e)
    except ReadTimeoutError as e :
        scrape_message = "connection lost, but do not worry - it will work again next time (probably)"
        print(e)
    except Exception as e:
        scrape_message = "something else went wrong. someone ping andy pls\n\n" + str(e)
        try: 
            traceback.print_exception(e)
        except:
            print('printing traceback failed lol')

    if scrape_message != "loop successful" : 
        log = client.get_channel(private_log_id)
        await log.send(scrape_message)

    print('done\n')
    
    return


    try:
        await user_scrape(client)
    except:
        ""

    


async def curate(channel):
    print('curating...')
    from Helper_Functions.mongo_silly import get_mongo, dump_mongo

    curator_count = await get_mongo('curator')

    # thread call getting the latest curator stuff
    curation = await thread_curate(curator_count) #await asyncio.to_thread(thread_curate) 

    # get the current curator page and update its curator count
    data = await get_mongo('curator')
    data['Curator Count'] = curation[0]

    # dump new count
    dump = await dump_mongo("curator", data)

    # if there were updates send them to the channel
    if len(curation) > 1:
        for embed in curation[1]:
            await channel.send(embed=embed)

    del curator_count
    del curation
    del data

    

def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper


@to_thread
def thread_curate(curator_count):
    # call to the curator file
    return checkCuratorCount(curator_count)

async def scrape(channel):
    print('scraping...')
    from Helper_Functions.mongo_silly import get_mongo, dump_mongo
    database_name = await get_mongo('name')
    curator_count = await get_mongo('curator')
    unfinished = await get_mongo('unfinished')

    # thread call scraping the new data
    updates = await thread_scrape(database_name, curator_count, unfinished) #asyncio.to_thread(thread_scrape)
    """ [{embeds}, number(?), database_name, curator_count, unfinished_games, database_tier]]
    """

    if updates == None : return "empty scrape"

    # dump the data back onto mongodb
    dump1 = await dump_mongo("name", updates[2]) # name
    dump2 = await dump_mongo("curator", updates[3]) # curator
    dump2andahalf = await dump_mongo('unfinished', updates[4]) # unfinished
    dump3 = await dump_mongo('tier', updates[5]) # tier

    # send out each update
    for dict in updates[0]:
        await channel.send(file=dict['Image'], embed=dict['Embed'])
    
    del updates
    del dump1
    del dump2
    del dump2andahalf
    del dump3
    del database_name
    del curator_count
    del unfinished

    return "loop successful"


@to_thread
def thread_scrape(database_name, curator_count, unfinished):
    # call to the scrape file
    return get_games(database_name, curator_count, unfinished)


async def user_scrape(client : discord.Client):
    """Takes in the `discord.Client` associated with the bot and sends messages."""
    # databases
    database_name = await get_mongo('name')
    database_user = await get_mongo('user')

    # channels
    casino_channel = client.get_channel(casino_id)
    log_channel = client.get_channel(log_id)
    private_log_channel = client.get_channel(private_log_id)

    # get returns
    returns = await thread_user(database_name, database_user)

    # go through the returns
    for return_value in returns :
        # you've reached the end
        if return_value == "Updated" : continue

        # change the rank
        elif return_value[:5:] == "rank:" : continue

        # log channel shit
        elif return_value[:4:] == "log:" :
            await log_channel.send(return_value[5::])

        # casino channel shit
        elif return_value[:7:] == "casino:":
            await casino_channel.send(return_value[8::])

        # else
        else :
            await private_log_channel.send("BOT ERROR: recieved unrecognized update code: \n'{}'".format(return_value))
            

@to_thread
def thread_user(database_name, database_user):
    json_response = []
    i = 0
    done_fetching = False
    returns : list[str] = []
    while (not done_fetching):
        try:
            api_response = requests.get("https://cedb.me/api/users/all?limit=100offset={}".format(str((i-1)*100)))
            j = json.loads(api_response.text)
            json_response += j
            i += 1
            done_fetching = len(j) == 0
        except:
            print("fetching failed... :(")
            return None
    
    print('done fetching')
    for user in json_response:
        if user['id'] not in database_user : continue
        try: returns += update_p(0, "", database_user, database_name, user_ce_data=user)
        except: continue
    
    print('done updating')

    return returns