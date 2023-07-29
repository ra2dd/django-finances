from binance.spot import Spot
import datetime, json, string
import os

from .models import Asset, AssetPriceHistory

class PriceHistory():
    def __init__(self, ticker):
        self.ticker = ticker
        self.price = None

def import_crypto_price_history(ticker):

    client = Spot(base_url='https://testnet.binance.vision', api_key=os.environ.get('BINANCEAPI_API_KEY', ''), api_secret=os.environ.get('BINANCEAPI_SECRET_KEY', '')) 

    if not client:
        raise Exception('Error getting crypto price history data, no client.')
    
    asset = Asset.objects.filter(ticker=ticker.upper())
                                 
    if len(asset) > 1:
        raise Exception("Cannot fetch data. There is more than one asset with given ticker.")
    
    elif len(asset) == 0:
        raise Exception("Cannot fetch data. There is no asset with given ticker.")
    
    elif len(asset) == 1:

        asset_price_history = AssetPriceHistory.objects.all()
        print(asset_price_history)
        #Check latest price history for an asset
    

    