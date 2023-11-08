from django.core.management.base import BaseCommand, CommandError
from portfolio.models import Asset

class Command(BaseCommand):
    help = "Import and crate database records for stock and currency assets."

    def handle(self, *args, **options):

        try:
            stocks = [
                ['Coca-Cola', 'KO'], ['IBM', 'IBM'],
                ['Apple', 'AAPL'], ['Microsoft', 'MSFT'], 
                ['Google', 'GOOG'], ['Meta', 'META'],
            ]

            for stock in stocks:
                if len(Asset.objects.filter(ticker=stock[1].upper()).filter(type='stock')) > 0:
                    print(f'{stock[0]} stock exists')
                else:
                    stock_record = Asset(name=stock[0], api_name=stock[1].lower(), ticker=stock[1].upper(), type='stock', slug=stock[1].lower())
                    stock_record.save()

            currencies = [
                ['Euro', 'EUR'], ['US Dollar', 'USD'], ['British Pound', 'GBP'],
            ]

            for currency in currencies:
                if len(Asset.objects.filter(ticker=currency[1].upper()).filter(type='currency')) > 0:
                    print(f'{currency[0]} currency exists')
                else:
                    currency_record = Asset(name=currency[0], api_name=currency[1].lower(), ticker=currency[1].upper(), type='currency', slug=currency[1].lower())
                    currency_record.save()

        except Exception as error:
            raise CommandError(f'Cannot create stock and currency asset records. {error}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created stock and currency asset records.')
        )