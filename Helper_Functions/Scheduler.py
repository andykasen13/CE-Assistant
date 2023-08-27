from discord.ext import tasks
import json
import time
import datetime

from Helper_Functions.end_time import roll_failed

from apscheduler.schedulers.background import BackgroundScheduler


sched = BackgroundScheduler()

def test(arg1, arg2, arg4, arg3):
    print("yaya")

def get_tasks(client):
    users = json.loads(open("./Jasons/users2.json").read())
    fin = []

    for user_str in users:
        user = users[user_str]
        
        for current_roll in user["Current Rolls"]:
            if not 'End Time' in list(current_roll):
                continue

            fin.append({
                "End Time" : current_roll["End Time"],
                "Event Name" : current_roll["Event Name"],
                "CE ID": user["CE ID"]
            })

    # with open("./Jasons/tasks.json", "w") as f:
    #     json.dump(fin, f, indent=4)

    create_schedule(client)


def create_schedule(client):
    log_channel = client.get_channel(1141886539157221457)
    casino_channel = client.get_channel(811286469251039333)

    tasks = json.loads(open("./Jasons/tasks.json").read())
    #read roles from other thing then do shit with those
    for task in tasks:

        date_time = datetime.datetime.utcfromtimestamp(int(task["End Time"]-14400))
        event_name = task["Event Name"]
        user_id = task["CE ID"]
        sched.add_job(test, 'date', run_date = date_time, args = [event_name, casino_channel, user_id, log_channel])

    sched.start()
