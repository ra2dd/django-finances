from binance.spot import Spot
import datetime, json, string
import os

from ..models import Asset, AssetPriceHistory

class PriceHistory():
    def __init__(self, ticker):
        self.ticker = ticker
        self.price = None

def datetime_to_timestamp(date):
    return round(datetime.datetime.timestamp(date))

def timestamp_to_datetime(timestamp):

    timestamp_length = len(str(timestamp))

    if timestamp_length == 13:
        return datetime.datetime.fromtimestamp(timestamp/1000)
    elif timestamp_length == 10:
        return datetime.datetime.fromtimestamp(timestamp)
    else:
        raise Exception(f'Timestamp length is out of range - {timestamp_length}')

def import_binance_balance(api_key, api_secret):

    client = Spot(base_url='https://testnet.binance.vision', api_key=api_key, api_secret=api_secret) 

    if not client:
        raise Exception('Error getting crypto price history data, no client.')
    else:

        # Get account information and balance 
        user_balance = client.account()
        # print(json.dumps(user_balance, indent=4))

        for balance in user_balance['balances']:
            print(balance['asset'])
            print(float(balance['free']) + float(balance['locked']))
    
        



    

    