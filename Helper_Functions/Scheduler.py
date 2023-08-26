from discord.ext import tasks
import json
import time
import datetime

from Helper_Functions.end_time import roll_failed

from apscheduler.schedulers.background import BackgroundScheduler


sched = BackgroundScheduler()


def test(this, that):
    print(this + " and " + that)


def get_tasks():
    users = json.loads(open("./Jasons/users2.json").read())
    fin = {}
    datetimes = []

    for user_str in users:
        user = users[user_str]
        
        for current_roll in user["Current Rolls"]:
            if not 'End Time' in list(current_roll):
                continue

            fin[current_roll["End Time"]] = {
                "Event Name" : current_roll["Event Name"],
                "User CE ID": user["CE ID"]
            }



    # # with open("./Jasons/tasks.json", "w") as f:
    # #     json.dump(fin, f, indent=4)

    # print("Scheduled")
    # print(datetimes)
    # print(datetimes[0])


def create_schedule():
                
    #read roles from other thing then do shit with those
    
    #         date_time = datetime.datetime.utcfromtimestamp(int(current_roll["End Time"]))
    #         this = "this"
    #         that = "that"
    #         sched.add_job(test, 'date', run_date = date_time, args = [this,that])

    # sched.start()
    return

# task_dict = json.loads(open("./Jasons/tasks.json").read())
# task_list = get_tasks()



# @tasks.loop(time=task_list)
# async def process_schedule():
#     current_time = int(time.time())
#     current_dict = task_dict[current_time]

#     print(current_dict['Event Name'])
#     print(current_dict['User CE ID'])
#     # roll_failed(task_list[current_time]['Event Name'], task_list[current_time]['User CE ID'])






    
