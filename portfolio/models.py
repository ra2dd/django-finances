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
    )
    
    CURRENCY_TYPE =(
        ('eur', 'Euro'),
        ('usd', 'Dollar'),
    )

    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_TYPE,
    )


class CashHistory(models.Model):
    amount = models.DecimalField(max_digits=19, decimal_places=10)

    date = models.DateField()

    cash = models.ForeignKey(
        Cash,
        on_delete=models.SET_NULL,
    )

