# Generated by Django 4.2 on 2023-07-21 16:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0009_alter_asset_type_alter_exchange_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assetbalancehistory',
            options={'get_latest_by': ['date'], 'ordering': ['-date']},
        ),
        migrations.AlterModelOptions(
            name='assetpricehistory',
            options={'get_latest_by': ['date'], 'ordering': ['-date']},
        ),
    ]
