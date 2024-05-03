import requests
import os
from nowpayment import NowPayments
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env')

API_KEY = os.getenv('NP_API_KEY')
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')

def get_jwt_token():
    global API_KEY
    global EMAIL
    global PASSWORD
    # Create a NowPayment instance
    api = NowPayments(API_KEY)
    # First we should log in using email and password
    login = api.payout.login(email=EMAIL, password=PASSWORD)
    # if the login is successful, we will get a token in the response
    # we will use this token to fill the `jwt_token` parameter
    # if not successful, we will get an error message
    if not login.get("token"):
        # raise Exception("Login failed. Check your email and password.")
        return False

    return login["token"]

def get_status_invoice_id(invoice_id):
    global API_KEY
    token = get_jwt_token()
    url = 'https://api.nowpayments.io/v1/payment/'

    headers = {
        'Authorization': f'Bearer {token}',
        'x-api-key': f'{API_KEY}',
    }

    params = {
        'limit': '500',
        'page': '0',
        'sortBy': 'created_at',
        'orderBy': 'asc',
        'invoiceId': f'{invoice_id}',
    }

    response = requests.get(url, headers=headers, params=params)

    print(response.json())
    return response.json()['data'][0]

def get_new_invoice(price):
    global API_KEY
    api = NowPayments(API_KEY)

    invoice = api.payment.create_invoice(
        price_amount=price,
        price_currency="USD",
    )
    return invoice.get("id")