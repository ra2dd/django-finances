from django.core.management.base import BaseCommand, CommandError
from ...utils import server_util

class Command(BaseCommand):
    help = "Imports price data about crypto assets"

    def handle(self, *args, **options):

        try:
            server_util.import_current_crypto_price()
        except Exception as error:
            raise CommandError(f'Cannot import crypto price history. {error}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully imported crypto price history.')
        )