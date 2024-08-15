import datetime
from decimal import Decimal

from portfolio.models import AssetBalanceHistory


class TotalDayBalance:
    def __init__(self, date, value):
        self.date = date
        self.values = [value]

        
class DailyBalanceUtil:
    def __init__(self, user_all_balance_list):
        # List containing total TotalDayBalance objects
        # starting from first user asset balance date to today. 
        self.user_daily_balance_history = []
        self.user_all_balance_list = user_all_balance_list


    def get_user_daily_balance_history(self):
        """
        Function that calculates value for each user asset for each day
        and then sums it returning list of objects containing information
        about each day and corresponding portfolio value.
        """

        # loop through user's all AssetBalance objects 
        for balance in self.user_all_balance_list:
            
            # auxiliary variables for knowing last date and value 
            # that was calculated in certain AssetBalance
            last_date, last_value = None, None

            # auxilary variable for storing last AssetBalanceHistory object 
            last_balance_history = None

            print(f'start {balance}')

            # loop through user's all AssetBalanceHistory objects associated with certain AssetBalance
            for balance_history in balance.assetbalancehistory_set.all():
                
                print(f'  balance start {balance_history.date}')

                # auxiliary variable for checking if records were filled in before adding 
                # AssetBalanceHistory object to user_daily_balance_history
                records_filled = False

                # if it's not a first iteration of the current loop
                if last_date != None:

                    # If last_date + 1 day is not a AssetBalanceHistory current date
                    # fill in missing dates between AssetBalanceHistory object dates with records.
                    while (last_date + datetime.timedelta(days=1) != balance_history.date):
                            
                        print(f'    middle fill, last_date - {last_date + datetime.timedelta(days=1)}') 
                        
                        # Add one day to last_date, because we are going to be filling it with data from last_balance_history
                        last_date += datetime.timedelta(days=1)
                        
                        # add value using last available balance amount and price
                        self._fetch_price_and_add_user_balance(last_balance_history, last_date)

                        records_filled = True   
                    """
                        If records were filled before adding new AssetBalanceHistory object 
                        one day needs to be addded to last_date, because we already filled 
                        user_daily_balance_history with last_day data from last_balance_history
                        and next day matches our current iteration AssetBalanceHistory day
                    """
                    if(records_filled):
                            last_date += datetime.timedelta(days=1)

                
                """
                    Check if it is the first iteration of current AssetBalance object.
                    Or if the last_date equals current AssetBalanceHistory object date
                    and it's time to update AssetBalanceHistory holding for calculations
                """
                if last_date == None or last_date == balance_history.date:
                    print(f'    equals, last_date - {last_date}')

                    # add value using current balance history and associated date
                    self._fetch_price_and_add_user_balance(balance_history, balance_history.date)

                    # set last_date so we know last date in current AssetBalance that was added into user_daily_balance_history
                    # helpful in filling not existing dates between AssetBalanceHistory object dates
                    last_date = balance_history.date

                """
                    set auxilary variable with last AssetBalanceHistory object, so we 
                    have the latest object data for completing missing dates between 
                    AssetBalanceHistory objects or missing dates between last
                    AssetBalanceHistory object and today
                """
                last_balance_history = balance_history

            """
                if after iterating over all AssetBalanceHistory objects 
                the last_date is still behind today
            """
            if(last_date < datetime.date.today()):
                print(f'      filling end loop from: {last_date} to {datetime.date.today()}')

                """
                    interate until all missing dates between last AssetBalanceHistory 
                    object and today are added to user_daily_balance_history
                """
                while (last_date < datetime.date.today()):
                    # print(f'      fill loop, last_date - {last_date + datetime.timedelta(days=1)}')

                    # add one day to last_date, because it's data will be added to user_daily_balance_history
                    last_date += datetime.timedelta(days=1)

                    # Update price if it exists for new date
                    price_history_objs = last_balance_history.balance.asset.assetpricehistory_set.filter(date=last_date)
                    if(len(price_history_objs) > 0):
                        last_price_history = price_history_objs.first().price

                    # set last_value using latest AssetBalanceHistory amount
                    #  multiplied by latest matching price
                    last_value = self._calculate_asset_value(
                        last_balance_history.amount, last_price_history)
                    
                    # add value to the final list 
                    self._add_user_daily_balance(last_date, last_value)

        # loop for adding all balance values in respective dates
        for day_balance in self.user_daily_balance_history:
            # print(f'{day_balance.date}, {day_balance.values}')
            sum_of_day_balances = 0

            for day_asset_value in day_balance.values:
                sum_of_day_balances += day_asset_value

            day_balance.values = round(sum_of_day_balances, 2)
        
        self.user_daily_balance_history.sort(key=lambda b: b.date)
        return self.user_daily_balance_history
    

    def _fetch_price_and_add_user_balance(
            self, balance_history: AssetBalanceHistory, 
            date: datetime.date) -> None:
        # Get price
        latest_asset_price = self._get_last_available_price_for_asset(
            balance_history, date)
        # Calculate asset value
        asset_value = self._calculate_asset_value(
            balance_history.amount, latest_asset_price)
        # Add value to final list
        self._add_user_daily_balance(date, asset_value)
        

    def _get_last_available_price_for_asset(
                self, balance_history: AssetBalanceHistory, 
                date: datetime.date) -> Decimal:
        price_history_objects = balance_history.balance.asset.assetpricehistory_set
        
        # Check if asset price record for a requested date exists
        if(len(filtered_objs := price_history_objects.filter(date=date)) > 0):
            return filtered_objs.first().price
        
        # If it doesn't exist go back one day at a time and get last avaiable price
        for minus_days in range(10000):
            if len(filtered_objs := price_history_objects.filter(
                date=date - datetime.timedelta(days=minus_days))) > 0:
                return filtered_objs.first().price
        # TODO: handle a scenario when loop iterates without returning price


    def _calculate_asset_value(self, amount: Decimal, price: Decimal) -> Decimal:
        return amount * price
    

    def _add_user_daily_balance(self, date: datetime.date, last_value: Decimal) -> None:

        # If balance with last_day exists append value to object
        for total_balance in self.user_daily_balance_history:
            if(total_balance.date == date):
                total_balance.values.append(last_value)
                return
            
        # If it wasn't added create a new object                       
        self.user_daily_balance_history.append(TotalDayBalance(date, last_value))