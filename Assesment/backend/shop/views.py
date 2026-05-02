from django.shortcuts import render
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product

@api_view(['POST'])
def purchase(request):
    product_id = request.data.get('product_id')

    try:
        with transaction.atomic():
            product = Product.objects.select_for_update().get(id=product_id)

            if product.stock > 0:
                product.stock -= 1
                product.save()
                return Response({"message": "Purchase successful"})
            else:
                return Response({"error": "Out of stock"}, status=400)

    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)
