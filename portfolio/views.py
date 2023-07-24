from django.shortcuts import render
from .models import Portfolio, Asset, AssetBalance, AssetBalanceHistory, AssetPriceHistory, Exchange, ApiConnection
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import generic

class UserCurrentAsset:
            def __init__(self, name, ticker, type, latest_price, latest_holding, latest_value):
                self.name = name
                self.ticker = ticker
                self.type = type
                self.latest_price = latest_price
                self.latest_holding = latest_holding
                self.latest_value = latest_value

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

        context = {
            'user_balance_list': user_balance_list,
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





