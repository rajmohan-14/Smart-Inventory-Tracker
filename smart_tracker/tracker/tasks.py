from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail

from .models import Product, PriceHistory
from .scraper import scrape_price
from django.utils import timezone
from datetime import timedelta

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
        
        raise self.retry(exc=exc, countdown=10)


    PriceHistory.objects.create(
        product=product,
        price=new_price
    )


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
@shared_task
def cleanup_old_price_history():
    cutoff_date = timezone.now() - timedelta(days=30)

    deleted_count, _ = PriceHistory.objects.filter(
        checked_at__lt=cutoff_date
    ).delete()

    print(f"Deleted {deleted_count} old price records.")