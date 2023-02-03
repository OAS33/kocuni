import sqlite3
from os import remove

try:
    remove("user.db")
except FileNotFoundError:
    pass

connection = sqlite3.connect("user.db")
c = connection.cursor()

c.execute("""CREATE TABLE users (
        number text,
        status integer,
        balance integer,
        prompt text,
        lastactive integer,
        usedcodes text,
        chatlog text
    )""")

connection.commit()

connection.close()

print("exit")
