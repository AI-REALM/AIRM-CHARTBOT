# Import required classes from the library
import json, asyncio, os, re
from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta
from telegram.constants import ParseMode
from ..model.crud import get_user_by_id, create_user
from ..info.dext import dx_get_info, get_picture, get_heatmap
from .admin_commands import admin_notify, log_function
from ..info.cex import cex_exact_info, cex_info_symbol_market_pair, cex_historical_info, get_detailed_info, get_picture_cex
from ..info.ta import ta_response
from .user_settings import default_chain, default_condition
from dotenv import load_dotenv
load_dotenv(dotenv_path='.env')

admin = int(os.getenv('ADMIN'))

chains_default_name = {
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

candidate_blocksize = {
    'market_cap_calc':'Market Cap',
    'market_cap_diluted_calc': 'FD market cap',
    '24h_vol_cmc' : 'Volume in USD 24h',
    'tvl' : 'Total value locked',
    '24h_vol_to_market_cap': 'Volume 24h / Market cap',
    'market_cap_to_tvl':'Market cap / TVL' 
}

candidate_datasource = {
    'CryptoWithoutBTC' : 'Crypto coins (Excluding Bitcoin)',
    'Crypto' : 'Crypto coins',
    'CryptoWithoutStable' : 'Crypto coins (Excluding Stablecoins)',
    'CryptoDeFi' : 'Coins DeFi'
}

def recommend_pair(chain_info, user_input):
    same_chain_name_token = []
    others_token = []
    for i in chain_info:
        if len(user_input)>15:
            k = i.quote_token.name if i.base_token.address == user_input else i.base_token.name
        else:
            k = i.quote_token.name if user_input in i.base_token.symbol else i.base_token.name
        if i.chain_id[0:3].lower() in k.lower():
            same_chain_name_token.append(i)
        else:
            others_token.append(i)
    
    if same_chain_name_token:
        max_price = 0
        max_item = same_chain_name_token[0]
        for i in same_chain_name_token:
            if i.price_usd and float(i.price_usd) > max_price:
                max_item = i
        return max_item
    else:
        max_price = 0
        max_item = others_token[0]
        for i in others_token:
            if i.price_usd and float(i.price_usd) > max_price:
                max_item = i
        return max_item

def format_number(num):
    suffixes = ['T', 'B', 'M', 'K']
    
    for i, suf in enumerate(suffixes):
        n = 10**(3*(4-i))
        if num >= n:
            return f'{num/n:.1f}{suf}'
    rounded_number = round(num, 3)
    return rounded_number

def escape_special_characters(text):
    # Define the pattern for special characters that need to be escaped
    pattern = r'(\\|\[|\]|\(|\)|~|>|#|\+|-|=|\||\{|\}|\.|!)'
    
    # Use the sub method from re to replace the characters with their escaped versions
    escaped_text = re.sub(pattern, r'\\\1', text)
    
    return escaped_text

# /dx handling functions
async def dx_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Define the response message and buttons 
    message = update.message or update.callback_query.message
    
    text = update.message.text or update.callback_query.data
    if text.strip() == "/dx":
        i_text = (
            "💡 The `/dx` command requires a ticker. For example: `/dx btc`. "
            "Or: type `/help` for assistance."
        )
        # Save the sent message object into a variable `sent_message`
        sent_message = await message.reply_text(i_text, parse_mode=ParseMode.MARKDOWN)
        # Wait for 5 seconds
        await asyncio.sleep(5)
        # Use `sent_message.message_id` to reference the correct message ID
        await sent_message.delete()
        return None

    user_input = text.split("/dx ")[-1]

    chat_id = message.chat_id
    user = get_user_by_id(chat_id)
    if not user:
        user = create_user(chat_id)

    sent_message = await message.reply_text(f'Searching info of `{user_input}` on {user.chain} for {user.interval} period', parse_mode=ParseMode.MARKDOWN)

    chain_name, info = dx_get_info(default_chain=user.chain, user_input=user_input)
    
    if info:
        if chain_name == True:
            await dx_final_response(message=sent_message, context=context, chain_info=info, interval=user.interval, indicators=user.indicators, style=user.style)
        else:
            # await sent_message.edit_text(f'⚠ There isn\'t info of {user_input} on {user.chain}. So researching on {chain_name}.')
            await dx_select_platform(message=sent_message, context=context, chain_info=info, user_input=user_input, interval=user.interval, indicators=user.indicators, style=user.style)
    else:
        log_function(log_type="dx_chart", chat_id=message.chat_id, chain_id=user.chain, chain_address=user_input, result="Not found dex pair")
        await admin_notify(context=context, admin_chat_id=admin, user_chat_id=message.chat_id, rquest_type='DX Chart', user_input=f'`{user_input}`', result_code="Not found dex pair")
        await sent_message.edit_text(f'❌ This {"symbol" if len(user_input) > 20 else "address"} you entered is either not available on supported exchanges or could not be matched to a project by our search algorithm. Please contact me directly @fieryfox617',parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(5)
        await sent_message.delete()
        # sent_message.reply_photo()

async def dx_final_response(message: Update.message, context: ContextTypes.DEFAULT_TYPE, chain_info:dict, interval:str, indicators:str, style:str) -> None:
    file_path = "screen.png"
    await message.edit_text(f'Generating chart for `{chain_info.pair_address}` on {chain_info.chain_id} for {interval} period', parse_mode=ParseMode.MARKDOWN)
    runing, picture = get_picture(chain=chain_info.chain_id, address=chain_info.pair_address, file_path=file_path, indicators=indicators, style=style, interval=interval)
    if runing == False:
        log_function(log_type="dx_chart", chat_id=message.chat_id, chain_id=chain_info.chain_id, chain_address=chain_info.pair_address, result="Failed in Chart Scrapping")
        await admin_notify(context=context, admin_chat_id=admin, user_chat_id=message.chat_id, rquest_type='DX Chart', user_input=f'`{picture}`', result_code='Failed in Chart Scrapping')
        await message.edit_text(f'❌ This {"symbol" if len(chain_info.pair_address) > 20 else "address"} you entered is either not available on supported exchanges or could not be matched to a project by our search algorithm. Please contact me directly @fieryfox617',parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(5)
        await message.delete()
        return None
    # chart_url = picture.split("/")[-2]
    chain = chains_default_name[chain_info.chain_id]
    pair = f'<a href=\'{chain_info.url}\'>{chain_info.base_token.name} / {chain_info.quote_token.name}</a>'
    price = chain_info.price_usd if chain_info.price_usd else None
    create_date = chain_info.pair_created_at
    if create_date:
        created_date = f'🗓️ Created date: {create_date.strftime(format="%Y-%m-%d")}\n'
    else:
        created_date = None
    if interval == '5m':
        price_chain = chain_info.price_change.m5
        pair_count = chain_info.transactions.m5
        volume = chain_info.volume.m5
    elif interval == '1h':
        price_chain = chain_info.price_change.h1
        pair_count = chain_info.transactions.h1
        volume = chain_info.volume.h1
    elif interval == '6h':
        price_chain = chain_info.price_change.h6
        pair_count = chain_info.transactions.h6
        volume = chain_info.volume.h6
    elif interval == '1D':
        price_chain = chain_info.price_change.h24
        pair_count = chain_info.transactions.h24
        volume = chain_info.volume.h24
    liquidity = chain_info.liquidity
    interval_keyboard = []
    times = ['5m','1h','6h','1D']
    for i in times:
        if i == interval:
            interval_keyboard.append(InlineKeyboardButton(text="🔄", callback_data=f'dx_{chain_info.chain_id}_{chain_info.pair_address}_{i}'))
        else:
            interval_keyboard.append(InlineKeyboardButton(text=i, callback_data=f'dx_{chain_info.chain_id}_{chain_info.pair_address}_{i}'))
    ta_i_keyboard = []
    if picture:
        ta_i_keyboard.append(InlineKeyboardButton(text="👁 TA", callback_data=f'ta_{picture}'))
    ta_i_keyboard.append(InlineKeyboardButton(text="ℹ", callback_data=f'i_DX_{chain_info.chain_id}_{chain_info.pair_address}_{interval}'))
    reply_markup = InlineKeyboardMarkup([interval_keyboard, ta_i_keyboard])
    await message.delete()
    with open(file_path, 'rb') as f:
        final = await context.bot.send_photo(
            photo = f,
            chat_id=message.chat_id,
            caption=(
                f'📌 Chain: {chain} ({interval})\n\n'
                f'🏦 DEX Platform: {chain_info.dex_id}\n\n'
                f'💸 Pair: {pair}\n\n'
                f'💰 Price USD: {chain_info.price_usd if chain_info.price_usd is not None else "-"}'
                f"{f' ({price_chain}% Change)' if price_chain is not None else ''}\n"
                f'🌊 Volume: {f"${volume}" if volume > 0 else "--"}\n'
                f'💦 Liquidity: Total: ${format_number(liquidity.usd)}\n'
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
        log_function(log_type="dx_chart", chat_id=message.chat_id, chain_id=chain_info.chain_id, chain_address=chain_info.pair_address, result="successful")

async def dx_select_platform(message: Update.message, context: ContextTypes.DEFAULT_TYPE, chain_info:dict, user_input:str, interval:str, indicators:str, style:str) ->None:
    platforms = {}
    for i in chain_info:
        if len(i) < 25:
            token = recommend_pair(chain_info=chain_info[i], user_input=user_input)
            platforms[i] = token
    keyboard = []
    keys = list(platforms.keys())
    back_button_flag=True
    if len(keys) == 1:
        await dx_final_response(message=message, context=context, chain_info=platforms[keys[0]], interval=interval, indicators=indicators, style=style)
    else:
        for i in range(0, len(keys), 3):
            rows = []
            for y in range(0,3):
                try:
                    title = f'{platforms[keys[i+y]].dex_id}'
                    call_back = f'dx_{platforms[keys[i+y]].chain_id}_{platforms[keys[i+y]].pair_address}_{interval}'
                    rows.append(InlineKeyboardButton(title, callback_data=call_back))
                except:
                    rows.append(InlineKeyboardButton("✖ Close", callback_data='dx_close'))
                    back_button_flag=False
                    break
            keyboard.append(rows)
        if back_button_flag:
            keyboard.append([InlineKeyboardButton("✖ Close", callback_data='dx_close')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await message.edit_text(
            "Which DEX platform would you like to use?", reply_markup=reply_markup
        )

async def dx_callback_handle(update: Update, context: ContextTypes.DEFAULT_TYPE)->None:
    message = update.callback_query.message
    text = update.callback_query.data
    chain_id = text.split("_")[1]
    if chain_id == "close":
        await message.delete()
    else:
        pair_address = text.split("_")[2]
        interval = text.split("_")[3]
        chat_id = message.chat_id
        user = get_user_by_id(chat_id)
        if not user:
            user = create_user(chat_id)
        await message.delete()
        sent_message = await context.bot.send_message(text= f'Searching info of `{pair_address}` on {chain_id} for {interval} period', chat_id=message.chat_id, parse_mode=ParseMode.MARKDOWN)
        chain_name, info = dx_get_info(default_chain=chain_id, user_input=pair_address)
        if chain_name == True:
            await dx_final_response(message=sent_message, context=context, chain_info=info, interval=interval, indicators=user.indicators, style=user.style)
        else:
            await dx_select_platform(message=sent_message, context=context, chain_info=info, user_input=pair_address, interval=interval, indicators=user.indicators, style=user.style)

# /i handling functions
async def i_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Define the response message and buttons 
    message = update.message or update.callback_query.message
    
    text = update.message.text or update.callback_query.data
    if text.strip() == "/i":
        i_text = (
            "💡 The `/i` command requires a ticker. For example: `/i btc`. "
            "Or: type `/help` for assistance."
        )
        # Save the sent message object into a variable `sent_message`
        sent_message = await message.reply_text(i_text, parse_mode=ParseMode.MARKDOWN)
        # Wait for 5 seconds
        await asyncio.sleep(5)
        # Use `sent_message.message_id` to reference the correct message ID
        await sent_message.delete()
        return None

    user_input = text.split("/i ")[-1]
    if len(user_input) > 20:        
        chat_id = message.chat_id
        user = get_user_by_id(chat_id)
        if not user:
            user = create_user(chat_id)

        sent_message = await message.reply_text(f'Searching info of `{user_input}` on {user.chain} for {user.interval} period', parse_mode=ParseMode.MARKDOWN)

        chain_name, info = dx_get_info(default_chain=user.chain, user_input=user_input)
        if info:
            if chain_name == True:
                await i_final_response(message=sent_message,context=context, chain_info=info, interval=user.interval)
            else:
                # await sent_message.edit_text(f'⚠ There isn\'t info of {user_input} on {user.chain}. So researching on {chain_name}.')
                await i_select_platform(message=sent_message, context=context, chain_info=info, user_input=user_input, interval=user.interval)
        else:
            log_function(log_type="info", chat_id=message.chat_id, chain_id=user.chain, chain_address=user_input, result="Not found info of chain")
            await admin_notify(context=context, admin_chat_id=admin, user_chat_id=message.chat_id, rquest_type='Info', user_input=f'`{user_input}`', result_code="Not found info of chain")
            await sent_message.edit_text(f'❌ This {"symbol" if len(user_input) > 20 else "address"} you entered is either not available on supported exchanges or could not be matched to a project by our search algorithm. Please contact me directly @fieryfox617',parse_mode=ParseMode.MARKDOWN)
            await asyncio.sleep(5)
            await sent_message.delete()
    else:
        keyboard = [
            InlineKeyboardButton(text="CEX", callback_data=f'i_CX_{user_input}'),
            InlineKeyboardButton(text="DEX", callback_data=f'i_DX_{user_input}')
        ]
        reply_markup = InlineKeyboardMarkup([keyboard])
        await message.reply_text(f'What kind of data do you want?',parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

async def i_final_response(message: Update.message, context: ContextTypes.DEFAULT_TYPE, chain_info:dict, interval:str) -> None:
    chain = chains_default_name[chain_info.chain_id]
    pair = f'<a href=\'{chain_info.url}\'>{chain_info.base_token.name} / {chain_info.quote_token.name}</a>'
    price = chain_info.price_usd if chain_info.price_usd else None
    create_date = chain_info.pair_created_at
    if create_date:
        created_date = f'🗓️ Created date: {create_date.strftime(format="%Y-%m-%d")}\n'
    else:
        created_date = None
    if interval == '5m':
        price_chain = chain_info.price_change.m5
        pair_count = chain_info.transactions.m5
        volume = chain_info.volume.m5
    elif interval == '1h':
        price_chain = chain_info.price_change.h1
        pair_count = chain_info.transactions.h1
        volume = chain_info.volume.h1
    elif interval == '6h':
        price_chain = chain_info.price_change.h6
        pair_count = chain_info.transactions.h6
        volume = chain_info.volume.h6
    elif interval == '1D':
        price_chain = chain_info.price_change.h24
        pair_count = chain_info.transactions.h24
        volume = chain_info.volume.h24
    liquidity = chain_info.liquidity
    keyboard = []
    times = ['5m','1h','6h','1D']
    for i in times:
        if i == interval:
            keyboard.append(InlineKeyboardButton(text="🔄", callback_data=f'i_DX_{chain_info.chain_id}_{chain_info.pair_address}_{i}'))
        else:
            keyboard.append(InlineKeyboardButton(text=i, callback_data=f'i_DX_{chain_info.chain_id}_{chain_info.pair_address}_{i}'))
    keyboard.append(InlineKeyboardButton(text="📈", callback_data=f'chart_DX_{chain_info.chain_id}_{chain_info.pair_address}_{interval}'))
    reply_markup = InlineKeyboardMarkup([keyboard])

    await message.edit_text(
        text=(
            f'📌 Chain: {chain} ({interval})\n\n🏦 DEX Platform: {chain_info.dex_id}\n\n💸 Pair: {pair} \n{created_date if created_date else ""}\n💰 Price USD: {chain_info.price_usd if chain_info.price_usd else "-"} {f"({price_chain}%)" if chain_info.price_usd else ""}\n🛒 PairtransactionCount: Buy: {format_number(pair_count.buys)} / Sell: {format_number(pair_count.sells)}\n\n🌊 Volume: {"--" if volume == 0 else f"${volume}"}\n\n💦 Liquidity: Total: ${format_number(liquidity.usd)}\n     Base: {format_number(liquidity.base)}({chain_info.base_token.symbol}) / Quote: {format_number(liquidity.quote)}({chain_info.quote_token.symbol})'
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )
    log_function(log_type="i_DX", chat_id=message.chat_id, chain_id=chain_info.chain_id, chain_address=chain_info.pair_address, result="successful")

async def i_select_platform(message: Update.message, context: ContextTypes.DEFAULT_TYPE, chain_info:dict, user_input:str, interval) ->None:
    platforms = {}
    for i in chain_info:
        if len(i) < 25:
            token = recommend_pair(chain_info=chain_info[i], user_input=user_input)
            platforms[i] = token
    keyboard = []
    keys = list(platforms.keys())
    back_button_flag=True
    if len(keys) == 1:
        await i_final_response(message=message, context=context, chain_info=platforms[keys[0]], interval=interval)
    else:
        for i in range(0, len(keys), 3):
            rows = []
            for y in range(0,3):
                try:
                    title = f'{platforms[keys[i+y]].dex_id}'
                    call_back = f'i_DX_{platforms[keys[i+y]].chain_id}_{platforms[keys[i+y]].pair_address}_{interval}'
                    rows.append(InlineKeyboardButton(title, callback_data=call_back))
                except:
                    rows.append(InlineKeyboardButton("✖ Close", callback_data='i_close'))
                    back_button_flag=False
                    break
            keyboard.append(rows)
        if back_button_flag:
            keyboard.append([InlineKeyboardButton("✖ Close", callback_data='i_close')])

        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await message.edit_text(
            "Which DEX platform would you like to use?", reply_markup=reply_markup
        )

async def i_cx_final_response(message: Update.message, context: ContextTypes.DEFAULT_TYPE, chain_info:dict, interval:str, indicators:str, style:str) -> None:
    symbol = chain_info["market_pair_base"]["exchange_symbol"]
    market_id = chain_info["market_id"]
    await message.edit_text(f'Generating chart for `{symbol}` on {chain_info["exchange"]["name"]} for {interval} period', parse_mode=ParseMode.MARKDOWN)
    
    detailed_info = get_detailed_info(symbol=symbol)
    if type(detailed_info) == str:
        log_function(log_type="i_CX", chat_id=message.chat_id, chain_id=symbol, chain_address=chain_info["exchange"]["name"], result=f'{detailed_info}')
        await admin_notify(context=context, admin_chat_id=admin, user_chat_id=message.chat_id, rquest_type='Info CX', user_input=f'`{symbol}`, `{chain_info["exchange"]["name"]}`', result=f'{detailed_info}')
        await message.edit_text(f'❌ This symbol {symbol} you entered is either not available on supported exchanges or could not be matched to a project by our search algorithm. Please contact me directly @fieryfox617',parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(5)
        await message.delete()
        return None
    
    price = round(chain_info["quote"]["USD"]["price"], 3)
    volume_24h = round(chain_info["quote"]["USD"]["volume_24h"],3)
    market_cap = round(detailed_info["quote"]["USD"]["market_cap"],3)

    keyboard = []
    keyboard.append(InlineKeyboardButton(text="🔄", callback_data=f'i_CX_{symbol}_{market_id}_{interval}'))
    keyboard.append(InlineKeyboardButton(text="📈", callback_data=f'chart_CX_{symbol}_{market_id}_{interval}'))
    reply_markup = InlineKeyboardMarkup([keyboard])
    await message.edit_text(
        text=f'📌 Project: {detailed_info["name"]}/{symbol}\n'
        f'🗓️ Create Date: {detailed_info["date_added"].split("T")[0].replace("-", " ")}\n\n'
        f'💰 Price USD: ${"{:,}".format(price)}\n'
        f'💵 Market cap: ${"{:,}".format(market_cap)}\n'
        f'🪙 Supply: Total: {format_number(detailed_info["total_supply"])} / Circ: {format_number(detailed_info["circulating_supply"])}\n\n'
        f'🌊 Volume 24h: ${"{:,}".format(volume_24h)}',
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )
    log_function(log_type="i_CX", chat_id=message.chat_id, chain_id=symbol, chain_address=chain_info["exchange"]["name"], result="successful")

async def i_cx_select_platform(message: Update.message, context: ContextTypes.DEFAULT_TYPE, chain_info:dict, user_input:str, interval:str, indicators:str, style:str) ->None:
    exchanges = {}
    for i in chain_info:
        exchange_name = i["exchange"]["slug"]
        if exchange_name in exchanges:
            exchanges[exchange_name].append(i)
        else:
            exchanges[exchange_name] = [i]
    
    keyboard = []
    keys = list(exchanges.keys())
    back_button_flag=True
    if len(keys) == 1:
        await i_cx_final_response(message=message, context=context, chain_info=exchanges[keys[0]][0], interval=interval, indicators=indicators, style=style)
    else:
        for i in range(0, len(keys), 3):
            rows = []
            for y in range(0,3):
                try:
                    title = f'{exchanges[keys[i+y]][0]["exchange"]["name"]}'
                    call_back = f'i_CX_{exchanges[keys[i+y]][0]["market_pair_base"]["exchange_symbol"]}_{exchanges[keys[i+y]][0]["market_id"]}_{interval}'
                    rows.append(InlineKeyboardButton(title, callback_data=call_back))
                except:
                    rows.append(InlineKeyboardButton("✖ Close", callback_data='i_close'))
                    back_button_flag=False
                    break
            keyboard.append(rows)
        if back_button_flag:
            keyboard.append([InlineKeyboardButton("✖ Close", callback_data='i_close')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await message.edit_text(
            "Which exchange would you like to use?", reply_markup=reply_markup
        )

async def i_callback_handle(update: Update, context: ContextTypes.DEFAULT_TYPE)->None:
    message = update.callback_query.message
    text = update.callback_query.data
    kind = text.split("_")[1]
    if kind == "close":
        await message.delete()
    elif kind == "DX":
        if len(text.split("_")) == 3:
            user_input = text.split("_")[2]        
            chat_id = message.chat_id
            user = get_user_by_id(chat_id)
            if not user:
                user = create_user(chat_id)
            await message.delete()
            sent_message = await message.reply_text(f'Searching info of `{user_input}` on {user.chain} for {user.interval} period', parse_mode=ParseMode.MARKDOWN)

            chain_name, info = dx_get_info(default_chain=user.chain, user_input=user_input)
            if info:
                if chain_name == True:
                    await i_final_response(message=sent_message,context=context, chain_info=info, interval=user.interval)
                else:
                    # await sent_message.edit_text(f'⚠ There isn\'t info of {user_input} on {user.chain}. So researching on {chain_name}.')
                    await i_select_platform(message=sent_message, context=context, chain_info=info, user_input=user_input, interval=user.interval)
            else:
                log_function(log_type="info_dx", chat_id=message.chat_id, chain_id=user.chain, chain_address=user_input, result="Not found info of DEX chain")
                await admin_notify(context=context, admin_chat_id=admin, user_chat_id=message.chat_id, rquest_type='Info DX', user_input=f'`{user_input}`', result_code="Not found info of DEX chain")
                await sent_message.edit_text(f'❌ This {"symbol" if len(user_input) > 20 else "address"} you entered is either not available on supported exchanges or could not be matched to a project by our search algorithm. Please contact me directly @fieryfox617',parse_mode=ParseMode.MARKDOWN)
                await asyncio.sleep(5)
                await sent_message.delete()
        else:
            chain_id = text.split("_")[2]
            pair_address = text.split("_")[3]
            interval = text.split("_")[4]
            await message.delete()
            sent_message = await context.bot.send_message(text=f'Searching info of `{pair_address}` on {chain_id} for {interval} period', chat_id=message.chat_id, parse_mode=ParseMode.MARKDOWN)
            
            chain_name, info = dx_get_info(default_chain=chain_id, user_input=pair_address)
            if chain_name == True:
                await i_final_response(message=sent_message, context=context, chain_info=info, interval=interval)
            else:
                await i_select_platform(message=sent_message, context=context, chain_info=info, user_input=pair_address, interval=interval)

    elif kind == "CX":
        if len(text.split("_")) == 3:
            user_input = text.split("_")[2]

            chat_id = message.chat_id
            user = get_user_by_id(chat_id)
            if not user:
                user = create_user(chat_id)
            await message.delete()
            sent_message = await message.reply_text(f'Searching info of `{user_input}` for {user.interval} period', parse_mode=ParseMode.MARKDOWN)

            info = cex_info_symbol_market_pair(symbol=user_input)
            
            if type(info) != str:
                if len(info) == 1:
                    await i_cx_final_response(message=sent_message, context=context, chain_info=info[0], interval=user.interval, style=user.style)
                else:
                    # await sent_message.edit_text(f'⚠ There isn\'t info of {user_input} on {user.chain}. So researching on {chain_name}.')
                    await i_cx_select_platform(message=sent_message, context=context, chain_info=info, user_input=user_input, interval=user.interval, indicators=user.indicators, style=user.style)
            else:
                log_function(log_type="info_cx", chat_id=message.chat_id, chain_id=user.chain, chain_address=user_input, result=f"{info}")
                await admin_notify(context=context, admin_chat_id=admin, user_chat_id=message.chat_id, rquest_type='Info CX', user_input=f'`{user_input}`', result_code=f'{info}')
                await sent_message.edit_text(f'❌ This {"symbol" if len(user_input) > 20 else "address"} you entered is either not available on supported exchanges or could not be matched to a project by our search algorithm. Please contact me directly @fieryfox617',parse_mode=ParseMode.MARKDOWN)
                await asyncio.sleep(5)
                await sent_message.delete()
        else:
            chain_symbol = text.split("_")[2]
            market_pair = int(text.split("_")[3])
            interval = text.split("_")[4]
            chat_id = message.chat_id
            user = get_user_by_id(chat_id)
            if not user:
                user = create_user(chat_id)
            await message.delete()
            info = cex_exact_info(symbol=chain_symbol, market_pair=market_pair)
            if type(info) != str:
                sent_message = await context.bot.send_message(text= f'Searching info of `{chain_symbol}` on {info["exchange"]["name"]} for {interval} period', chat_id=message.chat_id, parse_mode=ParseMode.MARKDOWN)
                await i_cx_final_response(message=sent_message, context=context, chain_info=info, interval=interval, indicators=user.indicators, style=user.style)
            else:
                log_function(log_type="info_cx", chat_id=message.chat_id, chain_id=user.chain, chain_address=user_input, result=f"{info}")
                await admin_notify(context=context, admin_chat_id=admin, user_chat_id=message.chat_id, rquest_type='Info CX', user_input=f'`{user_input}`', result_code=f'{info}')
                sent_message = await context.bot.send_message(text=f'❌ This symbol {chain_symbol} you entered is either not available on supported exchanges or could not be matched to a project by our search algorithm. Please contact me directly @fieryfox617',parse_mode=ParseMode.MARKDOWN)
                await asyncio.sleep(5)
                await sent_message.delete()
                return None
    else:
        pass

# /chart handling functions
async def chart_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Define the response message and buttons 
    message = update.message or update.callback_query.message
    
    text = update.message.text or update.callback_query.data
    if text.strip() == "/chart":
        i_text = (
            "💡 The `/chart` command requires a ticker. For example: `/chart btc`. "
            "Or: type `/help` for assistance."
        )
        # Save the sent message object into a variable `sent_message`
        sent_message = await message.reply_text(i_text, parse_mode=ParseMode.MARKDOWN)
        # Wait for 5 seconds
        await asyncio.sleep(5)
        # Use `sent_message.message_id` to reference the correct message ID
        await sent_message.delete()
        return None

    user_input = text.split("/chart ")[-1]
    if len(user_input) > 20:
        chat_id = message.chat_id
        user = get_user_by_id(chat_id)
        if not user:
            user = create_user(chat_id)

        sent_message = await message.reply_text(f'Generating chart for `{user_input}` on {user.chain} for {user.interval} period', parse_mode=ParseMode.MARKDOWN)

        chain_name, info = dx_get_info(default_chain=user.chain, user_input=user_input)
        if info:
            if chain_name == True:
                await chart_final_response(message=sent_message, context=context, chain_info=info, interval=user.interval, indicators=user.indicators, style=user.style)
            else:
                # await sent_message.edit_text(f'⚠ There isn\'t info of {user_input} on {user.chain}. So researching on {chain_name}.')
                await chart_select_platform(message=sent_message, context=context, chain_info=info, user_input=user_input, interval=user.interval, indicators=user.indicators, style=user.style)
        else:
            log_function(log_type="chart", chat_id=message.chat_id, chain_id=user.chain, chain_address=user_input, result="Not found info of chain")
            await admin_notify(context=context, admin_chat_id=admin, user_chat_id=message.chat_id, rquest_type='Chart', user_input=f'`{user_input}`', result_code="Not found info of chain")
            await sent_message.edit_text(f'❌ This {"symbol" if len(user_input) > 20 else "address"} you entered is either not available on supported exchanges or could not be matched to a project by our search algorithm. Please contact me directly @fieryfox617',parse_mode=ParseMode.MARKDOWN)
            await asyncio.sleep(5)
            await sent_message.delete()
            # sent_message.reply_photo()
    else:
        keyboard = [
            InlineKeyboardButton(text="CEX", callback_data=f'chart_CX_{user_input}'),
            InlineKeyboardButton(text="DEX", callback_data=f'chart_DX_{user_input}')
        ]
        reply_markup = InlineKeyboardMarkup([keyboard])
        await message.reply_text(f'What kind of data do you want?',parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

async def chart_final_response(message: Update.message,context: ContextTypes.DEFAULT_TYPE, chain_info:dict, interval:str, indicators:str, style:str) -> None:
    file_path = "screen.png"
    running, picture = get_picture(chain=chain_info.chain_id, address=chain_info.pair_address, file_path=file_path, indicators=indicators, style=style, interval=interval)
    if running == False:
        log_function(log_type="chart_dx", chat_id=message.chat_id, chain_id=chain_info.chain_id, chain_address=chain_info.pair_address, result="Failed in Chart Scrapping")
        await admin_notify(context=context, admin_chat_id=admin, user_chat_id=message.chat_id, rquest_type='Chart Dex', user_input=f'`{picture}`', result_code='Failed in Chart Scrapping')
        await message.edit_text(f'❌ This {"symbol" if len(chain_info.pair_address) > 20 else "address"} you entered is either not available on supported exchanges or could not be matched to a project by our search algorithm. Please contact me directly @fieryfox617',parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(5)
        await message.delete()
        return None
    
    keyboard = []
    if picture:
        keyboard.append(InlineKeyboardButton(text="👁 TA", callback_data=f'ta_{picture}'))
    keyboard.append(InlineKeyboardButton(text="🔄", callback_data=f'chart_DX_{chain_info.chain_id}_{chain_info.pair_address}_{interval}'))
    keyboard.append(InlineKeyboardButton(text="ℹ", callback_data=f'i_DX_{chain_info.chain_id}_{chain_info.pair_address}_{interval}'))
    reply_markup = InlineKeyboardMarkup([keyboard])
    await message.delete()
    with open(file_path, 'rb') as f:
        await context.bot.send_photo(
            photo = f,
            chat_id=message.chat_id,
            reply_markup=reply_markup
        )
        log_function(log_type="chart_dx", chat_id=message.chat_id, chain_id=chain_info.chain_id, chain_address=chain_info.pair_address, result="successful")

async def chart_select_platform(message: Update.message, context: ContextTypes.DEFAULT_TYPE, chain_info:dict, user_input:str, interval:str, indicators:str, style:str) ->None:
    platforms = {}
    for i in chain_info:
        if len(i) < 25:
            token = recommend_pair(chain_info=chain_info[i], user_input=user_input)
            platforms[i] = token
    keyboard = []
    keys = list(platforms.keys())
    back_button_flag=True
    if len(keys) == 1:
        await chart_final_response(message=message, context=context, chain_info=platforms[keys[0]], interval=interval, indicators=indicators, style=style)
    else:
        for i in range(0, len(keys), 3):
            rows = []
            for y in range(0,3):
                try:
                    title = f'{platforms[keys[i+y]].dex_id}'
                    call_back = f'chart_DX_{platforms[keys[i+y]].chain_id}_{platforms[keys[i+y]].pair_address}_{interval}'
                    rows.append(InlineKeyboardButton(title, callback_data=call_back))
                except:
                    rows.append(InlineKeyboardButton("✖ Close", callback_data='chart_close'))
                    back_button_flag=False
                    break
            keyboard.append(rows)
        if back_button_flag:
            keyboard.append([InlineKeyboardButton("✖ Close", callback_data='chart_close')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await message.edit_text(
            "Which exchange would you like to use?", reply_markup=reply_markup
        )

async def chart_cx_final_response(message: Update.message, context: ContextTypes.DEFAULT_TYPE, chain_info:dict, interval:str, indicators:str, style:str) -> None:
    file_path = "cex_chart.png"
    symbol = chain_info["market_pair_base"]["exchange_symbol"]
    exchange = chain_info["exchange"]["slug"]
    market_id = chain_info["market_id"]
    await message.edit_text(f'Generating chart for `{symbol}` on {chain_info["exchange"]["name"]} for {interval} period', parse_mode=ParseMode.MARKDOWN)
    now = datetime.now()
    user_interval = ""
    period = ""
    if interval == '5m':
        start = now - timedelta(minutes=2500)
        user_interval = 5
        period = "hourly"
    elif interval == '1h':
        start = now - timedelta(hours=500)
        user_interval = 60
        period = "hourly"
    elif interval == '6h':
        start = now - timedelta(days=90)
        user_interval = 360
        period = "hourly"
    elif interval == '1D':
        start = now - timedelta(days=90)
        user_interval = 1440
        period = "daily"
    
    picture = cex_historical_info(symbol=symbol, time_start=start.strftime("%Y-%m-%dT%H:%M:%S"), time_end=now.strftime("%Y-%m-%dT%H:%M:%S"), interval=user_interval, period=period, file_path=file_path, style=style)
    running, picture = get_picture_cex(exchange=exchange, chain=symbol, file_path=file_path, style=style, indicators=indicators, interval=user_interval)
    if running == False:
        log_function(log_type="chart_cx", chat_id=message.chat_id, chain_id=symbol, chain_address=exchange, result="Failed in CEX Chart Generation")
        await admin_notify(context=context, admin_chat_id=admin, user_chat_id=message.chat_id, rquest_type='Chart Cex',user_input=f'`{symbol}`, `{exchange}`', result_code='Failed in CEX Chart Generation')
        await message.edit_text(f'❌ This symbol {symbol} you entered is either not available on supported exchanges or could not be matched to a project by our search algorithm. Please contact me directly @fieryfox617',parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(5)
        await message.delete()
        return None

    keyboard = []
    if picture:
        keyboard.append(InlineKeyboardButton(text="👁 TA", callback_data=f'ta_{picture}'))
    keyboard.append(InlineKeyboardButton(text="🔄", callback_data=f'chart_CX_{symbol}_{market_id}_{interval}'))
    keyboard.append(InlineKeyboardButton(text="ℹ", callback_data=f'i_CX_{symbol}_{market_id}_{interval}'))
    reply_markup = InlineKeyboardMarkup([keyboard])
    await message.delete()
    with open(file_path, 'rb') as f:
        await context.bot.send_photo(
            photo = f,
            chat_id=message.chat_id,
            reply_markup=reply_markup
        )
        log_function(log_type="chart_cx", chat_id=message.chat_id, chain_id=symbol, chain_address=exchange, result="successful")

async def chart_cx_select_platform(message: Update.message, context: ContextTypes.DEFAULT_TYPE, chain_info:dict, user_input:str, interval:str, indicators:str, style:str) ->None:
    exchanges = {}
    for i in chain_info:
        exchange_name = i["exchange"]["slug"]
        if exchange_name in exchanges:
            exchanges[exchange_name].append(i)
        else:
            exchanges[exchange_name] = [i]
    
    keyboard = []
    keys = list(exchanges.keys())
    back_button_flag=True
    if len(keys) == 1:
        await chart_cx_final_response(message=message, context=context, chain_info=exchanges[keys[0]][0], interval=interval, indicators=indicators, style=style)
    else:
        for i in range(0, len(keys), 3):
            rows = []
            for y in range(0,3):
                try:
                    title = f'{exchanges[keys[i+y]][0]["exchange"]["name"]}'
                    call_back = f'chart_CX_{exchanges[keys[i+y]][0]["market_pair_base"]["exchange_symbol"]}_{exchanges[keys[i+y]][0]["market_id"]}_{interval}'
                    rows.append(InlineKeyboardButton(title, callback_data=call_back))
                except:
                    rows.append(InlineKeyboardButton("✖ Close", callback_data='chart_close'))
                    back_button_flag=False
                    break
            keyboard.append(rows)
        if back_button_flag:
            keyboard.append([InlineKeyboardButton("✖ Close", callback_data='chart_close')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await message.edit_text(
            "Which exchange would you like to use?", reply_markup=reply_markup
        )

async def chart_callback_handle(update: Update, context: ContextTypes.DEFAULT_TYPE)->None:
    message = update.callback_query.message
    text = update.callback_query.data
    kind = text.split("_")[1]
    if kind == "close":
        await message.delete()
    elif kind == "DX":
        if len(text.split("_")) == 3:
            user_input = text.split("_")[2]

            chat_id = message.chat_id
            user = get_user_by_id(chat_id)
            if not user:
                user = create_user(chat_id)
            await message.delete()
            sent_message = await message.reply_text(f'Generating chart for `{user_input}` on {user.chain} for {user.interval} period', parse_mode=ParseMode.MARKDOWN)

            chain_name, info = dx_get_info(default_chain=user.chain, user_input=user_input)
            if info:
                if chain_name == True:
                    await chart_final_response(message=sent_message, context=context, chain_info=info, interval=user.interval, indicators=user.indicators, style=user.style)
                else:
                    # await sent_message.edit_text(f'⚠ There isn\'t info of {user_input} on {user.chain}. So researching on {chain_name}.')
                    await chart_select_platform(message=sent_message, context=context, chain_info=info, user_input=user_input, interval=user.interval, indicators=user.indicators, style=user.style)
            else:
                log_function(log_type="chart_dx", chat_id=message.chat_id, chain_id=user.chain, chain_address=user_input, result="Not found info of DEX chain")
                await admin_notify(context=context, admin_chat_id=admin, user_chat_id=message.chat_id, rquest_type='Chart Dex', user_input=f'`{user_input}`', result_code="Not found info of DEX chain")
                await sent_message.edit_text(f'❌ This {"symbol" if len(user_input) > 20 else "address"} you entered is either not available on supported exchanges or could not be matched to a project by our search algorithm. Please contact me directly @fieryfox617',parse_mode=ParseMode.MARKDOWN)
                await asyncio.sleep(5)
                await sent_message.delete()
                # sent_message.reply_photo()
        else:
            chain_id = text.split("_")[2]
            pair_address = text.split("_")[3]
            interval = text.split("_")[4]
            chat_id = message.chat_id
            user = get_user_by_id(chat_id)
            if not user:
                user = create_user(chat_id)
            await message.delete()
            sent_message = await context.bot.send_message(text=f'Generating chart for token-pair(`{pair_address}`) on {chain_id} for {interval} period',chat_id=message.chat_id, parse_mode=ParseMode.MARKDOWN)
            chain_name, info = dx_get_info(default_chain=chain_id, user_input=pair_address)
            if chain_name == True:
                await chart_final_response(message=sent_message, context=context, chain_info=info, interval=interval, indicators=user.indicators, style=user.style)
            else:
                await chart_select_platform(message=sent_message, context=context, chain_info=info, user_input=pair_address, interval=interval, indicators=user.indicators, style=user.style)
    elif kind == "CX":
        if len(text.split("_")) == 3:
            user_input = text.split("_")[2]

            chat_id = message.chat_id
            user = get_user_by_id(chat_id)
            if not user:
                user = create_user(chat_id)
            await message.delete()
            sent_message = await message.reply_text(f'Searching info of `{user_input}` for {user.interval} period', parse_mode=ParseMode.MARKDOWN)

            info = cex_info_symbol_market_pair(symbol=user_input)
            
            if type(info) != str:
                if len(info) == 1:
                    await chart_cx_final_response(message=sent_message, context=context, chain_info=info[0], interval=user.interval, indicators=user.indicators, style=user.style)
                else:
                    # await sent_message.edit_text(f'⚠ There isn\'t info of {user_input} on {user.chain}. So researching on {chain_name}.')
                    await chart_cx_select_platform(message=sent_message, context=context, chain_info=info, user_input=user_input, interval=user.interval, indicators=user.indicators, style=user.style)
            else:
                log_function(log_type="chart_cx", chat_id=message.chat_id, chain_id=user.chain, chain_address=user_input, result=f'{info}')
                await admin_notify(context=context, admin_chat_id=admin, user_chat_id=message.chat_id, rquest_type='Chart Cex', user_input=f'`{user_input}`', result_code=f'{info}')
                await sent_message.edit_text(f'❌ This {"symbol" if len(user_input) > 20 else "address"} you entered is either not available on supported exchanges or could not be matched to a project by our search algorithm. Please contact me directly @fieryfox617',parse_mode=ParseMode.MARKDOWN)
                await asyncio.sleep(5)
                await sent_message.delete()
                # sent_message.reply_photo()
        else:
            chain_symbol = text.split("_")[2]
            market_pair = int(text.split("_")[3])
            interval = text.split("_")[4]
            chat_id = message.chat_id
            user = get_user_by_id(chat_id)
            if not user:
                user = create_user(chat_id)
            await message.delete()
            info = cex_exact_info(symbol=chain_symbol, market_pair=market_pair)
            if type(info) != str:
                sent_message = await context.bot.send_message(text= f'Searching info of `{chain_symbol}` on {info["exchange"]["name"]} for {interval} period', chat_id=message.chat_id, parse_mode=ParseMode.MARKDOWN)
                await chart_cx_final_response(message=sent_message, context=context, chain_info=info, interval=interval, indicators=user.indicators, style=user.style)
            else:
                log_function(log_type="chart_cx", chat_id=message.chat_id, chain_id=user.chain, chain_address=user_input, result=f'{info}')
                await admin_notify(context=context, admin_chat_id=admin, user_chat_id=message.chat_id, rquest_type='Chart Cex', user_input=f'`{user_input}`', result_code=f'{info}')
                sent_message = await context.bot.send_message(text=f'❌ This symbol {chain_symbol} you entered is either not available on supported exchanges or could not be matched to a project by our search algorithm. Please contact me directly @fieryfox617',parse_mode=ParseMode.MARKDOWN)
                await asyncio.sleep(5)
                await sent_message.delete()
                return None

# /heatmap handling functions
async def heatmap_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    # Define the response message and buttons
    message = update.message or update.callback_query.message 
    keyboard = []
    for i in candidate_datasource:
        keyboard.append([InlineKeyboardButton(candidate_datasource[i], callback_data=f'heatmap_{i}')])
    keyboard.append([InlineKeyboardButton("✖ Close", callback_data='heatmap_close')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await message.reply_text(
            'Which datasource do you like to use?', reply_markup=reply_markup
        )

async def heatmap_blocksize_handle(message: Update.message, context: ContextTypes.DEFAULT_TYPE, datasource:str) -> None:
    
    # Define the response message and buttons
    keyboard = []
    for i in candidate_blocksize:
        keyboard.append([InlineKeyboardButton(candidate_blocksize[i], callback_data=f'heatmap_{datasource}_{i}')])
        
    keyboard.append([InlineKeyboardButton("✖ Close", callback_data='heatmap_close')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await message.edit_text(
            'Which blocksize do you like to use?', reply_markup=reply_markup
        )
    
async def heatmap_callback_handle(update: Update, context: ContextTypes.DEFAULT_TYPE)->None:
    message = update.callback_query.message
    text = update.callback_query.data
    datasource = text.split("_")[1]
    if datasource == "close":
        await message.delete()
    else:
        if len(text.split("_")) == 2:
            await heatmap_blocksize_handle(message=message, context=context, datasource=datasource)
        else:
            blocksize = "_".join(text.split("_")[2::])
            await message.edit_text(f'Generating heatmap by {candidate_blocksize[blocksize]} on {candidate_datasource[datasource]}')
            heatmap_path = "heatmap.png"
            heatmap = get_heatmap(datasource=datasource, blocksize=blocksize, file_path=heatmap_path)
            if heatmap != True:
                log_function(log_type="heatmap", chat_id=message.chat_id, chain_id=candidate_datasource[datasource], chain_address=candidate_blocksize[blocksize], result="Failed in heatmap generation")
                await admin_notify(context=context, admin_chat_id=admin, user_chat_id=message.chat_id, rquest_type='Heatmap', user_input=f'`{heatmap}`', result_code='Failed in heatmap generation')
                await message.edit_text(f'❌ Failed in heatmap by {candidate_blocksize[blocksize]} on {candidate_datasource[datasource]}. Please contact me directly @fieryfox617')
                await asyncio.sleep(5)
                await message.delete()
                return None
            
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text="🔄", callback_data=f'heatmap_{datasource}_{blocksize}')]])
            await message.delete()
            with open(heatmap_path, 'rb') as f:
                await context.bot.send_photo(
                    photo=f,
                    chat_id=message.chat_id,
                    caption=f'🕋 Datasource: {candidate_datasource[datasource]}\n📐 Blocksize: {candidate_blocksize[blocksize]}',
                    reply_markup=reply_markup
                )
                log_function(log_type="heatmap", chat_id=message.chat_id, chain_id=candidate_datasource[datasource], chain_address=candidate_blocksize[blocksize], result="successful")

# /cx handling functions
async def cx_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Define the response message and buttons 
    message = update.message or update.callback_query.message
    
    text = update.message.text or update.callback_query.data
    if text.strip() == "/cx":
        i_text = (
            "💡 The `/cx` command requires a ticker. For example: `/cx btc`. "
            "Or: type `/help` for assistance."
        )
        # Save the sent message object into a variable `sent_message`
        sent_message = await message.reply_text(i_text, parse_mode=ParseMode.MARKDOWN)
        # Wait for 5 seconds
        await asyncio.sleep(5)
        # Use `sent_message.message_id` to reference the correct message ID
        await sent_message.delete()
        return None

    user_input = text.split("/cx ")[-1]

    chat_id = message.chat_id
    user = get_user_by_id(chat_id)
    if not user:
        user = create_user(chat_id)

    sent_message = await message.reply_text(f'Searching info of `{user_input}` for {user.interval} period', parse_mode=ParseMode.MARKDOWN)

    info = cex_info_symbol_market_pair(symbol=user_input)
    
    if type(info) != str:
        if len(info) == 1:
            await cx_final_response(message=sent_message, context=context, chain_info=info[0], interval=user.interval, style=user.style)
        else:
            # await sent_message.edit_text(f'⚠ There isn\'t info of {user_input} on {user.chain}. So researching on {chain_name}.')
            await cx_select_platform(message=sent_message, context=context, chain_info=info, user_input=user_input, interval=user.interval, indicators=user.indicators, style=user.style)
    else:
        log_function(log_type="cx_chart", chat_id=message.chat_id, chain_id=user.chain, chain_address=user_input, result=f"{info}")
        await admin_notify(context=context, admin_chat_id=admin, user_chat_id=message.chat_id, rquest_type='CX Chart', user_input=f'`{user_input}`', result_code=f"{info}")        
        await sent_message.edit_text(f'❌ This {"symbol" if len(user_input) > 20 else "address"} you entered is either not available on supported exchanges or could not be matched to a project by our search algorithm. Please contact me directly @fieryfox617',parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(5)
        await sent_message.delete()
        # sent_message.reply_photo()

async def cx_final_response(message: Update.message, context: ContextTypes.DEFAULT_TYPE, chain_info:dict, interval:str, indicators:str, style:str) -> None:
    file_path = "cex_chart.png"
    symbol = chain_info["market_pair_base"]["exchange_symbol"]
    exchange = chain_info["exchange"]["slug"]
    market_id = chain_info["market_id"]
    await message.edit_text(f'Generating chart for `{symbol}` on {chain_info["exchange"]["name"]} for {interval} period', parse_mode=ParseMode.MARKDOWN)
    now = datetime.now()
    user_interval = ""
    period = ""
    if interval == '5m':
        start = now - timedelta(minutes=2500)
        user_interval = 5
        period = "hourly"
    elif interval == '1h':
        start = now - timedelta(hours=500)
        user_interval = 60
        period = "hourly"
    elif interval == '6h':
        start = now - timedelta(days=90)
        user_interval = 360
        period = "hourly"
    elif interval == '1D':
        start = now - timedelta(days=90)
        user_interval = 1440
        period = "daily"
    exchange = i["exchange"]["slug"]
    running, picture = get_picture_cex(exchange=exchange, chain=symbol, file_path=file_path, style=style, indicators=indicators, interval=user_interval)
    detailed_info = get_detailed_info(symbol=symbol)
    # picture = cex_historical_info(symbol=symbol, time_start=start.strftime("%Y-%m-%dT%H:%M:%S"), time_end=now.strftime("%Y-%m-%dT%H:%M:%S"), interval=user_interval, period=period, file_path=file_path, style=style)
    if running == False or type(detailed_info) == str:
        if type(detailed_info) == str:
            log_function(log_type="cx_chart", chat_id=message.chat_id, chain_id=symbol, chain_address=exchange, result=f'{detailed_info}')
            await admin_notify(context=context, admin_chat_id=admin, user_chat_id=message.chat_id, rquest_type='CX Chart', user_input=f'`{symbol}`, `{exchange}`', result_code=f'{detailed_info}')
        else:
            log_function(log_type="cx_chart", chat_id=message.chat_id, chain_id=symbol, chain_address=exchange, result="Failed in CEX chart Generation")
            await admin_notify(context=context, admin_chat_id=admin, user_chat_id=message.chat_id, rquest_type='CX Chart', user_input=f'`{symbol}`, `{exchange}`', result_code="Failed in CEX chart Generation")
        await message.edit_text(f'❌ This symbol {symbol} you entered is either not available on supported exchanges or could not be matched to a project by our search algorithm. Please contact me directly @fieryfox617',parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(5)
        await message.delete()
        return None
    
    price = round(chain_info["quote"]["USD"]["price"], 3)
    volume_24h = round(chain_info["quote"]["USD"]["volume_24h"],3)
    
    market_cap = round(detailed_info["quote"]["USD"]["market_cap"],3)

    interval_keyboard = []
    times = ['5m','1h','6h','1D']
    for i in times:
        if i == interval:
            interval_keyboard.append(InlineKeyboardButton(text="🔄", callback_data=f'cx_{symbol}_{market_id}_{i}'))
        else:
            interval_keyboard.append(InlineKeyboardButton(text=i, callback_data=f'cx_{symbol}_{market_id}_{i}'))
    ta_i_keyboard = []
    if picture:
        ta_i_keyboard.append(InlineKeyboardButton(text="👁 TA", callback_data=f'ta_{picture}'))
    ta_i_keyboard.append(InlineKeyboardButton(text="ℹ", callback_data=f'i_CX_{symbol}_{market_id}_{i}'))
    reply_markup = InlineKeyboardMarkup([interval_keyboard, ta_i_keyboard])
    await message.delete()
    with open(file_path, 'rb') as f:
        await context.bot.send_photo(
            photo = f,
            chat_id=message.chat_id,
            caption=f'📌 Project: {detailed_info["name"]}/{symbol} ({interval})\n\n💰 Price USD: ${"{:,}".format(price)}\n💵 Market cap: ${"{:,}".format(market_cap)}\n🌊 Volume 24h: ${"{:,}".format(volume_24h)}',
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
        log_function(log_type="cx_chart", chat_id=message.chat_id, chain_id=symbol, chain_address=exchange, result="successful")

async def cx_select_platform(message: Update.message, context: ContextTypes.DEFAULT_TYPE, chain_info:dict, user_input:str, interval:str, indicators:str, style:str) ->None:
    exchanges = {}
    for i in chain_info:
        exchange_name = i["exchange"]["slug"]
        if exchange_name in exchanges:
            exchanges[exchange_name].append(i)
        else:
            exchanges[exchange_name] = [i]
    
    keyboard = []
    keys = list(exchanges.keys())
    back_button_flag=True
    if len(keys) == 1:
        await cx_final_response(message=message, context=context, chain_info=exchanges[keys[0]][0], interval=interval, indicators=indicators, style=style)
    else:
        for i in range(0, len(keys), 3):
            rows = []
            for y in range(0,3):
                try:
                    title = f'{exchanges[keys[i+y]][0]["exchange"]["name"]}'
                    call_back = f'cx_{exchanges[keys[i+y]][0]["market_pair_base"]["exchange_symbol"]}_{exchanges[keys[i+y]][0]["market_id"]}_{interval}'
                    rows.append(InlineKeyboardButton(title, callback_data=call_back))
                except:
                    rows.append(InlineKeyboardButton("✖ Close", callback_data='cx_close'))
                    back_button_flag=False
                    break
            keyboard.append(rows)
        if back_button_flag:
            keyboard.append([InlineKeyboardButton("✖ Close", callback_data='cx_close')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await message.edit_text(
            "Which exchange would you like to use?", reply_markup=reply_markup
        )

async def cx_callback_handle(update: Update, context: ContextTypes.DEFAULT_TYPE)->None:
    message = update.callback_query.message
    text = update.callback_query.data
    chain_symbol = text.split("_")[1]
    if chain_symbol == "close":
        await message.delete()
    else:
        market_pair = int(text.split("_")[2])
        interval = text.split("_")[3]
        chat_id = message.chat_id
        user = get_user_by_id(chat_id)
        if not user:
            user = create_user(chat_id)
        await message.delete()
        info = cex_exact_info(symbol=chain_symbol, market_pair=market_pair)
        if type(info) != str:
            sent_message = await context.bot.send_message(text= f'Searching info of `{chain_symbol}` on {info["exchange"]["name"]} for {interval} period', chat_id=message.chat_id, parse_mode=ParseMode.MARKDOWN)
            await cx_final_response(message=sent_message, context=context, chain_info=info, interval=interval, indicators=user.indicators, style=user.style)
        else:
            log_function(log_type="cx_chart", chat_id=message.chat_id, chain_id=user.chain, chain_address=chain_symbol, result=f'{info}')
            await admin_notify(context=context, admin_chat_id=admin, user_chat_id=message.chat_id, rquest_type='CX Chart', user_input=f'`{chain_symbol}`, {market_pair}', result_code=f'{info}')        
            sent_message = await context.bot.send_message(text=f'❌ This symbol {chain_symbol} you entered is either not available on supported exchanges or could not be matched to a project by our search algorithm. Please contact me directly @fieryfox617',parse_mode=ParseMode.MARKDOWN)
            await asyncio.sleep(5)
            await sent_message.delete()
            return None
    
async def ta_handle(update: Update, context: ContextTypes.DEFAULT_TYPE)->None:
    message = update.callback_query.message
    text = update.callback_query.data
    chart_url = text.split("_")[1]
    await message.delete()
    send_message = await context.bot.send_message(text= f'🧠⏳️ Analyzing chart image, this might take a few moments. Please wait...', chat_id=message.chat_id, parse_mode=ParseMode.MARKDOWN)
    
    info = ta_response(chart_url=chart_url)
    if info:
        await send_message.edit_text(text= f'{info}', parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        log_function(log_type="ta", chat_id=message.chat_id, chain_id="", chain_address=chart_url, result=f'successful') 
    else:
        log_function(log_type="ta", chat_id=message.chat_id, chain_id="", chain_address=chart_url, result=f'Failed in analysis')
        await admin_notify(context=context, admin_chat_id=admin, user_chat_id=message.chat_id, rquest_type='Technial Analysis', user_input=f'`{chart_url}`', result_code=f'Failed in analysis')
        await send_message.edit_text(text= f'❌ Technical analysis has failed on this chart. This may be due to an internal error or the chart does not have enough information to be analysed. If you need more details please contact me directly @fieryfox617', parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        await asyncio.sleep(5)
        await send_message.delete()
        return None

# general chat handler function
async def general_chat_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message or update.callback_query.message
    chat_id = message.chat_id
    user = get_user_by_id(chat_id)
    if not user:
        user = create_user(chat_id)
    commands = user.status.split("_")
    if user.status.startswith("Add_Notify"):
        text = update.message.text or update.callback_query.data
        message_id = int(user.status.split("_")[-1])

        if chat_id < 0 and not "@AIRMAuditorBOT" in text:
            pass
        else:
            if "@AIRMAuditorBOT" in text:
                text = text.replace("@AIRMAuditorBOT", "").strip()
            keyboard = []
            keyboard.append([InlineKeyboardButton("CEX", callback_data=f'N_C_{text}'), InlineKeyboardButton("DEX", callback_data=f'N_D_{text}')])
            keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='N_add_notify'), InlineKeyboardButton("✖ Cancel", callback_data='settings_notify')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await message.delete()
            await context.bot.edit_message_text(
                text=
                f'* Add New Alert & Notification *\n\n'
                f'*Symbol:* {text}\n\n'
                f"What platform do you want?",
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=reply_markup, 
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )

    elif user.status.startswith('N_Edit_V_'):
        text = update.message.text or update.callback_query.data
        if chat_id < 0 and not "@AIRMAuditorBOT" in text:
            pass
        else:
            if "@AIRMAuditorBOT" in text:
                text = text.replace("@AIRMAuditorBOT", "").strip()
            symbol = commands[3]
            message_id = int(commands[-1])
            keyboard = []
            keyboard.append([InlineKeyboardButton("No", callback_data=f'N_Edit_{int(symbol)}'), InlineKeyboardButton("Yes", callback_data=f'N_Edit_V_{text}_Y_{int(symbol)}')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await message.delete()
            reply_text= f'Are you sure you want to change the limited value to {text}?'
            await context.bot.edit_message_text(
                text=escape_special_characters(reply_text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=reply_markup, 
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
    
    elif len(commands) == 8:
        text = update.message.text or update.callback_query.data
        if chat_id < 0 and not "@AIRMAuditorBOT" in text:
            pass
        else:
            role = commands[1]
            name = commands[2]
            symbol = commands[3]
            chain = commands[4]
            platform = commands[5]
            condition = commands[6]
            message_id = int(commands[7])
            if "@AIRMAuditorBOT" in text:
                text = text.replace("@AIRMAuditorBOT", "").strip()
            keyboard = []
            keyboard.append([InlineKeyboardButton("Telegram", callback_data=f'N_{role}_N_S_C_P_C_{text}_T')])
            keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f'N_{role}_N_S_C_P_{condition}'), InlineKeyboardButton("✖ Cancel", callback_data='settings_notify')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await message.delete()
            reply_text = f'* Add New Alert & Notification *\n\n*Exchange Type:* DEX\n*Name:* {name}\n*Symbol:* {symbol}\n*Chain:* {default_chain[chain]}\n*DEX Platform*: {platform}\n*Monitored Item:* {default_condition[condition]}\n*Limited Value:* {text}\n\nPlease choose notification type.'
            await context.bot.edit_message_text(
                text= escape_special_characters(reply_text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=reply_markup, 
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
