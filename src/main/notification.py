import json, re
from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
from telegram.constants import ParseMode
from ..model.crud import *
from ..info.dext import get_token_chain_symbol
from .admin_commands import admin_notify, log_function

def escape_special_characters(text):
    # Define the pattern for special characters that need to be escaped
    pattern = r'(\\|\[|\]|\(|\)|~|>|#|\+|-|=|\||\{|\}|\.|!)'
    
    # Use the sub method from re to replace the characters with their escaped versions
    escaped_text = re.sub(pattern, r'\\\1', text)
    
    return escaped_text

def notification_handles():
    notifies = get_notify_all()
    org_notification = {}
    if notifies:
        for i in notifies:
            if org_notification.get(i.symbol):
                if org_notification[i.symbol].get(i.name):
                    if org_notification[i.symbol][i.name].get(i.chain):
                        if org_notification[i.symbol][i.name][i.chain].get(i.platform):
                            if org_notification[i.symbol][i.name][i.chain][i.platform].get(i.condition):
                                org_notification[i.symbol][i.name][i.chain][i.platform][i.condition].append([i.chat_id, i.value, i.notify_method])
                            else:
                                org_notification[i.symbol][i.name][i.chain][i.platform][i.condition] = [[i.chat_id, i.value, i.notify_method]]
                        else:
                            org_notification[i.symbol][i.name][i.chain][i.platform] = {
                                i.condition: [[i.chat_id, i.value, i.notify_method]]
                            }
                    else:
                        org_notification[i.symbol][i.name][i.chain] = {
                            i.platform: {
                                i.condition: [[i.chat_id, i.value, i.notify_method]]
                            }
                        }
                else:
                    org_notification[i.symbol][i.name] = {
                        i.chain: {
                            i.platform: {
                                i.condition: [[i.chat_id, i.value, i.notify_method]]
                            }
                        }
                    }
                
            else:
                org_notification[i.symbol] = {
                    i.name : {
                        i.chain: {
                            i.platform: {
                                i.condition: [[i.chat_id, i.value, i.notify_method]]
                            }
                        }
                    }
                }
    
    return org_notification

def notification_current_list(org_notification:dict):
    send_notification = []
    for symbol in org_notification.keys():
        info = get_token_chain_symbol(chain=symbol)
        for i in info:
            if i.price_change.m5 != 0:
                if i.base_token.symbol == symbol:
                    if i.base_token.name in list(org_notification[symbol].keys()):
                        if i.chain_id in list(org_notification[symbol][i.base_token.name].keys()):
                            if i.dex_id in list(org_notification[symbol][i.base_token.name][i.chain_id].keys()):
                                for condition in org_notification[symbol][i.base_token.name][i.chain_id][i.dex_id].keys():
                                    for value in org_notification[symbol][i.base_token.name][i.chain_id][i.dex_id][condition]:
                                        if condition == 'P':
                                            if i.price_usd >= value[1]:
                                                send_notification.append([value[0], f'The price of {i.base_token.name} exceeded ${value[1]} at ${i.price_usd}.', i.chain_id, i.pair_address, 'P'])
                                        elif condition == 'V':
                                            if i.volume.h24 >= value[1]:
                                                send_notification.append([value[0], f'The volume(24h) of {i.base_token.name} exceeded {value[1]} at {i.volume.h24}.', i.chain_id, i.pair_address, 'V'])
                                        elif condition == 'L':
                                            if i.liquidity.usd >= value[1]:
                                                send_notification.append([value[0], f'The liquidity of {i.base_token.name} exceeded ${value[1]} at ${i.liquidity.usd}.', i.chain_id, i.pair_address, 'L'])
                    else:
                        pass
                else:
                    pass
    return send_notification

async def send_notifications_to_users(send_notifications:list, context: ContextTypes.DEFAULT_TYPE):
    for i in send_notifications:
        keyboard = []
        if i[4] == 'V':
            keyboard.append([InlineKeyboardButton(text = 'ℹ More Information', callback_data=f'i_DX_{i[2]}_{i[3]}_1D')])
        else:
            keyboard.append([InlineKeyboardButton(text = 'ℹ More Information', callback_data=f'i_DX_{i[2]}_{i[3]}_5m')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        log_function(log_type='notification', chat_id=i[0], chain_id=i[2], chain_address=i[3], result='Succesfully')
        await context.bot.send_message(
            chat_id=i[0], 
            text=escape_special_characters(i[1]),
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN_V2
        )

async def send_message(context: ContextTypes.DEFAULT_TYPE):
    org_notification = notification_handles()
    send_notifications = notification_current_list(org_notification=org_notification)
    await send_notifications_to_users(send_notifications=send_notifications, context=context)