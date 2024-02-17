

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

# file management
import os
import shutil

# thread management
import asyncio
import typing
from bson import ObjectId
from discord.ext import tasks

from selenium.common.exceptions import StaleElementReferenceException

# other local files
from Web_Interaction.curator import checkCuratorCount
from Web_Interaction.scraping import get_games
from Helper_Functions.mongo_silly import get_mongo, dump_mongo, get_unix



# dictating which channel the info will be sent to
channel_number = 1128742486416834570   #1135993275162050690

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
async def master_loop(client, mongo_client):
    print('loop engaged...')
    

    correct_channel = client.get_channel(channel_number)

    # start the curate function
    await curate(correct_channel, mongo_client)

    # start the scrape function
    try: # timeout the function after 10 minutes. it keeps getting stuck smh my head
        async with asyncio.timeout(600):
            scrape_message = await scrape(correct_channel, mongo_client)
    except TimeoutError:
        scrape_message = "function timed out!!!"
    except StaleElementReferenceException as e:
        scrape_message = "stale element!!! wahoo!! please ping andy even though he will cry"
        print(e)

    log = client.get_channel(1141886539157221457)
    await log.send(scrape_message)

    print('done\n')


async def curate(channel, mongo_client):
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

async def scrape(channel, mongo_client):
    print('scraping...')
    from Helper_Functions.mongo_silly import get_mongo, dump_mongo
    database_name = await get_mongo('name')
    curator_count = await get_mongo('curator')
    unfinished = await get_mongo('unfinished')

    # thread call scraping the new data
    updates = await thread_scrape(database_name, curator_count, unfinished) #asyncio.to_thread(thread_scrape)

    if updates == None : return "empty scrape?"

    # dump the data back onto mongodb
    dump1 = await dump_mongo("name", updates[2]) # name
    updates[3]['_id'] = ObjectId('64f8d63592d3fe5849c1ba35')
    dump2 = await dump_mongo("curator", updates[3]) # curator
    dump2andahalf = await dump_mongo('unfinished', updates[4]) # unfinished
    updates[5]['_id'] = ObjectId('64f8bc4d094bdbfc3f7d0050')
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