

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

# file management
import os
import shutil

# thread management
import asyncio
import typing
from discord.ext import tasks

# other local files
from Web_Interaction.curator import checkCuratorCount
from Web_Interaction.scraping import get_games


# dictating which channel the info will be sent to
channel_number = 1128742486416834570   #1135993275162050690

# dedicate times every fifteen minutes
utc = datetime.timezone.utc
times = [
  datetime.time(hour=0, minute=0, tzinfo=utc),
  datetime.time(hour=0, minute=15, tzinfo=utc),
  datetime.time(hour=0, minute=30, tzinfo=utc),
  datetime.time(hour=0, minute=45, tzinfo=utc),
  datetime.time(hour=1, minute=0, tzinfo=utc),
  datetime.time(hour=1, minute=15, tzinfo=utc),
  datetime.time(hour=1, minute=30, tzinfo=utc),
  datetime.time(hour=1, minute=45, tzinfo=utc),
  datetime.time(hour=2, minute=0, tzinfo=utc),
  datetime.time(hour=2, minute=15, tzinfo=utc),
  datetime.time(hour=2, minute=30, tzinfo=utc),
  datetime.time(hour=2, minute=45, tzinfo=utc),
  datetime.time(hour=3, minute=0, tzinfo=utc),
  datetime.time(hour=3, minute=15, tzinfo=utc),
  datetime.time(hour=3, minute=30, tzinfo=utc),
  datetime.time(hour=3, minute=45, tzinfo=utc),
  datetime.time(hour=4, minute=0, tzinfo=utc),
  datetime.time(hour=4, minute=15, tzinfo=utc),
  datetime.time(hour=4, minute=30, tzinfo=utc),
  datetime.time(hour=4, minute=45, tzinfo=utc),
  datetime.time(hour=5, minute=0, tzinfo=utc),
  datetime.time(hour=5, minute=15, tzinfo=utc),
  datetime.time(hour=5, minute=30, tzinfo=utc),
  datetime.time(hour=5, minute=45, tzinfo=utc),
  datetime.time(hour=6, minute=0, tzinfo=utc),
  datetime.time(hour=6, minute=15, tzinfo=utc),
  datetime.time(hour=6, minute=30, tzinfo=utc),
  datetime.time(hour=6, minute=45, tzinfo=utc),
  datetime.time(hour=7, minute=0, tzinfo=utc),
  datetime.time(hour=7, minute=15, tzinfo=utc),
  datetime.time(hour=7, minute=30, tzinfo=utc),
  datetime.time(hour=7, minute=45, tzinfo=utc),
  datetime.time(hour=8, minute=0, tzinfo=utc),
  datetime.time(hour=8, minute=15, tzinfo=utc),
  datetime.time(hour=8, minute=30, tzinfo=utc),
  datetime.time(hour=8, minute=45, tzinfo=utc),
  datetime.time(hour=9, minute=0, tzinfo=utc),
  datetime.time(hour=9, minute=15, tzinfo=utc),
  datetime.time(hour=9, minute=30, tzinfo=utc),
  datetime.time(hour=9, minute=45, tzinfo=utc),
  datetime.time(hour=10, minute=0, tzinfo=utc),
  datetime.time(hour=10, minute=15, tzinfo=utc),
  datetime.time(hour=10, minute=30, tzinfo=utc),
  datetime.time(hour=10, minute=45, tzinfo=utc),
  datetime.time(hour=11, minute=0, tzinfo=utc),
  datetime.time(hour=11, minute=15, tzinfo=utc),
  datetime.time(hour=11, minute=30, tzinfo=utc),
  datetime.time(hour=11, minute=45, tzinfo=utc),
  datetime.time(hour=12, minute=0, tzinfo=utc),
  datetime.time(hour=12, minute=15, tzinfo=utc),
  datetime.time(hour=12, minute=30, tzinfo=utc),
  datetime.time(hour=12, minute=45, tzinfo=utc),
  datetime.time(hour=13, minute=0, tzinfo=utc),
  datetime.time(hour=13, minute=15, tzinfo=utc),
  datetime.time(hour=13, minute=30, tzinfo=utc),
  datetime.time(hour=13, minute=45, tzinfo=utc),
  datetime.time(hour=14, minute=0, tzinfo=utc),
  datetime.time(hour=14, minute=15, tzinfo=utc),
  datetime.time(hour=14, minute=30, tzinfo=utc),
  datetime.time(hour=14, minute=45, tzinfo=utc),
  datetime.time(hour=15, minute=0, tzinfo=utc),
  datetime.time(hour=15, minute=15, tzinfo=utc),
  datetime.time(hour=15, minute=30, tzinfo=utc),
  datetime.time(hour=15, minute=45, tzinfo=utc),
  datetime.time(hour=16, minute=0, tzinfo=utc),
  datetime.time(hour=16, minute=15, tzinfo=utc),
  datetime.time(hour=16, minute=30, tzinfo=utc),
  datetime.time(hour=16, minute=45, tzinfo=utc),
  datetime.time(hour=17, minute=0, tzinfo=utc),
  datetime.time(hour=17, minute=15, tzinfo=utc),
  datetime.time(hour=17, minute=30, tzinfo=utc),
  datetime.time(hour=17, minute=45, tzinfo=utc),
  datetime.time(hour=18, minute=0, tzinfo=utc),
  datetime.time(hour=18, minute=15, tzinfo=utc),
  datetime.time(hour=18, minute=30, tzinfo=utc),
  datetime.time(hour=18, minute=45, tzinfo=utc),
  datetime.time(hour=19, minute=0, tzinfo=utc),
  datetime.time(hour=19, minute=15, tzinfo=utc),
  datetime.time(hour=19, minute=30, tzinfo=utc),
  datetime.time(hour=19, minute=45, tzinfo=utc),
  datetime.time(hour=20, minute=0, tzinfo=utc),
  datetime.time(hour=20, minute=15, tzinfo=utc),
  datetime.time(hour=20, minute=30, tzinfo=utc),
  datetime.time(hour=20, minute=45, tzinfo=utc),
  datetime.time(hour=21, minute=0, tzinfo=utc),
  datetime.time(hour=21, minute=15, tzinfo=utc),
  datetime.time(hour=21, minute=30, tzinfo=utc),
  datetime.time(hour=21, minute=45, tzinfo=utc),
  datetime.time(hour=22, minute=0, tzinfo=utc),
  datetime.time(hour=22, minute=15, tzinfo=utc),
  datetime.time(hour=22, minute=30, tzinfo=utc),
  datetime.time(hour=22, minute=45, tzinfo=utc),
  datetime.time(hour=23, minute=0, tzinfo=utc),
  datetime.time(hour=23, minute=15, tzinfo=utc),
  datetime.time(hour=23, minute=30, tzinfo=utc),
  datetime.time(hour=23, minute=45, tzinfo=utc)
  ,datetime.time(hour=17, minute=31, tzinfo=utc)
]


# big daddy loop that runs every fifteen minutes
@tasks.loop(time=times)
async def master_loop(client):
    print('loop engaged...')

    correct_channel = client.get_channel(channel_number)

    # start the curate function
    await curate(correct_channel)

    # start the scrape function
    await scrape(correct_channel)


    print('done')


async def curate(channel):
    print('curating...')

    # thread call getting the latest curator stuff
    curation = await thread_curate() #await asyncio.to_thread(thread_curate) 

    # get the current curator page and update its curator count
    data = json.loads(open("./Jasons/curator_count.json").read())
    data['Curator Count'] = curation[0]

    # dump new count
    with open("./Jasons/curator_count.json", "w") as jsonFile:
        json.dump(data, jsonFile, indent=4)

    # if there were updates send them to the channel
    if len(curation) > 1:
        for embed in curation[1]:
            await channel.send(embed=embed)
    

def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper


@to_thread
def thread_curate():
    # call to the curator file
    return checkCuratorCount()


async def scrape(channel):
    print('scraping...')

    # thread call scraping the new data
    updates = await thread_scrape() #asyncio.to_thread(thread_scrape)
    print('here')
    # send out each update
    for dict in updates[0]:
        await channel.send(file=dict['Image'], embed=dict['Embed'])

    # delete and replace 'Pictures' with an empty folder
    shutil.rmtree('./Pictures')
    os.mkdir('./Pictures')


@to_thread
def thread_scrape():
    # call to the scrape file
    return get_games()