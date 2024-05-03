import requests
import os
import re
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from ..model.crud import *
from nowpayment import NowPayments
from dotenv import load_dotenv
from ..main.admin_commands import admin_notify, log_function

load_dotenv(dotenv_path='.env')

API_KEY = os.getenv('NP_API_KEY')
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
admin = int(os.getenv('ADMIN'))

def escape_special_characters(text):
    # Define the pattern for special characters that need to be escaped
    pattern = r'(\\|\[|\]|\(|\)|~|>|#|\+|-|=|\||\{|\}|\.|!)'
    
    # Use the sub method from re to replace the characters with their escaped versions
    escaped_text = re.sub(pattern, r'\\\1', text)
    
    return escaped_text

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

    return response.json()['data']

def get_new_invoice(price):
    global API_KEY
    api = NowPayments(API_KEY)

    invoice = api.payment.create_invoice(
        price_amount=price,
        price_currency="USD",
    )
    return invoice.get("id")

async def checking_and_update_invoice(context: ContextTypes.DEFAULT_TYPE):
    users_invoice = {}
    users = get_users_invoice_enable()
    for user in users:
        users_invoice[str(user.invoice)] = user.id
    print(users_invoice)

    for invoice in users_invoice:
        status = get_status_invoice_id(invoice)
        print(status)
        for i in status:
            if i['payment_status'] == "finished":
                user = update_premium(id=users_invoice[invoice], price=i["price_amount"])
                if user:
                    reply_text = 'Congratulations! Your payment has been confirmed. Your plan has been upgraded.'
                    await context.bot.send_message(
                        chat_id=users_invoice[invoice], 
                        text=escape_special_characters(reply_text),
                        parse_mode=ParseMode.MARKDOWN_V2
                    )
                    log_function(log_type="new_premium", chat_id=users_invoice[invoice], chain_id="invoice", chain_address="confirm", result="successful")
                    await admin_notify(context=context, admin_chat_id=admin, user_chat_id=users_invoice[invoice], rquest_type='Info CX', user_input=f'Invoice, `{users_invoice[invoice]}`:`{i["price_amount"]}`', result=f'Successfully')
                    break
                else:
                    log_function(log_type="new_premium", chat_id=users_invoice[invoice], chain_id="invoice", chain_address="confirm", result="Failed in updating databse")
                    await admin_notify(context=context, admin_chat_id=admin, user_chat_id=users_invoice[invoice], rquest_type='Info CX', user_input=f'Invoice, `{users_invoice[invoice]}`:`{i["price_amount"]}`', result=f'Failed in Updateing database')
                    break