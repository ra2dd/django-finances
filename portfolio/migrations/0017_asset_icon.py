# Generated by Django 4.2 on 2023-08-15 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0016_alter_exchange_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='icon',
            field=models.ImageField(null=True, upload_to='assets/'),
        ),
    ]