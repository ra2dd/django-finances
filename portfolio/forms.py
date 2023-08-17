from django import forms

from django.core.exceptions import ValidationError
from .views import connections_views
from .tasks import client_tasks
from .models import ApiConnection

def check_connection(exchange_name, api_key_data, secret_key_data):
    connection_response = None

    if exchange_name == 'binance':
            connection_response = client_tasks.check_binance_connection(api_key_data, secret_key_data)
    
    if connection_response == True:
        pass
    elif connection_response == False:
        raise ValidationError(f'Error connecting to {exchange_name} with given api data, please check if api key and secret key are correct.')
    elif connection_response == 'no-connection':
        raise ValidationError(f'Error connecting to {exchange_name} server, please contact site admin or try again.')
    elif connection_response == None:
        raise ValidationError(f'Connection for {exchange_name} exchange not implemented')
    else:
        raise ValidationError('Error, please contact site admin.')


class ConnectionAddModelForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        self.exchange_object = kwargs.pop('exchange_object', None)
        self.user_object = kwargs.pop('user_object', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        api_key_data = cleaned_data['api_key']
        secret_key_data = cleaned_data['secret_key']

        check_connection(self.exchange_object.name.lower(), api_key_data, secret_key_data)

        api_connection = ApiConnection.objects.filter(broker=self.exchange_object, owner=self.user_object)
        if len(api_connection) == 1:
            api_connection[0].delete()
        elif len(api_connection) > 1:
            raise ValidationError('Error, please contact site admin.')
    
    class Meta:
        model = connections_views.ApiConnection
        fields = ['api_key', 'secret_key']

