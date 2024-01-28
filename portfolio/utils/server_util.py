import datetime, json
import requests
import time as t
from django.core.files import File
from io import BytesIO
from PIL import Image
from django.conf import settings
from decouple import config

from ..models import Asset, AssetPriceHistory
from .constants import START_DATE


headers = {'accept': 'application/json'}

def datetime_to_timestamp(date):
    if type(date) == datetime.date:
        date = datetime.datetime.combine(date, datetime.time())

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
    return f'https://api.coingecko.com/api/v3/coins/{name.lower()}/market_chart/range?vs_currency=usd&from={startDate}&to={endDate}&precision={precision}&x_cg_demo_api_key={config("COINGECKO_API_KEY")}'

def construct_current_crypto_price_url(api_name_list):
    url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids='

    for api_name in api_name_list:
        url += f'{api_name}%2C%20'

    url = url[0:(len(url)-6)]
    url += f'&order=market_cap_desc&per_page=100&page=1&sparkline=false&locale=en&x_cg_demo_api_key={config("COINGECKO_API_KEY")}'

    return url


def construct_stock_price_history_url(symbol):
    return f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=compact&apikey={config("ALPHAVANTAGE_API_KEY")}'

def construct_current_stock_price_url(symbol):
    return f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={config("ALPHAVANTAGE_API_KEY")}'


def construct_currency_price_history_url(symbol):
    return f'https://www.alphavantage.co/query?function=FX_DAILY&from_symbol=USD&to_symbol={symbol}&apikey={config("ALPHAVANTAGE_API_KEY")}'

def construct_current_currency_price_url(symbol):
    return f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency={symbol}&apikey={config("ALPHAVANTAGE_API_KEY")}'


def check_query_len_euqals_one(asset_query):
    if len(asset_query) > 1:
        raise Exception("Cannot fetch data. There is more than one asset with given api name.")
    
    elif len(asset_query) == 0:
        raise Exception("Cannot fetch data. There is no asset with given api_name.")
    
    elif len(asset_query) == 1:
        return True


def import_crypto_price_history(*argv):
    
    for api_name in argv:
        asset = Asset.objects.filter(api_name=api_name.lower()).filter(type='cryptocurrency')
                                    
        if check_query_len_euqals_one(asset) == True:
            
            # Check if there are any price history for given assset
            asset_price_history = asset[0].assetpricehistory_set.all()
            if len(asset_price_history) > 0:

                # Delete all asset price history
                for price_history in asset_price_history:
                    price_history.delete()

            # Define the start date and end date of price history fetching
            '''
            Start date needs to be at least 3 months in the past
            otherwise api will return hourly or minute data range
            '''
            if (datetime.date.today() - datetime.timedelta(weeks=13) < START_DATE):
                startdate = datetime.date.today() - datetime.timedelta(weeks=13)
                startDateTimestamp = datetime_to_timestamp(startdate)
            else:
                startDateTimestamp = datetime_to_timestamp(START_DATE)

            endDate = datetime.datetime.now()
            endDateTimestamp = datetime_to_timestamp(endDate) 

            # Fetch price data from constructed url   
            response = requests.get(construct_crypto_price_history_url(asset[0].api_name.lower(), startDateTimestamp, endDateTimestamp, 8), headers=headers)
            json_response = json.loads(response.content)

            # Create database records from fetched data
            for priceHistory in json_response["prices"]:
                
                new_date = timestamp_to_datetime(priceHistory[0]).date()
                print(new_date)
                if (new_date < START_DATE):
                    continue

                print(f'adding price history for {api_name} {new_date} {priceHistory[1]}')
                record = AssetPriceHistory(asset=asset[0], date=new_date, price=priceHistory[1])   
                record.save()  


    
def import_current_crypto_price():

    all_crypto = Asset.objects.filter(type='cryptocurrency')
    api_name_list = []
    api_limit = 0

    for crypto in all_crypto:
        api_name_list.append(crypto.api_name.lower())

    response = requests.get(construct_current_crypto_price_url(api_name_list), headers=headers)
    json_response = json.loads(response.content)
    
    for api_asset in json_response:
        asset = Asset.objects.filter(api_name=api_asset['id'].lower()).filter(type='cryptocurrency')
                                    
        if check_query_len_euqals_one(asset) == True:

            # Check if there is price data from previous day
            if len(asset[0].assetpricehistory_set.filter(date=datetime.date.today() - datetime.timedelta(days=1))) == 1:
                
                # Check if there is price data from today
                price_from_today = asset[0].assetpricehistory_set.filter(date=datetime.date.today())

                if len(price_from_today) > 1:
                    raise Exception("Cannot proceed. There is more than one price history from today.")

                elif len(price_from_today) == 1:
                    price_from_today[0].delete()

                print(f'adding todays price for {api_asset}')
                record = AssetPriceHistory(asset=asset[0], date=datetime.date.today(), price=api_asset['current_price'])   
                record.save()
            
            else:
                if(api_limit > int(config("COINGECKO_RATE_LIMIT"))):
                    t.sleep(80)
                    api_limit = 0
                    
                api_limit += 1
                print(f'importing all history {api_asset}')
                import_crypto_price_history(api_asset['id'])


def import_stock_price_history(*argv):
    
    for api_name in argv:
        asset = Asset.objects.filter(api_name=api_name.lower()).filter(type='stock')
                                    
        if check_query_len_euqals_one(asset) == True:
            
            # Check if there are any price history for given assset
            if len(asset[0].assetpricehistory_set.all()) > 0:
                asset_price_history = asset[0].assetpricehistory_set.all()

                # Delete all asset price history
                for price_history in asset_price_history:
                    price_history.delete()

            # Fetch price data from constructed url   
            response = requests.get(construct_stock_price_history_url(api_name))
            json_response = json.loads(response.content)
            
            # Create database records from fetched data
            for trading_day in json_response["Time Series (Daily)"]:
                
                new_date = datetime.datetime.strptime(trading_day, '%Y-%m-%d').date()

                if new_date >= START_DATE:
                    
                    # Calculate average price from day's high and low price
                    average_price = round((float(json_response["Time Series (Daily)"][trading_day]['3. low']) + float(json_response["Time Series (Daily)"][trading_day]['2. high'])) / 2, 2)

                    record = AssetPriceHistory(asset=asset[0], date=new_date, price=average_price)   
                    record.save()  
                

def import_current_stock_price():

    all_stocks = Asset.objects.filter(type='stock')

    for stock in all_stocks:
        api_name = stock.api_name.lower()
        asset = Asset.objects.filter(api_name=api_name).filter(type='stock')
                                    
        if check_query_len_euqals_one(asset) == True:

            # Check if past data exists for an asset
            previous_day = datetime.date.today() - datetime.timedelta(days=1)
            missing_day_count = 0

            for day in range(7):
                if len(asset[0].assetpricehistory_set.filter(date=previous_day)) == 0:
                    missing_day_count += 1
                previous_day -= datetime.timedelta(days=1)
                
            if missing_day_count >= 7:
                import_stock_price_history(api_name)
                continue

            # Fetch price data from constructed url   
            response = requests.get(construct_current_stock_price_url(api_name))
            json_response = json.loads(response.content)
            last_refreshed_day = datetime.datetime.strptime(json_response["Meta Data"]["3. Last Refreshed"],'%Y-%m-%d %H:%M:%S').date()

            for trading_day in json_response["Time Series (5min)"]: 
                new_price = json_response["Time Series (5min)"][trading_day]['1. open']
                break

            # Check if last refreshed day is in the past
            if last_refreshed_day < datetime.date.today():
                # Check if AssetPriceHistory record exists for last refreshed day in the past
                if len(asset[0].assetpricehistory_set.filter(date=last_refreshed_day)) == 1:
                    continue

            elif last_refreshed_day == datetime.date.today():
                
                # Check if there is price data from today
                price_from_today = asset[0].assetpricehistory_set.filter(date=datetime.date.today())
                
                if len(price_from_today) > 1:
                    raise Exception("Cannot proceed. There is more than one price history from today.")

                elif len(price_from_today) == 1:
                    if price_from_today == new_price:
                        continue
                    else: 
                        price_from_today[0].delete()

            record = AssetPriceHistory(asset=asset[0], date=last_refreshed_day, price=new_price)   
            record.save()


def import_currency_price_history(*argv):
    
    for api_name in argv:
        asset = Asset.objects.filter(api_name=api_name.lower()).filter(type='currency')
                                    
        if check_query_len_euqals_one(asset) == True:
            
            # Check if there are any price history for given assset
            if len(asset[0].assetpricehistory_set.all()) > 0:
                asset_price_history = asset[0].assetpricehistory_set.all()

                # Delete all asset price history
                for price_history in asset_price_history:
                    price_history.delete()

            # Fetch price data from constructed url   
            response = requests.get(construct_currency_price_history_url(api_name))
            json_response = json.loads(response.content)
            
            # Create database records from fetched data
            for trading_day in json_response["Time Series FX (Daily)"]:
                
                new_date = datetime.datetime.strptime(trading_day, '%Y-%m-%d').date()

                if new_date >= START_DATE:
                    
                    # Calculate average price from day's high and low price
                    average_price = round((float(json_response["Time Series FX (Daily)"][trading_day]['3. low']) + float(json_response["Time Series FX (Daily)"][trading_day]['2. high'])) / 2, 4)

                    record = AssetPriceHistory(asset=asset[0], date=new_date, price=average_price)   
                    record.save()  


def import_current_currency_price():
    
    all_currency = Asset.objects.filter(type='currency')

    for currency in all_currency:
        api_name = currency.api_name.lower()
        asset = Asset.objects.filter(api_name=api_name).filter(type='currency')
                                    
        if check_query_len_euqals_one(asset) == True:

            # Check if past data exists for an asset
            previous_day = datetime.date.today() - datetime.timedelta(days=1)
            missing_day_count = 0

            for day in range(7):
                if len(asset[0].assetpricehistory_set.filter(date=previous_day)) == 0:
                    missing_day_count += 1
                previous_day -= datetime.timedelta(days=1)

            if missing_day_count >= 7:
                import_currency_price_history(api_name)
                continue

            # Fetch price data from constructed url   
            response = requests.get(construct_current_currency_price_url(api_name))
            json_response = json.loads(response.content)
            last_refreshed_day = datetime.datetime.strptime(json_response["Realtime Currency Exchange Rate"]["6. Last Refreshed"],'%Y-%m-%d %H:%M:%S').date()
            new_price = round(float(json_response["Realtime Currency Exchange Rate"]["5. Exchange Rate"]), 4)
            
            # Check if last refreshed day is in the past
            if last_refreshed_day < datetime.date.today():
                # Check if AssetPriceHistory record exists for last refreshed day in the past
                if len(asset[0].assetpricehistory_set.filter(date=last_refreshed_day)) == 1:
                    continue

            elif last_refreshed_day == datetime.date.today():
                
                # Check if there is price data from today
                price_from_today = asset[0].assetpricehistory_set.filter(date=datetime.date.today())

                if len(price_from_today) > 1:
                    raise Exception("Cannot proceed. There is more than one price history from today.")

                elif len(price_from_today) == 1:
                    if price_from_today == new_price:
                        continue
                    else: 
                        price_from_today[0].delete()

            record = AssetPriceHistory(asset=asset[0], date=last_refreshed_day, price=new_price)   
            record.save()
                    


def get_crypto_assets(asset_number):

    import math

    if asset_number % 100 == 0:
        page = math.floor(asset_number/100)
        per_page = 100
    elif asset_number < 100 :
        page = math.floor(asset_number/100) + 1
        per_page = asset_number - (page -1) * 100
    else:
        return print('Function argument must subtract by 100 without remainder or be less than 100')

    response = requests.get(f'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page={per_page}&page={page}&sparkline=false&locale=en&x_cg_demo_api_key={config("COINGECKO_API_KEY")}', headers=headers)
    json_response = json.loads(response.content)

    # Print response for testing purpouses
    # print(json.dumps(json_response, indent=4))

    '''
    # Code for deleting all assets and their history from database
    crypto_assets = Asset.objects.filter(type='cryptocurrency')
    for crypto_asset in crypto_assets:
        crypto_asset.delete()

    crypto_assets_ph = AssetPriceHistory.objects.all()
    for crypto_asset_ph in crypto_assets_ph:
        crypto_asset_ph.delete()
    '''

    for response_asset in json_response:

        asset = Asset.objects.filter(api_name=response_asset['id']).filter(type='cryptocurrency')
        if len(asset) == 0:
            print(f'no asset with api_name {response_asset["id"]}, adding...')
            
            # Creating asset record in database
            asset_record = Asset(name=response_asset["name"], api_name=response_asset["id"], ticker=response_asset["symbol"].upper(), type='cryptocurrency', slug=response_asset["symbol"].lower())
            # Code for saving icon to database ImageField 
            # asset_record.icon.save(response_asset["symbol"] + '.png', File.open(BytesIO(image_request.content)))           
            asset_record.save()

            # Creating image file in project
            fetch_headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36'}
            image_request = requests.get(response_asset["image"], headers=fetch_headers)
            img = Image.open(BytesIO(image_request.content))
            img.save(f'{settings.BASE_DIR}/portfolio/static/images/assets/cryptocurrency/{response_asset["symbol"].lower()}.png')
        
        elif len(asset) > 1:
            raise Exception(f'Too many assets records with api_name {response_asset["id"]} in database')
        elif len(asset) == 1:
            print(f'asset with api_name {response_asset["id"]} exists')           