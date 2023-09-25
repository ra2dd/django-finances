from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


def asset_icon_path(instance, filename):
    return "portfolio/static/media/images/assets/{0}/{1}".format(instance.type, filename)


class Portfolio(models.Model):
    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True
    )

    def __str__(self):
        return f'Portfolio {self.pk}'


class Exchange(models.Model):
    name = models.CharField(max_length=64)

    EXCHANGE_TYPE = (
        ('brokerage_house', 'Brokerage House'),
        ('crypto_exchange', 'Cryptocurrency Exchange'),
        ('manual_trades', 'Manual Trades')
    )

    type = models.CharField(
        max_length=16,
        choices=EXCHANGE_TYPE,
    )

    url = models.URLField(max_length=200, blank=True)

    api_url = models.URLField(max_length=200, blank=True)
    
    class Meta:
        ordering = ['name']

    def is_user_connected(self, user_obj):
        return bool(ApiConnection.objects.filter(broker=self.id).filter(owner=user_obj))

    def get_absolute_url(self):
        """Returns the URL to access a detail record for exchange."""
        return reverse('exchange-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object"""
        return f'{self.name}'
    

class ApiConnection(models.Model):
    broker = models.ForeignKey(
        Exchange,
        on_delete=models.SET_NULL,
        null=True
    )

    api_key = models.CharField(max_length=256)

    secret_key = models.CharField(max_length=256)

    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self):
        """String for representing the Model object"""
        return f'{self.owner.username[0].upper() + self.owner.username[1:]} api keys - {self.broker}'


class Asset(models.Model):
    name = models.CharField(max_length=64)

    api_name = models.CharField(max_length=32, unique=True)

    ticker = models.CharField(max_length=16)

    type = models.CharField(max_length=32)

    ASSET_TYPE = (
        ('stock', 'Stock'),
        ('cryptocurrency', 'Cryptocurrency'),
        ('currency', 'Currency')
    )

    type = models.CharField(
        max_length=16,
        choices=ASSET_TYPE,
    )

    icon = models.ImageField(upload_to=asset_icon_path, null=True, blank=True)
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return f'{self.ticker} - {self.name}'
    

class AssetPriceHistory(models.Model):
    asset = models.ForeignKey(
        Asset,
        on_delete=models.SET_NULL,
        null=True,
    )

    date = models.DateField()

    price = models.DecimalField(max_digits=19, decimal_places=8)

    class Meta:
        ordering = ['date']
        get_latest_by = ['date']

    def __str__(self):
        return f'{self.asset} {self.date} - {self.price}'


class AssetBalance(models.Model):
    portfolio = models.ForeignKey(
        Portfolio, 
        on_delete=models.SET_NULL,
        null=True,
    )

    asset = models.ForeignKey(
        Asset,
        on_delete=models.SET_NULL,
        null= True,
    )

    broker = models.ForeignKey(
        Exchange,
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        ordering = ['asset']

    def __str__(self):
        return f'{self.portfolio} - {self.asset} - {self.broker}'


class AssetBalanceHistory(models.Model):
    amount = models.DecimalField(max_digits=19, decimal_places=8)

    date = models.DateField()

    balance = models.ForeignKey(
        AssetBalance,
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        ordering = ['date']
        get_latest_by = ['date']

    def round_amount(self):
        return round(self.amount, 2)

    def __str__(self):
        return f'{self.balance} - {self.amount}'

