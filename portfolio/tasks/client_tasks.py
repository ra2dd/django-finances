from binance.spot import Spot
import datetime, json, string
import os

from ..models import Asset, AssetPriceHistory

class PriceHistory():
    def __init__(self, ticker):
        self.ticker = ticker
        self.price = None

def datetime_to_timestamp(date):
    return round(datetime.datetime.timestamp(date) * 1000)

def import_crypto_price_history(ticker):

    client = Spot(base_url='https://testnet.binance.vision', api_key=os.environ.get('BINANCEAPI_API_KEY', ''), api_secret=os.environ.get('BINANCEAPI_SECRET_KEY', '')) 

    if not client:
        raise Exception('Error getting crypto price history data, no client.')
    
        



    

    