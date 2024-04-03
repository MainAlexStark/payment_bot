import stripe
#sk_test_51P1EAC2NjvorfF0cOK7Wn4XcUEW5ww03W6kuKL8iAuBdTK929TDpY7akrrEt6GGsUjR8bMckbL323Ug9cb7IJmsZ00qs5mSuQB

# class Stripe():
#     def __init__(self, api_key:str) -> None:
#         self.api_key = api_key


#     def get_pay_link(self):
#         return stripe.PaymentLink.create(
#         line_items=[{"price": "price_1MoC3TLkdIwHu7ixcIbKelAC", "quantity": 1}],
#         )


# stripe = Stripe("sk_test_51P1EAC2NjvorfF0cOK7Wn4XcUEW5ww03W6kuKL8iAuBdTK929TDpY7akrrEt6GGsUjR8bMckbL323Ug9cb7IJmsZ00qs5mSuQB")

# print(stripe.get_pay_link())


stripe.api_key = "sk_test_51P1EAC2NjvorfF0cOK7Wn4XcUEW5ww03W6kuKL8iAuBdTK929TDpY7akrrEt6GGsUjR8bMckbL323Ug9cb7IJmsZ00qs5mSuQB"

stripe.PaymentLink.create(
  line_items=[{"price": "price_1MoC3TLkdIwHu7ixcIbKelAC", "quantity": 1}],
)