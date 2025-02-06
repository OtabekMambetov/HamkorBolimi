from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Product, Order

@login_required
def partner_home(request):
    products = Product.objects.filter(partner=request.user)
    return render(request, 'partner/home.html', {'products': products})

@login_required
def partner_statistics(request):
    products = Product.objects.filter(partner=request.user)
    orders = Order.objects.filter(product__in=products)
    return render(request, 'partner/statistics.html', {'orders': orders})

def partner_home(request):
    return render(request, 'partner/home.html')

