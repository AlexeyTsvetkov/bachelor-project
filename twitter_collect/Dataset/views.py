from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage

from twitter_collect.Dataset.models import Dataset
from twitter_collect.Sentiment_Tag.models import Tweet
from twitter_collect.Dataset.forms import DatasetForm, ConfirmationForm


def list_datasets(request):
    datasets = Dataset.objects.all()

    return render(request, 'Dataset/list_datasets.html', {'datasets': datasets})


def create_dataset(request):
    if request.method == 'POST':
        form = DatasetForm(request.POST)
        if form.is_valid():
            dataset = Dataset()
            dataset.name = form.cleaned_data['name']
            dataset.description = form.cleaned_data['description']
            dataset.save()

            return HttpResponseRedirect(reverse('list_datasets'))
    else:
        form = DatasetForm()

    return render(request, 'Dataset/create_dataset.html', {'form': form})


def delete_dataset(request, id):
    if request.method == 'POST':
        form = ConfirmationForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['for_sure']:
                dataset = Dataset.objects.get(id=id)
                dataset.delete()
            return HttpResponseRedirect(reverse('list_datasets'))
    else:
        form = ConfirmationForm()

    dataset = Dataset.objects.get(id=id)

    return render(request, 'Dataset/delete_dataset.html',
                  {'form': form,
                   'dataset': dataset})


def view_dataset(request, id):
    dataset = Dataset.objects.get(id=id)
    tweets_list = Tweet.objects.filter(dataset=dataset)
    paginator = Paginator(tweets_list, 25)

    page = request.GET.get('page')

    try:
        tweets = paginator.page(page)
    except InvalidPage:
        tweets = paginator.page(1)

    return render(request, 'Dataset/view_dataset.html', {'dataset': dataset, 'tweets': page})


def export_dataset(request):
    pass


def add_tweet_to_dataset(request, dataset_id):
    pass