from django.core.management.base import BaseCommand, CommandError
from ...utils import server_util

class Command(BaseCommand):
    help = "Import and crate database records for crypto assets."

    def add_arguments(self, parser):
        parser.add_argument("asset_number", nargs=1, type=int)

    def handle(self, *args, **options):

        try:
            server_util.get_crypto_assets(options["asset_number"][0])
        except Exception as error:
            raise CommandError(f'Cannot import crypto asset records. {error}')

        self.stdout.write(
            self.style.SUCCESS('Successfully imported crypto asset record.')
        )