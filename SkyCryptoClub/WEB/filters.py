import django_filters
from ..API.models import Exchange, PlatformCurrency, FoundDeposit, Account, Profile, Withdrawal, \
                         SupportCategory, SupportTicket, Question, FAQCategory
from django import forms
from django_filters.widgets import RangeWidget

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

class DepositFilter(django_filters.FilterSet):

    tipId = django_filters.CharFilter(field_name='tipId', widget=forms.TextInput(attrs={'class': 'form-control'}), lookup_expr='contains')

    account = django_filters.ModelChoiceFilter(empty_label='Account', field_name='account', queryset=Account.objects.all(), 
                                                widget=forms.Select(attrs={'class': 'col-12 col-xl-6 selectpicker', 'data-style':"select-with-transition", 'data-size':"5"}))

    class Meta:
        model = FoundDeposit
        fields = []

    def __init__(self, *args, **kwargs):
        self.profile = kwargs.pop('profile')
        super(DepositFilter, self).__init__(*args, **kwargs)
        self.filters["account"].queryset = Account.objects.filter(profile=self.profile)


class WithdrawFilter(django_filters.FilterSet):
    tipId = django_filters.CharFilter(field_name='tipId', widget=forms.TextInput(attrs={'class': 'form-control'}), lookup_expr='contains')

    account = django_filters.ModelChoiceFilter(empty_label='Account', field_name='account', queryset=Account.objects.all(), 
                                                widget=forms.Select(attrs={'class': 'col-12 col-xl-6 selectpicker', 'data-style':"select-with-transition", 'data-size':"5"}))

    class Meta:
        model = Withdrawal
        fields = []

    def __init__(self, *args, **kwargs):
        self.profile = kwargs.pop('profile')
        super(WithdrawFilter, self).__init__(*args, **kwargs)
        self.filters["account"].queryset = Account.objects.filter(profile=self.profile)


class TicketsFilter(django_filters.FilterSet):
    category = django_filters.ModelMultipleChoiceFilter(field_name='category', queryset=SupportCategory.objects.all(), 
                                                widget=forms.SelectMultiple(attrs={'class': 'col-12 selectpicker', 'data-style':"select-with-transition", 'data-size':"5"}))

    date_range = django_filters.DateFromToRangeFilter(field_name='created_at', widget=RangeWidget(attrs={'type': 'date', 'class': 'col-12 col-lg-6 form-control datetime'}))

    class Meta:
        model = SupportTicket
        fields = []
        

class FAQFilter(django_filters.FilterSet):
    category = django_filters.ModelMultipleChoiceFilter(field_name='category', queryset=FAQCategory.objects.all(), 
                                                widget=forms.SelectMultiple(attrs={'class': 'col-12 selectpicker', 'data-style':"select-with-transition", 'data-size':"5"}))

    class Meta:
        model = Question
        fields = []

    def __init__(self, *args, **kwargs):
        super(FAQFilter, self).__init__(*args, **kwargs)
        self.filters["category"].queryset = self.filters["category"].queryset.order_by('order')