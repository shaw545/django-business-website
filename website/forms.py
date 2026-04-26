from django import forms
from .models import Product


class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={"multiple": True}))
        super().__init__(*args, **kwargs)


class ProductForm(forms.ModelForm):
    extra_images = MultipleFileField(required=False)

    class Meta:
        model = Product
        exclude = ["seller"]