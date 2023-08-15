from discord.ext import tasks
import datetime
import json
from bs4 import BeautifulSoup
import discord
import requests

ce_james_icon = "https://cdn.discordapp.com/attachments/1028404246279888937/1136056766514339910/CE_Logo_M3.png"


async def single_run(client, requested_reviews=0):
    if requested_reviews > 0:
        data = json.loads(open("./Jasons/curator_count.json").read())
        curation = checkCuratorCount()
        data['Curator Count'] = curation[0]
        embeds=[]
        if len(curation) > 1:
            embeds = curation[1]

        with open("./Jasons/curator_count.json", "w") as jsonFile:
            json.dump(data, jsonFile, indent=4)
    else:
        embeds = curatorUpdate(requested_reviews)

    for embed in embeds:
        correctChannel = client.get_channel(1128742486416834570)
        await correctChannel.send(embed=embed)



def getCuratorCount():
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


def checkCuratorCount():
    number = getCuratorCount()
    current_count = json.loads(open("./Jasons/curator_count.json").read())['Curator Count']
    if number != current_count:
        embeds = curatorUpdate(int(number)-int(current_count))
        return [number, embeds]
    else:
        return [number]
    


def curatorUpdate(num: int) :
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



    embeds = []

    x = 0
    while x < len(descriptions):
        embed = discord.Embed(
            title="CE Curator",
            color=0x000000,
            timestamp=datetime.datetime.now()
        )

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
            icon_url=ce_james_icon)
        embed.set_author(name="New game added to curator!", url="https://store.steampowered.com/curator/36185934/")


        embeds.append(embed)
        x+=1

    return embeds

    