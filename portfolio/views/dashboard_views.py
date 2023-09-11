from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import generic
import json, datetime

from ..models import Portfolio, Asset, AssetBalance, AssetBalanceHistory, AssetPriceHistory, Exchange, ApiConnection
from ..utils import server_tasks, client_tasks, dashboard_balance
     
     
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
        
        user_holdings_list = dashboard_balance.get_user_asset_holdings_with_values_list(user_all_balance_list)
        asset_type_ratio_tuple_list_json = json.dumps(dashboard_balance.get_asset_type_ratio_tuple_list(user_holdings_list), default=str)
        
        user_daily_balance_history = dashboard_balance.get_user_daily_balance_history(user_all_balance_list)
        user_daily_balance_history_json = json.dumps([obj.__dict__ for obj in user_daily_balance_history], default=str)

        latest_balance_value = user_daily_balance_history[-1].values

        if len(user_daily_balance_history) > 14:
            change_seven_days = latest_balance_value - user_daily_balance_history[-7].values
        else:
            change_seven_days = format(0.0, '.2f')

        current_date = datetime.datetime.now().strftime("%B %-d, %Y")

        
        latest_balance_value = 1000
        change_seven_days = 100

        """
        TODO:
            check if there is recent assetpricehistory in calculating user daily total balance list
            check if price history values are duplicated in calculating user daily total balance list
        """

        context = {
            'user_holdings_list': user_holdings_list[:5],
            'user_daily_balance_history': user_daily_balance_history,
            'user_daily_balance_history_json': user_daily_balance_history_json,
            'asset_type_ratio_tuple_list_json': asset_type_ratio_tuple_list_json,
            'latest_balance_value': latest_balance_value,
            'change_seven_days': change_seven_days,
            'current_date': current_date,
        }
        return context