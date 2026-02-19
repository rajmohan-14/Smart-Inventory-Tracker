from celery import shared_task
from .models import Product, PriceHistory
from .scraper import scrape_price

@shared_task
def check_product(product_id):
    product = Product.objects.get(id=product_id)
    
    new_price = scrape_price(product.url)
    
    if new_price is None:
        return
    
    PriceHistory.objects.create(
        product=product,
        price=new_price
    )
    
    # SMART RESET LOGIC
    if new_price >= product.target_price:
        product.last_alerted_price = None
    
    elif new_price < product.target_price:
        if product.last_alerted_price is None:
            print("Send email alert 🚨")
            product.last_alerted_price = new_price
    
    product.current_price = new_price
    product.save()