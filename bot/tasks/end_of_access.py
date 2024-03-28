from datetime import datetime, timedelta
from strings.en import strings
from keyboards.tasks.free_trial import free_trial_end_keyboard
from db import UserDataBase

# Функция для проверки базы данных на окончание пробного периода
async def check_trial_end(bot, days: int):
    # Подключитесь к базе данных и получите список пользователей, у которых пробный период заканчивается через 2 дня
    users_to_notify = await get_users_to_notify(days)

    # Отправьте уведомление каждому пользователю
    for user_id in users_to_notify:
        await bot.send_message(user_id, strings['end_free_trial'], free_trial_end_keyboard)

# Функция для получения списка пользователей, у которых пробный период заканчивается через 2 дня
async def get_users_to_notify(days: int):
    users_to_notify = []
    now = datetime.datetime.now()

    db = UserDataBase('DB/users.db')

    # Подключаемся к базе данных
    conn = db.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT id, start_free_trial FROM users")
    rows = cursor.fetchall()

    for row in rows:
        id = row[0]
        date_str = row[1]
        date = datetime.strptime(date_str, '%d.%m.%Y')
        if date > datetime.strptime(now, '%d.%m.%Y') + timedelta(days=days):
            users_to_notify.append(id)

    conn.close()

    # Здесь вам нужно подключиться к вашей базе данных и получить список пользователей с датами окончания пробного периода
    # Проверьте каждого пользователя, если его дата окончания пробного периода меньше чем threshold_date, добавьте его в список users_to_notify

    return users_to_notify