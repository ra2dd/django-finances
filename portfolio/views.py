from typing import Any, Dict
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import generic
import datetime, random, sys, os

from .models import Portfolio, Asset, AssetBalance, AssetBalanceHistory, AssetPriceHistory, Exchange, ApiConnection
from .tasks import server_tasks

class UserCurrentAsset:
    def __init__(self, name, ticker, type, latest_price, latest_holding, latest_value):
        self.name = name
        self.ticker = ticker
        self.type = type
        self.latest_price = latest_price
        self.latest_holding = latest_holding
        self.latest_value = latest_value

class UserTotalBalanceHistory:
    def __init__(self, date, value):
        self.date = date
        self.values = [value]

     
def index(request):
    """View function for the home page of the site."""

    portfolio_object = Portfolio.objects.all()[0]

    context = {
        'portfolio_object': portfolio_object,
    }

    return render(request, 'index.html', context=context)


class DashboardView(generic.TemplateView, LoginRequiredMixin):
    """View function for the user dashboard"""

    template_name = 'dashboard.html'

    def get_context_data(self):

        # Get all asset balances of current user portfolio
        user_all_balance_list = Portfolio.objects.filter(owner=self.request.user)[0].assetbalance_set.all()
        
        # Auxilary variable for storing asset information for the next loop iteration
        same_latest_balance = (False, False)

        # context list for holding user current asset holdings objects
        user_balance_list = []

        # Loop throgh balances to add amount, price and value attrributes to balance queryset
        for balance in user_all_balance_list:
            
            # Get asset price
            asset_latest_price = balance.asset.assetpricehistory_set.latest().price

            # Get asset holding
            asset_latest_holding = balance.assetbalancehistory_set.latest().amount
        
            # Check if asset holding is the same as asset holding in previous iteration
            if (same_latest_balance[0] == balance.asset):
                # If True add previous holding to current holding
                asset_latest_holding += same_latest_balance[1]

                # Remove last context list object from previous interation
                user_balance_list.pop()

            # Set auxilary tuple variable for storing balance to the next iteration
            same_latest_balance = (balance.asset, balance.assetbalancehistory_set.latest().amount)
            
            # Create asset value attribute
            asset_latest_value = asset_latest_price * asset_latest_holding

            # Create UserCurrentAsset object and append it to the context list
            user_balance_list.append(UserCurrentAsset(balance.asset.name, balance.asset.ticker, balance.asset.type, round(asset_latest_price, 2), round(asset_latest_holding, 2), round(asset_latest_value, 2)))


        """
        # AssetPriceHistory database data creation

        # Define a start date of data creation
        date_new = datetime.datetime(2023, 7, 10)

        # Define a asset ticker that we will be creating data for
        ticker = 'USD'

        # Define the price range our asset will be created in
        price_range = (1 ,1) 
        
        # Loop through dates until it's today date
        while (date_new <= datetime.datetime.now()):
            
            # Check if asset price history already exists for certain day
            if AssetPriceHistory.objects.filter(date=date_new).filter(asset__ticker=ticker):

                print(f'already in use - {date_new}')
                date_new += datetime.timedelta(days=1)

            else:
                # Create a record with defined parameters
                record = AssetPriceHistory(asset=Asset.objects.filter(ticker=ticker)[0], date=date_new, price=random.randint(price_range))   
                record.save()

                print(f'created {record}')
                date_new += datetime.timedelta(days=1) 
        """



        # context list containing total daily user balance list
        # starting from first user asset balance date to today
        user_total_balance_history = []

        # loop through user's all AssetBalance objects 
        for balance in user_all_balance_list:
            
            # auxiliary variable for knowing last date that was calculated in certain AssetBalance
            last_date = None
            # auxiliary variable for knowing last value that was calculated in certain AssetBalance
            last_value = None
            # auxilary variable for storing last AssetBalanceHistory object 
            last_balance_history = None

            print(f'start {balance}')
            test = 0

            # loop through user's all AssetBalanceHistory objects associated with certain AssetBalance
            for balance_history in balance.assetbalancehistory_set.all():
                
                print(f'  loop start{balance_history.date}')

                # auxiliary variable for checking if records were filled in before adding 
                # AssetBalanceHistory object to user_total_balance_history
                records_filled = False

                # if it's not a first iteration of the AssetBalanceHistory loop
                if last_date != None:
                    """
                        If last_date + 1 day is not a AssetBalanceHisotry current date
                        fill in missing dates between AssetBalanceHisotry object dates with records.
                    """
                    while (last_date + datetime.timedelta(days=1) != balance_history.date):
                            
                            # auxiliary variable for knowing if user_total_balance_history object exists with certain date
                            added_to_existing_list = False
                            print(f'    loop, last_date - {last_date + datetime.timedelta(days=1)}') 
                            
                            # Add one day to last_date, because we are going to be filling it with data from last_balance_history
                            last_date += datetime.timedelta(days=1)
                            
                            # set last_value to AssetBalanceHistory amount from last iteration multiplied by AssetPriceHistory price matching last AssetBalanceHistory date
                            last_value = last_balance_history.amount * balance_history.balance.asset.assetpricehistory_set.filter(date=last_date)[0].price

                            for total_balance in user_total_balance_history:

                                if(total_balance.date == last_date):
                                    total_balance.values.append(last_value)
                                    added_to_existing_list = True
                                    break

                            if not added_to_existing_list:                      
                                user_total_balance_history.append(UserTotalBalanceHistory(last_date, last_value))

                            records_filled = True   
                    """
                        If records were filled before adding new AssetBalanceHistory object 
                        one day needs to be addded to last_date, because we already filled 
                        user_total_balance_history with last_day data from last_balance_history
                        and next day matches our current iteration AssetBalanceHistory day
                    """
                    if(records_filled):
                            last_date += datetime.timedelta(days=1)



                # auxiliary variable for knowing if user_total_balance_history object exists with certain date
                added_to_existing_list = False
                
                """
                    Check if it is the first iteration of current AssetBalance object.
                    Or if the last_date equals current AssetBalanceHistory object date
                    and it's time to update AssetBalanceHistory holding for calculations
                """
                if last_date == None or last_date == balance_history.date:
                    print(f'    equals, last_date - {last_date}')

                    # set last_value to current AssetBalanceHistory amount multiplied by AssetPriceHistory price matching AssetBalanceHistory date
                    last_value = balance_history.amount * balance_history.balance.asset.assetpricehistory_set.filter(date=balance_history.date)[0].price
                    
                    """
                        loop through user_total_balance_history list 
                        checking if current AssetBalanceHistory date is in the list
                    """
                    for total_balance in user_total_balance_history:
                        
                        # if it is in the list append last_value to object with date matching current AssetBalanceHistory date
                        if(total_balance.date == balance_history.date):
                            total_balance.values.append(last_value)

                            # Set variable to True, so we can check later if asset was already added to user_total_balance_history
                            added_to_existing_list = True

                            # after loop found the matching date exit the loop to save computation time
                            break

                    # if user_total_balance_history doesn't have object with date matching current AssetBalanceHistory
                    # create new object in user_total_balance_history and add current AssetBalanceHistory object
                    if not added_to_existing_list:                      
                        user_total_balance_history.append(UserTotalBalanceHistory(balance_history.date, last_value))

                    # set last_date so we know last date in current AssetBalance that was added into user_total_balance_history
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
                    object and today are added to user_total_balance_history
                """
                while (last_date < datetime.date.today()):
                    print(f'      fill loop, last_date - {last_date + datetime.timedelta(days=1)}')

                    added_to_existing_list = False 
                    # add one day to last_date, because it's data will be added to user_total_balance_history
                    last_date += datetime.timedelta(days=1)

                    # set last_value to latest AssetBalanceHistory amount multiplied by AssetPriceHistory price matching last AssetBalanceHistory date
                    last_value = last_balance_history.amount * last_balance_history.balance.asset.assetpricehistory_set.filter(date=last_date)[0].price
                    
                    for total_balance in user_total_balance_history:

                        if(total_balance.date == last_date):
                            total_balance.values.append(last_value)
                            added_to_existing_list = True
                            break

                    if not added_to_existing_list:                      
                        user_total_balance_history.append(UserTotalBalanceHistory(last_date, last_value))

        # loop for adding all balance values in respective dates
        for day_balance in user_total_balance_history:

            sum_of_day_balances = 0

            for day_asset_value in day_balance.values:
                sum_of_day_balances += day_asset_value

            day_balance.values = sum_of_day_balances

        """
        TODO:
            check if there is recent assetpricehistory in calculating user daily total balance list
            check if price history values are duplicated in calculating user daily total balance list
        """
    
        context = {
            'user_balance_list': user_balance_list,
            'user_total_balance_history': user_total_balance_history
        }
        return context
    

class ConnectionsView(generic.TemplateView, LoginRequiredMixin):
    """View function for user wallet connections"""

    template_name = 'connections/connections.html'

    def get_context_data(self):

        connected_crypto_exchenges_list = []
        connected_brokerages_list = []

        for exchange in Exchange.objects.all():
            if (exchange.apiconnection_set.filter(owner=self.request.user)):

                setattr(exchange, 'connected', True)

                if (exchange.type == 'crypto_exchange'):
                    connected_crypto_exchenges_list.append(exchange)

                elif (exchange.type == 'brokerage_house'):
                    connected_brokerages_list.append(exchange)


        context = {
            'connected_crypto_exchenges_list': connected_crypto_exchenges_list,
            'connected_brokerages_list': connected_brokerages_list,
        }
        return context
    

class PriceHistoryView(generic.ListView, LoginRequiredMixin):
    
    template_name = 'backend/crypto_price_history.html'
    model = Asset

    def get_queryset(self):
        return Asset.objects.filter(type__exact='cryptocurrency')
    
    def get_context_data(self, **kwargs):
        server_tasks.import_crypto_price_history('trx')

        context = super().get_context_data(**kwargs)
        return context







