from django import forms


def apply_module_gating(form, tenant, gated_fields):
    """Retire du formulaire les champs dont le module organisation associé
    est désactivé — ex. {"position": "positions_enabled"}. Contrairement à un
    simple masquage en template, un champ retiré ici est aussi ignoré côté
    validation : impossible de le renseigner malgré tout via une requête
    forgée pendant que le module est désactivé pour cette organisation."""
    if tenant is None:
        return
    from apps.tenants.org_settings import get_org_setting

    for field_name, setting_key in gated_fields.items():
        if field_name in form.fields and not get_org_setting(tenant, setting_key):
            del form.fields[field_name]


class BootstrapModelFormMixin:
    """Ajoute les classes Bootstrap adaptées à chaque type de widget."""

    CHECK_WIDGETS = (forms.CheckboxInput, forms.CheckboxSelectMultiple, forms.RadioSelect)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = "form-check-input" if isinstance(field.widget, self.CHECK_WIDGETS) else "form-control"
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} {css_class}".strip()
