from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    url = models.URLField()
    current_price = models.FloatField()
    target_price = models.FloatField()
    in_stock = models.BooleanField(default=True)
    last_checked = models.DateTimeField(auto_now=True)
    last_alerted_price = models.FloatField(null=True, blank=True)
    next_check_time = models.DateTimeField(default=timezone.now)

class PriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField()
    checked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.price}"
    def __str__(self):
        return self.name