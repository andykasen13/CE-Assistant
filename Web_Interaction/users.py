from Helper_Functions.mongo_silly import *
import json

async def update_all() :
    # pull from mongodb
    database_name = await get_mongo('name')
    database_user = await get_mongo('user')

    # get the full leaderboard
    index = 0
    finished_scraping = False
    json_response = []
    while not finished_scraping :
        try:
            print('fetching first {} users'.format((index+1)*100))
            api = requests.get("https://cedb.me/api/leaderboards?limit=100&offset={}".format(index*100))
            jsons = json.loads(api.text)
        except:
            print('missed users {} through {}'.format(index*100+1, (index+1)*100))
        json_response += jsons
        finished_scraping = len(jsons) == 0
        index+=1
    
    for user in json_response :
        if user['userId'] not in database_user : continue
        
    