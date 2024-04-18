import sqlite3
from datetime import datetime, timedelta
import pandas as pd

import shutil
import os
import json

class DataBase():
    def __init__(self, file_path: str) -> None:
        self._file_path = file_path

    def _connect(self) -> None:
        conn = sqlite3.connect(self._file_path)
        return conn
    
    def execute(self, command: str):
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(command)
        result = cursor.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        return result
    
    def get(self, command: str):
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(command)
        result = cursor.fetchall()

        conn.commit()
        cursor.close()
        conn.close()

        return result
    

class DataBaseInterface():
    def __init__(self, file_path: str, table_name: str) -> None:
        self._db = DataBase(file_path=file_path)
        self._table_name = table_name

    def create(self) -> bool:

        try:

            command = '''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY,
                            start_date TEXT,
                            ref_id INTEGER,
                            num_purchases INTEGER,
                            ref_num INTEGER,
                            ref_id_user INTEGER,
                            Gasoil_Charta TEXT,
                            Crude_Oil_Charta TEXT
                        )'''
            
            self._db.execute(command=command)

            return True

        except Exception as e:
            return False
            print(f"Error create table. Error: {e}")

    def print(self) -> None:
        columns = self._db.get(f"PRAGMA table_info({self._table_name})")
        for column in columns:
            print(column[1])
        print(columns)

        rows = self._db.get(f"SELECT * FROM {self._table_name}")
        for row in rows:
            print(row)

    """ USER """
    def is_user(self, user_id: int | str) -> bool:
        command = f"SELECT * FROM {self._table_name} WHERE id = {user_id}"
        result = self._db.get(command=command)
        return len(result) > 0
    
    def add_user(self, user_id: int | str) -> bool:
        try:
            today = datetime.now().strftime("%d.%m.%Y")

            command = f"INSERT INTO {self._table_name} (id, start_date) \
                        VALUES ({user_id}, '{today}')"
            self._db.execute(command=command)

            return True

        except Exception as e:
            print(e)
            return False

    def del_user(self, user_id: int | str) -> bool:
        try:
            command = f"DELETE FROM {self._table_name} WHERE id = {user_id}"
            self._db.execute(command=command)

            return True

        except Exception as e:
            print(e)
            return False
        
    def get_users(self) -> list:
        ids = []

        command = f"SELECT id FROM {self._table_name}"
        result = self._db.get(command=command)

        for id in result: ids.append(id[0])

        return ids
        
    """ COLUMN """
    def get_column(self, user_id: int | str, column: str):
        try:
            command = f"SELECT {column} FROM {self._table_name} WHERE id = {user_id}"
            return self._db.execute(command=command)[0]
        except Exception as e:
            print(f"Error get column value. Error: {e}\ncolumn={column}, user_id={user_id}")
    
    def add_column(self, column: str, type: str) -> bool:
        try:
            command = f"ALTER TABLE {self._table_name} ADD COLUMN {column} {type}"
            self._db.execute(command=command)

            return True

        except Exception as e:
            print(e)
            return False

    def del_column(self, column: str) -> bool:
        try:
            command = f"ALTER TABLE {self._table_name} DROP COLUMN {column}"
            self._db.execute(command=command)

            return True

        except Exception as e:
            print(e)
            return False
        
    """ USER DATA"""
    def get_data(self, user_id: int | str) -> tuple:
        command = f"SELECT * FROM {self._table_name} WHERE id = {user_id}"
        return self._db.execute(command=command)
    
    def change_data(self, user_id: int | str, column: str, new_value) -> bool:
        try:
            print(f"change data. user_id={user_id}, column={column}, new_value={new_value}")
            if new_value is not None:
                command = f"UPDATE {self._table_name} SET {column} = '{new_value}' WHERE id = {user_id}"
            else:
                command = f"UPDATE {self._table_name} SET {column} = NULL WHERE id = {user_id}"
            self._db.execute(command=command)

            return True

        except Exception as e:
            print(e)
            return False

class Config():
    def __init__(self, file_path: str) -> None:
        self._file_path = file_path
    
    def get(self) -> dict:
        with open(self._file_path) as file:
            return json.load(file)
        
    def post(self, data: dict) -> bool:
        try:
            with open(self._file_path, 'w') as file:
                json.dump(data, file, indent=4)
                file.truncate()
                return True
        except Exception as e:
            print(e)
            return False


""" TEST DataBase """
file_path = 'data/Database.db'
if os.path.exists(file_path):
    db = DataBaseInterface(file_path, "users")
    #print(db.change_data(user_id='1849088118', column='start_date', new_value='01.03.2024'))
    #print(db.del_user(684124197))
    db.create()
    db.print()
    shutil.copyfile('data/Database.db', 'data/database_copy.db')
else:
    raise Exception(f'File {file_path} not found')

""" TEST Config """
file_path = 'data/config.json'
if os.path.exists(file_path):
    config_client = Config(file_path)
    config = config_client.get()
    print("CONFIG=",config)
else:
    raise Exception(f'File {file_path} not found')