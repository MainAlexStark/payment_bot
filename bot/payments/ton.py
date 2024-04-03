import requests

class TON():
    def __init__(self, api_key) -> None:
        self.api_key = api_key


    def get_order_preview(self, order_id: str):
        headers = {
        'Wpay-Store-Api-Key': self.api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        }

        response = requests.get("https://pay.wallet.tg/wpay/store-api/v1/order/" + f"order/preview?id={order_id}", headers=headers)

        data = response.json()

        if (response.status_code != 200) or (data['status'] not in ["SUCCESS", "ALREADY"]):
            print("# code: %s json: %s", response.status_code, data)
            return ''

        return data['data']


    def get_pay_link(self, user_id: str, amount: str, description: str, bot_url: str, externalId: str):
        headers = {
        'Wpay-Store-Api-Key': self.api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        }

        payload = {
        'amount': {
            'currencyCode': 'USD',  # выставляем счет в долларах США
            'amount': amount,
        },
        'description': description,
        'externalId': externalId,  # ID счета на оплату в вашем боте
        'timeoutSeconds': 300,  # время действия счета в секундах
        'customerTelegramUserId': user_id,  # ID аккаунта Telegram покупателя
        'returnUrl': bot_url,  # после успешной оплаты направить покупателя в наш бот
        'failReturnUrl': 'https://t.me/wallet',  # при отсутствии оплаты оставить покупателя в @wallet
        }

        response = requests.post(
        "https://pay.wallet.tg/wpay/store-api/v1/order",
        json=payload, headers=headers, timeout=10
        )
        data = response.json()

        if (response.status_code != 200) or (data['status'] not in ["SUCCESS", "ALREADY"]):
            print("# code: %s json: %s", response.status_code, data)
            return ''

        return data['data']['payLink']