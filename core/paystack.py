import requests
from django.conf import settings

class Paystack:
    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.base_url = settings.PAYSTACK_URL
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

    def initialize_transaction(self, email, amount, order_id):
        """
        Initializes a transaction and returns the authorization URL.
        Amount must be in Kobo (Naira * 100).
        """
        url = f"{self.base_url}/transaction/initialize"
        
        data = {
            "email": email,
            "amount": int(amount * 100), # Convert to Kobo
            "metadata": {"order_id": order_id},
            "callback_url": "http://127.0.0.1:8000/checkout/verify/" # Frontend will handle this
        }

        try:
            response = requests.post(url, headers=self.headers, json=data)
            response_data = response.json()
            
            if response_data['status']:
                return {
                    'status': True, 
                    'auth_url': response_data['data']['authorization_url'],
                    'access_code': response_data['data']['access_code'],
                    'reference': response_data['data']['reference']
                }
            return {'status': False, 'message': response_data.get('message', 'Initialization failed')}
        except Exception as e:
            return {'status': False, 'message': str(e)}

    def verify_transaction(self, reference):
        """
        Verifies the transaction status with Paystack.
        """
        url = f"{self.base_url}/transaction/verify/{reference}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response_data = response.json()
            
            if response_data['status'] and response_data['data']['status'] == 'success':
                return {'status': True, 'amount': response_data['data']['amount']}
            return {'status': False}
        except Exception as e:
            return {'status': False, 'message': str(e)}