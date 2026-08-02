from django import forms

from .models import LeaveType


class LeaveRequestForm(forms.Form):
    leave_type = forms.ModelChoiceField(queryset=LeaveType.objects.none(), label="Type de congé")
    start_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    comment = forms.CharField(label="Commentaire", required=False, widget=forms.Textarea(attrs={"rows": 2}))

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} form-control".strip()
        self.fields["leave_type"].queryset = LeaveType.objects.all_tenants().filter(tenant=tenant, is_active=True)
