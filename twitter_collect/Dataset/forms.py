from django import forms


class DatasetForm(forms.Form):
    name = forms.CharField(max_length=200)
    description = forms.CharField(max_length=500, required=False, widget=forms.Textarea)


class ConfirmationForm(forms.Form):
    for_sure = forms.BooleanField("Are you sure?")