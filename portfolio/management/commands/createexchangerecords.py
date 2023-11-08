from django.core.management.base import BaseCommand, CommandError
from portfolio.models import Exchange
from django.utils.text import slugify

class Command(BaseCommand):
    help = "Crate database records for exchanges."

    def handle(self, *args, **options):

        try:
            exchanges = [
                ['Binance', 'crypto_exchange', 'https://www.binance.com/', 'https://api.binance.com'],
                ['Gate io', 'crypto_exchange', 'https://www.gate.io/', 'https://api.gateio.ws/api/v4'],
                ['Manual Trades', 'manual_trades', '', ''],
            ]

            for exchange in exchanges:
                if len(Exchange.objects.filter(name=exchange[0])) > 0:
                    print(f'{exchange[0]} exchange exists')
                else:
                    exchange_record = Exchange(
                        name=exchange[0], 
                        type=exchange[1], 
                        url=exchange[2], 
                        api_url=exchange[3],
                        slug=slugify(exchange[0]))
                    exchange_record.save()

        except Exception as error:
            raise CommandError(f'Cannot create exchange records. {error}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created exchanges records.')
        )