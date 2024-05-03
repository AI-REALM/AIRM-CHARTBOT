import json, re
from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
from telegram.constants import ParseMode
from ..model.crud import *
from ..info.dext import get_token_chain_symbol
from ..info.cex import cex_info_symbol_market_pair

# Chains that users can select
default_chain = {
    'ethereum':'Ethereum',
    'solana':'Solana',
    'bsc':'BSC',
    'arbitrum':'arbitrum',
    'polygon':'Polygon',
    'base':'Base',
    'optimism':'Optimism',
    'avalanche':'Avalanche',
    'zksync':'zkSync',
    'pulsechain':'PulseChain',
    'mantle':'Mantle',
    'sui':'Sui',
    'osmosis':'Osmosis',
    'manta':'Manta',
    'canto':'Canto',
    'aptos':'Aptos',
    'metis':'Metis',
    'scroll':'Scroll',
    'linea':'Linea',
    'oasissapphire':'Oasis Sapphire',
    'fantom':'Fantom',
    'cronos':'Cronos',
    'mode':'Mode',
    'celo':'Celo',
    'sei':'Sei',
    'moonbeam':'Moonbeam',
    'kava':'Kava',
    'zetachain':'ZetaChain',
    'core':'Core',
    'astar':'Astar',
    'polygonzkevm':'Polygon zkEVM',
    'conflux':'Conflux',
    'starknet':'Starknet',
    'near':'NEAR',
    'filecoin':'Filecoin',
    'godwoken':'Godwoken',
    'smartbch':'SmartBCH',
    'flare':'Flare',
    'gnosischain':'Gnosis Chain',
    'evmos':'Evmos',
    'aurora':'Aurora',
    'injective':'Injective',
    'beam':'Beam',
    'arbitrumnova':'Arbitrum Nova',
    'acala':'Acala',
    'zkfair':'ZKFair',
    'opbnb':'opBNB',
    'telos':'Telos',
    'avalanchedfk':'Avalanche DFK',
    'goerli':'Goerli',
    'moonriver':'Moonriver',
    'iotex':'IoTeX',
    'kcc':'KCC',
    'wanchain':'Wanchain',
    'boba':'Boba',
    'velas':'Velas',
    'okc':'OKC',
    'elastos':'Elastos',
    'meter':'Meter',
    'shibarium':'Shibarium',
    'ethereumclassic':'Ethereum Classic',
    'neonevm':'Neon EVM',
    'sxnetwork':'SX Network',
    'fuse':'Fuse',
    'oasisemerald':'Oasis Emerald',
    'harmony':'Harmony',
    'tombchain':'Tomb Chain',
    'milkomedacardano':'Milkomedacardano',
    'stepnetwork':'Step Network',
    'thundercore':'ThunderCore',
    'dogechain':'Dogechain',
    'bitgert':'Bitgert',
    'ethereumpow':'EthereumPoW',
    'loopnetwork':'Loop Network',
    'energi':'Energi',
    'kardiachain':'KardiaChain',
    'combo':'COMBO',
    'redlightchain':'Redlight Chain',
    'syscoin':'Syscoin',
    'ethereumfair':'EthereumFair'
}

default_condition = {
  'P': 'Price', 
  'V': 'Volume(24h)',
  'L': 'Liquidity',
  'M': 'MarketCap'
}

default_con_type = {
  'M': 'More', 
  'L': 'Less',
  'C': 'Change'
}

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

def get_exact_name_symbol(symbol:str):
    info = get_token_chain_symbol(chain=symbol)
    cryptos = []
    for i in info:
        if [i.base_token.name, i.base_token.symbol] in cryptos:
            pass
        else:
            cryptos.append([i.base_token.name, i.base_token.symbol])
    keyboard = []
    for i in range(0, len(cryptos), 2):
        title1 = f'{cryptos[i][0]}, {cryptos[i][1]}'
        call_back1 = f'N_A_D_{cryptos[i][0]}_{cryptos[i][1]}'
        try:
            title2 = f'{cryptos[i+1][0]}, {cryptos[i+1][1]}'
            call_back2 = f'N_A_D_{cryptos[i+1][0]}_{cryptos[i+1][1]}'
            keyboard.append([InlineKeyboardButton(title1, callback_data=call_back1), InlineKeyboardButton(title2, callback_data=call_back2)])
        except:
            keyboard.append([InlineKeyboardButton(title1, callback_data=call_back1)])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f'N_A_{symbol}'), InlineKeyboardButton("✖ Cancel", callback_data='settings_notify')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    if cryptos:
        return True, reply_markup
    else:
        return False, reply_markup

def get_exact_basic_chain(name:str, symbol:str):
    info = get_token_chain_symbol(chain=symbol)
    chains = []
    for i in info:
        if i.base_token.name == name and i.base_token.symbol == symbol:
            if i.chain_id in chains:
                pass
            else:
                chains.append(i.chain_id)
    keyboard = []
    for i in range(0, len(chains), 2):
        title1 = f'{default_chain[chains[i]]}'
        call_back1 = f'N_A_D_N_S_{chains[i]}'
        try:
            title2 = f'{default_chain[chains[i+1]]}'
            call_back2 = f'N_A_D_N_S_{chains[i+1]}'
            keyboard.append([InlineKeyboardButton(title1, callback_data=call_back1), InlineKeyboardButton(title2, callback_data=call_back2)])
        except:
            keyboard.append([InlineKeyboardButton(title1, callback_data=call_back1)])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f'N_A_D_{symbol}'), InlineKeyboardButton("✖ Cancel", callback_data='settings_notify')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    return reply_markup

def get_exact_platform(name:str, symbol:str, chain:str):
    info = get_token_chain_symbol(chain=symbol)
    platforms = []
    for i in info:
        if i.base_token.name == name and i.base_token.symbol == symbol and i.chain_id == chain:
            if i.dex_id in platforms:
                pass
            else:
                platforms.append(i.dex_id)
    keyboard = []
    for i in range(0, len(platforms), 3):
        rows = []
        for y in range(0,3):
            try:
                title = f'{platforms[i+y]}'
                call_back = f'N_A_D_N_S_C_{platforms[i+y]}'
                rows.append(InlineKeyboardButton(title, callback_data=call_back))
            except:
                break
        keyboard.append(rows)
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f'N_A_D_{name}_{symbol}'), InlineKeyboardButton("✖ Cancel", callback_data='settings_notify')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    return reply_markup

def get_extract_exchange_symbol(symbol:str):
    name, info = cex_info_symbol_market_pair(symbol=symbol)
    keyboard = []
    if not name:
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f'N_A_{symbol}'), InlineKeyboardButton("✖ Cancel", callback_data='settings_notify')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        return False, reply_markup
    else:        
        keys = list(info.keys())
        
        for i in range(0, len(keys), 3):
            rows = []
            for y in range(0,3):
                try:
                    title = f'{info[keys[i+y]][0]["exchange"]["name"]}'
                    call_back = f'N_A_C_{name[0]}_{info[keys[i+y]][0]["market_pair_base"]["exchange_symbol"]}_{info[keys[i+y]][0]["exchange"]["slug"]}_{name[1]}'
                    rows.append(InlineKeyboardButton(title, callback_data=call_back))
                except:
                    break
            keyboard.append(rows)
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f'N_A_{info[keys[0]][0]["market_pair_base"]["exchange_symbol"]}'), InlineKeyboardButton("✖ Cancel", callback_data='settings_notify')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        return True, reply_markup
    

async def notification_details_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.callback_query.message  # Get the message object
    chat_id = message.chat_id
    user = get_user_by_id(chat_id)
    if not user:
        user = create_user(chat_id)
    query = update.callback_query
    commands = query.data.split("_")

    notify = get_notify_by_id(notify_id=int(commands[-1]))
    keyboard = []
    keyboard.append([
        InlineKeyboardButton("🔙 Back to the list", callback_data=f'settings_notify'),
        InlineKeyboardButton("📝 Edit notification", callback_data=f'N_E_{int(commands[-1])}')
    ])
    reply_markup = InlineKeyboardMarkup(keyboard)
    if notify.crypto_type == "D":
        reply_text = f'*{notify.name}*\n\n*Exchange Type:* DEX\n*Symbol:* {notify.symbol}\n*Chain:* {default_chain[notify.chain]}\n*DEX Platform*: {notify.platform}\n*Monitored Item:* {default_condition[notify.condition]} ({default_con_type[notify.con_type]})\n*Limited Value:* {notify.value}\n*Notification Type:* {'Telegram' if notify.notify_method == 'T' else 'Email'}\n'
    else:
        reply_text = f'*{notify.name}*\n\n*Exchange Type:* CEX\n*Symbol:* {notify.symbol}\n*Exchange:* {default_platform[notify.chain]}\n*Monitored Item:* {default_condition[notify.condition]} ({default_con_type[notify.con_type]})\n*Limited Value:* {notify.value}\n*Notification Type:* {'Telegram' if notify.notify_method == 'T' else 'Email'}\n'
    await message.edit_text(
        text= escape_special_characters(reply_text),
        reply_markup=reply_markup, 
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_web_page_preview=True
    )

# Define the Indicators command callback function
async def notification_edit_calling_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Define the response message and buttons
    message = update.callback_query.message  # Get the message object
    chat_id = message.chat_id
    user = get_user_by_id(chat_id)
    if not user:
        user = create_user(chat_id)
    query = update.callback_query
    commands = query.data.split("_")
    user_status = user.status.split("_")
    if len(commands) == 3:
        notify_id = int(commands[2])

        notify = get_notify_by_id(notify_id=notify_id)
        keyboard = []
        keyboard.append([
            InlineKeyboardButton("📊 Monitored Item", callback_data=f'N_E_{notify.crypto_type}_C_{int(notify_id)}'),
            InlineKeyboardButton("🌊 Limited Value", callback_data=f'N_E_{notify.crypto_type}_V_{int(notify_id)}'),
        ])
        keyboard.append([
            InlineKeyboardButton("🗑 Delete", callback_data=f'N_E_D_{int(notify_id)}'),
            InlineKeyboardButton("🔙 Back to the list", callback_data=f'settings_notify')                
        ])
        reply_markup = InlineKeyboardMarkup(keyboard)
        if notify.crypto_type == "D":
            reply_text = f'*Edit {notify.name} notification info*\n\n*Exchange Type:* DEX\n*Symbol:* {notify.symbol}\n*Chain:* {default_chain[notify.chain]}\n*DEX Platform*: {notify.platform}\n*Monitored Item:* {default_condition[notify.condition]} ({default_con_type[notify.con_type]})\n*Limited Value:* {notify.value}\n*Notification Type:* {'Telegram' if notify.notify_method == 'T' else 'Email'}\n'
        else:
            reply_text = f'*Edit {notify.name} notification info*\n\n*Exchange Type:* CEX\n*Symbol:* {notify.symbol}\n*Exchange:* {default_platform[notify.chain]}\n*Monitored Item:* {default_condition[notify.condition]} ({default_con_type[notify.con_type]})\n*Limited Value:* {notify.value}\n*Notification Type:* {'Telegram' if notify.notify_method == 'T' else 'Email'}\n'
        await message.edit_text(
            text= escape_special_characters(reply_text),
            reply_markup=reply_markup, 
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True
        )

    elif len(commands) == 5:
        role = commands[2]
        name = commands[3]
        notify_id = commands[4]
        
        user = update_status(id=chat_id, status=f"N_E_{role}_{name}_{notify_id}_{message.message_id}")
        if name == 'C':
            keyboard = []
            if role == "D":
                keyboard.append([
                    InlineKeyboardButton("Price", callback_data=f'N_E_{role}_C_P_{int(notify_id)}'), 
                    InlineKeyboardButton("Volume(24h)", callback_data=f'N_E_{role}_C_V_{int(notify_id)}'),
                    InlineKeyboardButton("Liquidity", callback_data=f'N_E_{role}_C_L_{int(notify_id)}')
                ])
            else:
                keyboard.append([
                    InlineKeyboardButton("Price", callback_data=f'N_E_{role}_C_P_{int(notify_id)}'), 
                    InlineKeyboardButton("Volume(24h)", callback_data=f'N_E_{role}_C_V_{int(notify_id)}'),
                    InlineKeyboardButton("Supply", callback_data=f'N_E_{role}_C_L_{int(notify_id)}'),
                    InlineKeyboardButton("Market Cap", callback_data=f'N_E_{role}_C_L_{int(notify_id)}')
                ])
            keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f'N_E_{int(notify_id)}')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            reply_text = f'Please choose new item you like to monitor.'
            await message.edit_text(
                text= escape_special_characters(reply_text),
                reply_markup=reply_markup, 
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
        elif name == 'V':
            user = update_status(id=chat_id, status=f"N_E_{role}_V_{int(notify_id)}_{message.message_id}")
            keyboard = []
            keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f'N_E_{int(notify_id)}')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            reply_text = f'Please enter new limit values for this condition.'
            await message.edit_text(
                text= escape_special_characters(reply_text),
                reply_markup=reply_markup, 
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
        elif name == 'D':
            keyboard = []
            keyboard.append([InlineKeyboardButton("No", callback_data=f'N_E_{int(notify_id)}'), InlineKeyboardButton("Yes", callback_data=f'N_E_{role}_D_Y_{int(notify_id)}')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            reply_text = f'Are you sure you want to delete this notification?'
            await message.edit_text(
                text= escape_special_characters(reply_text),
                reply_markup=reply_markup, 
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
        
    elif len(commands) == 6:
        role = commands[2]
        name = user_status[3]
        method = commands[4]
        notify_id = commands[5]
        
        if name == 'C':
            user = update_status(id=chat_id, status=f"N_E_{role}_{name}_{method}_{notify_id}_{message.message_id}")
            keyboard = []
            keyboard.append([
                InlineKeyboardButton("More", callback_data=f'N_E_{role}_C_{method}_M_{int(notify_id)}'), 
                InlineKeyboardButton("Less", callback_data=f'N_E_{role}_C_{method}_L_{int(notify_id)}')
            ])
            reply_markup = InlineKeyboardMarkup(keyboard)
            reply_text = f'Select the condition type.'
            await message.edit_text(
                text=escape_special_characters(reply_text),
                reply_markup=reply_markup, 
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
        elif name == 'V':
            user = update_status(id=chat_id, status=f"N_E_{role}_{name}_{method}_{notify_id}_{message.message_id}")
            keyboard = []
            keyboard.append([InlineKeyboardButton("No", callback_data=f'N_E_{role}_C_{int(notify_id)}'), InlineKeyboardButton("Yes", callback_data=f'N_E_{role}_V_{method}_Y_{int(notify_id)}')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            reply_text = f'Are you sure you want to change the limited value to {method}?'
            await message.edit_text(
                text=escape_special_characters(reply_text),
                reply_markup=reply_markup, 
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
        elif name == 'D':
            notify = delete_notification(notify_id=int(notify_id))
            user = update_status(id=chat_id, status=f"Notification")
            keyboard = []
            keyboard.append([InlineKeyboardButton("🔙 Back to the notification list", callback_data=f'settings_notify')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            reply_text = f'{'Successfully deleted the notification.' if notify else 'Failed to delete notification.'}'
            await message.edit_text(
                text=escape_special_characters(reply_text),
                reply_markup=reply_markup, 
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )

    elif len(commands) == 7:
        role = commands[2]
        condition = commands[3]
        value = commands[4]
        check = commands[5]
        notify_id = commands[6]

        if condition == 'C':
            user = update_status(id=chat_id, status=f"N_E_{role}_{condition}_{value}_{check}_{notify_id}_{message.message_id}")
            keyboard = []
            keyboard.append([InlineKeyboardButton("No", callback_data=f'N_E_{role}_C_{int(notify_id)}'), InlineKeyboardButton("Yes", callback_data=f'N_E_{role}_C_{value}_{check}_Y_{int(notify_id)}')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            reply_text = f'Are you sure you want to change the monitored item to {default_condition[value]} ({default_con_type[check]})?'
            await message.edit_text(
                text= escape_special_characters(reply_text),
                reply_markup=reply_markup, 
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
        elif condition == 'V':
            notify = change_value(notify_id=int(notify_id), value=float(value))
            user = update_status(id=chat_id, status=f"notification")
            keyboard = []
            keyboard.append([InlineKeyboardButton("🔙 Back to the notification list", callback_data=f'settings_notify')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            reply_text = f'{'Successfully changed the limited value.' if notify else 'Failed to change notification limited value.'}'
            await message.edit_text(
                text= escape_special_characters(reply_text),
                reply_markup=reply_markup, 
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
    elif len(commands) == 8:
        role = commands[2]
        condition = commands[3]
        value = commands[4]
        value2 = commands[5]
        check = commands[6]
        notify_id = commands[7]

        if condition == 'C':
            notify = change_condition(notify_id=int(notify_id), condition=value, con_type= value2)
            user = update_status(id=chat_id, status=f"notification")
            keyboard = []
            keyboard.append([InlineKeyboardButton("🔙 Back to the notification list", callback_data=f'settings_notify')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            reply_text = f'{'Successfully changed the condition settings.' if notify else 'Failed to change notification condition settings.'}'
            await message.edit_text(
                text= escape_special_characters(reply_text),
                reply_markup=reply_markup, 
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )


async def notification_add_calling_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Define the response message and buttons
    message = update.callback_query.message  # Get the message object
    chat_id = message.chat_id
    user = get_user_by_id(chat_id)
    if not user:
        user = create_user(chat_id)
    query = update.callback_query

    commands = query.data.split("_")
    user_status = user.status.split("_")

    # 1st Step: Enter Symbol
    if len(commands) == 2:
        if commands[1] == 'AD':
            user = update_status(id=chat_id, status=f"N_AD")
            keyboard = []
            keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='settings_notify')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            reply_text = "⚠ You can no longer set notifications. If you wish to set more, please upgrade your plan to premium."
            await message.edit_text(
                text=escape_special_characters(reply_text),
                reply_markup=reply_markup, 
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
        elif commands[1] == 'A':
            user = update_status(id=chat_id, status=f"N_A_{message.message_id}")
            keyboard = []
            keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='settings_notify')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await message.edit_text(
                "Enter the cryptocurrency symbol you want to set up notifications for",
                reply_markup=reply_markup, 
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
    elif len(commands) == 3:
        symbol = commands[2]
        keyboard = []
        keyboard.append([InlineKeyboardButton("CEX", callback_data=f'N_A_C_{symbol}'), InlineKeyboardButton("DEX", callback_data=f'N_A_D_{symbol}')])
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='N_A'), InlineKeyboardButton("✖ Cancel", callback_data='settings_notify')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        reply_text = f'* Add New Alert & Notification *\n\n*Symbol:* {symbol}\n\nWhat platform do you want?'
        await message.edit_text(
            text= escape_special_characters(reply_text), 
            reply_markup=reply_markup, 
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True
        )
    elif len(commands) == 4:
        role = commands[2]
        symbol = commands[3]
        user = update_status(id=chat_id, status=f"N_A_{role}_{symbol}_{message.message_id}")
        if role == "D":
            res, reply_markup = get_exact_name_symbol(symbol=symbol)
            if res:
                reply_text = f'* Add New Alert & Notification *\n\n*Exchange Type:* DEX\n*Symbol:* {symbol}\n\nExactly what cryptocurrency do you want? Please check.             '
            else:
                reply_text = f'* Add New Alert & Notification *\n\n*Exchange Type:* DEX\n*Symbol:* {symbol}\n\n❌This address you entered is either not available on supported exchanges or does not match a project in our search algorithm.'
            await message.edit_text(
                text=escape_special_characters(reply_text),
                reply_markup=reply_markup, 
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
        elif role == "C":
            res, reply_markup = get_extract_exchange_symbol(symbol=symbol)
            if res:
                reply_text = f'* Add New Alert & Notification❕ *\n\n*Exchange Type:* CEX\n*Symbol:* {symbol}\n\nWhich exchange would you like to use?             '
            else:
                reply_text = f'* Add New Alert & Notification *\n\n*Exchange Type:* CEX\n*Symbol:* {symbol}\n\n❌This address you entered is either not available on supported exchanges or does not match a project in our search algorithm.'
            await message.edit_text(
                text=escape_special_characters(reply_text),
                reply_markup=reply_markup, 
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
    elif len(commands) == 5:
        role = commands[2]
        name = commands[3]
        symbol = commands[4]
        user = update_status(id=chat_id, status=f"N_A_{role}_{name}_{symbol}_{message.message_id}")
        if role == "D":
            reply_markup = get_exact_basic_chain(name=name, symbol=symbol)
            reply_text = f'* Add New Alert & Notification *\n\n*Exchange Type:* DEX\n*Name:* {name}\n*Symbol:* {symbol}\n\nWhich chain would you use a cryptocurrency built on?               '
            await message.edit_text(
                text=escape_special_characters(reply_text),
                reply_markup=reply_markup, 
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
    elif len(commands) == 6:
        role = user_status[2]
        name = user_status[3]
        symbol = user_status[4]
        chain = commands[5]
        user = update_status(id=chat_id, status=f"N_A_{role}_{name}_{symbol}_{chain}_{message.message_id}")
        if role == "D":
            reply_markup = get_exact_platform(name=name, symbol=symbol, chain=chain)
            reply_text = f'* Add New Alert & Notification *\n\n*Exchange Type:* DEX\n*Name:* {name}\n*Symbol:* {symbol}\n*Chain:* {default_chain[chain]}\n\nPlease select target DEX platform?                  '
            await message.edit_text(
                text=escape_special_characters(reply_text),
                reply_markup=reply_markup, 
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
    elif len(commands) == 7:
        role = user_status[2]
        if role == "D":
            name = user_status[3]
            symbol = user_status[4]
            chain = user_status[5]
            platform = commands[6]
            user = update_status(id=chat_id, status=f"N_A_{role}_{name}_{symbol}_{chain}_{platform}_{message.message_id}")
            keyboard = []
            keyboard.append([
                InlineKeyboardButton("Price", callback_data=f'N_A_D_N_S_C_P_P'), 
                InlineKeyboardButton("Volume(24h)", callback_data=f'N_A_D_N_S_C_P_V'),
                InlineKeyboardButton("Liquidity", callback_data=f'N_A_D_N_S_C_P_L'),])
            keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f'N_A_D_N_S_{chain}'), InlineKeyboardButton("✖ Cancel", callback_data='settings_notify')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            reply_text = f'* Add New Alert & Notification *\n\n*Exchange Type:* DEX\n*Name:* {name}\n*Symbol:* {symbol}\n*Chain:* {default_chain[chain]}\n*DEX Platform*: {platform}\n\nWhich item would you like to monitor?'
            await message.edit_text(
                text=escape_special_characters(reply_text),
                reply_markup=reply_markup, 
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
        elif role == "C":
            name = commands[3]
            symbol = commands[4]
            chain = commands[5]
            platform = commands[6]
            user = update_status(id=chat_id, status=f"N_A_{role}_{name}_{symbol}_{chain}_{platform}_{message.message_id}")
            keyboard = []
            keyboard.append([
                InlineKeyboardButton("Price", callback_data=f'N_A_C_N_S_C_E_P'), 
                InlineKeyboardButton("Volume(24h)", callback_data=f'N_A_C_N_S_C_E_V'),
                InlineKeyboardButton("Supply", callback_data=f'N_A_C_N_S_C_E_S'),
                InlineKeyboardButton("Market cap", callback_data=f'N_A_C_N_S_C_E_M')
            ])
            keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f'N_A_C_{symbol}'), InlineKeyboardButton("✖ Cancel", callback_data='settings_notify')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            reply_text = f'* Add New Alert & Notification *\n\n*Exchange Type:* CEX\n*Name:* {name}\n*Symbol:* {symbol}\n*Exchange:* {default_platform[chain]}\n\nWhich item would you like to monitor?'
            await message.edit_text(
                text=escape_special_characters(reply_text),
                reply_markup=reply_markup, 
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
    elif len(commands) == 8:
        role = user_status[2]
        name = user_status[3]
        symbol = user_status[4]
        chain = user_status[5]
        platform = user_status[6]
        condition = commands[7]
        user = update_status(id=chat_id, status=f"N_A_{role}_{name}_{symbol}_{chain}_{platform}_{condition}_{message.message_id}")
        keyboard = []
        if condition == 'P':
            keyboard.append([
                InlineKeyboardButton("More", callback_data=f'{query.data}_M'), 
                InlineKeyboardButton("Less", callback_data=f'{query.data}_L'),
                InlineKeyboardButton("Changed", callback_data=f'{query.data}_C')])
        else:
            keyboard.append([
                InlineKeyboardButton("More", callback_data=f'{query.data}_M'), 
                InlineKeyboardButton("Less", callback_data=f'{query.data}_L')])

        
        if role == "D":
            keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f'{'_'.join(commands[:6])}_{platform}'), InlineKeyboardButton("✖ Cancel", callback_data='settings_notify')])
            reply_text = f'* Add New Alert & Notification *\n\n*Exchange Type:* DEX\n*Name:* {name}\n*Symbol:* {symbol}\n*Chain:* {default_chain[chain]}\n*DEX Platform*: {platform}\n*Monitored Item:* {default_condition[condition]}\n\nPlease select the conditions type.'
        else:
            keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f'N_A_C_{name}_{symbol}_{chain}_{platform}'), InlineKeyboardButton("✖ Cancel", callback_data='settings_notify')])
            reply_text = f'* Add New Alert & Notification *\n\n*Exchange Type:* CEX\n*Name:* {name}\n*Symbol:* {symbol}\n*Exchange:* {default_platform[chain]}\n*Monitored Item:* {default_condition[condition]}\n\nPlease select the conditions type.'
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.edit_text(
            text=escape_special_characters(reply_text),
            reply_markup=reply_markup, 
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True
        )
    elif len(commands) == 9:
        role = user_status[2]
        name = user_status[3]
        symbol = user_status[4]
        chain = user_status[5]
        platform = user_status[6]
        condition = user_status[7]
        con_type = commands[8]
        user = update_status(id=chat_id, status=f"N_A_{role}_{name}_{symbol}_{chain}_{platform}_{condition}_{con_type}_{message.message_id}")
        keyboard = []
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f'{'_'.join(commands[:7])}_{condition}'), InlineKeyboardButton("✖ Cancel", callback_data='settings_notify')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        if role == "D":
            reply_text = f'* Add New Alert & Notification *\n\n*Exchange Type:* DEX\n*Name:* {name}\n*Symbol:* {symbol}\n*Chain:* {default_chain[chain]}\n*DEX Platform*: {platform}\n*Monitored Item:* {default_condition[condition]} ({default_con_type[con_type]})\n\nPlease enter limit values for this condition.'
        else:
            reply_text = f'* Add New Alert & Notification *\n\n*Exchange Type:* CEX\n*Name:* {name}\n*Symbol:* {symbol}\n*Exchange:* {default_platform[chain]}\n*Monitored Item:* {default_condition[condition]} ({default_con_type[con_type]})\n\nPlease enter limit values for this condition.'
        await message.edit_text(
            text=escape_special_characters(reply_text),
            reply_markup=reply_markup, 
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True
        )
    elif len(commands) == 10:
        role = user_status[2]
        name = user_status[3]
        symbol = user_status[4]
        chain = user_status[5]
        platform = user_status[6]
        condition = user_status[7]
        con_type = commands[8]
        value = float(commands[9])
        user = update_status(id=chat_id, status=f"N_A_{role}_{name}_{symbol}_{chain}_{platform}_{condition}_{con_type}_{value}_{message.message_id}")
        keyboard = []
        keyboard.append([InlineKeyboardButton("Telegram", callback_data=f'{'_'.join(commands[:9])}_{value}_T')])
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f'{'_'.join(commands[:8])}_{con_type}'), InlineKeyboardButton("✖ Cancel", callback_data='settings_notify')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        if role == "D":
            reply_text = f'* Add New Alert & Notification *\n\n*Exchange Type:* DEX\n*Name:* {name}\n*Symbol:* {symbol}\n*Chain:* {default_chain[chain]}\n*DEX Platform*: {platform}\n*Monitored Item:* {default_condition[condition]} ({default_con_type[con_type]})\n*Limited Value:* {value}\n\nPlease choose notification type.'
        else:
            reply_text = f'* Add New Alert & Notification *\n\n*Exchange Type:* CEX\n*Name:* {name}\n*Symbol:* {symbol}\n*Exchange:* {default_platform[chain]}\n*Monitored Item:* {default_condition[condition]} ({default_con_type[con_type]})\n*Limited Value:* {value}\n\nPlease choose notification type.'
        await message.edit_text(
            text=escape_special_characters(reply_text),
            reply_markup=reply_markup, 
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True
        )
    elif len(commands) == 11:
        role = user_status[2]
        name = user_status[3]
        symbol = user_status[4]
        chain = user_status[5]
        platform = user_status[6]
        condition = user_status[7]
        con_type = user_status[8]
        value = float(commands[9])
        notify_type = commands[10]
        user = update_status(id=chat_id, status=f"N_A_{role}_{name}_{symbol}_{chain}_{platform}_{condition}_{con_type}_{value}_{notify_type}_{message.message_id}")
        keyboard = []
        keyboard.append([
            InlineKeyboardButton("🔙 Back", callback_data=f'{'_'.join(commands[:9])}_{value}'),
            InlineKeyboardButton("📝 Submit", callback_data=f'{'_'.join(commands[:9])}_V_T_S'), 
            InlineKeyboardButton("✖ Cancel", callback_data='settings_notify')
        ])
        reply_markup = InlineKeyboardMarkup(keyboard)
        if role == "D":
            reply_text = f'* Add New Alert & Notification *\n\n*Exchange Type:* DEX\n*Name:* {name}\n*Symbol:* {symbol}\n*Chain:* {default_chain[chain]}\n*DEX Platform*: {platform}\n*Monitored Item:* {default_condition[condition]}\n*Limited Value:* {value}\n*Notification Type:* {'Telegram' if notify_type == 'T' else 'Email'}\n'
        else:
            reply_text = f'* Add New Alert & Notification *\n\n*Exchange Type:* CEX\n*Name:* {name}\n*Symbol:* {symbol}\n*Exchange:* {default_platform[chain]}\n*Monitored Item:* {default_condition[condition]}\n*Limited Value:* {value}\n*Notification Type:* {'Telegram' if notify_type == 'T' else 'Email'}\n'
        await message.edit_text(
            text= escape_special_characters(reply_text),
            reply_markup=reply_markup, 
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True
        )
    elif len(commands) == 12:
        role = user_status[2]
        name = user_status[3]
        symbol = user_status[4]
        chain = user_status[5]
        platform = user_status[6]
        condition = user_status[7]
        con_type = user_status[8]
        value = float(user_status[9])
        notify_type = user_status[10]
        user = create_notification(chat_id=chat_id, crypto_type=role, name=name, symbol=symbol, chain=chain, platform=platform, condition=condition, con_type=con_type, value=value, notify_method=notify_type)
        if user:
            user = update_status(id=chat_id, status=f"Notifcation")
            keyboard = []
            keyboard.append([InlineKeyboardButton("🔙 Back to the notification list", callback_data=f'settings_notify')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            reply_text = f'New alerts and notifications have been set up successfully!'
            await message.edit_text(
                text= escape_special_characters(reply_text),
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True,
                reply_markup=reply_markup
            )
