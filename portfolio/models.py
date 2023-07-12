from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

class Portfolio(models.Model):
    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True
    )


class Cash(models.Model):
    portfolio = models.ForeignKey(
        Portfolio, 
        on_delete=models.SET_NULL,
        null=True,
    )
    
    CURRENCY_TYPE = (
        ('EUR', 'Euro'),
        ('USD', 'Dollar'),
    )

    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_TYPE,
    )

class CashHistory(models.Model):
    amount = models.DecimalField(max_digits=19, decimal_places=2)

    date = models.DateField()

    cash = models.ForeignKey(
        Cash,
        on_delete=models.SET_NULL,
        null=True,
    )


class Stock(models.Model):
    portfolio = models.ForeignKey(
        Portfolio, 
        on_delete=models.SET_NULL,
        null=True,
    )
    
    STOCK_NAME = (
        ('MSFT', 'Microsoft'),
        ('KO', 'Coca Cola'),
    )

    name = models.CharField(
        max_length=5,
        choices=STOCK_NAME,
    )

class StockHistory(models.Model):
    amount = models.DecimalField(max_digits=19, decimal_places=6)

    date = models.DateField()

    stock = models.ForeignKey(
        Stock,
        on_delete=models.SET_NULL,
        null=True,
    )


class Crypto(models.Model):
    portfolio = models.ForeignKey(
        Portfolio, 
        on_delete=models.SET_NULL,
        null=True,
    )
    
    CRYPTO_NAME = (
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
    )

    name = models.CharField(
        max_length=5,
        choices=CRYPTO_NAME,
    )

class CryptoHistory(models.Model):
    amount = models.DecimalField(max_digits=19, decimal_places=10)

    date = models.DateField()

    crypto = models.ForeignKey(
        Crypto,
        on_delete=models.SET_NULL,
        null=True,
    )

