from django import forms
from models import Account
from models import Feature


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ("name",)


class FeatureForm(forms.ModelForm):
    class Meta:
        model = Feature
        fields = ("name", "permission_type", "permission_level", "boolean_permission",
                  "limit_permission")

