from discord.ext import tasks
import datetime
import json
from bs4 import BeautifulSoup
import discord
import requests


async def getCuratorCount():
    veggies = {'cc': 'us', 'l' : 'english'}
    broth = requests.get("https://store.steampowered.com/curator/36185934/", params=veggies)
    soup = BeautifulSoup(broth.text, features="html.parser")
    noodle = soup.find_all("span")
    for noodlet in noodle:
        try:
            if noodlet['id'] == "Recommendations_total":
                number = noodlet.string
        except:
            continue
    return number


async def checkCuratorCount(client):
    number = await getCuratorCount()
    current_count = json.loads(open("./Jasons/curator_count.json").read())['Current Reviews']
    if number != current_count:
        await curatorUpdate(int(number)-int(current_count), client)
        return number
    else:
        return number
    

utc = datetime.timezone.utc
times = [
    datetime.time(hour=3, tzinfo=utc),
    datetime.time(hour=6, tzinfo=utc),
    datetime.time(hour=9, tzinfo=utc),
    datetime.time(hour=12, tzinfo=utc),
    datetime.time(hour=15, tzinfo=utc),
    datetime.time(hour=18, tzinfo=utc),
    datetime.time(hour=21, tzinfo=utc),
    datetime.time(hour=0, tzinfo=utc),
    datetime.time(hour=18, minute=55)
]


@tasks.loop(time = times)
async def loop(client):
    with open("./Jasons/curator_count.json", "r+") as jsonFile:
        data = json.load(jsonFile)
    data['Current Reviews'] = await checkCuratorCount(client)
    print(data)

    with open("./Jasons/curator_count.json", "w") as jsonFile:
        json.dump(data, jsonFile, indent = 4)


async def curatorUpdate(num: int, client) :
    payload = {'cc': 'us', 'l' : 'english'}
    response = requests.get("https://store.steampowered.com/curator/36185934/", params=payload)
    html = BeautifulSoup(response.text, features="html.parser")

    descriptions = []
    app_ids = []
    links = []

    divs = html.find_all('div')
    for div in divs:
        try:
            if div["class"][0] == "recommendation_desc":
                descriptions.append(div.string.replace('\t', '').replace('\r', '').replace('\n', ''))
            if div["class"][0] == "recommendation_readmore":
                links.append(div.contents[0]["href"][43:])
        except:
            continue
    del descriptions[num:]

    onlyAs = html.find_all('a')
    for a in onlyAs:
        try:
            app_ids.append(a["data-ds-appid"])
        except:
            continue
    del app_ids[num:]


    embed = discord.Embed(
        title="CE Curator",
        color=0x000000,
        timestamp=datetime.datetime.now()
    )


    x = 0
    while x < len(descriptions):
    #TODO: add the link to the full review
        correctAppID = app_ids[x]

# Open and save the JSON data
        payload = {'appids': correctAppID, 'cc' : 'US'}
        response = requests.get("https://store.steampowered.com/api/appdetails?", params = payload)
        jsonData = json.loads(response.text)
    
    # Save important information
        gameTitle = jsonData[correctAppID]['data']['name']
        imageLink = jsonData[correctAppID]['data']['header_image']
        if(jsonData[correctAppID]['data']['is_free']) :
            gamePrice = "Free"
        else: gamePrice = jsonData[correctAppID]['data']['price_overview']['final_formatted']
        # TODO: get discounts working
        gameNameWithLinkFormat = gameTitle.replace(" ", "_")
        

        embed = discord.Embed(
            title = gameTitle,
            url=f"https://store.steampowered.com/app/{correctAppID}/{gameNameWithLinkFormat}/",
            colour = 0x000000,
            timestamp=datetime.datetime.now()
        )

        embed.add_field(name="Review", value=descriptions[x], inline=False)
        embed.add_field(name="Price", value=gamePrice, inline=True)
        embed.add_field(name="CE Link", value=f"[Click here]({links[x]})", inline=True)
        embed.set_image(url=imageLink)
        embed.set_footer(text="CE Assistant",
            icon_url="https://cdn.discordapp.com/attachments/639112509445505046/891449764787408966/challent.jpg")
        embed.set_author(name="New game added to curator!", url="https://store.steampowered.com/curator/36185934/")
    
        correctChannel = client.get_channel(1128742486416834570)
        await correctChannel.send(embed=embed)
        x+=1

    