from django import forms
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm


class BootstrapFormMixin:
    """Ajoute la classe Bootstrap `form-control` à tous les champs — évite
    d'avoir à le refaire dans chaque template avec django-widget-tweaks."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} form-control".strip()


class LoginForm(BootstrapFormMixin, forms.Form):
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={"autofocus": True, "autocomplete": "email"}),
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()


class PasswordResetRequestForm(BootstrapFormMixin, forms.Form):
    email = forms.EmailField(label="E-mail", widget=forms.EmailInput(attrs={"autofocus": True}))

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()


class BootstrapSetPasswordForm(BootstrapFormMixin, SetPasswordForm):
    pass


class BootstrapPasswordChangeForm(BootstrapFormMixin, PasswordChangeForm):
    pass
