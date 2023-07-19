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


class Asset(models.Model):
    name = models.CharField(max_length=64)

    ticker = models.CharField(max_length=16)

    def __str__(self):
        return f'{self.ticker} - {self.name}'


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

    def __str__(self):
        return f'{self.portfolio} - {self.asset}'


class AssetBalanceHistory(models.Model):
    amount = models.DecimalField(max_digits=19, decimal_places=2)

    date = models.DateField()

    balance = models.ForeignKey(
        AssetBalance,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.balance} - {self.amount}'

