from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from portfolio.models import Exchange

class ExchangeListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Exchange.objects.create(name='test_exchange_1', type='brokerage_house')

    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='zkdi8320')


    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('exchanges'))
        self.assertRedirects(response, '/accounts/login/?next=/portfolio/exchanges/')

    def test_view_url(self):
        login = self.client.login(username='testuser1', password='zkdi8320')
        response = self.client.get('/portfolio/exchanges/')

        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

    def test_is_user_connected_attribute(self):
        login = self.client.login(username='testuser1', password='zkdi8320')
        response = self.client.get('/portfolio/exchanges/')
        first_object = response.context['object_list'][0]

        # object.is_user_connected should return False if it exists
        self.assertEqual(first_object.is_user_connected, False)

        
class ExchangeDetailViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='zkdi8320')
        self.exchange_1 = Exchange.objects.create(name='test_exchange_1', type='brokerage_house')


    def test_redirect_if_not_logged_in(self):
        pk = self.exchange_1.pk
        response = self.client.get(reverse(('exchange-detail'), kwargs={'pk': pk}))
        self.assertRedirects(response, f'/accounts/login/?next=/portfolio/exchanges/{pk}' )

    def test_view_url(self):
        login = self.client.login(username='testuser1', password='zkdi8320')
        pk = self.exchange_1.pk
        response = self.client.get(f'/portfolio/exchanges/{pk}')

        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

    def test_is_user_connected_attribute(self):
        login = self.client.login(username='testuser1', password='zkdi8320')
        pk = self.exchange_1.pk
        response = self.client.get(f'/portfolio/exchanges/{pk}')
        object = response.context['object']

        # object.is_user_connected should return False if it exists
        self.assertEqual(object.is_user_connected, False)
        