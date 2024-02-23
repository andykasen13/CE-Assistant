# --------- web imports ---------
import requests
from Helper_Functions.Scheduler import startup_sched
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Literal
from bson import ObjectId
import time
import datetime
from datetime import timedelta
from Helper_Functions.end_time import months_to_days


mongo_ids = {
    "name" : ObjectId('64f8d47f827cce7b4ac9d35b'),
    "tier" : ObjectId('64f8bc4d094bdbfc3f7d0050'),
    "curator" : ObjectId('64f8d63592d3fe5849c1ba35'),
    "tasks" : ObjectId('64f8d6b292d3fe5849c1ba37'),
    "user" : ObjectId('64f8bd1b094bdbfc3f7d0051'),
    "unfinished" : ObjectId('650076a9e35bbc49b06c9881')
}
# ----------------------------------------------------------------------------------------------------------------------------
uri = "mongodb+srv://andrewgarcha:KUTo7dCtGRy4Nrhd@ce-cluster.inrqkb3.mongodb.net/?retryWrites=true&w=majority"
mongo_client = AsyncIOMotorClient(uri)

mongo_database = mongo_client['database_name']
collection = mongo_client['database_name']['ce-collection']

# get and set mongo databases
mongo_names = Literal["name", "tier", "curator", "user", "tasks", "unfinished"]
async def get_mongo(title : mongo_names):
    """Returns the MongoDB associated with `title`."""
    return await collection.find_one({'_id' : mongo_ids[title]})

async def dump_mongo(title : mongo_names, data) :
    """Dumps the MongoDB given by `title` and passed by `data`."""
    return await collection.replace_one({'_id' : mongo_ids[title]}, data)


# get unix timestamp for x days from now
def get_unix(days = 0, minutes = -1, months = -1):
    """Returns a unix timestamp for `days` days (or `minutes` minutes) from the current time."""
    # return right now
    if(days == "now") : return int(time.mktime((datetime.datetime.now()).timetuple()))
    
    # return minutes
    elif (minutes != -1) : return int(time.mktime((datetime.datetime.now()+timedelta(minutes=minutes)).timetuple()))

    # return months
    elif (months != -1) : 
        days = months_to_days(months)
        return get_unix(days)

    # return days
    else: return int(time.mktime((datetime.datetime.now()+timedelta(days)).timetuple()))

# ----------------------------------------------------------------------------------------------------------------------------