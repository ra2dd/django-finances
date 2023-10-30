from django.core.management.base import BaseCommand, CommandError
from ...utils import server_util

class Command(BaseCommand):
    help = "Import and crate database records for crypto assets."

    def handle(self, *args, **options):

        try:
            server_util.get_crypto_assets()
        except Exception as error:
            raise CommandError(f'Cannot import crypto asset records. {error}')

        self.stdout.write(
            self.style.SUCCESS('Successfully imported crypto asset record.')
        )