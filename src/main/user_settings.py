import json, re
from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
from telegram.constants import ParseMode
from ..model.crud import *
from ..info.dext import get_token_chain_symbol

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

# Indicators that are possible
default_indicators = {
  'OBV': 'On Balance Volume', 
  'ADI': 'Accumulation/Distribution',
  'ADX': 'Average Directional Index',
  'AO': 'Aroon',
  'MACD': 'Moving Average Convergence Divergence',
  'RSI': 'Relative Strength Index',
  'SO': 'Stochastic',
  'BB': 'Bollinger Bands',
  'IC': 'Ichimoku Cloud',
  'MA': 'MA Cross',
  'MAE': 'Moving Average Exponential',
  'MAM': 'Moving Average Multiple',
  'VWAP': 'Volume Weighted Average Price',
  'VO': 'Volume Oscillator'
}

default_condition = {
  'P': 'Price', 
  'V': 'Volume\(24h\)',
  'L': 'Liquidity',
  'M': 'MarketCap'
}

def escape_special_characters(text):
    # Define the pattern for special characters that need to be escaped
    pattern = r'(\\|\[|\]|\(|\)|~|>|#|\+|-|=|\||\{|\}|\.|!)'
    
    # Use the sub method from re to replace the characters with their escaped versions
    escaped_text = re.sub(pattern, r'\\\1', text)
    
    return escaped_text

# Define the settigns command callback function
async def settings_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Define the response message and buttons
    message = update.message or update.callback_query.message  # Get the message object
    try:
        query_data = update.callback_query.data
    except:
        query_data = "settings"
    chat_id = message.chat_id
    user = get_user_by_id(chat_id)
    if not user:
        user = create_user(chat_id)
    
    keyboard = [[
        InlineKeyboardButton("📈 Indicators", callback_data='settings_indicators'),
        InlineKeyboardButton("⏳ Interval", callback_data='settings_interval'),
    ],
    [
        InlineKeyboardButton("🎨 Style", callback_data='settings_style'),
        InlineKeyboardButton("🌏 Timezone", callback_data='settings_timezone'),
    ],
    [
        InlineKeyboardButton("🔗 Default Chain", callback_data='settings_chain'),
    ],
    [
        InlineKeyboardButton("⏰ Alerts & Notification", callback_data='settings_notify'),
    ],
    [
        InlineKeyboardButton("✖ Close Settings", callback_data='close_settings')
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    keyboard = []
    if query_data == "settings_back":
        await message.edit_text(
            f'Current settings:\n\n📈 Indicators: {user.indicators if user.indicators else ""}\n⏳ Interval: {user.interval}\n🎨 Style: {user.style}\n🌏 Timezone: {user.timezone}\n🔗 Default Chain: {default_chain[user.chain]}', reply_markup=reply_markup
        )
    else:
        await message.reply_text(
            f'Current settings:\n\n📈 Indicators: {user.indicators if user.indicators else ""}\n⏳ Interval: {user.interval}\n🎨 Style: {user.style}\n🌏 Timezone: {user.timezone}\n🔗 Default Chain: {default_chain[user.chain]}', reply_markup=reply_markup
        )

# Define the Indicators command callback function
async def indicators_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Define the response message and buttons
    message = update.callback_query.message  # Get the message object
    chat_id = message.chat_id
    user = get_user_by_id(chat_id)
    if not user:
        user = create_user(chat_id) 
    user_indicators = []
    if user.indicators:
        user_indicators = user.indicators.split(",")
    keyboard = []
    keys = list(default_indicators.keys())
    for i in keys:
        rows = []
        title1 = f'✅ {default_indicators[i]}' if i in user_indicators else f'☑ {default_indicators[i]}'
        call_back1 = f'settings_indicators_{i}'
        rows.append(InlineKeyboardButton(title1, callback_data=call_back1))
        keyboard.append(rows)
    keyboard.append([InlineKeyboardButton("⬅ Back to Settings", callback_data='settings_back')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message.edit_text(
        "Which indicators do you want to use?\n<i>Tip: read more about technical indicators in <a href='https://www.investopedia.com/top-7-technical-analysis-tools-4773275'>this Investopedia article</a></i>", 
        reply_markup=reply_markup, 
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

# Define the interval command callback function
async def interval_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Define the response message and buttons
    message = update.callback_query.message  # Get the message object
    chat_id = message.chat_id
    user = get_user_by_id(chat_id)
    if not user:
        user = create_user(chat_id)
    time = ["5m", "1h","6h", "1D"]

    keyboard = []
    for i in range(0, len(time), 2):
        title1 = f'🟢 {time[i]}' if time[i] == user.interval else f'🔘 {time[i]}'
        call_back1 = f'settings_interval_{time[i]}'
        title2 = f'🟢 {time[i+1]}' if time[i+1] == user.interval else f'🔘 {time[i+1]}'
        call_back2 = f'settings_interval_{time[i+1]}'
        keyboard.append([InlineKeyboardButton(title1, callback_data=call_back1), InlineKeyboardButton(title2, callback_data=call_back2)])
    
    keyboard.append([InlineKeyboardButton("⬅ Back to Settings", callback_data='settings_back')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message.edit_text(
        "What chart interval do you want to use?", reply_markup=reply_markup
    )

# Define the style command callback function
async def style_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Define the response message and buttons
    message = update.callback_query.message  # Get the message object
    chat_id = message.chat_id
    user = get_user_by_id(chat_id)
    if not user:
        user = create_user(chat_id)
    # possible styles of charts
    styles = {
        "bar":"Bars",
        "candle":"Candles",
        "hollowCandle":"Hollow candles",
        "line":"Line",
        "lineWithMarkers":"Line with markers",
        "stepline":"Step line",
        "area":"Area",
        "hlcArea":"HLC area",
        "baseline":"Baseline",
        "hilo":"High-low",
        "ha":"Heikin Ashi"
    }

    keyboard = []
    for i in range(0, len(styles.keys()), 2):
        title1 = f'🟢 {styles[list(styles.keys())[i]]}' if list(styles.keys())[i] == user.style else f'🔘 {styles[list(styles.keys())[i]]}'
        call_back1 = f'settings_style_{list(styles.keys())[i]}'
        try:
            title2 = f'🟢 {styles[list(styles.keys())[i+1]]}' if list(styles.keys())[i+1] == user.style else f'🔘 {styles[list(styles.keys())[i+1]]}'
            call_back2 = f'settings_style_{list(styles.keys())[i+1]}'
            keyboard.append([InlineKeyboardButton(title1, callback_data=call_back1), InlineKeyboardButton(title2, callback_data=call_back2)])
        except:
            keyboard.append([InlineKeyboardButton("⬅ Back to Settings", callback_data='settings_back')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message.edit_text(
        "What chart style do you want to use?", reply_markup=reply_markup
    )

# Define the timezone command callback function
async def timezone_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Define the response message and buttons
    message = update.callback_query.message  # Get the message object
    chat_id = message.chat_id
    user = get_user_by_id(chat_id)
    if not user:
        user = create_user(chat_id)
    timezone = {
        "America/Bogota" : "(UTC-5) Bogota", 
        "America/Chicago" : "(UTC-6) Chicago", 
        "America/Los_Angeles" : "(UTC-8) LOS Angeles", 
        "America/New_York" : "(UTC-5) New york", 
        "America/Phoenix" : "(UTC-7) Phoenix", 
        "America/Toronto" : "(UTC-5) Toronto", 
        "Asia/Bahrain" : "(UTC+3) Bahrain", 
        "Asia/Bangkok" : "(UTC+7) Bangkok", 
        "Asia/Dubai" : "(UTC+4) Dubai", 
        "Asia/Hong_Kong" : "(UTC+8) Hong Kong", 
        "Asia/Kuwait" : "(UTC+3) Kuwait", 
        "Asia/Qatar" : "(UTC+3) Qatar", 
        "Asia/Shanghai" : "(UTC+8) Shanghai", 
        "Asia/Singapore" : "(UTC+8) Singapore", 
        "Asia/Taipei" : "(UTC+8) Taipei", 
        "Asia/Tehran" : "(UTC+3:30) Tehran", 
        "Asia/Tokyo" : "(UTC+9) Tokyo", 
        "Atlantic/Reykjavik" : "(UTC+0) Reykjavik", 
        "Australia/Perth" : "(UTC+8) Perth", 
        "Australia/Sydney" : "(UTC+11) Sydney", 
        "Europe/Amsterdam" : "(UTC+1) Amsterdam", 
        "Europe/Berlin" : "(UTC+1) Berlin", 
        "Europe/Brussels" : "(UTC+1) Brussels", 
        "Europe/Budapest" : "(UTC+1) Budapest", 
        "Europe/Copenhagen" : "(UTC+1) Copenhagen", 
        "Europe/London" : "(UTC+0) London", 
        "Europe/Madrid" : "(UTC+1) Madrid", 
        "Europe/Moscow" : "(UTC+3) Moscow", 
        "Europe/Oslo" : "(UTC+1) Oslo", 
        "Europe/Paris" : "(UTC+1) Paris", 
        "Europe/Rome" : "(UTC+1) Rome", 
        "Europe/Stockholm" : "(UTC+1) Stockholm", 
        "Europe/Zurich" : "(UTC+1) Zurich", 
        "Pacific/Honolulu" : "(UTC-10) Honolulu", 
        "US/Mountain" : "(UTC-7) Mountain"
    }
    keys = list(timezone.keys())
    keyboard = []
    for i in range(0, len(keys), 2):
        title1 = f'🟢 {timezone[keys[i]]}' if keys[i] == user.timezone else f'🔘 {timezone[keys[i]]}'
        call_back1 = f'settings_timezone_{keys[i]}'
        try:
            title2 = f'🟢 {timezone[keys[i+1]]}' if keys[i+1] == user.timezone else f'🔘 {timezone[keys[i+1]]}'
            call_back2 = f'settings_timezone_{keys[i+1]}'

            keyboard.append([InlineKeyboardButton(title1, callback_data=call_back1), InlineKeyboardButton(title2, callback_data=call_back2)])
        except:
            keyboard.append([InlineKeyboardButton(title1, callback_data=call_back1), InlineKeyboardButton("⬅ Back to Settings", callback_data='settings_back')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message.edit_text(
        "What timezone do you want to use?\n<i>Please note: this is only a selection of the <a href='https://www.tradingview.com/charting-library-docs/latest/ui_elements/timezones/'>supported timezones</a></i>", 
        reply_markup=reply_markup, 
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

# Define the exchange command callback function
async def chain_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Define the response message and buttons
    message = update.callback_query.message  # Get the message object
    chat_id = message.chat_id
    user = get_user_by_id(chat_id)
    if not user:
        user = create_user(chat_id)
    keyboard = []
    keys = list(default_chain.keys())
    back_button_flag = True
    for i in range(0, len(keys), 4):
        rows = []
        for y in range(0,4):
            try:
                title = f'🟢 {default_chain[keys[i+y]]}' if keys[i+y] == user.chain else f'🔘 {default_chain[keys[i+y]]}'
                call_back = f'settings_chain_{keys[i+y]}'
                rows.append(InlineKeyboardButton(title, callback_data=call_back))
            except:
                rows.append(InlineKeyboardButton("⬅ Back to Settings", callback_data='settings_back'))
                back_button_flag=False
                break
        keyboard.append(rows)

    if back_button_flag:
        keyboard.append([InlineKeyboardButton("⬅ Back to Settings", callback_data='settings_back')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message.edit_text(
        "Which chain would you like to use as the default chain?", reply_markup=reply_markup
    )

# Define the settgins update function
async def update_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.callback_query.message  # Get the message object
    chat_id = message.chat_id
    query = update.callback_query
    commands = query.data.split("_")
    if commands[1] == 'indicators':
        key = commands[2]
        indcators = list(default_indicators.keys())
        user = get_user_by_id(chat_id)
        if not user:
            user = create_user(chat_id) 
        user_indicators = []
        if user.indicators:
            user_indicators = user.indicators.split(",")
        if key in user_indicators:
            user_indicators.remove(key)
        else:
            user_indicators.append(key)
        new_indicator = []
        for i in indcators:
            new_indicator.append(i) if i in user_indicators else ""
        update_indicators(id=chat_id, indicators=','.join(new_indicator))

        await indicators_dashboard(update, context)
    elif commands[1] == 'interval':
        time = commands[2]
        update_interval(id=chat_id, interval=time)

        await interval_dashboard(update, context)
    elif commands[1] == 'style':
        style = commands[2]
        update_style(id=chat_id, style=style)

        await style_dashboard(update, context)
    elif commands[1] == 'timezone':
        timezone = commands[2::]
        update_timezone(id=chat_id, timezone="_".join(timezone))

        await timezone_dashboard(update, context)
    elif commands[1] == 'chain':
        chain = commands[2]
        update_chain(id=chat_id, chain=chain)

        await chain_dashboard(update, context)
    else:
        pass

async def handling_settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    commands = query.data.split("_")
    if len(commands) == 1:
        await settings_dashboard(update, context)
    elif len(commands) == 2:
        if commands[1] == 'back':
            await settings_dashboard(update, context)
        elif commands[1] == 'indicators':
            await indicators_dashboard(update, context)
        elif commands[1] == 'interval':
            await interval_dashboard(update, context)
        elif commands[1] == 'style':
            await style_dashboard(update, context)
        elif commands[1] == 'timezone':
            await timezone_dashboard(update, context)
        elif commands[1] == 'chain':
            await chain_dashboard(update, context)
        elif commands[1] == 'notify':
            await notification_dashboard(update, context)
    elif len(commands) >= 3:
        await update_settings(update, context)


# Define the /stats command handler
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Get today's date in the format YYYY-MM-DD
    today_date = datetime.now().strftime("%Y-%m-%d")
    user_count = count_user()
    with open("chart_log.txt", 'r', encoding='utf-8') as f:
        chart_count = len(f.readlines())
        f.close()
        
    with open("log.txt", 'r', encoding='utf-8') as f:
        imporession_count = len(f.readlines())
        f.close()
    # Define the stats message with the current date
    stats_message = (f'📊 *AI Realm stats for {today_date}:*\n\n'
                     f'💬 Groups using AI Realm Bot: *719*\n'
                     f'👤 Unique users: *{user_count}*\n'
                     f'🪄 Charts generated: *{chart_count}*\n'
                     f'👁️ User impressions: *{imporession_count + chart_count}*')
    # Send the stats message
    await update.message.reply_text(stats_message, parse_mode=ParseMode.MARKDOWN)

# Define the notification initial dashboard function
async def notification_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Define the response message and buttons
    message = update.callback_query.message  # Get the message object
    chat_id = message.chat_id
    notifies = get_notify_by_chat_id(chat_id)
    user = get_user_by_id(chat_id)
    if not user:
        user = create_user(chat_id)
    user = update_status(id=chat_id, status="DX")
    keyboard = []
    if notifies:
        for i in range(0, len(notifies), 2):
            title1 = f'{notifies[i].name}({default_chain[notifies[i].chain]}, {notifies[i].platform})'
            call_back1 = f'N_DA_{notifies[i].notify_id}'
            try:
                title2 = f'{notifies[i+1].name}({default_chain[notifies[i+1].chain]}, {notifies[i+1].platform})'
                call_back2 = f'N_DA_{notifies[i+1].notify_id}'
                keyboard.append([InlineKeyboardButton(title1, callback_data=call_back1), InlineKeyboardButton(title2, callback_data=call_back2)])
            except:
                keyboard.append([InlineKeyboardButton(title1, callback_data=call_back1)])
    
    keyboard.append([InlineKeyboardButton("➕ Add new alert", callback_data='N_add_notify'), InlineKeyboardButton("⬅ Back to Settings", callback_data='settings_back')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    text = 'Choose a notification from the list below:' if notifies else "You haven't set up any notifications!"
    await message.edit_text(
        text, 
        reply_markup=reply_markup, 
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

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
        call_back1 = f'N_D_{cryptos[i][0]}_{cryptos[i][1]}'
        try:
            title2 = f'{cryptos[i+1][0]}, {cryptos[i+1][1]}'
            call_back2 = f'N_D_{cryptos[i+1][0]}_{cryptos[i+1][1]}'
            keyboard.append([InlineKeyboardButton(title1, callback_data=call_back1), InlineKeyboardButton(title2, callback_data=call_back2)])
        except:
            keyboard.append([InlineKeyboardButton(title1, callback_data=call_back1)])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f'N_{symbol}'), InlineKeyboardButton("✖ Cancel", callback_data='settings_notify')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    return reply_markup

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
        call_back1 = f'N_D_N_S_{chains[i]}'
        try:
            title2 = f'{default_chain[chains[i+1]]}'
            call_back2 = f'N_D_N_S_{chains[i+1]}'
            keyboard.append([InlineKeyboardButton(title1, callback_data=call_back1), InlineKeyboardButton(title2, callback_data=call_back2)])
        except:
            keyboard.append([InlineKeyboardButton(title1, callback_data=call_back1)])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f'N_D_{symbol}'), InlineKeyboardButton("✖ Cancel", callback_data='settings_notify')])
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
                call_back = f'N_D_N_S_C_{platforms[i+y]}'
                rows.append(InlineKeyboardButton(title, callback_data=call_back))
            except:
                break
        keyboard.append(rows)
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f'N_D_{name}_{symbol}'), InlineKeyboardButton("✖ Cancel", callback_data='settings_notify')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    return reply_markup


# Define the Indicators command callback function
async def notification_calling_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Define the response message and buttons
    message = update.callback_query.message  # Get the message object
    chat_id = message.chat_id
    user = get_user_by_id(chat_id)
    if not user:
        user = create_user(chat_id)
    query = update.callback_query
    commands = query.data.split("_")
    user_status = user.status.split("_")
    if "N_add_notify" in query.data:
        user = update_status(id=chat_id, status=f"Add_Notify_{message.message_id}")
        keyboard = []
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='settings_notify')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.edit_text(
            "Enter the cryptocurrency symbol you want to set up notifications for",
            reply_markup=reply_markup, 
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True
        )
    elif len(commands) == 2:
        symbol = commands[1]
        keyboard = []
        keyboard.append([InlineKeyboardButton("CEX", callback_data=f'N_C_{symbol}'), InlineKeyboardButton("DEX", callback_data=f'N_D_{symbol}')])
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='N_add_notify'), InlineKeyboardButton("✖ Cancel", callback_data='settings_notify')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.edit_text(
            text=
            f'* Add New Alert & Notification *\n\n*Symbol:* {symbol}\n\nWhat platform do you want?',
            reply_markup=reply_markup, 
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True
        )
    elif len(commands) == 3:
        symbol = commands[2]
        role = commands[1]
        if role == 'DA':
            notify = get_notify_by_id(notify_id=int(symbol))
            keyboard = []
            keyboard.append([
                InlineKeyboardButton("🔙 Back to the list", callback_data=f'settings_notify'),
                InlineKeyboardButton("📝 Edit notification", callback_data=f'N_Edit_{int(symbol)}')
            ])
            reply_markup = InlineKeyboardMarkup(keyboard)
            reply_text = f'*{notify.name}*\n\n*Exchange Type:* DEX\n*Symbol:* {notify.symbol}\n*Chain:* {default_chain[notify.chain]}\n*DEX Platform*: {notify.platform}\n*Monitored Item:* {default_condition[notify.condition]}\n*Limited Value:* {notify.value}\n*Notification Type:* {'Telegram' if notify.notify_id == 'T' else 'Email'}\n'
            await message.edit_text(
                text= escape_special_characters(reply_text),
                reply_markup=reply_markup, 
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
        elif role == 'Edit':
            notify = get_notify_by_id(notify_id=int(symbol))
            keyboard = []
            keyboard.append([
                InlineKeyboardButton("📊 Monitored Item", callback_data=f'N_Edit_C_{int(symbol)}'),
                InlineKeyboardButton("🌊 Limited Value", callback_data=f'N_Edit_V_{int(symbol)}'),
            ])
            keyboard.append([
                InlineKeyboardButton("🗑 Delete", callback_data=f'N_Edit_D_{int(symbol)}'),
                InlineKeyboardButton("🔙 Back to the list", callback_data=f'settings_notify')                
            ])
            reply_markup = InlineKeyboardMarkup(keyboard)
            reply_text = f'*Edit {notify.name} notification info*\n\n*Exchange Type:* DEX\n*Symbol:* {notify.symbol}\n*Chain:* {default_chain[notify.chain]}\n*DEX Platform*: {notify.platform}\n*Monitored Item:* {default_condition[notify.condition]}\n*Limited Value:* {notify.value}\n*Notification Type:* {'Telegram' if notify.notify_id == 'T' else 'Email'}\n'
            await message.edit_text(
                text= escape_special_characters(reply_text),
                reply_markup=reply_markup, 
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
        elif role == "D":
            user = update_status(id=chat_id, status=f"N_{role}_{symbol}_{message.message_id}")
            reply_markup = get_exact_name_symbol(symbol=symbol)
            reply_text = f'* Add New Alert & Notification *\n\n*Exchange Type:* DEX\n*Symbol:* {symbol}\n\nExactly what cryptocurrency do you want? Please check\.             '
            await message.edit_text(
                text=escape_special_characters(reply_text),
                reply_markup=reply_markup, 
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
    elif len(commands) == 4:
        name = commands[2]
        symbol = commands[3]
        role = commands[1]
        user = update_status(id=chat_id, status=f"N_{role}_{name}_{symbol}_{message.message_id}")
        if role == 'Edit':
            if name == 'C':
                keyboard = []
                keyboard.append([
                    InlineKeyboardButton("Price", callback_data=f'N_Edit_C_P_{int(symbol)}'), 
                    InlineKeyboardButton("Volume(24h)", callback_data=f'N_Edit_C_V_{int(symbol)}'),
                    InlineKeyboardButton("Liquidity", callback_data=f'N_Edit_C_L_{int(symbol)}'),])
                keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f'N_Edit_{int(symbol)}')])
                reply_markup = InlineKeyboardMarkup(keyboard)
                await message.edit_text(
                    text=
                    f'Please choose new item you like to monitor\.',
                    reply_markup=reply_markup, 
                    parse_mode=ParseMode.MARKDOWN_V2,
                    disable_web_page_preview=True
                )
            elif name == 'V':
                user = update_status(id=chat_id, status=f"N_Edit_V_{int(symbol)}_{message.message_id}")
                keyboard = []
                keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f'N_Edit_{int(symbol)}')])
                reply_markup = InlineKeyboardMarkup(keyboard)
                await message.edit_text(
                    text=
                    f'Please enter new limit values for this condition\.',
                    reply_markup=reply_markup, 
                    parse_mode=ParseMode.MARKDOWN_V2,
                    disable_web_page_preview=True
                )
            elif name == 'D':
                keyboard = []
                keyboard.append([InlineKeyboardButton("No", callback_data=f'N_Edit_{int(symbol)}'), InlineKeyboardButton("Yes", callback_data=f'N_Edit_D_Y_{int(symbol)}')])
                reply_markup = InlineKeyboardMarkup(keyboard)
                await message.edit_text(
                    text=
                    f'Are you sure you want to delete this notification?',
                    reply_markup=reply_markup, 
                    parse_mode=ParseMode.MARKDOWN_V2,
                    disable_web_page_preview=True
                )
        elif role == "D":
            reply_markup = get_exact_basic_chain(name=name, symbol=symbol)
            reply_text = f'* Add New Alert & Notification *\n\n*Exchange Type:* DEX\n*Name:* {name}\n*Symbol:* {symbol}\n\nWhich chain would you use a cryptocurrency built on?               '
            await message.edit_text(
                text=escape_special_characters(reply_text),
                reply_markup=reply_markup, 
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
    elif len(commands) == 5:
        role = user_status[1]
        name = user_status[2]
        symbol = user_status[3]
        chain = commands[4]
        user = update_status(id=chat_id, status=f"N_{role}_{name}_{symbol}_{chain}_{message.message_id}")
        if commands[1] == 'Edit':
            if commands[2] == 'C':
                keyboard = []
                keyboard.append([InlineKeyboardButton("No", callback_data=f'N_Edit_C_{int(symbol)}'), InlineKeyboardButton("Yes", callback_data=f'N_Edit_C_{commands[3]}_Y_{int(symbol)}')])
                reply_markup = InlineKeyboardMarkup(keyboard)
                await message.edit_text(
                    text=
                    f'Are you sure you want to change the monitored item to {default_condition[commands[3]]}?',
                    reply_markup=reply_markup, 
                    parse_mode=ParseMode.MARKDOWN_V2,
                    disable_web_page_preview=True
                )
            elif commands[2] == 'V':
                keyboard = []
                keyboard.append([InlineKeyboardButton("No", callback_data=f'N_Edit_{int(symbol)}'), InlineKeyboardButton("Yes", callback_data=f'N_Edit_V_{commands[3]}_Y_{int(symbol)}')])
                reply_markup = InlineKeyboardMarkup(keyboard)
                await message.edit_text(
                    text=
                    f'Are you sure you want to change the limited value to {commands[3]}?',
                    reply_markup=reply_markup, 
                    parse_mode=ParseMode.MARKDOWN_V2,
                    disable_web_page_preview=True
                )
            elif commands[2] == 'D':
                notify = delete_notification(notify_id=int(commands[-1]))
                keyboard = []
                keyboard.append([InlineKeyboardButton("🔙 Back to the notification list", callback_data=f'settings_notify')])
                reply_markup = InlineKeyboardMarkup(keyboard)
                await message.edit_text(
                    text=
                    f'{'Successfully deleted the notification\.' if notify else 'Failed to delete notification\.'}',
                    reply_markup=reply_markup, 
                    parse_mode=ParseMode.MARKDOWN_V2,
                    disable_web_page_preview=True
                )
        elif role == "D":
            reply_markup = get_exact_platform(name=name, symbol=symbol, chain=chain)
            reply_text = f'* Add New Alert & Notification *\n\n*Exchange Type:* DEX\n*Name:* {name}\n*Symbol:* {symbol}\n*Chain:* {default_chain[chain]}\n\nPlease select target DEX platform?                  '
            await message.edit_text(
                text=escape_special_characters(reply_text),
                reply_markup=reply_markup, 
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
    elif len(commands) == 6:
        role = user_status[1]
        name = user_status[2]
        symbol = user_status[3]
        chain = user_status[4]
        platform = commands[5]
        user = update_status(id=chat_id, status=f"N_{role}_{name}_{symbol}_{chain}_{platform}_{message.message_id}")
        if commands[1] == 'Edit':
            if commands[2] == 'C':
                notify = change_condition(notify_id=int(commands[-1]), condition=commands[3])
                keyboard = []
                keyboard.append([InlineKeyboardButton("🔙 Back to the notification list", callback_data=f'settings_notify')])
                reply_markup = InlineKeyboardMarkup(keyboard)
                await message.edit_text(
                    text=
                    f'{'Successfully changed the monitered item\.' if notify else 'Failed to change notification monitoring item\.'}',
                    reply_markup=reply_markup, 
                    parse_mode=ParseMode.MARKDOWN_V2,
                    disable_web_page_preview=True
                )
            elif commands[2] == 'V':
                notify = change_value(notify_id=int(commands[-1]), value=float(commands[3]))
                keyboard = []
                keyboard.append([InlineKeyboardButton("🔙 Back to the notification list", callback_data=f'settings_notify')])
                reply_markup = InlineKeyboardMarkup(keyboard)
                await message.edit_text(
                    text=
                    f'{'Successfully changed the limited value\.' if notify else 'Failed to change notification limited value\.'}',
                    reply_markup=reply_markup, 
                    parse_mode=ParseMode.MARKDOWN_V2,
                    disable_web_page_preview=True
                )
        elif role == "D":
            keyboard = []
            keyboard.append([
                InlineKeyboardButton("Price", callback_data=f'N_D_N_S_C_P_P'), 
                InlineKeyboardButton("Volume(24h)", callback_data=f'N_D_N_S_C_P_V'),
                InlineKeyboardButton("Liquidity", callback_data=f'N_D_N_S_C_P_L'),])
            keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f'N_D_N_S_{chain}'), InlineKeyboardButton("✖ Cancel", callback_data='settings_notify')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            reply_text = f'* Add New Alert & Notification *\n\n*Exchange Type:* DEX\n*Name:* {name}\n*Symbol:* {symbol}\n*Chain:* {default_chain[chain]}\n*DEX Platform*: {platform}\n\nWhich item would you like to monitor?'
            await message.edit_text(
                text=escape_special_characters(reply_text),
                reply_markup=reply_markup, 
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
    elif len(commands) == 7:
        role = user_status[1]
        name = user_status[2]
        symbol = user_status[3]
        chain = user_status[4]
        platform = user_status[5]
        condition = commands[6]
        user = update_status(id=chat_id, status=f"N_{role}_{name}_{symbol}_{chain}_{platform}_{condition}_{message.message_id}")
        keyboard = []
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f'N_D_N_S_C_{platform}'), InlineKeyboardButton("✖ Cancel", callback_data='settings_notify')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        reply_text = f'* Add New Alert & Notification *\n\n*Exchange Type:* DEX\n*Name:* {name}\n*Symbol:* {symbol}\n*Chain:* {default_chain[chain]}\n*DEX Platform*: {platform}\n*Monitored Item:* {default_condition[condition]}\n\nPlease enter limit values for this condition.'
        await message.edit_text(
            text=escape_special_characters(reply_text),
            reply_markup=reply_markup, 
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True
        )
    elif len(commands) == 8:
        role = user_status[1]
        name = user_status[2]
        symbol = user_status[3]
        chain = user_status[4]
        platform = user_status[5]
        condition = user_status[6]
        value = float(commands[7])
        keyboard = []
        keyboard.append([InlineKeyboardButton("Telegram", callback_data=f'N_{role}_N_S_C_P_C_{value}_T')])
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f'N_{role}_N_S_C_P_{condition}'), InlineKeyboardButton("✖ Cancel", callback_data='settings_notify')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        reply_text = f'* Add New Alert & Notification *\n\n*Exchange Type:* DEX\n*Name:* {name}\n*Symbol:* {symbol}\n*Chain:* {default_chain[chain]}\n*DEX Platform*: {platform}\n*Monitored Item:* {default_condition[condition]}\n*Limited Value:* {value}\n\nPlease choose notification type.'
        await message.edit_text(
            text=escape_special_characters(reply_text),
            reply_markup=reply_markup, 
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True
        )
    elif len(commands) == 9:
        role = user_status[1]
        name = user_status[2]
        symbol = user_status[3]
        chain = user_status[4]
        platform = user_status[5]
        condition = user_status[6]
        value = float(commands[7])
        notify_type = commands[8]
        user = update_status(id=chat_id, status=f"N_{role}_{name}_{symbol}_{chain}_{platform}_{condition}_{value}_{notify_type}_{message.message_id}")
        keyboard = []
        keyboard.append([
            InlineKeyboardButton("🔙 Back", callback_data=f'N_D_N_S_C_P_C_{value}'),
            InlineKeyboardButton("📝 Submit", callback_data=f'N_D_N_S_C_P_C_V_N_S'), 
            InlineKeyboardButton("✖ Cancel", callback_data='settings_notify')
        ])
        reply_markup = InlineKeyboardMarkup(keyboard)
        reply_text = f'* Add New Alert & Notification *\n\n*Exchange Type:* DEX\n*Name:* {name}\n*Symbol:* {symbol}\n*Chain:* {default_chain[chain]}\n*DEX Platform*: {platform}\n*Monitored Item:* {default_condition[condition]}\n*Limited Value:* {value}\n*Notification Type:* {'Telegram' if notify_type == 'T' else 'Email'}\n'

        await message.edit_text(
            text= escape_special_characters(reply_text),
            reply_markup=reply_markup, 
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True
        )
    elif len(commands) == 10:
        role = user_status[1]
        name = user_status[2]
        symbol = user_status[3]
        chain = user_status[4]
        platform = user_status[5]
        condition = user_status[6]
        value = float(user_status[7])
        notify_type = user_status[8]
        user = create_notification(chat_id=chat_id, crypto_type=role, name=name, symbol=symbol, chain=chain, platform=platform, condition=condition, value=value, notify_method=notify_type)
        if user:
            await message.edit_text(
                text=
                f'New alerts and notifications have been set up successfully\!',
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
