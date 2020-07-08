from .API.models import ProfileBan, Profile
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from functools import wraps
from django.http import HttpResponseRedirect
from django.urls import reverse

def not_platform_banned(function):
    @wraps(function)
    def is_banned(request, *args, **kwargs):
        if request.user.is_authenticated:
            profile = Profile.objects.filter(user=request.user).first()
            bans = ProfileBan.objects.filter(profile=profile, totalBan=True, banDue__gte=timezone.now())
            if len(bans) > 0 and not request.user.is_staff:
                return HttpResponseRedirect(reverse('index'))
        return function(request, *args, **kwargs)

    return is_banned

def not_exchange_banned(function):
    @wraps(function)
    def is_banned(request, *args, **kwargs):
        if request.user.is_authenticated:
            profile = Profile.objects.filter(user=request.user).first()
            bans = ProfileBan.objects.filter(profile=profile, exchangeBan=True, banDue__gte=timezone.now())
            if len(bans) > 0 and not request.user.is_staff:
                return HttpResponseRedirect(reverse('index'))
        return function(request, *args, **kwargs)

    return is_banned