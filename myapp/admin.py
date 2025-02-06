from django.contrib import admin
from .models import Partner, Product, Category


class PartnerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'company_name', 'is_approved')
    search_fields = ('full_name', 'company_name')
    list_filter = ('is_approved',)
    list_editable = ('is_approved',)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'partner', 'price')
    search_fields = ('name', 'partner__company_name')
    list_filter = ('partner',)

admin.site.register(Category)
admin.site.register(Partner, PartnerAdmin)
admin.site.register(Product, ProductAdmin)
