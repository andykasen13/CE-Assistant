import os
import getpass
import platform

# hee hee I hope this works

USER_NAME = getpass.getuser()
bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % USER_NAME


async def restart(file):
    if not os.path.isfile(bat_path + "/Boot_CE_Assistant.bat") and platform.platform() == 'Windows':
        await add_to_windows_startup(file)
    os.system("shutdown /r /t 0")


async def add_to_windows_startup(file, file_path=""):
    
    if file_path == "":
        file_path = os.path.dirname(os.path.realpath(file))

    with open(bat_path + '\\' + "Boot_CE_Assistant.bat", "w+") as bat_file:
        bat_file.write(r'''@echo off
pip install discord selenium pillow requests bs4 apscheduler pymongo motor chromedriver_binary webdriver_manager
cd %s
git pull
python main.py
pause''' % file_path)
                       




