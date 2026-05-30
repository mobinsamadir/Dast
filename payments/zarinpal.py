import requests

class AbstractPaymentGateway:
    def request_payment(self, amount, description, user_phone):
        raise NotImplementedError

    def verify_payment(self, amount, authority):
        raise NotImplementedError

class ZarinpalGateway(AbstractPaymentGateway):
    # ZARINPAL_MERCHANT_ID should be read from settings/env vars here later
    # e.g., settings.ZARINPAL_MERCHANT_ID
    # CALLBACK_URL = settings.ZARINPAL_CALLBACK_URL

    def request_payment(self, amount, description, user_phone):
        # TODO: Implement actual HTTP request to Zarinpal sandbox/live endpoint
        # url = 'https://api.zarinpal.com/pg/v4/payment/request.json'
        # data = {
        #     "merchant_id": settings.ZARINPAL_MERCHANT_ID,
        #     "amount": amount * 10, # Convert Toman to Rial if needed
        #     "callback_url": settings.ZARINPAL_CALLBACK_URL,
        #     "description": description,
        #     "metadata": {"mobile": user_phone}
        # }
        # response = requests.post(url, json=data)
        # return response.json()
        pass

    def verify_payment(self, amount, authority):
        # TODO: Implement actual HTTP request to Zarinpal verification endpoint
        # url = 'https://api.zarinpal.com/pg/v4/payment/verify.json'
        # data = {
        #     "merchant_id": settings.ZARINPAL_MERCHANT_ID,
        #     "amount": amount * 10,
        #     "authority": authority
        # }
        # response = requests.post(url, json=data)
        # return response.json()
        pass
