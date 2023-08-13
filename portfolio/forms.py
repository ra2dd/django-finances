from django import forms

from django.core.exceptions import ValidationError
from .views import connections_views
from .tasks import client_tasks

class AddConnectionModelForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        # data = (self.cleaned_data['api_key'], self.cleaned_data['secret_key'])
        api_key_data = cleaned_data['api_key']
        secret_key_data = cleaned_data['secret_key']

        if client_tasks.check_binance_connection(api_key_data, secret_key_data) == False:
            raise ValidationError('Error connecting with given api data, please check if api key and secret key are correct.')
    
    class Meta:
        model = connections_views.ApiConnection
        fields = ['api_key', 'secret_key']

