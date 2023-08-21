import json


async def get_tasks():
    users = json.loads(open("./Jasons/users2.json").read())
    fin = {}

    for user_str in users:
        user = users[user_str]
        
        for current_roll in user["Current Rolls"]:
            fin[current_roll["End Time"]] = {
                "Event Name" : current_roll["Event Name"],
                "User CE ID": user["CE ID"]
            }
            print(current_roll)

    with open("./Jasons/tasks.json", "w") as f:
        json.dump(fin, f, indent=4)
