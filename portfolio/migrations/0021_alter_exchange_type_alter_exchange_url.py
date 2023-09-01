# Generated by Django 4.2 on 2023-08-31 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0020_alter_asset_icon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exchange',
            name='type',
            field=models.CharField(choices=[('brokerage_house', 'Brokerage House'), ('crypto_exchange', 'Cryptocurrency Exchange'), ('manual_trades', 'Manual Trades')], max_length=16),
        ),
        migrations.AlterField(
            model_name='exchange',
            name='url',
            field=models.URLField(blank=True),
        ),
    ]