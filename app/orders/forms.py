from django import forms
from django.forms import BaseFormSet, formset_factory


class RequestItemForm(forms.Form):
    item_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            "class": "input input-bordered w-full",
            "placeholder": 'What do you want made? e.g. "Dragon figurine"',
        }),
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "textarea textarea-bordered w-full",
            "rows": 2,
            "placeholder": "Size, color, material… (optional)",
        }),
    )
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={"class": "input input-bordered w-full", "min": 1}),
    )
    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "file-input file-input-bordered w-full"}),
    )
    reference_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            "class": "input input-bordered w-full",
            "placeholder": "Link to Makerworld, Thingiverse, etc. (optional)",
        }),
    )

    def clean(self):
        cleaned = super().clean()
        # Skip validation entirely for a fully-blank extra row.
        if not any(cleaned.get(f) for f in ("item_name", "description", "image", "reference_url")):
            self.cleaned_data = {}
            self.errors.clear()
        return cleaned


class BaseRequestItemFormSet(BaseFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        filled = [f for f in self.forms if f.cleaned_data.get("item_name")]
        if not filled:
            raise forms.ValidationError("Add at least one item to your request.")


RequestItemFormSet = formset_factory(
    RequestItemForm,
    formset=BaseRequestItemFormSet,
    extra=1,
)
