from django.shortcuts import render
from .models import Portfolio, Asset, AssetBalance, AssetBalanceHistory, AssetPriceHistory, Exchange, ApiConnection
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import generic

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

        # Get portfolio of current user
        user_portfolio = Portfolio.objects.filter(owner=self.request.user)[0]
        
        # Get all assets
        assets_list = Asset.objects.all()
        asset_price_history_list = AssetPriceHistory.objects.all()
        latest_price_history_list = []

        # Get the latest price of each asset and put its object into array
        for asset in assets_list:
            latest_price_history_list.append(asset.assetpricehistory_set.latest())

        context = {
            'user_portfolio': user_portfolio,
            'latest_price_history_list': latest_price_history_list,
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





