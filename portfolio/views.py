from django.shortcuts import render
from .models import Portfolio, Asset, AssetBalance, AssetBalanceHistory, AssetPriceHistory
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






