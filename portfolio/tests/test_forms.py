import datetime

from django.test import SimpleTestCase

from portfolio.forms import AssetBalanceHistoryForm
from portfolio.utils.constants import START_DATE


class AssetBalanceHistoryFormTest(SimpleTestCase):

    def test_date_before_start_date(self):
        date = START_DATE - datetime.timedelta(days=1)
        form = AssetBalanceHistoryForm(data={ 'date': date, 'amount': 1, 'exchange': 1 })
        self.assertFalse(form.is_valid())

    def test_date_after_today(self):
        date = datetime.date.today() + datetime.timedelta(days=1)
        form = AssetBalanceHistoryForm(data={ 'date': date, 'amount': 1, 'exchange': 1 })
        self.assertFalse(form.is_valid())

    def test_date_today(self):
        date = datetime.date.today()
        form = AssetBalanceHistoryForm(data={ 'date': date, 'amount': 1, 'exchange': 1 })
        self.assertTrue(form.is_valid())

    def test_date_max_past(self):
        form = AssetBalanceHistoryForm(data={ 'date': START_DATE, 'amount': 1, 'exchange': 1 })
        self.assertTrue(form.is_valid())
        print(form.errors)
    