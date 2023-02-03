import sqlite3
from os import system
from time import time


def get():
    system("cls")
    num = input("User number(with country code, without the '+'):")
    try:
        sql = f"SELECT * FROM users WHERE number = {num}"
        c.execute(sql)
        connection.commit()
        got = c.fetchall()[0]
        if got == []:
            print(f"number: {num} is not on the database")
            input("Press any key to continue...")
            return False
        print(
            f"{got[0]}:\n    Status: {got[1]}\n    Token balance: {got[2]}\n    Used codes: {got[5]}\nPrompt: {got[3]}\n")
        return "SUCCESS"
    except sqlite3.OperationalError as e:
        print(f"number: {num} is not on the database")
        input("Press any key to continue...")
        return False


def change():
    system("cls")
    num = input("User number(with country code, without the '+'):")
    choice = int(input("0-Ban/1-allow:"))
    try:
        sql = f'UPDATE users SET "status" = {choice} WHERE number = {num}'
        c.execute(sql)
        connection.commit()
        return "SUCCESS"
    except sqlite3.OperationalError as e:
        print(f"number: {num} is not on the database")
        input("press any key to continue...")


def credit():
    system("cls")
    num = input("User number(with country code, without the '+'):")
    choice = int(input("Set user credits:"))
    try:
        sql = f'UPDATE users SET "balance" = {choice} WHERE number = {num}'
        c.execute(sql)
        connection.commit()
        return "SUCCESS"
    except sqlite3.OperationalError as e:
        print(f"number: {num} is not on the database")
        input("press any key to continue...")


def get_all():
    c.execute("SELECT * FROM users")
    items = c.fetchall()
    connection.commit()
    system("cls")
    for user in items:
        print(f"\n{user[0]}:")
        if user[1] == 0:
            print("    Status: BANNED")
        else:
            print("    Status: ALLOWED")
        print("    Token balance:", user[2])
        print("    Prompt:", user[3][:80], "...")
        print("    Epoch:", user[4])
    return "SUCCESS"


def exit_():
    connection.close()
    exit()


def delete():
    num = input("User number(with country code, without the '+'):")
    sql = f'DELETE FROM users WHERE number = "{num}"'
    try:
        c.execute(sql)
        connection.commit()
        return "SUCCESS"
    except sqlite3.OperationalError as e:
        print(f"number: {num} is not on the database")
        input("press any key to continue...")
    system("cls")


def add():
    num = input('User number(with country code, without the '+'):')
    balance = int(input("User credits:"))
    prompt = input("user prompt:")
    epoch = int(time()) if input(
        "seconds passed since epoch(0 for auto):") == "0" else int(input("Manual epoch:"))
    sql = f'INSERT INTO users VALUES ("{num}", 1, {balance}, "{prompt}", {epoch}, "", "")'
    c.execute(sql)
    connection.commit()
    return "SUCCESS"


options = {1: get, 2: change, 3: credit,
           4: delete, 5: add, 6: exit_, 7: get_all}
if __name__ == "__main__":
    connection = sqlite3.connect("user.db")
    c = connection.cursor()
    while True:
        system("cls")
        print("""welcome to the database management system\n\n
Please choose an option:\n    
    1-Get user\n
    2-Change user status\n
    3-Change user credits\n
    4-Delete user\n
    5-Add user\n
    6-Exit\n
    7-Get all""")
        try:
            choice = options[int(input("Your choice:"))]
        except:
            print("please select a valid option")
            input("press any key to continue...")
            continue
        # try:
        system("cls")
        response = choice()
        # except:
        #   input("An error occurred\nPress any key to continue...")
        if response == False:
            continue
        print(response)
        input("press any key to continue...")
