from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
class StaticViewSitemap(Sitemap):
    def items(self):
        return ['index', 'faq', 'terms', 'contact', 'login', 'register', 'recover-password']
    def location(self, item):
        return reverse(item)