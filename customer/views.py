from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CustomerProfile
from partner.models import Product, Order
from django.contrib import messages

@login_required
def customer_home(request):
    products = Product.objects.all()
    return render(request, 'customer/home.html', {'products': products})

@login_required
def place_order(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        Order.objects.create(customer=request.user, product=product, quantity=quantity)
        messages.success(request, "Buyurtma muvaffaqiyatli qabul qilindi!")
        return redirect('customer_home')
    return render(request, 'customer/place_order.html', {'product': product})

def customer_home(request):
    return render(request, 'customer/home.html')
