from turtle import color
from web3 import Web3
import json, os, math, statistics
import requests
from etherscan import Etherscan
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from operator import itemgetter
import numpy
import seaborn as sns

api_key = '3TIXWXERJIF3P1WG8ZB5QQSFYUGFW5C1I9'
eth = Etherscan(f'{api_key}')
w3 = Web3(Web3.HTTPProvider('https://eth-mainnet.alchemyapi.io/v2/g8E7SWPSitoMKPgSl5o7b2nuZx4ZUN-H'))

def get_txs_by_contract_old(add, sblock, eblock, sort):
    r = requests.get(
        "https://api.etherscan.io/api",
        params={
            "module": "account",
            "action": "tokennfttx",
            "contractaddress": add,
            "startblock": sblock,
            "endblock": eblock,
            "page": 1,
            "offset": 10000,
            "sort": sort,
            "apikey": api_key,
        },
        headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, '
                               'like Gecko) Chrome/50.0.2661.102 Safari/537.36'},  timeout=10)
    return(r.json()["result"])

def get_txs_by_contract(add, sblock, eblock, sort):
    list_txs=[]
    aux_sblock = sblock
    while 1:
        r = requests.get(
            "https://api.etherscan.io/api",
            params={
                "module": "account",
                "action": "tokennfttx",
                "contractaddress": add,
                "startblock": aux_sblock,
                "endblock": eblock,
                "page": 1,
                "offset": 10000,
                "sort": sort,
                "apikey": api_key,
            },
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, '
                                'like Gecko) Chrome/50.0.2661.102 Safari/537.36'})
        list_txs.extend(r.json()["result"])
        if len(r.json()["result"]) < 10000: break
        else: aux_sblock = int(r.json()["result"][-1]["blockNumber"])
    print('done')
    return(list_txs)

def get_txs_by_address(add, sblock, eblock, sort):
    list_txs=[]
    aux_sblock = sblock
    while 1:
        r = requests.get(
            "https://api.etherscan.io/api",
            params={
                "module": "account",
                "action": "tokennfttx",
                "address": add,
                "startblock": aux_sblock,
                "endblock": eblock,
                "page": 1,
                "offset": 10000,
                "sort": sort,
                "apikey": api_key,
            },
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, '
                                'like Gecko) Chrome/50.0.2661.102 Safari/537.36'})
        list_txs.extend(r.json()["result"])
        if len(r.json()["result"]) < 10000: break
        else: aux_sblock = int(r.json()["result"][-1]["blockNumber"])
    return(list_txs)

def get_type(df):
    path = f'/Users/rafaelcizeskinitchai/Documents/FeistyAnalytics/REPORT_PFP/FeistyReport/DATA/aux/get_type'

    if not os.path.exists(path):
                os.makedirs(path)

    for i in range(0, len(df)):
        print(f"Getting type of tx {i+1} out {len(df)}. ({(i+1)*100/len(df)})")
        try:
            tx = w3.eth.get_transaction(df.iloc[i]['hash'])

            abi_endpoint = f"https://api.etherscan.io/api?module=contract&action=getabi&address={tx['to']}&apikey={api_key}"
            abi = json.loads(requests.get(abi_endpoint).text)

            contract = w3.eth.contract(address=tx['to'], abi=abi['result'])

            func_obj, func_params = contract.decode_function_input(tx['input'])

            df.loc[i, 'type']=func_obj.__class__.__name__
        except:
            df.loc[i, 'type']="fail"
        df.to_pickle(f'{path}/dataframe.pkl')
    return(df)

def plot_mints_contract(df, timeframe):
    df['timeStamp'] = df['timeStamp'].astype(int)
    initial_timestamp = df.iloc[0]["timeStamp"]
    final_timestamp = df.iloc[-1]['timeStamp']

    if timeframe == 'daily':
        aux_interval = 86400
    if timeframe == 'hourly':
        aux_interval = 3600
    if timeframe == 'minutely':
        aux_interval = 60

    total_number_intervals = math.ceil((final_timestamp - initial_timestamp)/aux_interval)
    sales = [0]*total_number_intervals
    time = [initial_timestamp]*total_number_intervals
    for i in range(1,total_number_intervals+1):
        sales[i-1] = len(df[(df['timeStamp']>=(initial_timestamp + ((i-1)*aux_interval))) & (df['timeStamp']<(initial_timestamp + ((i)*aux_interval)))])
        time[i-1] = initial_timestamp + ((i)*aux_interval)
    
    time = mdates.epoch2num(time)

    fig = plt.figure(figsize=(10,5))
    public_sale = mdates.epoch2num(1645634753)



    #plt.axvline(x=public_sale, color='red', alpha = 0.6)
    if timeframe == 'daily':
        plt.bar(time, sales, width=0.9, alpha=0.8)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%D'))
    if timeframe == 'hourly':
        plt.bar(time, sales, width=0.9*(1/24), alpha=0.8)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H'))
    if timeframe == 'minutely':
        plt.bar(time, sales, width=0.9*(1/1440), alpha=0.8)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%M'))
    
    plt.xlabel('Time')
    plt.ylabel('# of tokens minted')
    plt.show()

def plot_mints_contract_byblock(df, timestamp_sale):
    df['blockNumber'] = df['blockNumber'].astype(int)
    
    public_sale_block = int(eth.get_block_number_by_timestamp(timestamp=timestamp_sale, closest="before"))

    print(public_sale_block)
    initial_block = public_sale_block #df.iloc[0]["blockNumber"]
    final_block = df.iloc[-1]['blockNumber']

    total_blocks = final_block - initial_block
    print(total_blocks)
    
    sales = [0]*total_blocks
    block = [initial_block]*total_blocks
    for i in range(0,total_blocks):
        aux_block = initial_block + i
        sales[i] = len(df[(df['blockNumber']==aux_block)])
        block[i] = i
    
    fig = plt.figure(figsize=(2.5,5))

    #plt.axvline(x=public_sale_block, color='red', alpha = 0.6)
    plt.bar(block, sales, width=0.9, alpha=0.8)
    plt.xticks(range(0,3))
    plt.xlabel('n-th block after public sale timestamp')
    plt.ylabel('# of tokens minted')
    plt.show()

def plot_gas_by_timestamp(df, timeframe):
    df['timeStamp'] = df['timeStamp'].astype(int)
    initial_timestamp = df.iloc[0]["timeStamp"]
    final_timestamp = df.iloc[-1]['timeStamp']

    if timeframe == 'daily':
        aux_interval = 86400
    if timeframe == 'hourly':
        aux_interval = 3600
    if timeframe == 'minutely':
        aux_interval = 60

    total_number_intervals = math.ceil((final_timestamp - initial_timestamp)/aux_interval)
    gas_mean = [0]*total_number_intervals
    gas_median = [0]*total_number_intervals
    time = [initial_timestamp]*total_number_intervals
    for i in range(1,total_number_intervals+1):
        filtered_df = df[(df['timeStamp']>=(initial_timestamp + ((i-1)*aux_interval))) & (df['timeStamp']<(initial_timestamp + ((i)*aux_interval)))]
        gas_mean[i-1] = w3.fromWei(filtered_df['gasPrice'].mean(axis=0),'Gwei')
        gas_median[i-1] = w3.fromWei(filtered_df['gasPrice'].median(axis=0),'Gwei')
        time[i-1] = initial_timestamp + ((i)*aux_interval)
    
    time = mdates.epoch2num(time)

    fig = plt.figure(figsize=(10,5))
    public_sale = mdates.epoch2num(1645634753)



    plt.axvline(x=public_sale, color='red', linewidth=0.9, alpha = 0.6)
    plt.plot(time, gas_mean, linewidth=2.9, alpha=0.8)
    #plt.plot(time, gas_median, linewidth=2.9, color = 'green', alpha=0.8)
    if timeframe == 'daily':
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%D'))
    if timeframe == 'hourly':
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H'))
    if timeframe == 'minutely':
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%M'))
    plt.yscale('log')
    plt.xlabel('Time')
    plt.ylabel('Mean Gas Price(Gwei)')
    plt.show()

def get_distribution_tokens_per_address(df, number_holders):
    dict_add={}
    for count in range(0, len(df)):
        add_aux = df['to'].iloc[count]
        id_aux = df['tokenID'].iloc[count]
        gas_aux = df['gasPrice'].iloc[count]
        if add_aux not in dict_add:
            dict_add[add_aux] = {'tokens':[id_aux], 'gas': [gas_aux]}
        else: 
            dict_add[add_aux]['tokens'].append(id_aux)
            dict_add[add_aux]['gas'].append(gas_aux)
    
    print(len(dict_add))
    list_aux = [0]*len(dict_add)
    i=0
    for key in dict_add:
        list_aux[i] = [len(dict_add[key]['tokens']), statistics.mean(dict_add[key]['gas']), statistics.median(dict_add[key]['gas']), key]
        i+=1
    list_aux=sorted(list_aux, key=itemgetter(0), reverse=True)

    list_final = [0]*len(list_aux)
    list_mean = [0]*len(list_aux)
    list_median = [0]*len(list_aux)
    for i in range(0,len(list_aux)):
        list_final[i] = list_aux[i][0]
        list_mean[i] = list_aux[i][1]
        list_median[i] = list_aux[i][2]

    quantiles = statistics.quantiles(list_final, n=4)
    fig = plt.figure(figsize=(5,5))
    mean = w3.fromWei(int(statistics.mean(list_mean)),'Gwei')
    median = w3.fromWei(int(statistics.median(list_median)),'Gwei')
    print(f"Total number of tokens minted: {sum(list_final)}.\nNumber of unique add: {len(list_final)}.\nMean: {statistics.mean(list_final)}.\nMedian: {statistics.median(list_final)}.\nMean Gas(Gwei): {mean}.\nMedian Gas(Gwei): {median}\n\nQuantiles: {quantiles}")
    print(sum(list_final[0:20]))
    plt.bar(range(1,number_holders+1), list_final[0:number_holders], width = 0.8, alpha=0.8)
    plt.ylabel('# of tokens minted')
    plt.xlabel('n-th largest mintooooor')
    #plt.yticks(range(0,3))
    plt.xticks(range(0,number_holders, math.floor(number_holders/5)))
    plt.show()

def get_list_tokens(df, add):
    list_tokens = []
    for i in range(0, len(df)):
        if (df.iloc[i]['to'] == add) or (Web3.toChecksumAddress(df['to'].iloc[i]) == add):
            list_tokens.append(df.iloc[i]['tokenID'])
        if (df.iloc[i]['from'] == add) or (Web3.toChecksumAddress(df['from'].iloc[i]) == add):
            try:
                list_tokens.remove(df.iloc[i]['tokenID'])
            except:
                print(f'ERROR: COULD NOT FIND TOKENID {df.iloc[i]["tokenID"]} from collection {df.iloc[i]["tokenName"]} -- tx hash{df.iloc[i]["hash"]}')
    return list_tokens


df_addresses = pd.read_pickle('/Users/rafaelcizeskinitchai/Documents/FeistyAnalytics/REPORT_PFP/FeistyReport/DATA/wallet/df_addresses.pkl')
path = '/Users/rafaelcizeskinitchai/Documents/FeistyAnalytics/REPORT_PFP/FeistyReport/DATA/wallet/'

list_tokens = []
list_slugs = []
for i in df_addresses.iterrows():
    slug=i[1]['slug']
    list_slugs.append(slug)
    df_aux = pd.read_pickle(f'{path}/{slug}/dataframe.pkl')
    aux_list = df_aux['tokenName'].unique()
    aux_list.sort()
    list_tokens.extend(aux_list)
list_tokens = list(dict.fromkeys(list_tokens))
list_tokens.sort()

matrix_count = numpy.zeros((len(df_addresses), len(list_tokens)))

for count_token in range(0, len(list_tokens)):
    key = list_tokens[count_token]
    for count_address in df_addresses.iterrows():
        add_index = int(count_address[0])
        slug=count_address[1]['slug']
        df_aux = pd.read_pickle(f'{path}/{slug}/dataframe.pkl')
        filtered_df = df_aux[df_aux['tokenName']==key]
        list_aux = get_list_tokens(filtered_df, count_address[1]['address'])
        matrix_count[add_index, count_token] = len(list_aux)
        #print(f'{slug} owns {len(list_aux)} tokens from {key} collection.')

#print(matrix_count)
za = (matrix_count > 0)
#print(za)
dict_aux={}
for column in range(0, len(matrix_count[0,:])):
    if za[:, column].sum()>1:
        dict_aux[list_tokens[column]] = matrix_count[:, column]/max(matrix_count[:, column])
        print(f'{list_tokens[column]}: {matrix_count[:, column]}')
#
final_df = pd.DataFrame(dict_aux, index=['add1', 'add2', 'add3'])
print(final_df)
sns.heatmap(final_df, cmap="YlGnBu", square=True)
plt.show()
# %%
