from django import forms

from .models import Attendance


class ClockForm(forms.Form):
    clock_type = forms.ChoiceField(choices=Attendance.ClockType.choices)
    latitude = forms.DecimalField(max_digits=10, decimal_places=7)
    longitude = forms.DecimalField(max_digits=10, decimal_places=7)
    gps_accuracy = forms.DecimalField(max_digits=8, decimal_places=2, required=False)
    is_gps_mocked = forms.BooleanField(required=False)
    client_time = forms.DateTimeField(required=False)
    # CDC §9.7 : renseigné par le client lors de la synchronisation d'un
    # pointage mis en file d'attente hors ligne (IndexedDB) — absent en
    # fonctionnement normal (mode ONLINE implicite).
    mode = forms.ChoiceField(choices=Attendance.Mode.choices, required=False)
