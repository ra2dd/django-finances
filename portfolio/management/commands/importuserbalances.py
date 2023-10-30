from django.core.management.base import BaseCommand, CommandError
from ...utils import client_util
from ...models import Portfolio, ApiConnection

class Command(BaseCommand):
    help = "Imports all user balances from ApiConnections"

    def handle(self, *args, **options):

        try:
            portfolio_list = Portfolio.objects.all()

            for portfolio in portfolio_list:
                user = portfolio.owner
                user_apiconnection_list = ApiConnection.objects.filter(owner=user)

                for apiconnection in user_apiconnection_list:
                    exchange = apiconnection.broker

                    # Import asset balances
                    client_util.import_balance(exchange, apiconnection, user)
                    print(f'imported balances from {exchange} using {apiconnection}')

        except Exception as error:
            raise CommandError(f'Cannot import user balances from ApiConnections. {error}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully imported user balances from ApiConnections.')
        )