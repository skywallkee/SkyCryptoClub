from django.contrib import admin
from .models import Update, Feature

# Register your models here.
class UpdateAdmin(admin.ModelAdmin):
    fields = ['title', 'date', 'released']

admin.site.register(Update, UpdateAdmin)

# Register your models here.
class FeatureAdmin(admin.ModelAdmin):
    fields = ['title', 'description', 'featureType', 'update']

admin.site.register(Feature, FeatureAdmin)