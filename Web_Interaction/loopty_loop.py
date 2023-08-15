from asyncio import to_thread
import asyncio
from discord.ext import tasks
from datetime import datetime
import datetime
import json
import os
import shutil

from Web_Interaction.curator import checkCuratorCount
from Web_Interaction.scraping import get_games

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
  datetime.time(hour=23, minute=45, tzinfo=utc),
  datetime.time(hour=4, minute=34, tzinfo=utc)
]


@tasks.loop(time=times)
async def master_loop(client):
    print('loop engaged...')
    await curate(client)
    await scrape(client)
    print('done')


async def curate(client):
    print('curating...')
    data = json.loads(open("./Jasons/curator_count.json").read())
    curation = await asyncio.to_thread(thread_curate) #thread_curate()
    data['Curator Count'] = curation[0]
    print(data)

    with open("./Jasons/curator_count.json", "w") as jsonFile:
        json.dump(data, jsonFile, indent=4)

    if len(curation) > 1:
        correctChannel = client.get_channel(1128742486416834570)
        for embed in curation[1]:
            await correctChannel.send(embed=embed)
    

# @to_thread
def thread_curate():
    return checkCuratorCount()



async def scrape(client):
    print('scraping...')
    updates = await asyncio.to_thread(thread_scrape)

    correctChannel = client.get_channel(1128742486416834570) #1135993275162050690
    for dict in updates[0]:
        await correctChannel.send(file=dict['Image'], embed=dict['Embed'])

    
    shutil.rmtree('./Pictures')
    os.mkdir('./Pictures')


# @to_thread
def thread_scrape():
    return get_games()