from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
import datetime, random
from portfolio.models import Portfolio, Exchange, Asset, AssetBalance, AssetBalanceHistory


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
                    amount = 0.8
                case 'crypto':
                    amount = 0.4
                case 'currency':
                    amount = 300 

            date = START_DATE
            
            for day in range(4):
                date = date + datetime.timedelta(days=random.randint(4,6))
                amount = round(amount * (1 + random.randint(1,3)/100), 2)
                abh_record = AssetBalanceHistory(amount=amount, date=date, balance=assetbalance_record)
                abh_record.save()  


class Command(BaseCommand):
    help = "Imports data about crypto assets"

    def handle(self, *args, **options):

        try:
            user = User.objects.filter(username='demo')[0]
            create_test_user_data(user)

        except:
            raise CommandError('Cannot create user test data.')

        self.stdout.write(
            self.style.SUCCESS('Successfully created test user data.')
        )