from django import forms
from models import Account
from models import Feature
from models import Webhook


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ("name",)


class FeatureForm(forms.ModelForm):
    class Meta:
        model = Feature
        fields = ("name", "permission_type", "permission_level", "boolean_permission",
                  "limit_permission")


class WebhookForm(forms.ModelForm):
    class Meta:
        model = Webhook
        fields = ("type", "is_active", "param1", "param2", "param3", "param4", "param5")

