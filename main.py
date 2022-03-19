from etherscan import Etherscan
from matplotlib import collections
from numpy import argmax
import pandas as pd
from web3 import Web3
import requests
from functions import get_list_tokens, get_txs_by_contract, get_txs_by_address, get_type, plot_gas_by_timestamp, plot_mints_contract, plot_mints_contract_byblock, get_distribution_tokens_per_address
import os, json, statistics
from operator import itemgetter
from datetime import datetime



api_key = '3TIXWXERJIF3P1WG8ZB5QQSFYUGFW5C1I9'
eth = Etherscan(f'{api_key}')
w3 = Web3(Web3.HTTPProvider('https://eth-mainnet.alchemyapi.io/v2/g8E7SWPSitoMKPgSl5o7b2nuZx4ZUN-H'))

acc = '0x673F8E83b4943B39038b2C08B64CFe27890251A1'
null_add = '0x0000000000000000000000000000000000000000'

list_crap = ['RUDE KIDZ' ,'Mercedes Benz','Rolex', 'Louis Vuitton', 'Gucci', 'Dolce Gabbana', 'Burberry', 'Benz', 'Hermes', 'Balenciaga', 'Nintendo', 'APPLE', 'Coca Cola', 'PATEK PHILIPPE', 'ADIDAS', 'Louis Vuitton Ape', 'Warner Bros nft', 'Bored Ape Nike Club', 'Grammy Awards', 'Clay Boys', 'Imaginary Ones', 'LEGO']


class Contract721:
    def __init__(self, slug, caddress):
        self.caddress = caddress
        self.slug = slug
        
        path = f'/Users/rafaelcizeskinitchai/Documents/FeistyAnalytics/REPORT_PFP/FeistyReport/DATA/contract/{self.slug}'

        try:
            df=pd.read_pickle(f'{path}/dataframe.pkl')
        except:
            request = get_txs_by_contract(self.caddress, 0, 99366295, sort='asc')
            if not os.path.exists(path):
                os.makedirs(path)
            df = pd.DataFrame(request)
            df = df.drop_duplicates(subset=['hash', 'tokenID'])
            df.to_pickle(f'{path}/dataframe.pkl')
        self.df = df

    def update_dataframe(self):
        path = f'/Users/rafaelcizeskinitchai/Documents/FeistyAnalytics/REPORT_PFP/FeistyReport/DATA/contract/{self.slug}'
        sblock_aux = int(self.df.iloc[-1]["blockNumber"])
        request = get_txs_by_contract(self.caddress, sblock_aux + 1, 99366295, sort='asc')
        new_df = pd.DataFrame(request)
        new_df = new_df.drop_duplicates(subset=['hash', 'tokenID'])
        print(f"{len(new_df)} new txs found.")
        #new_df_aux = get_type(new_df)
        df = pd.concat([self.df, new_df], ignore_index=True)
        df.to_pickle(f'{path}/dataframe.pkl')
        self.df = df

    def get_type_cadd(self):
        path = f'/Users/rafaelcizeskinitchai/Documents/FeistyAnalytics/REPORT_PFP/FeistyReport/DATA/contract/{self.slug}'
        df = get_type(self.df)    
        self.df = df
        self.df.to_pickle(f'{path}/dataframe.pkl')
        
    def show_mint(self, timeframe):
        df = (self.df[self.df['from']== '0x0000000000000000000000000000000000000000'])
        plot_mints_contract(df, timeframe)
        
    def show_mint_by_block(self, timestamp):
        df = (self.df[self.df['from']== '0x0000000000000000000000000000000000000000'])
        print(df['timeStamp'].iloc[-1])
        plot_mints_contract_byblock(df, timestamp)

    def get_stats_holders(self, holders, timestamp, when):
        self.df['timeStamp'] = self.df['timeStamp'].astype(int)
        self.df['gasPrice'] = self.df['gasPrice'].astype(int)
        if when == 'before':
            df = self.df[(self.df['timeStamp'] <= timestamp) & (self.df['from'] == '0x0000000000000000000000000000000000000000')]
        if when == 'after':
            df = self.df[(self.df['timeStamp'] > timestamp) & (self.df['from'] == '0x0000000000000000000000000000000000000000')]
        get_distribution_tokens_per_address(df, holders)
        
    def show_mean_gas(self, timeframe):
        self.df['gasPrice'] = self.df['gasPrice'].astype(int)
        df = (self.df[self.df['from']== '0x0000000000000000000000000000000000000000'])
        plot_gas_by_timestamp(df, timeframe)


    
class Wallet:
    def __init__(self, slug, address):
        self.slug=slug
        self.address=address

        path = f'/Users/rafaelcizeskinitchai/Documents/FeistyAnalytics/REPORT_PFP/FeistyReport/DATA/wallet/{self.slug}'
        try:
            df_addresses = df=pd.read_pickle('/Users/rafaelcizeskinitchai/Documents/FeistyAnalytics/REPORT_PFP/FeistyReport/DATA/wallet/df_addresses.pkl')
            if self.address not in df_addresses['address'].unique():
                to_be_add = [{'slug':self.slug, 'address':self.address}]
                new_df = pd.DataFrame(to_be_add)
                df_addresses = pd.concat([df_addresses, new_df], ignore_index=True)            
                df_addresses.to_pickle('/Users/rafaelcizeskinitchai/Documents/FeistyAnalytics/REPORT_PFP/FeistyReport/DATA/wallet/df_addresses.pkl')
                print(df_addresses)
        except:
            dict = [{'slug':self.slug, 'address':self.address}]
            df_addresses = pd.DataFrame(dict)
            df_addresses.to_pickle('/Users/rafaelcizeskinitchai/Documents/FeistyAnalytics/REPORT_PFP/FeistyReport/DATA/wallet/df_addresses.pkl')
            print(df_addresses)

        try:
            df=pd.read_pickle(f'{path}/dataframe.pkl')
            print(f'Stored data found.')
        except:
            print(f'No data stored. Seaching...')
            request = get_txs_by_address(self.address, 0, 99366295, sort='asc')
            print(f'A total of {len(request)} txs were collected.')
            if not os.path.exists(path):
                os.makedirs(path)
            df = pd.DataFrame(request)
            df = df.drop_duplicates(subset=['hash', 'tokenID'])
            df.to_pickle(f'{path}/dataframe.pkl')
            with open(f'{path}/address.txt', 'w') as the_file:
                the_file.write(self.address)
        self.df = df

    def get_type_add(self):
        path = f'/Users/rafaelcizeskinitchai/Documents/FeistyAnalytics/REPORT_PFP/FeistyReport/DATA/wallet/{self.slug}'
        df = get_type(self.df)    
        self.df = df
        self.df.to_pickle(f'{path}/dataframe.pkl')

    def update_dataframe(self):
        path = f'/Users/rafaelcizeskinitchai/Documents/FeistyAnalytics/REPORT_PFP/FeistyReport/DATA/wallet/{self.slug}'
        sblock_aux = int(self.df.iloc[-1]["blockNumber"])
        request = get_txs_by_address(self.address, sblock_aux + 1, 99366295, sort='asc')
        new_df = pd.DataFrame(request)
        new_df = new_df.drop_duplicates(subset=['hash', 'tokenID'])
        print(f"{len(new_df)} new txs found.")
        df = pd.concat([self.df, new_df], ignore_index=True)
        df.to_pickle(f'{path}/dataframe.pkl')
        self.df = df

    def resume_week(self, crap, timestamp_filter):
        #add = Web3.toChecksumAddress(lower_case_address)
        df = self.df[(-self.df["tokenName"].isin(crap)) & (self.df['timeStamp'] > timestamp_filter)]
        df['timeStamp'] = df['timeStamp'].astype(int)
        list_collection=[]
        list_id=[]
        list_date=[]
        list_type=[]
        list_hash=[]
        for i in range(0, len(df)):
            list_collection.append(df['tokenName'].iloc[i])
            list_id.append(df['tokenID'].iloc[i])
            list_date.append(datetime.fromtimestamp(df['timeStamp'].iloc[i]))
            list_hash.append(df['hash'].iloc[i])
            #print(f"\n\n{Web3.toChecksumAddress(df['from'].iloc[i])}\n\n{Web3.toChecksumAddress(df['to'].iloc[i])}\n\n{self.address}\n\n")
            if Web3.toChecksumAddress(df['from'].iloc[i]) == self.address: list_type.append('Out')
            if Web3.toChecksumAddress(df['to'].iloc[i]) == self.address: list_type.append('In')

        data_aux = {"Collection": list_collection, "ID": list_id, "Type": list_type,  "Date": list_date, 'list_hash': list_hash}
        new_df = pd.DataFrame.from_dict(data_aux)
        pd.set_option('display.max_colwidth', None)   
        for key in new_df['Collection'].unique():
            print(f"\n\n\n{new_df[new_df['Collection']==key]}\n\n\n")

        print(len(list_hash))

    def get_list_tokens(self):
        self.df['timeStamp'] = self.df['timeStamp'].astype(int)
        count=1
        print("Give me a timestamp or type 0 to current list.")
        timestamp=int(input())
        if timestamp == 0: timestamp = 99999999999999
        aux_list = self.df['tokenName'].unique()
        aux_list.sort()

        for key in aux_list:
            filtered_df = self.df[(self.df['tokenName'] == key) & (self.df['timeStamp'] <= timestamp)]
            list_tokens = get_list_tokens(filtered_df, self.address)
            if len(list_tokens) > 0: print(f'{count} - {key}: {list_tokens}   ({len(list_tokens)})')
            count += 1


# cadd = '0xca7ca7bcc765f77339be2d648ba53ce9c8a262bd' 
# slug = 'tubbycats'    
    
add = '0x1d4B9b250B1Bd41DAA35d94BF9204Ec1b0494eE3' 
slug = 'path'

# cadd = '0xeEAb9AB9E2C30Bbedba61758dc669f44a651A57d'
# slug = 'tartarus'

# cadd = '0x59468516a8259058baD1cA5F8f4BFF190d30E066'
# slug='invisiblefriends'

# add = '0x08f67B21C24BadBb6E8117020c3846909aC3e65C'
# slug='me'

# slug = 'jeebus'
# add = '0xef30fa2138a725523451688279b11216b0505e98'

# add = '0x020cA66C30beC2c4Fe3861a94E4DB4A498A35872'
# slug = 'machi'

# add = '0xc35c8d48553f02d0cded9a1eac241c4d628762f1'
# slug = 'loom'

pd.options.display.max_colwidth = 100
me = Wallet(slug, add)
# me.update_dataframe()
#me.get_list_tokens()


#%%
# %%
