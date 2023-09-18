from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from .forms import RegistrationForm
from portfolio.models import Portfolio


def register(request):
    """View used for user registration"""

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            portfolio_record = Portfolio(owner=user)
            portfolio_record.save()

            return HttpResponseRedirect(reverse('login'))

    else:
        form = RegistrationForm()

    context = { 
        'form': form,
    }

    return render(request, 'registration/register.html', context)