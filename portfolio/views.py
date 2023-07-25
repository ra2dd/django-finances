from django.shortcuts import render
from .models import Portfolio, Asset, AssetBalance, AssetBalanceHistory, AssetPriceHistory, Exchange, ApiConnection
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import generic
import datetime, random

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

        user_total_balance_history = []

        for balance in user_all_balance_list:
             
            last_date = None
            last_value = None
            last_balance = None
            print(f'start {balance}')
            test = 0

            for balance_history in balance.assetbalancehistory_set.all():

                record_added = False
                last_balance_history = balance_history
                while(not record_added):

                    added_to_existing_list = False

                    print(f'  loop start{balance_history.date}')
                    test += 1
                    if test > 50:
                        break

                    if last_date == None or last_date == balance_history.date:
                        print(f'    equals, last_date - {last_date}')    
                        last_value = balance_history.amount * balance_history.balance.asset.assetpricehistory_set.filter(date=balance_history.date)[0].price
                        
                        for total_balance in user_total_balance_history:

                            if(total_balance.date == balance_history.date):
                                total_balance.values.append(last_value)
                                added_to_existing_list = True

                        if not added_to_existing_list:                      
                            user_total_balance_history.append(UserTotalBalanceHistory(balance_history.date, last_value))
                            
                        last_date = balance_history.date
                        record_added = True

                        test += 1
                        if test > 50:
                            break
                    
                    else:
                        while (last_date + datetime.timedelta(days=1) != balance_history.date):
                            added_to_existing_list = False
                            print(f'    loop, last_date - {last_date + datetime.timedelta(days=1)}') 
                            last_date += datetime.timedelta(days=1)
                            last_value = balance_history.amount * balance_history.balance.asset.assetpricehistory_set.filter(date=last_date)[0].price

                            for total_balance in user_total_balance_history:

                                if(total_balance.date == last_date):
                                    total_balance.values.append(last_value)
                                    added_to_existing_list = True

                            if not added_to_existing_list:                      
                                user_total_balance_history.append(UserTotalBalanceHistory(last_date, last_value))

                            test += 1
                            if test > 50:
                                break

                        if(not record_added):
                            last_date += datetime.timedelta(days=1)

            print()
            print(last_date)
            print(datetime.date.today())
            print()
            if(last_date < datetime.date.today()):

                while (last_date < datetime.date.today()):
                    added_to_existing_list = False
                    print(f'      fill loop, last_date - {last_date + datetime.timedelta(days=1)}') 
                    last_date += datetime.timedelta(days=1)
                    last_value = last_balance_history.amount * last_balance_history.balance.asset.assetpricehistory_set.filter(date=last_date)[0].price
                    
                    for total_balance in user_total_balance_history:

                        if(total_balance.date == last_date):
                            total_balance.values.append(last_value)
                            added_to_existing_list = True

                    if not added_to_existing_list:                      
                        user_total_balance_history.append(UserTotalBalanceHistory(last_date, last_value))

                    test += 1
                    if test > 50:
                        break

        for day_balance in user_total_balance_history:

            sum_of_day_balances = 0

            for day_asset_value in day_balance.values:
                sum_of_day_balances += day_asset_value

            day_balance.values = sum_of_day_balances


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





