import sqlite3
from os import system

connection = sqlite3.connect("user.db")
c = connection.cursor()

while True:
    choice = int(
        input("1-Get chat log from number, 2-Start browsing chat logs(1/2):"))
    system("cls")

    if choice == 1:
        sql = f"SELECT chatlog FROM users WHERE number = {input('User number(with country code, without the '+'): ')}"
        try:
            c.execute(sql)
            connection.commit()
            got = c.fetchall()
        except sqlite3.OperationalError as e:
            print(e)
            continue
        print(got)

    else:
        while True:
            system("cls")
            sql = "SELECT chatlog FROM users"
            c.execute(sql)
            connection.commit()
            got = c.fetchone()
            try:
                if got == prev_got:
                    break
            except NameError:
                pass
            prev_got = got
            for text in got[0].split("¡"):
                print(text)
            input("\n\nPress enter to continue...")
        print("You have gone through all the users.")
        input("Press enter to continue...")
