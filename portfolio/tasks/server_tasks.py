import datetime, json, string
import requests, random

# from portfolio.tasks import server_tasks
# server_tasks.import_crypto_price_history('xlm')
headers = {'accept': 'application/json'}

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

def contruct_crypto_price_history_url(name, startDate, endDate):
    return f'https://api.coingecko.com/api/v3/coins/{name.lower()}/market_chart/range?vs_currency=usd&from={startDate}&to={endDate}&precision=6'


def import_crypto_price_history(ticker):
    
    asset = Asset.objects.filter(ticker=ticker.upper())
                                 
    if len(asset) > 1:
        raise Exception("Cannot fetch data. There is more than one asset with given ticker.")
    
    elif len(asset) == 0:
        raise Exception("Cannot fetch data. There is no asset with given ticker.")
    
    elif len(asset) == 1:

        if len(asset[0].assetpricehistory_set.all()) > 0:
            asset_price_history = asset[0].assetpricehistory_set.all()

            '''
            first_exisitng_record = asset_price_history[0]
            latest_exisitng_record = asset_price_history.latest()
            print(first_exisitng_record)
            print(latest_exisitng_record)
            '''

            for price_history in asset_price_history:
                price_history.delete()

        #Check latest price history for an asset
        startDate = datetime.datetime(2023, 5, 1)
        startDateTimestamp = datetime_to_timestamp(startDate) 

        # endDate = startDate + datetime.timedelta(weeks=1)
        endDate = datetime.datetime.now()
        endDateTimestamp = datetime_to_timestamp(endDate) 

        test = 1
        if test == 1:
            
            response = requests.get(contruct_crypto_price_history_url(asset[0].name.lower(), startDateTimestamp, endDateTimestamp), headers=headers)
            json_response = json.loads(response.content)

            for priceHistory in json_response["prices"]:

                print(f'[{timestamp_to_datetime(priceHistory[0])}, {priceHistory[1]}],\n ')

                new_date = timestamp_to_datetime(priceHistory[0])
                record = AssetPriceHistory(asset=asset[0], date=new_date, price=priceHistory[1])   
                record.save()  


    

    