from django.shortcuts import render, redirect
from ratelimit.decorators import ratelimit
from django.template import loader
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from ..API.views import valid_captcha, get_user_language, get_client_ip
from ..MESSAGES import MESSAGES

from .models import Update, Feature, FeatureRequest

@ratelimit(block=True, key='ip', rate='20/m')
@require_http_methods(["GET"])
def released(request):
    return redirect('/changelog/1/')

@ratelimit(block=True, key='ip', rate='20/m')
@require_http_methods(["GET"])
def upcoming(request):
    return redirect('/changelog/upcoming/1/')

@ratelimit(block=True, key='ip', rate='20/m')
@require_http_methods(["GET"])
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

    
@ratelimit(block=True, key='ip', rate='10/m')
@require_http_methods(["GET", "POST"])
def request(request):
    template    = loader.get_template('ChangeLog/request.html')
    context = {'messages': []}
    if request.method == "POST":
        if valid_captcha(request):
            message = request.POST.get('featureSummary')
            if not message or len(message) < 30:
                context['messages'].append(MESSAGES[get_user_language(request).name]["FEATURE_REQUEST"]["FAIL"]["ELABORATE"])
            else:
                user_ip = get_client_ip(request)
                current_date = timezone.now() - timezone.timedelta(hours=24)
                user_requests = FeatureRequest.objects.filter(date__gte=current_date)
                if len(user_requests) > 5:
                    context['messages'].append(MESSAGES[get_user_language(request).name]["FEATURE_REQUEST"]["FAIL"]["TOO_MANY"])
                else:
                    FeatureRequest.objects.create(summary=message, requested_by=user_ip)
                    context['messages'].append(MESSAGES[get_user_language(request).name]["FEATURE_REQUEST"]["SUCCESS"])
        else:
            context['messages'].append(MESSAGES[get_user_language(request).name]["CAPTCHA"]["FAIL"])
    return HttpResponse(template.render(context, request))