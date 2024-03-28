import sqlite3
import datetime

class UserDataBase():
    def __init__(self, file_name) -> None:
        self.file_name = file_name

    def connect(self):
        try:
            # Соединение с базой данных
            conn = sqlite3.connect(self.file_name)
            return conn
        except Exception as e:
            print(f'Ошибка при подключении к {self.file_name}\n Ошибка: {e}')


    def add_column(self, column_name: str, type: str):
        conn = self.connect()
        cursor = conn.cursor()

        # Добавляем столбец 'new_column' в таблицу 'my_table'
        cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {type}")

        conn.commit()
        conn.close()

    def del_column(self, column_name: str):
        conn = self.connect()
        cursor = conn.cursor()

        # Удаляем столбец 'old_column' из таблицы 'my_table'
        cursor.execute(f"ALTER TABLE users DROP COLUMN {column_name}")

        conn.commit()
        conn.close()

    def is_user(self, id: int) -> bool:
        # Соединение с базой данных
        try:
            conn = self.connect()

            cursor = conn.cursor()

            # Проверка наличия таблицы "users"
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if cursor.fetchone() is None:
                print("Таблица 'users' не найдена")
                cursor.close()
                conn.close()

            # Выборка всех значений столбца "id" из таблицы "users"
            cursor.execute("SELECT id FROM users")
            results = cursor.fetchall()

            # Закрытие соединения с базой данных
            cursor.close()
            conn.close()

            return (id,) in results

        except Exception as e:
            print(f'Ошибка при получении данных о пользователе в {self.file_name}\n Ошибка:{e}')

    def add_user(self, id: int):

        # Получаем текущую дату
        current_date = datetime.datetime.now().strftime("%d.%m.%Y")

        try:

            # Создаем подключение к базе данных
            conn = self.connect()

            cur = conn.cursor()

            # Создаем таблицу, если она еще не существует
            cur.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY,
                            free_trial BOOLEAN,
                            paid BOOLEAN,
                            start_free_trial TEXT
                        )''')

            # Добавляем информацию в таблицу
            cur.execute(f"INSERT INTO users (id, free_trial, paid, start_free_trial) \
                         VALUES ({id}, {True}, {False},  '{current_date}')")
            conn.commit()

            # Закрываем подключение
            conn.close()

            return True
        
        except Exception as e:

            print(f'Не удалось добавить пользователя в {self.file_name}\n Ошибка:{e}')


    def del_user(self, id:int):
        conn = self.connect()
        cursor = conn.cursor()

        column_name = 'id'
        value = id

        cursor.execute(f"DELETE FROM users WHERE {column_name} = ?", (value,))
        conn.commit()

        conn.close()
    

    def get_data(self, id: int):

        try:

            data = {}

            # Устанавливаем соединение с базой данных
            connection = self.connect()
            cursor = connection.cursor()

            # Пример значения, которое вам нужно найти
            desired_value = id  

            # Выполнение SQL запроса
            cursor.execute("SELECT * FROM users WHERE id = ?", (desired_value,))
            data = cursor.fetchone()

            # Закрываем соединение с базой данных
            cursor.close()
            connection.close()

            return data 
        
        except Exception as e:
            print(f'Не удалось получить data\n Ошибка:{e}')
        

    def change_data(self, id: int, column_name: str, new_value):

        try:

            # Устанавливаем соединение с базой данных
            connection = self.connect()
            cursor = connection.cursor()

            # SQL-запрос для поиска значения и выборки второго и третьего столбцов
            query = f"UPDATE users SET {column_name} = ? WHERE id = ?"

            # Выполняем запрос с выбранным значением
            cursor.execute(query, (new_value, id,))

            connection.commit()

            # Закрываем соединение с базой данных
            cursor.close()
            connection.close()

            return True
        
        except Exception as e:
            print(f'Не удалось изменить таблицу\n Ошибка:{e}')



    #### TEMP
    def print(self):
        # Подключаемся к базе данных
        conn = self.connect()
        cur = conn.cursor()

        # Запрос для получения информации о столбцах в таблице
        cur.execute('PRAGMA table_info(users)')

        # Получаем результат запроса
        columns = cur.fetchall()

        # Выводим названия столбцов
        for column in columns:
            print(column[1])

        # Выполняем запрос к базе данных
        cur.execute("SELECT * FROM users")

        # Получаем все строки из таблицы
        rows = cur.fetchall()

        # Выводим все строки
        for row in rows:
            print(row)

        # Закрываем соединение с базой данных
        conn.close()