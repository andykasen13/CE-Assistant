import json
import time
import datetime
from bson import ObjectId


from Helper_Functions.update import update_p

from apscheduler.schedulers.background import BackgroundScheduler
from motor.motor_asyncio import AsyncIOMotorClient


uri = "mongodb+srv://andrewgarcha:KUTo7dCtGRy4Nrhd@ce-cluster.inrqkb3.mongodb.net/?retryWrites=true&w=majority"
mongo_client = AsyncIOMotorClient(uri)

mongo_database = mongo_client['database_name']
collection = mongo_client['database_name']['ce-collection']

mongo_ids = {
    "name" : ObjectId('64f8d47f827cce7b4ac9d35b'),
    "tier" : ObjectId('64f8bc4d094bdbfc3f7d0050'),
    "curator" : ObjectId('64f8d63592d3fe5849c1ba35'),
    "tasks" : ObjectId('64f8d6b292d3fe5849c1ba37'),
    "user" : ObjectId('64f8bd1b094bdbfc3f7d0051')
}


sched = BackgroundScheduler()

async def add_task(time, args):
    sched.add_job(update_p, 'date', run_date=time, args=args)

async def startup_sched():
    user_info = await collection.find_one({'_id' : mongo_ids["user"]})
    database_name = await collection.find_one({'_id' : mongo_ids['name']})

    for user_str in user_info:
        if user_str == '_id' : continue
        user = user_info[user_str]
        
        for current_roll in user["Current Rolls"]:
            if not 'End Time' in list(current_roll):
                continue

            end_time = current_roll["End Time"]

            args = [
                user['Discord ID'],
                current_roll["Event Name"],
                user_info,
                database_name
            ]

            await add_task(end_time, args)

        for current_roll in user["Cooldowns"]:
            if not 'End Time' in list(current_roll):
                continue

            end_time = current_roll["End Time"]

            args = [
                user['Discord ID'],
                current_roll["Event Name"],
                user_info,
                database_name
            ]

            await add_task(end_time, args)

    sched.start()



# def test(arg1, arg2, arg5):
#     tasks = json.loads(open("./Jasons/tasks.json").read())
#     update_p(arg1, arg2)
#     if arg5 == -1:
#         return
#     tasks.pop(arg5)
#     with open("./Jasons/tasks.json", "w") as f:
#         json.dump(tasks, f, indent=4)



# def get_tasks(client):
#     users = json.loads(open("./Jasons/users2.json").read())
#     fin = []

#     for user_str in users:
#         user = users[user_str]
        
#         for current_roll in user["Current Rolls"]:
#             if not 'End Time' in list(current_roll):
#                 continue

#             fin.append({
#                 "End Time" : current_roll["End Time"],
#                 "Event Name" : current_roll["Event Name"],
#                 "CE ID": user["CE ID"]
#             })

    
#     with open("./Jasons/tasks.json", "w") as f:
#         json.dump(fin, f, indent=4)

#     create_schedule(client)


# def create_schedule(client):
#     log_channel = client.get_channel(1141886539157221457)
#     casino_channel = client.get_channel(811286469251039333)

#     tasks = json.loads(open("./Jasons/tasks.json").read())
#     indices = []

#     #read roles from other thing then do shit with those
#     for index, task in enumerate(tasks):
#         event_name = task["Event Name"]
#         user_id = task["CE ID"]
        
#         if task['End Time'] <= int(time.mktime((datetime.datetime.now()).timetuple())):
#             test(user_id, event_name, -1)
#             indices.insert(0, index)
#             continue

#         date_time = datetime.datetime.utcfromtimestamp(int(task["End Time"]-14400))
        
#         sched.add_job(test, 'date', run_date = date_time, args = [user_id, event_name])

#     for indice in indices:
#         tasks.pop(indice)

#     with open("./Jasons/tasks.json", "w") as f:
#         json.dump(tasks, f, indent=4)

    # sched.start()
