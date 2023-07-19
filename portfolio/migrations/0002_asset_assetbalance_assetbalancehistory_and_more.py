# Generated by Django 4.2 on 2023-07-19 09:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('ticker', models.CharField(max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='AssetBalance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='portfolio.asset')),
                ('portfolio', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='portfolio.portfolio')),
            ],
        ),
        migrations.CreateModel(
            name='AssetBalanceHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=19)),
                ('date', models.DateField()),
                ('balance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio.assetbalance')),
            ],
        ),
        migrations.RemoveField(
            model_name='cashhistory',
            name='cash',
        ),
        migrations.RemoveField(
            model_name='crypto',
            name='portfolio',
        ),
        migrations.RemoveField(
            model_name='cryptohistory',
            name='crypto',
        ),
        migrations.RemoveField(
            model_name='stock',
            name='portfolio',
        ),
        migrations.RemoveField(
            model_name='stockhistory',
            name='stock',
        ),
        migrations.DeleteModel(
            name='Cash',
        ),
        migrations.DeleteModel(
            name='CashHistory',
        ),
        migrations.DeleteModel(
            name='Crypto',
        ),
        migrations.DeleteModel(
            name='CryptoHistory',
        ),
        migrations.DeleteModel(
            name='Stock',
        ),
        migrations.DeleteModel(
            name='StockHistory',
        ),
    ]
