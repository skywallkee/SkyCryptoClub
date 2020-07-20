from django.contrib import admin
from .models import Update, Feature, FeatureRequest


class UpdateAdmin(admin.ModelAdmin):
    fields = ['title', 'date', 'released']

admin.site.register(Update, UpdateAdmin)


class FeatureAdmin(admin.ModelAdmin):
    fields = ['title', 'description', 'featureType', 'update']

admin.site.register(Feature, FeatureAdmin)


class FeatureRequestAdmin(admin.ModelAdmin):
    fields = ['summary', 'requested_by', 'date']

admin.site.register(FeatureRequest, FeatureRequestAdmin)