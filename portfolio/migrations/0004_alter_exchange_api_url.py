# Generated by Django 4.2 on 2023-07-19 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0003_exchange_alter_assetbalancehistory_amount_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exchange',
            name='api_url',
            field=models.URLField(blank=True),
        ),
    ]
