from django import forms

from .models import Service


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            "tags",
            "name",
            "slug",
            "short_description",
            "description",
            "price",
            "is_price_variable",
            "estimated_days",
            "image",
            "focal_x",
            "focal_y",
            "is_featured",
            "is_active",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "short_description": forms.Textarea(attrs={"rows": 2}),
            "focal_x": forms.HiddenInput(),
            "focal_y": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["price"].required = False
        self.fields["tags"].required = False

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("is_price_variable") and not cleaned.get("price"):
            from decimal import Decimal
            cleaned["price"] = Decimal("0.00")
        return cleaned
