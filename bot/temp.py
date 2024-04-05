import db

db =  db.UserDataBase('DB/users.db')

# 684124197
#6525546927
db.change_data(684124197,'free_trial' , False)
#db.change_data(6525546927,'start_free_trial' , '20.03.2024')
#db.del_user(6525546927)
#db.add_column('paid_test_channel_2', 'TEXT')
db.print()


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