from django.db import models
from shop.models import Product

class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['purchased_at']),
        ]

    def __str__(self):
        return f"Purchase of {self.product.name} x {self.quantity}"
