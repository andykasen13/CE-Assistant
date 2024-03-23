import json
import time
import datetime
from bson import ObjectId


from Helper_Functions.update import update_p

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from motor.motor_asyncio import AsyncIOMotorClient

sched = AsyncIOScheduler()

async def add_task(time, args):
    if time > datetime.datetime.now():
        sched.add_job(update_p, 'date', run_date=time, args=args)
    else:
        print("runtime missed. running update now for <@" + str(args[0]) + ">")
        await update_p(args[0], args[1], args[2], args[3])


async def startup_sched():
    from Helper_Functions.mongo_silly import get_mongo, dump_mongo
    user_info = await get_mongo('user')
    database_name = await get_mongo('name')

    for user_str in user_info:
        user = user_info[user_str]
        
        for current_roll in user['Current Rolls']:
            
            if not 'End Time' in list(current_roll):
                continue

            end_time = current_roll['End Time']
            end_time = datetime.datetime.fromtimestamp(end_time)
            

            args = [
                user['Discord ID'],
                current_roll['Event Name'],
                user_info,
                database_name
            ]

            #await add_task(end_time, args)

        for current_roll in user['Cooldowns']:
            if not 'End Time' in list(current_roll):
                continue

            end_time = current_roll['End Time']
            end_time = datetime.datetime.fromtimestamp(end_time)
            

            args = [
                user['Discord ID'],
                current_roll['Event Name'],
                user_info,
                database_name
            ]

            #await add_task(end_time, args)

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
        
#         for current_roll in user['Current Rolls']:
#             if not 'End Time' in list(current_roll):
#                 continue

#             fin.append({
#                 "End Time" : current_roll['End Time'],
#                 "Event Name" : current_roll['Event Name'],
#                 "CE ID": user['CE ID']
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
#         event_name = task['Event Name']
#         user_id = task['CE ID']
        
#         if task['End Time'] <= int(time.mktime((datetime.datetime.now()).timetuple())):
#             test(user_id, event_name, -1)
#             indices.insert(0, index)
#             continue

#         date_time = datetime.datetime.utcfromtimestamp(int(task['End Time']-14400))
        
#         sched.add_job(test, 'date', run_date = date_time, args = [user_id, event_name])

#     for indice in indices:
#         tasks.pop(indice)

#     with open("./Jasons/tasks.json", "w") as f:
#         json.dump(tasks, f, indent=4)

    # sched.start()
