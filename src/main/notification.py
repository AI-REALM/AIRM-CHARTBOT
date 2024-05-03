import json, re
from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
from telegram.constants import ParseMode
from ..model.crud import *
from ..info.dext import get_token_chain_symbol
from ..info.cex import cex_info_symbol_market_pair_id, get_detailed_info
from .admin_commands import admin_notify, log_function

default_platform = {
    "bybit":"Bybit",
    "okx":"OKX",
    "gate-io":"Gate.io",
    "coinbase-exchange":"Coinbase Exchange",
    "upbit":"Upbit",
    "bitget":"Bitget",
    "kucoin":"KuCoin",
    "bitflyer":"bitFlyer",
    "gemini":"Gemini",
    "exmo":"EXMO",
    "whitebit":"WhiteBIT",
    "bitrue":"Bitrue",
    "poloniex":"Poloniex",
    "bitmart":"BitMart",
    "bithumb":"Bithumb",
    "bitfinex":"Bitfinex",
    "kraken":"Kraken",
    "BingX":"BingX",
    "binance":"Binance"
}

def escape_special_characters(text):
    # Define the pattern for special characters that need to be escaped
    pattern = r'(\\|\[|\]|\(|\)|~|>|#|\+|-|=|\||\{|\}|\.|!)'
    
    # Use the sub method from re to replace the characters with their escaped versions
    escaped_text = re.sub(pattern, r'\\\1', text)
    
    return escaped_text

def notification_handles():
    notifies = get_notify_all()
    dex_notification = {}
    cex_notification = {}
    if notifies:
        for i in notifies:
            if i.crypto_type == "D":
                if dex_notification.get(i.symbol):
                    if dex_notification[i.symbol].get(i.name):
                        if dex_notification[i.symbol][i.name].get(i.chain):
                            if dex_notification[i.symbol][i.name][i.chain].get(i.platform):
                                if dex_notification[i.symbol][i.name][i.chain][i.platform].get(i.condition):
                                    dex_notification[i.symbol][i.name][i.chain][i.platform][i.condition].append([i.chat_id, i.value, i.con_type, i.chain, i.notify_method])
                                else:
                                    dex_notification[i.symbol][i.name][i.chain][i.platform][i.condition] = [[i.chat_id, i.value, i.con_type, i.chain, i.notify_method]]
                            else:
                                dex_notification[i.symbol][i.name][i.chain][i.platform] = {
                                    i.condition: [[i.chat_id, i.value, i.con_type, i.chain, i.notify_method]]
                                }
                        else:
                            dex_notification[i.symbol][i.name][i.chain] = {
                                i.platform: {
                                    i.condition: [[i.chat_id, i.value, i.con_type, i.chain, i.notify_method]]
                                }
                            }
                    else:
                        dex_notification[i.symbol][i.name] = {
                            i.chain: {
                                i.platform: {
                                    i.condition: [[i.chat_id, i.value, i.con_type, i.chain, i.notify_method]]
                                }
                            }
                        }
                    
                else:
                    dex_notification[i.symbol] = {
                        i.name : {
                            i.chain: {
                                i.platform: {
                                    i.condition: [[i.chat_id, i.value, i.con_type, i.chain, i.notify_method]]
                                }
                            }
                        }
                    }
            else:
                id = str(i.platform)
                if cex_notification.get(id):
                    if cex_notification[id].get(i.chain):
                        if cex_notification[id][i.chain].get(i.condition):
                                cex_notification[id][i.chain][i.condition].append([i.chat_id, i.value, i.con_type, i.chain, i.notify_method])
                        else:
                            cex_notification[id][i.chain][i.condition] = [[i.chat_id, i.value, i.con_type, i.chain, i.notify_method]]
                    else:
                        cex_notification[id][i.chain] = {
                            i.condition: [[i.chat_id, i.value, i.con_type, i.chain, i.notify_method]]
                        }
                else:
                    cex_notification[id]= {
                        i.chain : {
                            i.condition: [[i.chat_id, i.value, i.con_type, i.chain, i.notify_method]]
                        }
                    }
    return cex_notification, dex_notification

def notification_current_list_dex(org_notification:dict):
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
                                            if value[2] == "M":
                                                if i.price_usd >= value[1]:
                                                    send_notification.append([value[0], f'The price of {i.base_token.name} exceeded ${value[1]} at ${i.price_usd} on {value[3]}.', i.chain_id, i.pair_address, 'D', 'P'])
                                            elif value[2] == 'L':
                                                if i.price_usd <= value[1]:
                                                    send_notification.append([value[0], f'The price of {i.base_token.name} fell below ${value[1]} to ${i.price_usd} on {value[3]}.', i.chain_id, i.pair_address, 'D', 'P'])
                                        elif condition == 'V':
                                            if value[2] == "M":
                                                if i.volume.h24 >= value[1]:
                                                    send_notification.append([value[0], f'The volume(24h) of {i.base_token.name} exceeded {value[1]} at {i.volume.h24} on {value[3]}.', i.chain_id, i.pair_address, 'D', 'V'])
                                            elif value[2] == "L":
                                                if i.volume.h24 <= value[1]:
                                                    send_notification.append([value[0], f'The volume(24h) of {i.base_token.name} fell below {value[1]} at {i.volume.h24} on {value[3]}.', i.chain_id, i.pair_address, 'D', 'V'])
                                        elif condition == 'L':
                                            if value[2] == "M":
                                                if i.liquidity.usd >= value[1]:
                                                    send_notification.append([value[0], f'The liquidity of {i.base_token.name} exceeded ${value[1]} at ${i.liquidity.usd} on {value[3]}.', i.chain_id, i.pair_address, 'D', 'L'])
                                            elif value[2] == "L":
                                                if i.liquidity.usd >= value[1]:
                                                    send_notification.append([value[0], f'The liquidity of {i.base_token.name} fell below ${value[1]} at ${i.liquidity.usd} on {value[3]}.', i.chain_id, i.pair_address, 'D', 'L'])
                                            
                    else:   
                        pass
                else:
                    pass
    return send_notification

def notification_current_list_cex(org_notification:dict):
    send_notification = []
    for symbol_id in org_notification.keys():
        name, info = cex_info_symbol_market_pair_id(id=int(symbol_id))
        detailed_info = get_detailed_info(id=int(symbol_id))
        if name:
           for exchange in org_notification[symbol_id].keys():
               for condition in org_notification[symbol_id][exchange].keys():
                    for value in org_notification[symbol_id][exchange][condition]:
                        qutoes_price = [0, 0]
                        qutoes_volume = [0, 0]
                        for i in info[exchange]:
                            if qutoes_price[1] > i["quote"]["USD"]["price"]:
                                qutoes_price[1] = i["quote"]["USD"]["price"]
                            elif qutoes_price[0] < i["quote"]["USD"]["price"]:
                                qutoes_price[0] = i["quote"]["USD"]["price"]
                            
                            if qutoes_volume[1] > i["quote"]["USD"]["volume_24h"]:
                                qutoes_volume[1] = i["quote"]["USD"]["volume_24h"]
                            elif qutoes_volume[0] < i["quote"]["USD"]["volume_24h"]:
                                qutoes_volume[0] = i["quote"]["USD"]["volume_24h"]

                        if condition == 'P':
                            if value[2] == 'M':
                                if qutoes_price[0] >= value[1]:
                                    send_notification.append([value[0], f'The price of {name[0]} exceeded ${round(i["quote"]["USD"]["price"],3)} at ${round(value[1],3)} on {default_platform[value[3]]}.', i["market_pair_base"]["currency_id"], i["exchange"]["slug"], 'C', 'P'])
                            elif value[2] == 'L':
                                if qutoes_price[1] <= value[1]:
                                    send_notification.append([value[0], f'The price of {name[0]} fell below ${round(value[1],3)} to ${round(i["quote"]["USD"]["price"],3)} on {default_platform[value[3]]}.', i["market_pair_base"]["currency_id"], i["exchange"]["slug"], 'C', 'P'])
                        elif condition == 'V':
                            if value[2] == 'M':
                                if qutoes_volume[0] >= value[1]:
                                    send_notification.append([value[0], f'The volume(24h) of {name[0]} exceeded ${round(i["quote"]["USD"]["volume_24h"],3)} at ${round(value[1],3)} on {default_platform[value[3]]}.', i["market_pair_base"]["currency_id"], i["exchange"]["slug"], 'C', 'V'])
                            elif value[2] == 'L':
                                if qutoes_volume[1] <= value[1]:
                                    send_notification.append([value[0], f'The volume(24h) of {name[0]} fell below ${round(value[1],3)} to ${round(i["quote"]["USD"]["volume_24h"],3)} on {default_platform[value[3]]}.', i["market_pair_base"]["currency_id"], i["exchange"]["slug"], 'C', 'V'])
                        elif condition == 'S':
                            if value[2] == 'M':
                                if detailed_info["total_supply"] >= value[1]:
                                    send_notification.append([value[0], f'The supply of {name[0]} exceeded ${round(detailed_info["total_supply"],3)} at ${round(value[1],3)} on {default_platform[value[3]]}.', i["market_pair_base"]["currency_id"], i["exchange"]["slug"], 'C', 'S'])
                            elif value[2] == 'L':
                                if detailed_info["total_supply"] <= value[1]:
                                    send_notification.append([value[0], f'The supply of {name[0]} fell below ${round(value[1],3)} to ${round(detailed_info["total_supply"],3)} on {default_platform[value[3]]}.', i["market_pair_base"]["currency_id"], i["exchange"]["slug"], 'C', 'S'])
                        elif condition == 'M':
                            if value[2] == 'M':
                                if detailed_info["quote"]["USD"]["market_cap"] >= value[1]:
                                    send_notification.append([value[0], f'The market cap of {name[0]} exceeded ${round(detailed_info["quote"]["USD"]["market_cap"],3)} at ${round(value[1],3)} on {default_platform[value[3]]}.', i["market_pair_base"]["currency_id"], i["exchange"]["slug"], 'C', 'M'])
                            elif value[2] == 'L':
                                if detailed_info["quote"]["USD"]["market_cap"] <= value[1]:
                                    send_notification.append([value[0], f'The market cap of {name[0]} fell below ${round(value[1],3)} to ${round(detailed_info["quote"]["USD"]["market_cap"],3)} on {default_platform[value[3]]}.', i["market_pair_base"]["currency_id"], i["exchange"]["slug"], 'C', 'M'])
                        
        return send_notification

async def send_notifications_to_users(cex_send_notifications:list, dex_send_notifications:list, context: ContextTypes.DEFAULT_TYPE):
    send_messages = {}
    for i in dex_send_notifications:
        if i[4] == 'V':
            callback_data=f'i_{i[4]}X_{i[2]}_{i[3]}_1D'
        else:
            callback_data=f'i_{i[4]}X_{i[2]}_{i[3]}_1D'
        if send_messages.get(str(i[0])):
            send_messages[str(i[0])].append([i[1], callback_data])
        else:
            send_messages[str(i[0])] = [[i[1], callback_data]]

    for i in cex_send_notifications:
        if i[4] == 'V':
            callback_data=f'i_{i[4]}X_{i[2]}_{i[3]}_1D'
        else:
            callback_data=f'i_{i[4]}X_{i[2]}_{i[3]}_1D'
        if send_messages.get(str(i[0])):
            send_messages[str(i[0])].append([i[1], callback_data])
        else:
            send_messages[str(i[0])] = [[i[1], callback_data]]
    
    for users  in send_messages.keys():
        keyboard = []
        reply_text = "⏰ Notification Message\nHello, the status of the following cryptocurrencies has been updated.\n\n"
        for i, noti in enumerate(send_messages[users]):
            keyboard.append(InlineKeyboardButton(text = f'{i+1}', callback_data=noti[1]))
            reply_text = reply_text + f'{i+1}: ' + noti[0] +'\n'
        
        reply_markup = InlineKeyboardMarkup([keyboard])
        log_function(log_type='notification', chat_id=users, chain_id="", chain_address="", result='Succesfully')
        await context.bot.send_message(
            chat_id=int(users), 
            text=escape_special_characters(reply_text),
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN_V2
        )

async def send_message(context: ContextTypes.DEFAULT_TYPE):
    cex_notification, dex_notification = notification_handles()
    dex_send_notifications = notification_current_list_dex(org_notification=dex_notification)
    cex_send_notifications = notification_current_list_cex(org_notification=cex_notification)
    await send_notifications_to_users(cex_send_notifications=cex_send_notifications, dex_send_notifications=dex_send_notifications, context=context)