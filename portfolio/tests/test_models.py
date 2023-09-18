from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files import File
from io import BytesIO

from portfolio.models import Exchange, ApiConnection, Asset

class ExchangeModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='testuser1', password='zkdi8320')

        exchange_1 = Exchange.objects.create(name='test_exchange_1', type='brokerage_house')
        ApiConnection.objects.create(broker=exchange_1, api_key='test', secret_key='test', owner=user)

        exchange_2 = Exchange.objects.create(name='test_exchange_2', type='crypto_exchange')

    def test_name_max_length(self):
        exchange = Exchange.objects.get(id=1)
        max_length = exchange._meta.get_field('name').max_length
        self.assertEqual(max_length, 64)

    def test_get_absolute_url(self):
        exchange = Exchange.objects.get(id=1)
        self.assertEqual(exchange.get_absolute_url(), '/portfolio/exchanges/1')

    def test_is_user_connected(self):
        exchange_con = Exchange.objects.get(id=1)
        exchange_disc = Exchange.objects.get(id=2)
        user = User.objects.get(id=1)
        self.assertTrue(exchange_con.is_user_connected(user))
        self.assertFalse(exchange_disc.is_user_connected(user))
