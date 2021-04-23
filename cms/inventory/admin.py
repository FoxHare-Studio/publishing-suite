from django.contrib import admin

from .models import Catalog, Product, ProductSet

admin.site.register(Catalog)
admin.site.register(Product)
admin.site.register(ProductSet)
