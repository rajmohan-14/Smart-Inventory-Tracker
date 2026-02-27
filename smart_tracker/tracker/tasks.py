from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail

from .models import Product, PriceHistory
from .scraper import scrape_price


def calculate_next_interval(product, new_price):
    distance = new_price - product.target_price

    if distance > product.target_price * 0.3:
        return timedelta(hours=6)
    elif distance > product.target_price * 0.1:
        return timedelta(hours=2)
    elif distance > 0:
        return timedelta(minutes=15)
    else:
        return timedelta(minutes=10)


@shared_task(bind=True, max_retries=3)
def check_product(self, product_id):
    try:
        product = Product.objects.get(id=product_id)
        new_price = scrape_price(product.url)

        if new_price is None:
            raise Exception("Scraping failed")

    except Exception as exc:
        # Retry after 10 seconds
        raise self.retry(exc=exc, countdown=10)

    # Save price history
    PriceHistory.objects.create(
        product=product,
        price=new_price
    )

    # SMART RESET LOGIC
    if new_price >= product.target_price:
        product.last_alerted_price = None

    elif new_price < product.target_price:
        if product.last_alerted_price is None:
            send_mail(
                subject="Price Drop Alert 🚨",
                message=f"{product.name} is now ₹{new_price}",
                from_email=None,
                recipient_list=[product.user.email],
            )
            product.last_alerted_price = new_price

    # Adaptive scheduling
    interval = calculate_next_interval(product, new_price)
    product.next_check_time = timezone.now() + interval

    product.current_price = new_price
    product.save()


@shared_task
def check_all_products():
    products = Product.objects.filter(
        next_check_time__lte=timezone.now()
    )

    for product in products:
        check_product.delay(product.id)