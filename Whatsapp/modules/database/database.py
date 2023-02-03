import sqlite3
from time import time


class db:

    def __init__(self, path="user.db"):
        self.connection = sqlite3.connect(
            path, check_same_thread=False)
        self.c = self.connection.cursor()

    def get_all(self):
        self.c.execute("SELECT * FROM users")
        items = self.c.fetchall()
        self.connection.commit()
        return items

    def get(self, number):
        try:
            sql = f'SELECT * FROM users WHERE number = "{number}"'
            self.c.execute(sql)
            self.connection.commit()
            got = self.c.fetchall()
            if got == []:
                print(
                    f"[SYSTEM][DATABASE][GETUSER]: number: {number} is not on the database/get")
                return False
            return got
        except sqlite3.OperationalError as e:
            print(
                f"[SYSTEM][DATABASE][GETUSER]: number: {number} is not on the database/geterror: {e}")
            return False

    def clean_epoch(self):
        try:
            sql = f'''DELETE FROM users WHERE {int(time())} - lastactive > 25920000'''
            self.c.execute(sql)
            self.connection.commit()
            got = self.c.fetchall()
            return got
        except sqlite3.OperationalError as e:
            print(e)
            return False

    def add(self, number, status, balance, prompt):
        sql = f'INSERT INTO users VALUES ("{number}", {status}, {balance}, "{prompt}", {int(time())}, "", "")'
        self.c.execute(sql)
        self.connection.commit()
        return True

    def update(self, number, var, new_val):
        try:
            if type(new_val) == str:
                sql = f'UPDATE users SET {var} = "{new_val}" WHERE number = "{number}"'
            else:
                sql = f'UPDATE users SET {var} = {new_val} WHERE number = "{number}"'
            epoch_sql = f'UPDATE users SET lastactive = {int(time())} WHERE number = "{number}"'
            self.c.execute(sql)
            self.c.execute(epoch_sql)
            self.connection.commit()
            return True
        except sqlite3.OperationalError as e:
            print(
                f"[SYSTEM][DATABASE][UPDATEUSER]: number: {number} is not on the database/update: {e}")

    def delete(self):
        self.c.execute("DROP TABLE users")
        self.connection.commit()

    def exit(self):
        self.connection.close()
