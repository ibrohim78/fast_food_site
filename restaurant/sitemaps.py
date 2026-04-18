from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product

class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Product.objects.filter(is_available=True)

    def lastmod(self, obj):
        return None

    def location(self, obj):
        return reverse('restaurant:menu')

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            "restaurant:home",
            "restaurant:menu",
            "restaurant:about",
            "restaurant:contact",
            "restaurant:order",
            "restaurant:reservation",
            "restaurant:cart",
        ]

    def location(self, item):
        return reverse(item)
