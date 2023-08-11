import datetime, json, string
import sys, os
import requests, random

# from portfolio.tasks import server_tasks
# server_tasks.import_crypto_price_history('xlm')
headers = {'accept': 'application/json'}

from ..models import Asset, AssetPriceHistory

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


def construct_crypto_price_history_url(name, startDate, endDate, precision):
    return f'https://api.coingecko.com/api/v3/coins/{name.lower()}/market_chart/range?vs_currency=usd&from={startDate}&to={endDate}&precision={precision}'

def construct_current_crypto_price_url(*argv):
    url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids='

    for api_name in argv:
        url += f'{api_name}%2C%20'

    url = url[0:(len(url)-6)]
    url += '&order=market_cap_desc&per_page=100&page=1&sparkline=false&locale=en'

    return url


def construct_stock_price_history_url(symbol):
    return f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=compact&apikey={os.environ.get("ALPHAVANTAGE_API_KEY")}'

def construct_current_stock_price_url(symbol):
    return f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={os.environ.get("ALPHAVANTAGE_API_KEY")}'


def import_crypto_price_history(*argv):
    
    for api_name in argv:
        asset = Asset.objects.filter(api_name=api_name.lower()).filter(type='cryptocurrency')
                                    
        if len(asset) > 1:
            raise Exception("Cannot fetch data. There is more than one asset with given api name.")
        
        elif len(asset) == 0:
            raise Exception("Cannot fetch data. There is no asset with given api_name.")
        
        elif len(asset) == 1:
            
            # Check if there are any price history for given assset
            if len(asset[0].assetpricehistory_set.all()) > 0:
                asset_price_history = asset[0].assetpricehistory_set.all()

                # Delete all asset price history
                for price_history in asset_price_history:
                    price_history.delete()

            # Define the start date and end date of price history fetching
            startDate = datetime.datetime(2023, 5, 1)
            startDateTimestamp = datetime_to_timestamp(startDate) 

            endDate = datetime.datetime.now()
            endDateTimestamp = datetime_to_timestamp(endDate) 

            # Fetch price data from constructed url   
            response = requests.get(construct_crypto_price_history_url(asset[0].name.lower(), startDateTimestamp, endDateTimestamp, 8), headers=headers)
            json_response = json.loads(response.content)

            # Create database records from fetched data
            for priceHistory in json_response["prices"]:

                # print(f'[{timestamp_to_datetime(priceHistory[0])}, {priceHistory[1]}],\n ')

                new_date = timestamp_to_datetime(priceHistory[0])
                record = AssetPriceHistory(asset=asset[0], date=new_date, price=priceHistory[1])   
                record.save()  


    
def import_current_crypto_price(*argv):

    response = requests.get(construct_current_crypto_price_url(*argv), headers=headers)
    json_response = json.loads(response.content)
    
    for api_asset in json_response:
        asset = Asset.objects.filter(api_name=api_asset['id'].lower()).filter(type='cryptocurrency')
                                    
        if len(asset) > 1:
            raise Exception("Cannot fetch data. There is more than one asset with given api id.")
        
        elif len(asset) == 0:
            raise Exception("Cannot fetch data. There is no asset with given api id.")
        
        elif len(asset) == 1:
            # Check if there is price data from previous day
            if len(asset[0].assetpricehistory_set.filter(date=datetime.date.today() - datetime.timedelta(days=1))) == 1:
                
                # Check if there is price data from today
                price_from_today = asset[0].assetpricehistory_set.filter(date=datetime.date.today())

                if len(price_from_today) > 1:
                    raise Exception("Cannot proceed. There is more than one price history from today.")

                elif len(price_from_today) == 1:
                    price_from_today[0].delete()

                record = AssetPriceHistory(asset=asset[0], date=datetime.date.today(), price=api_asset['current_price'])   
                record.save()
            
            else:
                import_crypto_price_history(api_asset['id'])



def import_stock_price_history(*argv):
    
    for api_name in argv:
        asset = Asset.objects.filter(api_name=api_name.lower()).filter(type='stock')
                                    
        if len(asset) > 1:
            raise Exception("Cannot fetch data. There is more than one asset with given api name.")
        
        elif len(asset) == 0:
            raise Exception("Cannot fetch data. There is no asset with given api_name.")
        
        elif len(asset) == 1:
            
            # Check if there are any price history for given assset
            if len(asset[0].assetpricehistory_set.all()) > 0:
                asset_price_history = asset[0].assetpricehistory_set.all()

                # Delete all asset price history
                for price_history in asset_price_history:
                    price_history.delete()

            # Define the start date of price history fetching
            startDate = datetime.datetime(2023, 5, 1)
            startDateTimestamp = datetime_to_timestamp(startDate) 

            # Fetch price data from constructed url   
            response = requests.get(construct_stock_price_history_url(api_name))
            json_response = json.loads(response.content)
            
            # Create database records from fetched data
            for trading_day in json_response["Time Series (Daily)"]:
                
                new_date = datetime.datetime.strptime(trading_day, '%Y-%m-%d')

                if new_date >= startDate:
                    
                    # Calculate average price from day's high and low price
                    average_price = round((float(json_response["Time Series (Daily)"][trading_day]['3. low']) + float(json_response["Time Series (Daily)"][trading_day]['2. high'])) / 2, 2)

                    record = AssetPriceHistory(asset=asset[0], date=new_date, price=average_price)   
                    record.save()  
                

def import_current_stock_price(*argv):
    
    for api_name in argv:
        asset = Asset.objects.filter(api_name=api_name.lower()).filter(type='stock')
                                    
        if len(asset) > 1:
            raise Exception("Cannot fetch data. There is more than one asset with given api id.")
        
        elif len(asset) == 0:
            raise Exception("Cannot fetch data. There is no asset with given api id.")
        
        elif len(asset) == 1:
            # Check if there is price data from previous day
            if len(asset[0].assetpricehistory_set.filter(date=datetime.date.today() - datetime.timedelta(days=1))) == 1:
                
                # Check if there is price data from today
                price_from_today = asset[0].assetpricehistory_set.filter(date=datetime.date.today())

                if len(price_from_today) > 1:
                    raise Exception("Cannot proceed. There is more than one price history from today.")

                elif len(price_from_today) == 1:
                    price_from_today[0].delete()

                # Fetch price data from constructed url   
                response = requests.get(construct_current_stock_price_url(api_name))
                json_response = json.loads(response.content)

                for trading_day in json_response["Time Series (5min)"]: 
                    new_price = json_response["Time Series (5min)"][trading_day]['1. open']
                    break

                record = AssetPriceHistory(asset=asset[0], date=datetime.date.today(), price=new_price)   
                record.save()
            
            else:
                import_crypto_price_history(api_name)