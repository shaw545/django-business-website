from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Product


class SellerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    agree_terms = forms.BooleanField(
        required=True,
        label="I agree to the Terms and Conditions"
    )

    agree_privacy = forms.BooleanField(
        required=True,
        label="I agree to the Privacy Policy"
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
            "agree_terms",
            "agree_privacy",
        ]


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        return single_file_clean(data, initial)


class ProductForm(forms.ModelForm):
    extra_images = MultipleFileField(required=False)

    class Meta:
        model = Product
        fields = [
            "category",
            "name",
            "description",
            "price_sle",
            "price_usd",
            "image",
            "available",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "price_sle": forms.NumberInput(attrs={"class": "form-control"}),
            "price_usd": forms.NumberInput(attrs={"class": "form-control"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "available": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }