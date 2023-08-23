from binance.spot import Spot
import datetime, json, string
import os
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, Http404

from ..models import Asset, AssetPriceHistory, AssetBalance, AssetBalanceHistory, Exchange, Portfolio

class AssetsAmount():
    def __init__(self, ticker, amount):
        self.ticker = ticker
        self.amount = amount

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


'''Bianance api connection'''
def get_binance_client(api_key, api_secret):
    return Spot(base_url='https://testnet.binance.vision', api_key=api_key, api_secret=api_secret)


def import_binance_balance(api_key, api_secret):

    if check_binance_connection(api_key, api_secret) != True:
        return False

    client = get_binance_client(api_key, api_secret)
    user_balance = client.account()

    assets_amounts = []
    for balance in user_balance['balances']:
        assets_amounts.append(AssetsAmount(balance['asset'], float(balance['free']) + float(balance['locked'])))

        print(balance['asset'])
        print(float(balance['free']) + float(balance['locked']))

    return assets_amounts


def check_binance_connection(api_key, api_secret):

    client = get_binance_client(api_key, api_secret)

    # Check biannce api connection
    if client.ping() == {}:
        try:
            # Check if binance api keys are correct
            client.account()
        except:
            return False
        
        # If api keys ok -> return True
        return True
    
    else:
        return 'no-connection'
    


def import_balance(exchange, api_connection, user):

    if(exchange.name.lower() == 'binance'):
        assets_amounts = import_binance_balance(api_connection.api_key, api_connection.secret_key)
    else:
        raise Http404(f'Importing balance from {exchange.name} Exchange not yet implemented')
        return False
    
    for fetched_asset in assets_amounts:
        portfolio = Portfolio.objects.filter(owner=user)[0]
        asset = Asset.objects.filter(ticker=fetched_asset.ticker.lower())

        if len(asset) == 0:
            print(f'no asset with {fetched_asset.ticker} ticker in database')
            continue
        elif len(asset) > 1:
           raise Exception('Too many assets corresponding with given ticker.') 

        asset_balance_record = None
        asset_balance = AssetBalance.objects.filter(portfolio=portfolio, asset=asset[0], broker=exchange)


        if len(asset_balance) > 1: 
           raise Exception('Too many asset balances corresponding with given ticker.')
        if len(asset_balance) == 0:
            if fetched_asset.amount == 0:
                continue
            else:
                print(f'asset balance not exisiting for {fetched_asset.ticker}')
                asset_balance_record = AssetBalance(portfolio=portfolio, asset=asset[0], broker=exchange)
                asset_balance_record.save()

        print(f'creating asset balance history for {fetched_asset.ticker}') 
        if asset_balance_record == None:
            asset_balance_record = asset_balance[0]

        if fetched_asset.amount == 0 or 1 == 1:
            asset_balance_history_exists = AssetBalanceHistory.objects.filter(balance = asset_balance_record)         
            print(asset_balance_history_exists)

        check_asset_balance_history = AssetBalanceHistory.objects.filter(balance = asset_balance_record)     

        if len(check_asset_balance_history) > 0:
            latest_asset_balance_history = check_asset_balance_history.latest()    
            
            if fetched_asset.amount == 0 and latest_asset_balance_history.amount == 0:
                    continue

            if latest_asset_balance_history.date == datetime.date.today():
                    latest_asset_balance_history.delete()

        asset_balance_history_record = AssetBalanceHistory(amount=fetched_asset.amount, date=datetime.date.today(), balance=asset_balance_record)
        asset_balance_history_record.save()
        print(f'{asset_balance_history_record}\n')
        
        



    

    