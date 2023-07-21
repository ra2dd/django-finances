from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

class Portfolio(models.Model):
    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True
    )

    def __str__(self):
        return f'{self.owner.username} Portfolio {self.pk}'


class Exchange(models.Model):
    name = models.CharField(max_length=64)

    EXCHANGE_TYPE = (
        ('brokerage_house', 'Brokerage House'),
        ('crypto_exchange', 'Cryptocurrency Exchange'),
    )

    type = models.CharField(
        max_length=16,
        choices=EXCHANGE_TYPE,
    )

    url = models.URLField(max_length=200)

    api_url = models.URLField(max_length=200, blank=True)

    def __str__(self):
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
        return f'Api key {self.owner} - {self.broker}'


class Asset(models.Model):
    name = models.CharField(max_length=64)

    ticker = models.CharField(max_length=16)

    type = models.CharField(max_length=32)

    ASSET_TYPE = (
        ('stock', 'Stock'),
        ('cryptocurrency', 'Cryptocurrency'),
        ('cash', 'Cash')
    )

    type = models.CharField(
        max_length=16,
        choices=ASSET_TYPE,
    )

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
        ordering = ['-date']
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
        ordering = ['-date']
        get_latest_by = ['date']

    def __str__(self):
        return f'{self.balance} - {self.amount}'

