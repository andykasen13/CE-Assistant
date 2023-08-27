import json
import time
import datetime

from Helper_Functions.end_time import roll_failed

from apscheduler.schedulers.background import BackgroundScheduler


sched = BackgroundScheduler()

def test(arg1, arg2, arg4, arg3, arg5):
    tasks = json.loads(open("./Jasons/tasks.json").read())
    # roll_failed(arg1, arg2, arg4, arg3)
    if arg5 == -1:
        return
    tasks.pop(arg5)
    with open("./Jasons/tasks.json", "w") as f:
        json.dump(tasks, f, indent=4)



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

    
    with open("./Jasons/tasks.json", "w") as f:
        json.dump(fin, f, indent=4)

    create_schedule(client)


def create_schedule(client):
    log_channel = client.get_channel(1141886539157221457)
    casino_channel = client.get_channel(811286469251039333)

    tasks = json.loads(open("./Jasons/tasks.json").read())
    indices = []

    #read roles from other thing then do shit with those
    for index, task in enumerate(tasks):
        event_name = task["Event Name"]
        user_id = task["CE ID"]
        
        if task['End Time'] <= int(time.mktime((datetime.datetime.now()).timetuple())):
            test(event_name, casino_channel, user_id, log_channel, -1)
            indices.insert(0, index)
            continue

        date_time = datetime.datetime.utcfromtimestamp(int(task["End Time"]-14400))
        
        sched.add_job(test, 'date', run_date = date_time, args = [event_name, casino_channel, user_id, log_channel, index])

    for indice in indices:
        tasks.pop(indice)

    with open("./Jasons/tasks.json", "w") as f:
        json.dump(tasks, f, indent=4)

    sched.start()
