from django import forms
from twitter_collect.Sentiment_Tag.models import LANGUAGES
from twitter_collect.Dataset.models import Dataset


class SearchForm(forms.Form):
    query = forms.CharField()
    language = forms.ChoiceField(choices=LANGUAGES)
    max_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    since_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    count = forms.ChoiceField(choices=((i, i) for i in range(10, 110, 10)))


class DatasetForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(DatasetForm, self).__init__(*args, **kwargs)
        self.fields['dataset'] = forms.ModelChoiceField(queryset=Dataset.objects.all())