from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
import datetime, random
from portfolio.models import Portfolio, Exchange, Asset, AssetBalance, AssetBalanceHistory
from portfolio.utils.constants import START_DATE

def create_test_user_data(user):
    portfolio = get_object_or_404(Portfolio, owner=user)

    asset_data = [(['KO', 'IBM'], 'stock'), (['ETH', 'BNB'], 'crypto'), (['EUR'], 'currency')]
    exchange = get_object_or_404(Exchange, name='Manual Trades')

    for type in asset_data:
        for ticker in type[0]:
            print(ticker)
            asset = get_object_or_404(Asset, ticker=ticker)
            assetbalance_record = AssetBalance(portfolio=portfolio, asset=asset, broker=exchange)
            assetbalance_record.save()

            match type[1]:
                case 'stock':
                    amount = 2
                case 'crypto':
                    amount = 0.4
                case 'currency':
                    amount = 400 

            date = START_DATE
            
            for day in range(4):
                date = date + datetime.timedelta(days=random.randint(4,6))
                amount = round(amount * (1 + random.randint(1,3)/100), 2)
                abh_record = AssetBalanceHistory(amount=amount, date=date, balance=assetbalance_record)
                abh_record.save()  


class Command(BaseCommand):
    help = "Create test data for users"

    def add_arguments(self, parser):
        parser.add_argument("username", nargs=1, type=str)

    def handle(self, *args, **options):
        try:
            user = User.objects.filter(username=options["username"][0])[0]
            create_test_user_data(user)

        except Exception as error:
            raise CommandError(f'Cannot create user test data. {error}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created test user data.')
        )