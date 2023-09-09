class UserAssetHoldingInfo:
    def __init__(self, latest_price, latest_holding, latest_value):
        self.latest_price = latest_price
        self.latest_holding = latest_holding
        self.latest_value = latest_value


def get_asset_value_object(asset_balance_list):
    
    if len(asset_balance_list) == 0:
        '''
        zero = format(0.0, '.2f')
        return UserAssetHoldingInfo(zero, zero, zero)
        '''
        return None
    
    else:
        asset_holding_sum = 0
        for balance in asset_balance_list:

            # Sum asset holdings
            asset_holding_sum += balance.assetbalancehistory_set.latest().amount
        
        # Get asset price
        asset_latest_price = round(balance.asset.assetpricehistory_set.latest().price, 2)
        asset_latest_value = round(asset_latest_price * asset_holding_sum, 2)

        return UserAssetHoldingInfo(asset_latest_price, round(asset_holding_sum,2), asset_latest_value)