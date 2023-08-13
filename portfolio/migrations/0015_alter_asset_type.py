# Generated by Django 4.2 on 2023-08-11 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0014_alter_asset_api_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='type',
            field=models.CharField(choices=[('stock', 'Stock'), ('cryptocurrency', 'Cryptocurrency'), ('currency', 'Currency')], max_length=16),
        ),
    ]