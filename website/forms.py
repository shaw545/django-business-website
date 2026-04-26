from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group

from .models import Product


class SellerRegistrationForm(UserCreationForm):
    SELLER_TYPE_CHOICES = [
        ("personal", "Personal Seller"),
        ("business", "Business Seller"),
    ]

    seller_type = forms.ChoiceField(
        choices=SELLER_TYPE_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        label="Seller Type"
    )

    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "seller_type",
            "password1",
            "password2",
        ]

    def save(self, commit=True):
        user = super().save(commit=False)

        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()

            seller_type = self.cleaned_data.get("seller_type")

            if seller_type == "business":
                group, created = Group.objects.get_or_create(name="Business Sellers")
            else:
                group, created = Group.objects.get_or_create(name="Personal Sellers")

            user.groups.add(group)

        return user


class ProductForm(forms.ModelForm):
    extra_images = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            "multiple": True,
        })
    )

    class Meta:
        model = Product
        exclude = ["seller"]