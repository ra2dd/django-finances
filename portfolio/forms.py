from django import forms

from django.core.exceptions import ValidationError
from .views import connections_views
from .tasks import client_tasks

class AddConnectionModelForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        self.exchange_name = kwargs.pop('exchange_name', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        api_key_data = cleaned_data['api_key']
        secret_key_data = cleaned_data['secret_key']
        print(self.exchange_name)

        if self.exchange_name == 'binance':
            if client_tasks.check_binance_connection(api_key_data, secret_key_data) == False:
                raise ValidationError('Error connecting with given api data, please check if api key and secret key are correct.')
            elif client_tasks.check_binance_connection(api_key_data, secret_key_data) == 'no-connection':
                raise ValidationError('Error connecting to Binance server, please contact site admin or try again.')
        else:
            raise ValidationError('Connection for exchange not implemented')
    class Meta:
        model = connections_views.ApiConnection
        fields = ['api_key', 'secret_key']

