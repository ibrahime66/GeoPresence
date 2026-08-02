from django import forms

from .models import Attendance


class ClockForm(forms.Form):
    clock_type = forms.ChoiceField(choices=Attendance.ClockType.choices)
    latitude = forms.DecimalField(max_digits=10, decimal_places=7)
    longitude = forms.DecimalField(max_digits=10, decimal_places=7)
    gps_accuracy = forms.DecimalField(max_digits=8, decimal_places=2, required=False)
    is_gps_mocked = forms.BooleanField(required=False)
    client_time = forms.DateTimeField(required=False)
    photo = forms.ImageField()
