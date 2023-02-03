from shutil import disk_usage
from time import sleep
from modules.database.database import db


def clean_db():
    free = disk_usage("C:").free / 1024 / 1024 / 1024
    print(
        f"[SYSTEM][DATABASE][CLEANER]:Free space on the disk: {round(free, 2)}gb")
    if free < 8:
        database = db("modules/database/user.db")
        database.clean_epoch()
        print(f"[SYSTEM][DATABASE][CLEANER]:Clenaning successful")


STATUS = False


def storage_check_clock():
    print("[SYSTEM]:CLOCK FIREUP")
    global STATUS
    if STATUS == True:
        print("[SYSTEM][DATABASE][CLEANER]:CLOCK SHUTDOWN")
        return
    print("[SYSTEM][DATABASE][CLEANER]:CLOCK STARTED")
    while True:
        for i in range(24):
            print(f"[SYSTEM][DATABASE][CLEANER]:Sleeping, hour: {i}")
            sleep(3600)
        print("[SYSTEM][DATABASE][CLEANER]:Checking free space")
        clean_db()
