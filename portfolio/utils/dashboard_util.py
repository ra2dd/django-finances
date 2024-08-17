import json, datetime, random
from django.http import Http404
from django.shortcuts import get_object_or_404

from .constants import START_DATE
from ..models import Portfolio
from .daily_balance_util import DailyBalanceUtil

class UserCurrentAsset:
    def __init__(self, name, ticker, type, icon, latest_price, latest_holding, latest_value):
        self.name = name
        self.ticker = ticker
        self.type = type
        self.icon = icon
        self.latest_price = latest_price
        self.latest_holding = latest_holding
        self.latest_value = latest_value


class DashboardService:
    def __init__(self, user_object):
        self.portfolio = get_object_or_404(Portfolio, owner=user_object)
        self.all_balances = self.portfolio.assetbalance_set.all()
        self.user_holdings_list = self._get_user_asset_holdings_with_values_list()
        self.current_date = self._get_current_date()
        self.daily_balance_service = DailyBalanceUtil(self.all_balances)

    
    def get_dashboard_context(self):

        current_date = self._get_current_date()

        # If user doesn't have any holdings return just date
        if len(self.user_holdings_list) == 0:
            context = {'current_date': self.current_date}
            return context   
        
        asset_ratio = self._get_asset_type_ratio_tuple_list()
        asset_type_ratio_tuple_list_json = json.dumps(asset_ratio, default=str)
        top_asset_type_allocation = asset_ratio[0]
        
        user_daily_balance_history_json = self.daily_balance_service.get_user_daily_balance_history()

        user_daily_balance_history = self.daily_balance_service.user_daily_balance_history
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

        if self.user_holdings_list[0].latest_value == 0:
            top_asset_allocation = 0
        else:
            top_asset_allocation = round(self.user_holdings_list[0].latest_value / latest_balance_value * 100)

        context = {
            'user_holdings_list': self.user_holdings_list[:5],
            'user_daily_balance_history_json': user_daily_balance_history_json,
            'asset_type_ratio_tuple_list_json': asset_type_ratio_tuple_list_json,
            'latest_balance_value': latest_balance_value,
            'balance_change': balance_change,
            'current_date': current_date,
            'top_asset_type_allocation': top_asset_type_allocation,
            'top_asset_allocation': top_asset_allocation,
            'asset_ratio': asset_ratio,
            'current_date': self.current_date,
        }
        return context


    def _get_user_asset_holdings_with_values_list(self):
        
        # Auxilary variable for storing asset information for the next loop iteration (asset, asset amount)
        same_latest_balance = (False, False)

        # context list for holding user current asset holdings objects
        user_holdings_list = []

        # Loop throgh balances to add amount, price and value attrributes to balance queryset
        for balance in self.all_balances:
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
            user_holdings_list.append(
                UserCurrentAsset(
                    balance.asset.name, 
                    balance.asset.ticker, 
                    balance.asset.type, 
                    balance.asset.get_icon_path, 
                    round(asset_latest_price, 2), 
                    round(asset_latest_holding, 2), 
                    round(asset_latest_value, 2)))

        user_holdings_list.sort(reverse=True, key=lambda h: h.latest_value)
        return user_holdings_list


    def _get_asset_type_ratio_tuple_list(self):
        
        asset_ratio = {
            'cryptocurrency': 0,
            'stock': 0,
            'currency': 0,
        }
        
        # Sum user holdings based on type
        for holding in self.user_holdings_list:
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
             

    def _get_current_date(self):
        return datetime.datetime.now().strftime("%B %-d, %Y")