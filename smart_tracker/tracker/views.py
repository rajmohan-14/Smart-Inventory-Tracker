from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Product
from .models import PriceHistory
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg
from django.db.models.functions import TruncDay

@login_required
def product_detail(request, product_id):
    product = Product.objects.get(id=product_id, user=request.user)

    range_option = request.GET.get('range', '1d')

    now = timezone.now()

    if range_option == '1h':
        start_time = now - timedelta(hours=1)
        history = PriceHistory.objects.filter(
            product=product,
            checked_at__gte=start_time
        ).order_by('checked_at')

        dates = [h.checked_at.strftime("%H:%M") for h in history]
        prices = [h.price for h in history]

    elif range_option == '1m':
        start_time = now - timedelta(days=30)

        history = (
            PriceHistory.objects
            .filter(product=product, checked_at__gte=start_time)
            .annotate(day=TruncDay('checked_at'))
            .values('day')
            .annotate(avg_price=Avg('price'))
            .order_by('day')
        )

        dates = [h['day'].strftime("%Y-%m-%d") for h in history]
        prices = [h['avg_price'] for h in history]

    else:  # Default 1 day
        start_time = now - timedelta(days=1)
        history = PriceHistory.objects.filter(
            product=product,
            checked_at__gte=start_time
        ).order_by('checked_at')

        dates = [h.checked_at.strftime("%H:%M") for h in history]
        prices = [h.price for h in history]

    context = {
        'product': product,
        'dates': dates,
        'prices': prices,
        'selected_range': range_option
    }

    return render(request, 'tracker/product_detail.html', context)
@login_required
def product_detail(request, product_id):
    product = Product.objects.get(id=product_id, user=request.user)
    history = PriceHistory.objects.filter(product=product).order_by('checked_at')

    dates = [entry.checked_at.strftime("%Y-%m-%d %H:%M") for entry in history]
    prices = [entry.price for entry in history]

    context = {
        'product': product,
        'dates': dates,
        'prices': prices
    }

    return render(request, 'tracker/product_detail.html', context)

@login_required
def dashboard(request):
    products = Product.objects.filter(user=request.user)
    return render(request, 'tracker/dashboard.html', {'products': products})


@login_required
def add_product(request):
    if request.method == "POST":
        name = request.POST.get('name')
        url = request.POST.get('url')
        target_price = request.POST.get('target_price')

        Product.objects.create(
            user=request.user,
            name=name,
            url=url,
            target_price=target_price,
            current_price=0
        )

        return redirect('dashboard')

    return render(request, 'tracker/add_product.html')
