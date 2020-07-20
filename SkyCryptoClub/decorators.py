from .API.models import ProfileBan, Profile, IPBan
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

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def not_ip_banned(function):
    @wraps(function)
    def is_banned(request, *args, **kwargs):
        ipAddress = get_client_ip(request)
        ban = IPBan.objects.filter(ipAddress=ipAddress).first() 
        banned = False
        if ban and (ban.permanent or ban.due > timezone.now()):
            banned = True
            if request.user.is_authenticated and request.user.is_staff:
                banned = False
        if banned:
            return HttpResponseRedirect(reverse('ip-banned-page'))
        return function(request, *args, **kwargs)
    return is_banned

def ip_banned(function):
    @wraps(function)
    def is_banned(request, *args, **kwargs):
        ipAddress = get_client_ip(request)
        ban = IPBan.objects.filter(ipAddress=ipAddress).first() 
        banned = False
        if ban and (ban.permanent or ban.due > timezone.now()):
            banned = True
            if request.user.is_authenticated and request.user.is_staff:
                banned = False
        if banned:
            return function(request, *args, **kwargs)
        return HttpResponseRedirect(reverse('index'))
    return is_banned