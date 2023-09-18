from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
import json, datetime

from ..models import Portfolio
from ..utils import dashboard_util
     
     
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

        current_date = datetime.datetime.now().strftime("%B %-d, %Y")

        # Get all asset balances of current user portfolio
        user_all_balance_list = Portfolio.objects.filter(owner=self.request.user)[0].assetbalance_set.all()
        
        # Get list of user asset holdings
        user_holdings_list = dashboard_util.get_user_asset_holdings_with_values_list(user_all_balance_list)

        if len(user_holdings_list) > 0:
            asset_type_ratio_tuple_list_json = json.dumps(dashboard_util.get_asset_type_ratio_tuple_list(user_holdings_list), default=str)
            
            user_daily_balance_history = dashboard_util.get_user_daily_balance_history(user_all_balance_list)
            user_daily_balance_history_json = json.dumps([obj.__dict__ for obj in user_daily_balance_history], default=str)

            if len(user_daily_balance_history) > 0: 
                latest_balance_value = user_daily_balance_history[-1].values

                if len(user_daily_balance_history) > 30:
                    balance_change = (30, latest_balance_value - user_daily_balance_history[-30].values)
                elif len(user_daily_balance_history) > 7:
                    balance_change = (7, latest_balance_value - user_daily_balance_history[-7].values)
                else:
                    balance_change = (0, format(0.0, '.2f'))

            context = {
                'user_holdings_list': user_holdings_list[:5],
                'user_daily_balance_history_json': user_daily_balance_history_json,
                'asset_type_ratio_tuple_list_json': asset_type_ratio_tuple_list_json,
                'latest_balance_value': latest_balance_value,
                'balance_change': balance_change,
                'current_date': current_date,
            }
            return context
    
        else:
            context = {
                'current_date': current_date
            }

            return context

        """
        TODO:
            check if price history values are duplicated in calculating user daily total balance list
        """

        