import datetime

class UserAssetHoldingInfo:
    def __init__(self, latest_price, latest_holding, latest_value):
        self.latest_price = latest_price
        self.latest_holding = latest_holding
        self.latest_value = latest_value


def get_asset_value_object(asset_balance_list):
    
    if len(asset_balance_list) == 0:
        zero = format(0.0, '.2f')
        return UserAssetHoldingInfo('', '', '')
    
    else:
        asset_holding_sum = 0
        for balance in asset_balance_list:

            # Sum asset holdings
            asset_holding_sum += balance.assetbalancehistory_set.latest().amount
        
        # Get asset price
        asset_latest_price = round(balance.asset.assetpricehistory_set.latest().price, 2)
        asset_latest_value = round(asset_latest_price * asset_holding_sum, 2)

        return UserAssetHoldingInfo(asset_latest_price, round(asset_holding_sum,2), asset_latest_value)
    
    
def get_asset_price_change(asset, days):

    asset_price_history = asset.assetpricehistory_set.all().order_by('-date')
    latest_price_obj = asset_price_history.latest()
    day_difference = days
    iterations = 0

    for obj in asset_price_history:
        if (obj.date - latest_price_obj.date).days + days < day_difference:
            day_difference = (obj.date - latest_price_obj.date).days + days
            day_price = obj.price

        iterations += 1
        if (iterations > days):
            break
    
    return 100 -(round(latest_price_obj.price * 100 /day_price, 1))
    

        

