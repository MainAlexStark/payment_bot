import db, json
from datetime import datetime, timedelta

db_client =  db.UserDataBase('DB/users.db')

# 684124197
#6525546927
#db_client.change_data(6525546927,'free_trial' , 1)
#db_client.change_data(5221675666,'start_free_trial' , '27.03.2024')
#db_client.del_user(6525546927)
#db.add_column('paid_test_channel_2', 'TEXT')
#db_client.del_column('Crude')
db_client.print()

# получаем данные о пользователе
user_data = db_client.get_data(6525546927)

# Открываем JSON файл
with open('config.json') as file:
    config = json.load(file)
    
    # Получаем дату и приводим к нужному формату
    date_str = user_data[2]
    date = datetime.strptime(date_str, '%d.%m.%Y')
    now = datetime.now().strftime('%d.%m.%Y')

    end_data = date - timedelta(days=int(config['payment']["trial_period"])) + timedelta(days=int(config['payment']["days_notice"]))
    print(end_data)

# import requests

# def get_pay_link():
#     headers = {
#      'Wpay-Store-Api-Key': '6poiu1j8u2y4LXNnsSYt6ut99lCHdh55VT9C',
#      'Content-Type': 'application/json',
#      'Accept': 'application/json',
#     }

#     payload = {
#       'amount': {
#         'currencyCode': 'USD',  # выставляем счет в долларах США
#         'amount': '0.01',
#       },
#       'description': 'Goods and service.',
#       'externalId': '1',  # ID счета на оплату в вашем боте
#       'timeoutSeconds': 60 * 60,  # время действия счета в секундах
#       'customerTelegramUserId': '684124197',  # ID аккаунта Telegram покупателя
#       'returnUrl': 'https://t.me/mybot',  # после успешной оплаты направить покупателя в наш бот
#       'failReturnUrl': 'https://t.me/wallet',  # при отсутствии оплаты оставить покупателя в @wallet
#     }

#     response = requests.post(
#       "https://pay.wallet.tg/wpay/store-api/v1/order",
#       json=payload, headers=headers, timeout=10
#     )
#     data = response.json()

#     if (response.status_code != 200) or (data['status'] not in ["SUCCESS", "ALREADY"]):
#         print("# code: %s json: %s", response.status_code, data)
#         return ''

#     print( data['data']['payLink'])


# get_pay_link()