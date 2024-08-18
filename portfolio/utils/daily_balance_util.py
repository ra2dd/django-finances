import datetime
import json
from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist

from portfolio.models import AssetBalanceHistory, AssetPriceHistory


class TotalDayBalance:
    def __init__(self, date, value):
        self.date = date
        self.values = [value]


class PortfolioValueChange:
    def __init__(self, days, change, negative):
        self.days = days
        self.change = change
        self.negative = negative

        
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

            self._latest_available_price = None

            print(f'start {balance}')

            # loop through user's all AssetBalanceHistory objects associated with certain AssetBalance
            for balance_history in balance.assetbalancehistory_set.all():
                
                print(f'  balance start {balance_history.date}')

                # auxiliary variable for checking if records were filled in before adding 
                # AssetBalanceHistory object to user_daily_balance_history
                records_filled = False

                # if it's not a first iteration of the current loop
                if last_date != None:
                    # storing date for logging purposes
                    middle_fill_start = last_date

                    # If last_date + 1 day is not a AssetBalanceHistory current date
                    # fill in missing dates between AssetBalanceHistory object dates with records.
                    while (last_date + datetime.timedelta(days=1) != balance_history.date):
                
                        # Add one day to last_date, because we are going to be filling it with data from last_balance_history
                        last_date += datetime.timedelta(days=1)
                        
                        # add value using last available balance amount, price and date
                        self._process_price_and_add_user_balance(
                            last_balance_history, last_date, fetch_new_price=False)

                        records_filled = True   
                    """
                        If records were filled before adding new AssetBalanceHistory object 
                        one day needs to be addded to last_date, because we already filled 
                        user_daily_balance_history with last_day data from last_balance_history
                        and next day matches our current iteration AssetBalanceHistory day
                    """
                    if(records_filled):
                        print(f'    middle fill loop, from {middle_fill_start} to {last_date}') 
                        last_date += datetime.timedelta(days=1)

                
                """
                    Check if it is the first iteration of current AssetBalance object.
                    Or if the last_date equals current AssetBalanceHistory object date
                    and it's time to update AssetBalanceHistory holding for calculations
                """
                if last_date == None or last_date == balance_history.date:
                    print(f'    equals, last_date - {last_date}')

                    # add value using current balance history and associated date 
                    self._process_price_and_add_user_balance(
                        balance_history, balance_history.date, fetch_new_price=True)

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

                    # add value using last available user balance price and date
                    self._process_price_and_add_user_balance(
                        last_balance_history, last_date, fetch_new_price=False)

        self._sum_and_sort_user_balances_per_day()
        return self._convert_daily_balance_to_json()
    

    def _convert_daily_balance_to_json(self):
        return json.dumps([obj.__dict__ for obj in self.user_daily_balance_history], default=str)


    def _sum_and_sort_user_balances_per_day(self) -> None:
        # loop for adding all balance values in respective days
        for day_balance in self.user_daily_balance_history:
            sum_of_day_balances = 0
            for day_asset_value in day_balance.values:
                sum_of_day_balances += day_asset_value
            day_balance.values = round(sum_of_day_balances, 2)
        
        self.user_daily_balance_history.sort(key=lambda b: b.date)


    def _process_price_and_add_user_balance(
            self, balance_history: AssetBalanceHistory, 
            date: datetime.date,
            fetch_new_price: bool = True) -> None:
        
        # Check if there is a new available price
        price_history_objects = balance_history.balance.asset.assetpricehistory_set.all()
        price_updated = self._update_price_if_exist_for_asset(
            price_history_objects, date)
        
        # If there is no new available price and new price must be fetched
        # go to the past and get last available price
        if not price_updated and fetch_new_price:
            self._get__latest_available_price_for_asset(
                price_history_objects, date)
        
        # Calculate asset value and add it to final list
        self._calculate_value_and_add_it_to_final_list(
            balance_history.amount, date)
        

    def _get__latest_available_price_for_asset(
                self, price_history_objects: AssetPriceHistory, 
                date: datetime.date) -> None:
        """Go back one day at a time and get last avaiable asset price"""
        for minus_days in range(100):
            if len(filtered_objs := price_history_objects.filter(
                date=date - datetime.timedelta(days=minus_days))) > 0:
                self._latest_available_price = filtered_objs.first().price
                return
        raise ObjectDoesNotExist(
            f"AssetPriceHistory object with requested date: {date} and before doesn't exist.")


    def _update_price_if_exist_for_asset(
            self, price_history_objects: AssetPriceHistory,
            date: datetime.date) -> bool:
        """Update asset price record for a requested date if it exists"""

        if(len(filtered_objs := price_history_objects.filter(date=date)) > 0):
            self._latest_available_price = filtered_objs.first().price
            return True

        return False


    def _calculate_value_and_add_it_to_final_list(
            self, amount: Decimal, 
            date: datetime.date) -> None:
        # Calculate asset value
        asset_value = self._calculate_asset_value(
            amount, self._latest_available_price)
        # Add value to final list
        self._add_user_daily_balance(date, asset_value)


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

    
    def get_portfolio_value_change(self):
        latest_portfolio_value = self.user_daily_balance_history[-1].values

        # How many history days does user portfolio have
        history_len = len(self.user_daily_balance_history)
        if history_len > 30:
            days_change = 30
        elif history_len > 7:
            days_change = 7
        elif history_len > 1:
            days_change = 1
        else:
            days_change = 0

        return self._calculate_portfolio_change(days_change)

    
    def _calculate_portfolio_change(self, days_change):
        value_change = self.user_daily_balance_history[-1].values - self.user_daily_balance_history[-1 - days_change].values
        # Append absolute value change to an object
        # and add negative or positive symbol in a template (before currency symbol)
        return PortfolioValueChange(days_change, abs(value_change), value_change < 0)


