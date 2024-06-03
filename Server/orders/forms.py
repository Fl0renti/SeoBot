from django import forms
from .models import Order,Profile
from datetime import datetime, timedelta


class CreateNewOrder(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateNewOrder, self).__init__(*args, **kwargs)
        now = datetime.now()
        min_time = now.strftime('%Y-%m-%dT%H:%M')

        # Set minimum date and time
        self.fields['order_schedule'].widget.attrs['min'] = min_time

    class Meta:
        model = Order
        fields = ('domain_name', 'domain_type', 'active', 'work_sec', 'avg_sec', 'num_users', 'order_schedule')
        widgets = {
            'domain_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Domain Name'}),
            'domain_type': forms.Select(attrs={'class': 'form-control'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'work_sec': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Work Duration (seconds)', 'min': 30}),
            'avg_sec': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Average Seconds per Page', 'min': 30}),
            'num_users': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Number of Users', 'min': 1}),
            'order_schedule': forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'Select Order Schedule', 'type': 'datetime-local'}),
        }


class UpdateOrder(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UpdateOrder, self).__init__(*args, **kwargs)
        now = datetime.now()
        min_time = now.strftime('%Y-%m-%dT%H:%M')

        # Set minimum date and time
        self.fields['order_schedule'].widget.attrs['min'] = min_time


    class Meta:
        model = Order
        fields = ('domain_name',  'domain_type', 'active', 'work_sec', 'avg_sec', 'num_users', 'order_schedule')
        widgets = {
            'domain_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Domain Name'}),
            'domain_type': forms.Select(attrs={'class': 'form-control'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'work_sec': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Work Duration (seconds)', 'min': 30}),
            'avg_sec': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Average Seconds per Page', 'min': 30}),
            'num_users': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Number of Users', 'min': 1}),
            'order_schedule': forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'Select Order Schedule', 'type': 'datetime-local'}),
        }

class CreateNewProfile(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("proxy","UserAgent","domain_type","serverID")
        widgets = {
            "proxy": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Proxy:user:password',"autocomplete":"off"}),
            "UserAgent": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter User Agent',"autocomplete":"off"}),
            'domain_type': forms.Select(attrs={'class': 'form-control'}),
        }
class UpdateProfiles(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("proxy","UserAgent","domain_type","serverID")
        widgets = {
            "proxy": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Proxy:user:password',"autocomplete":"off"}),
            "UserAgent": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter User Agent',"autocomplete":"off"}),
            'domain_type': forms.Select(attrs={'class': 'form-control'}),
        }


class OrderActionForm(forms.Form):
    keyword_id = forms.IntegerField(widget=forms.HiddenInput())
    order_id = forms.IntegerField(widget=forms.HiddenInput())
    action = forms.CharField()
    second_action = forms.CharField(required=False)