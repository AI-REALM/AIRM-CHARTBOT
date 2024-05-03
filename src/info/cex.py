import os
import json
import subprocess
import coinmarketcapapi
import pandas as pd
import mplfinance as mpf
from dotenv import load_dotenv

# Load env of Coinmarketcap API
load_dotenv(dotenv_path='.env')
api_key = os.getenv('COINMAKRET_KEY')

# Set Coinmarketcap API
cmc_client = coinmarketcapapi.CoinMarketCapAPI(api_key)

cex_platform = ["bybit", "okx", "gate-io", "coinbase-exchange", "upbit", "bitget", "kucoin", "bitflyer", "gemini", "exmo", "whitebit", "bitrue", "poloniex", "bitmart", "bithumb", "bitfinex", "kraken", "BingX", "binance"]

def cex_info_symbol_market_pair(symbol):
    try:
        info = cmc_client.cryptocurrency_marketpairs_latest(symbol=symbol).data
        crypto_data = info[0]
    except Exception as e:
        try:
            info = cmc_client.cryptocurrency_marketpairs_latest(name=symbol).data
            crypto_data = info[0]
        except:
            candidates = cmc_client.cryptocurrency_info(symbol=symbol).data
            candidates_id = candidates[list(candidates.keys())[0]][0]["id"]
            try:
                info = cmc_client.cryptocurrency_marketpairs_latest(id=candidates_id).data
                crypto_data = info
            except:
                return False, e.rep.error_message
    market_pair = {}
    
    for i in crypto_data["market_pairs"]:
        if i["exchange"]["slug"] in cex_platform:
            if i["exchange"]["slug"] in market_pair:
                market_pair[i["exchange"]["slug"]].append(i)
            else:
                market_pair[i["exchange"]["slug"]] = [i]
        else:
            pass
    name = [crypto_data["name"], crypto_data["id"]]
    if market_pair == {}:
        return False, "There are no CEX data"
    else:
        return name, market_pair

def cex_exact_info(symbol, market_pair):
    try:
        info = cmc_client.cryptocurrency_marketpairs_latest(id=symbol).data
    except Exception as e:
        return e.rep.error_message
    market_chains = []
    for i in info["market_pairs"]:
        if i["exchange"]["slug"] == market_pair:
            market_chains.append(i)
    if market_pair:
        return market_chains
    else:
        return None

def cex_info_symbol_market_pair_id(id):
    info = cmc_client.cryptocurrency_marketpairs_latest(id=id).data
    market_pair = {}
    
    for i in info["market_pairs"]:
        if i["exchange"]["slug"] in cex_platform:
            if i["exchange"]["slug"] in market_pair:
                market_pair[i["exchange"]["slug"]].append(i)
            else:
                market_pair[i["exchange"]["slug"]] = [i]
        else:
            pass
    name = [info["name"], info["id"]]
    if market_pair == {}:
        return False, "There are no CEX data"
    else:
        return name, market_pair

def get_detailed_info(id):
    try:
        test = cmc_client.cryptocurrency_quotes_latest(id=id).data
        return test[str(id)]
    except Exception as e:
        return e.rep.error_message

def get_picture_cex(chain, exchange, file_path, indicators, style, interval):
    if indicators == None or indicators == "":
        process = subprocess.run(['node', 'src\\info\\chart\\cex.js', exchange, chain, file_path, 'nu', style, str(interval)], capture_output=True, text=True, encoding='utf-8')
        if process.returncode == 0:
            output = process.stdout
            data = json.loads(output)
            try:
                chart_url = data["copy_url"].split("/")[-2]
            except:
                chart_url = ''
            return True, chart_url
        else:
            return False, f'{exchange}, {chain} {file_path} nu {style} {interval}'
    else:
        process = subprocess.run(['node', 'src\\info\\chart\\cex.js', exchange, chain, file_path, indicators, style, str(interval)], capture_output=True, text=True, encoding='utf-8')
        if process.returncode == 0:
            output = process.stdout
            data = json.loads(output)
            try:
                chart_url = data["copy_url"].split("/")[-2]
            except:
                chart_url = ''
            return True, chart_url
        else:
            return False, f'{exchange}, {chain} {file_path} {indicators} {style} {interval}'