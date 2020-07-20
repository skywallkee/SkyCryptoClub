from django.shortcuts import render, redirect
from ratelimit.decorators import ratelimit
from django.template import loader
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.core.paginator import Paginator

from .models import Update, Feature

@ratelimit(block=True, key='ip', rate='20/m')
def released(request):
    return redirect('/changelog/1/')

@ratelimit(block=True, key='ip', rate='20/m')
def upcoming(request):
    return redirect('/changelog/upcoming/1/')

@ratelimit(block=True, key='ip', rate='20/m')
def changelogs(request, page):
    template    = loader.get_template('ChangeLog/index.html')

    updates = []

    released = 'upcoming' not in request.path
    for update in Update.objects.filter(released=released):
        features = Feature.objects.filter(update=update)
        new_features = features.filter(featureType='NEW')
        improved_features = features.filter(featureType='IMPROVED')
        fixed_features = features.filter(featureType='FIXED')
        removed_features = features.filter(featureType='REMOVED')
        other_features = features.difference(new_features).difference(improved_features).difference(fixed_features).difference(removed_features)
        updates.append(
            {
                'update': update,
                'features': {
                    'new': new_features,
                    'improved': improved_features,
                    'fixed': fixed_features,
                    'removed': removed_features,
                    'others': other_features,
                }
            }
        )

    displayPerPage = 5
    paginator = Paginator(updates, displayPerPage)

    totalPages = paginator.num_pages

    if page <= 0 or page > totalPages:
        return redirect('/changelog/1/')

    startPagination = max(page - 2, 1)
    endPagination = min(totalPages, startPagination + 4) + 1
    pages = [i for i in range(startPagination, endPagination)]
    canNext = paginator.page(page).has_next()
    canPrevious = paginator.page(page).has_previous()
    updates = paginator.page(page).object_list

    context = {'currentPage': page, 'updates': updates, 'pages': pages,
                'canNext': canNext, 'canPrevious': canPrevious, 'totalPages': totalPages}
    return HttpResponse(template.render(context, request))