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

def display_trendline(long_data, file_path, style):
    mc = mpf.make_marketcolors(up='#089981',down='#F23645',
                           edge={'up':'#089981','down':'#F23645'},
                           wick={'up':'#089981','down':'#F23645'},
                           volume = '#15547D',
                           ohlc='black')
    s  = mpf.make_mpf_style(marketcolors=mc, base_mpf_style='nightclouds')
    if style in ["line", 'lineWithMarkers', 'area', 'hlcarea', 'baseline']:
        fig, axes = mpf.plot(long_data, type='line', style=s, ylabel='Price', volume=True,
                         figsize=(20, 10),
                         returnfig=True)
    elif style in ["candle", 'hollowCandle', 'hilo', 'ha']:
        fig, axes = mpf.plot(long_data, type='candle', style=s, ylabel='Price', volume=True,
                            figsize=(20, 10),
                            returnfig=True)
    elif style == "stepline":
        fig, axes = mpf.plot(long_data, type='renko', style=s, ylabel='Price', volume=True,
                            figsize=(20, 10),
                            returnfig=True)
    else:
        mc = mpf.make_marketcolors(up='#089981',down='#F23645',
                           edge={'up':'#089981','down':'#F23645'},
                           wick={'up':'#089981','down':'#F23645'},
                           volume = '#15547D',
                           ohlc='i')
        s  = mpf.make_mpf_style(marketcolors=mc, base_mpf_style='nightclouds')
        fig, axes = mpf.plot(long_data, type='ohlc', style=s, ylabel='Price', volume=True,
                            figsize=(20, 10),
                            returnfig=True)
    fig.savefig(file_path, bbox_inches='tight')

def make_finance_chart(raw_data):
    columns = ["date", "open", "high", "low", "close", "volume"]
    date_data = []
    open_data = []
    high_data = []
    low_data = []
    close_data = []
    volume = []
    
    for i in raw_data:
        date_data.append(i["time_close"])
        open_data.append(i["quote"]["USD"]["open"])
        high_data.append(i["quote"]["USD"]["high"])
        low_data.append(i["quote"]["USD"]["low"])
        close_data.append(i["quote"]["USD"]["close"])
        volume.append(i["quote"]["USD"]["volume"])

    df = pd.DataFrame(list(zip(date_data, open_data, high_data, low_data, close_data, volume)), columns=columns)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index("date", inplace=True)
    # print(df.head())
    return df

def cex_historical_info(symbol, time_start, time_end, interval, period, file_path, style):
    parameters = {
        "symbol" : symbol,
        "time_start" : time_start,
        "time_end" : time_end,
        "interval" : interval,
        "time_period": period
    }
    # test = cmc_client.cryptocurrency_quotes_historical(**parameters)
    test= cmc_client.cryptocurrency_ohlcv_historical(**parameters)
    data = make_finance_chart(raw_data=test.data[symbol][0]["quotes"])

    try:
        display_trendline(long_data=data, file_path=file_path, style=style)
        return True
    except:
        return False

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
    print(f'{exchange} {chain} {file_path} nu {style} {interval}')
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