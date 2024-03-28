import os, json

# Получаем путь к текущему файлу temp.py
current_path = os.path.abspath(__file__)

# Формируем путь к файлу config.json
config_path = os.path.join(os.path.dirname(current_path), '../../config.json')

# Открываем JSON файл
with open(config_path) as file:
    config = json.load(file)

string = "start_message_admin"

for dict in config['commands']['user'].values():
    for command in dict:
        string += f"\n/{command}"

print(string)
