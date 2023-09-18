from django.core.management.base import BaseCommand, CommandError
from ...utils import server_util

class Command(BaseCommand):
    help = "Imports price data about stock and currency assets"

    def handle(self, *args, **options):

        try:
            server_util.import_current_stock_price()
            server_util.import_current_currency_price()
        except:
            raise CommandError('Cannot import stock and currency price history.')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully imported stock and currency price history.')
        )