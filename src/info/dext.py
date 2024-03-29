from dexscreener import DexscreenerClient
import os, json
from datetime import datetime
import subprocess

client = DexscreenerClient()

def get_token_pair_address(chain, address):
    try:
        info = client.get_token_pair(chain, address)
        return info
    except:
        try:
            info = client.get_token_pairs(address)
            return info
        except:
            return None
        
def get_token_chain_symbol(chain):
    return client.search_pairs(chain)

def dx_get_info(default_chain, user_input):
    if len(user_input) > 20: 
        
        info = get_token_pair_address(chain=default_chain, address=user_input)
        if info:
            if type(info) == list:
                return dex_token_address_handle(default_chain=default_chain, info=info)
                
            else:
                return True, info
        else:
            return True, None
    else:
        info = get_token_chain_symbol(chain=user_input)
        if info == []:
            return True, None
        else:
            return dex_token_address_handle(default_chain=default_chain, info=info)

def dex_token_address_handle(default_chain, info):
    dex_platforms = {}
    for i in info:
        if i.chain_id in dex_platforms:
            if i.dex_id in dex_platforms[i.chain_id]:
                dex_platforms[i.chain_id][i.dex_id].append(i)
            else:
                dex_platforms[i.chain_id][i.dex_id] = [i]
        else:
            dex_platforms[i.chain_id] = {i.dex_id:[i]}
    
    if default_chain in dex_platforms:
        return default_chain, dex_platforms[default_chain]
    
    max_price = 0
    chain_id = ""
    for i in dex_platforms:
        av_price = sum(sum(float(m.price_usd) if m.price_usd else 0 for m in dex_platforms[i][y]) for y in dex_platforms[i])
        num = sum(sum(1 if m.price_usd else 0 for m in dex_platforms[i][y]) for y in dex_platforms[i])
        if av_price/num > max_price:
            max_price = av_price/num
            chain_id = i
        
    return chain_id, dex_platforms[chain_id]

def get_picture(chain, address, file_path, indicators, style, interval):
    if indicators == None or indicators == "":
        process = subprocess.run(['node', 'src\\info\\chart\\index.js', chain, address, file_path, 'nu', style, interval], capture_output=True, text=True, encoding='utf-8')
        if process.returncode == 0:
            output = process.stdout
            data = json.loads(output)
            return True, data["copy_url"]
        else:
            return False, f'{chain} {address} {file_path} nu {style} {interval}'
    else:
        process = subprocess.run(['node', 'src\\info\\chart\\index.js', chain, address, file_path, indicators, style, interval], capture_output=True, text=True, encoding='utf-8')
        if process.returncode == 0:
            output = process.stdout
            data = json.loads(output)
            return True, data["copy_url"]
        else:
            return False, f'{chain} {address} {file_path} {indicators} {style} {interval}'

def get_heatmap(datasource, blocksize, file_path):
    process = subprocess.run(['node', 'src\\info\\chart\\heatmap.js', datasource, blocksize, file_path], capture_output=True, text=True, encoding='utf-8')
    if process.returncode == 0:
        return True
    else:
        return f'{datasource} {blocksize} {file_path}'