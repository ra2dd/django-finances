# Generated by Django 4.2 on 2023-07-19 14:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0005_alter_assetbalancehistory_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assetbalancehistory',
            options={'get_latest_by': ['date'], 'ordering': ['date']},
        ),
        migrations.AlterModelOptions(
            name='assetpricehistory',
            options={'get_latest_by': ['date'], 'ordering': ['date']},
        ),
    ]