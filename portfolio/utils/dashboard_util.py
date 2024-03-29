import json, datetime, random
from django.http import Http404
from django.shortcuts import get_object_or_404

from .constants import START_DATE
from ..models import Portfolio, AssetBalance, AssetBalanceHistory, Asset, Exchange

class UserCurrentAsset:
    def __init__(self, name, ticker, type, icon, latest_price, latest_holding, latest_value):
        self.name = name
        self.ticker = ticker
        self.type = type
        self.icon = icon
        self.latest_price = latest_price
        self.latest_holding = latest_holding
        self.latest_value = latest_value

class TotalDayBalance:
    def __init__(self, date, value):
        self.date = date
        self.values = [value]



def get_user_asset_holdings_with_values_list(user_all_balance_list):
    
    # Auxilary variable for storing asset information for the next loop iteration (asset, asset amount)
    same_latest_balance = (False, False)

    # context list for holding user current asset holdings objects
    user_holdings_list = []

    # Loop throgh balances to add amount, price and value attrributes to balance queryset
    for balance in user_all_balance_list:
        # TODO check if balance assetbalancehistory exists

        # Get asset price
        asset_latest_price = balance.asset.assetpricehistory_set.latest().price

        # Get asset holding
        try:
            asset_latest_holding = balance.assetbalancehistory_set.latest().amount
        except:
            raise Http404('Error calculating balance, please contact site admin.')
    
        # Check if asset holding is the same as asset holding in previous iteration
        if (same_latest_balance[0] == balance.asset):
            # If True add previous holding to current holding
            asset_latest_holding += same_latest_balance[1]

            # Remove last context list object from previous interation
            user_holdings_list.pop()

        # Set auxilary tuple variable for storing balance to the next iteration
        same_latest_balance = (balance.asset, asset_latest_holding)
        
        # Create asset value attribute
        asset_latest_value = asset_latest_price * asset_latest_holding

        # Create UserCurrentAsset object and append it to the context list
        user_holdings_list.append(UserCurrentAsset(balance.asset.name, balance.asset.ticker, balance.asset.type, balance.asset.get_icon_path, round(asset_latest_price, 2), round(asset_latest_holding, 2), round(asset_latest_value, 2)))

    user_holdings_list.sort(reverse=True, key=lambda h: h.latest_value)
    return user_holdings_list


def get_user_daily_balance_history(user_all_balance_list):

    # context list containing total daily user balance list
    # starting from first user asset balance date to today
    user_daily_balance_history = []

    # loop through user's all AssetBalance objects 
    for balance in user_all_balance_list:
        
        # auxiliary variable for knowing last date that was calculated in certain AssetBalance
        last_date = None
        # auxiliary variable for knowing last value that was calculated in certain AssetBalance
        last_value = None
        # auxilary variable for storing last AssetBalanceHistory object 
        last_balance_history = None
        # auxilary variable for stroing last price history exisiting day
        last_price_history = None

        print(f'start {balance}')

        # loop through user's all AssetBalanceHistory objects associated with certain AssetBalance
        for balance_history in balance.assetbalancehistory_set.all():
            
            print(f'  loop start{balance_history.date}')

            # auxiliary variable for checking if records were filled in before adding 
            # AssetBalanceHistory object to user_daily_balance_history
            records_filled = False

            # if it's not a first iteration of the AssetBalanceHistory loop
            if last_date != None:
                """
                    If last_date + 1 day is not a AssetBalanceHisotry current date
                    fill in missing dates between AssetBalanceHisotry object dates with records.
                """
                while (last_date + datetime.timedelta(days=1) != balance_history.date):
                        
                        # auxiliary variable for knowing if user_daily_balance_history object exists with certain date
                        added_to_existing_list = False
                        print(f'    loop, last_date - {last_date + datetime.timedelta(days=1)}') 
                        
                        # Add one day to last_date, because we are going to be filling it with data from last_balance_history
                        last_date += datetime.timedelta(days=1)
                        
                        if(len(balance_history.balance.asset.assetpricehistory_set.filter(date=last_date)) > 0):
                            last_price_history = balance_history.balance.asset.assetpricehistory_set.filter(date=last_date)[0].price
                        
                        elif last_price_history == None:
                            minus_days = 0
                            while last_price_history == None:
                                minus_days += 1
                                if len(balance_history.balance.asset.assetpricehistory_set.filter(date=last_date - datetime.timedelta(days=minus_days))) > 0:
                                    last_price_history = balance_history.balance.asset.assetpricehistory_set.filter(date=last_date - datetime.timedelta(days=minus_days))[0].price

                        # set last_value to AssetBalanceHistory amount from last iteration multiplied by AssetPriceHistory price matching last AssetBalanceHistory date
                        last_value = last_balance_history.amount * last_price_history

                        for total_balance in user_daily_balance_history:

                            if(total_balance.date == last_date):
                                total_balance.values.append(last_value)
                                added_to_existing_list = True
                                break

                        if not added_to_existing_list:                      
                            user_daily_balance_history.append(TotalDayBalance(last_date, last_value))

                        records_filled = True   
                """
                    If records were filled before adding new AssetBalanceHistory object 
                    one day needs to be addded to last_date, because we already filled 
                    user_daily_balance_history with last_day data from last_balance_history
                    and next day matches our current iteration AssetBalanceHistory day
                """
                if(records_filled):
                        last_date += datetime.timedelta(days=1)



            # auxiliary variable for knowing if user_daily_balance_history object exists with certain date
            added_to_existing_list = False
            
            """
                Check if it is the first iteration of current AssetBalance object.
                Or if the last_date equals current AssetBalanceHistory object date
                and it's time to update AssetBalanceHistory holding for calculations
            """
            if last_date == None or last_date == balance_history.date:
                print(f'    equals, last_date - {last_date}')

                if(len(balance_history.balance.asset.assetpricehistory_set.filter(date=balance_history.date)) > 0):
                    last_price_history = balance_history.balance.asset.assetpricehistory_set.filter(date=balance_history.date)[0].price
                    print(f'last price history - {last_price_history}')

                elif last_price_history == None:
                    minus_days = 0
                    while last_price_history == None:
                        minus_days += 1
                        if len(balance_history.balance.asset.assetpricehistory_set.filter(date=balance_history.date - datetime.timedelta(days=minus_days))) > 0:
                            last_price_history = balance_history.balance.asset.assetpricehistory_set.filter(date=balance_history.date - datetime.timedelta(days=minus_days))[0].price

                # set last_value to current AssetBalanceHistory amount multiplied by AssetPriceHistory price matching AssetBalanceHistory date
                last_value = balance_history.amount * last_price_history
                
                """
                    loop through user_daily_balance_history list 
                    checking if current AssetBalanceHistory date is in the list
                """
                for total_balance in user_daily_balance_history:
                    
                    # if it is in the list append last_value to object with date matching current AssetBalanceHistory date
                    if(total_balance.date == balance_history.date):
                        total_balance.values.append(last_value)

                        # Set variable to True, so we can check later if asset was already added to user_daily_balance_history
                        added_to_existing_list = True

                        # after loop found the matching date exit the loop to save computation time
                        break

                # if user_daily_balance_history doesn't have object with date matching current AssetBalanceHistory
                # create new object in user_daily_balance_history and add current AssetBalanceHistory object
                if not added_to_existing_list:                      
                    user_daily_balance_history.append(TotalDayBalance(balance_history.date, last_value))

                # set last_date so we know last date in current AssetBalance that was added into user_daily_balance_history
                # helpful in filling not existing dates in AssetBalanceHistory between existing dates
                last_date = balance_history.date

                # set record added to true so we can go to next AssetBalanceHistory iteration after checking if there are any 
                record_added = True

            """
                set auxilary variable with last AssetBalanceHistory object, so we 
                have the latest object data for completing missing dates between 
                AssetBalanceHistory objects or missing dates between last
                AssetBalanceHistory object and today
            """
            last_balance_history = balance_history

        print()
        print(last_date)
        print(datetime.date.today())
        print()
        """
            if after iterating over all AssetBalanceHistory objects 
            the last_date is still behind today
        """
        if(last_date < datetime.date.today()):

            """
                interate until all missing dates between last AssetBalanceHistory 
                object and today are added to user_daily_balance_history
            """
            while (last_date < datetime.date.today()):
                print(f'      fill loop, last_date - {last_date + datetime.timedelta(days=1)}')

                added_to_existing_list = False 
                # add one day to last_date, because it's data will be added to user_daily_balance_history
                last_date += datetime.timedelta(days=1)

                if(len(last_balance_history.balance.asset.assetpricehistory_set.filter(date=last_date)) > 0):
                            last_price_history = last_balance_history.balance.asset.assetpricehistory_set.filter(date=last_date)[0].price

                # set last_value to latest AssetBalanceHistory amount multiplied by AssetPriceHistory price matching last AssetBalanceHistory date
                last_value = last_balance_history.amount * last_price_history
                
                for total_balance in user_daily_balance_history:

                    if(total_balance.date == last_date):
                        total_balance.values.append(last_value)
                        added_to_existing_list = True
                        break

                if not added_to_existing_list:                      
                    user_daily_balance_history.append(TotalDayBalance(last_date, last_value))

    # loop for adding all balance values in respective dates
    for day_balance in user_daily_balance_history:

        sum_of_day_balances = 0

        for day_asset_value in day_balance.values:
            sum_of_day_balances += day_asset_value

        day_balance.values = round(sum_of_day_balances, 2)
    
    user_daily_balance_history.sort(key=lambda b: b.date)
    return user_daily_balance_history


def get_asset_type_ratio_tuple_list(user_holdings_list):
    
    asset_ratio = {
        'cryptocurrency': 0,
        'stock': 0,
        'currency': 0,
    }
    
    # Sum user holdings based on type
    for holding in user_holdings_list:
        asset_ratio[holding.type] += holding.latest_value
    
    # Sum complete holdings value
    asset_sum = 0
    for dict in asset_ratio:
        asset_sum += asset_ratio[dict]

    asset_type_ratio_tuple_list = []

    # Calculate asset type ratio based on the complate holdings sum
    # Append calculated values to list as tuples
    for dict in asset_ratio:
        value = asset_ratio[dict]
        if(asset_sum > 0):
            ratio = round(asset_ratio[dict] / asset_sum * 100, 2)
        else:
            ratio = 0
        dict = dict[:1].upper() + dict[1:]

        asset_type_ratio_tuple_list.append((dict, ratio, value))

    return sorted(asset_type_ratio_tuple_list, key=lambda d: float(d[1]), reverse=True)


def get_dashboard_context(user_obj):

    current_date = datetime.datetime.now().strftime("%B %-d, %Y")

    # Get all asset balances of current user portfolio
    user_all_balance_list = Portfolio.objects.filter(owner=user_obj)[0].assetbalance_set.all()
    
    # Get list of user asset holdings
    user_holdings_list = get_user_asset_holdings_with_values_list(user_all_balance_list)

    if len(user_holdings_list) > 0:
        asset_ratio = get_asset_type_ratio_tuple_list(user_holdings_list)

        asset_type_ratio_tuple_list_json = json.dumps(asset_ratio, default=str)
        top_asset_type_allocation = asset_ratio[0]
        
        user_daily_balance_history = get_user_daily_balance_history(user_all_balance_list)
        user_daily_balance_history_json = json.dumps([obj.__dict__ for obj in user_daily_balance_history], default=str)

        if len(user_daily_balance_history) > 0: 
            latest_balance_value = user_daily_balance_history[-1].values
            
            if len(user_daily_balance_history) > 30:
                balance_change = [30, latest_balance_value - user_daily_balance_history[-30].values]
            elif len(user_daily_balance_history) > 7:
                balance_change = [7, latest_balance_value - user_daily_balance_history[-7].values]
            else:
                balance_change = [0, format(0.0, '.2f')]

            if float(balance_change[1]) < 0:
                balance_change[1] *= -1
                balance_change.append('negative')

        if user_holdings_list[0].latest_value == 0:
            top_asset_allocation = 0
        else:
            top_asset_allocation = round(user_holdings_list[0].latest_value / latest_balance_value * 100)

        context = {
            'user_holdings_list': user_holdings_list[:5],
            'user_daily_balance_history_json': user_daily_balance_history_json,
            'asset_type_ratio_tuple_list_json': asset_type_ratio_tuple_list_json,
            'latest_balance_value': latest_balance_value,
            'balance_change': balance_change,
            'current_date': current_date,
            'top_asset_type_allocation': top_asset_type_allocation,
            'top_asset_allocation': top_asset_allocation,
            'asset_ratio': asset_ratio,
        }
        return context

    else:
        context = {
            'current_date': current_date
        }

        return context          