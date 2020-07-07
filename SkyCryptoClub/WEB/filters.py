import django_filters
from ..API.models import Exchange, PlatformCurrency
from django import forms

class ExchangeFilter(django_filters.FilterSet):
    from_currency = django_filters.ModelChoiceFilter(empty_label='From Currency', field_name='from_currency', queryset=PlatformCurrency.objects.all(),
                                                  widget=forms.Select(attrs={'class': 'col-12 col-xl-6 selectpicker', 'data-style':"select-with-transition", 'data-size':"5"}))

    to_currency = django_filters.ModelChoiceFilter(empty_label='To Currency', field_name='to_currency', queryset=PlatformCurrency.objects.all(),
                                                  widget=forms.Select(attrs={'class': 'col-12 col-xl-6 selectpicker', 'data-style':"select-with-transition", 'data-size':"5"}))

    min_requested = django_filters.NumberFilter(field_name='from_amount', lookup_expr='gte', label="Min Requested",
                                                  widget=forms.NumberInput(attrs={'class': 'form-control', 'step': "0.00000001", 'min':"0"}))

    max_requested = django_filters.NumberFilter(field_name='from_amount', lookup_expr='lte', label="Max Requested",
                                                  widget=forms.NumberInput(attrs={'class': 'form-control', 'step': "0.00000001", 'min':"0"}))

    min_given = django_filters.NumberFilter(field_name='to_amount', lookup_expr='gte', label="Min Given",
                                                  widget=forms.NumberInput(attrs={'class': 'form-control', 'step': "0.00000001", 'min':"0"}))

    max_given = django_filters.NumberFilter(field_name='to_amount', lookup_expr='lte', label="Max Given",
                                                  widget=forms.NumberInput(attrs={'class': 'form-control', 'step': "0.00000001", 'min':"0"}))

    class Meta:
        model = Exchange
        fields = []