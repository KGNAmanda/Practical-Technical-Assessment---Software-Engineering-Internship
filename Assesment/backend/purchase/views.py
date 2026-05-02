from django.shortcuts import render
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from shop.models import Product, Order, OrderItem
from purchase.models import Purchase
from django.db.models import Sum, F, Count
from django.utils import timezone
from datetime import timedelta

@api_view(['POST'])
def purchase(request):
    """
    Challenge 01: High-Concurrency Management
    POST /api/purchase/ - Purchase a product with stock management
    Handles concurrent requests ensuring stock never goes below zero
    """
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity', 1)

    try:
        quantity = int(quantity)
        if quantity <= 0:
            return Response(
                {"error": "Quantity must be positive"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            # Use select_for_update() for row-level locking to prevent race conditions
            product = Product.objects.select_for_update().get(id=product_id)

            if product.stock >= quantity:
                product.stock -= quantity
                product.save()
                
                # Record the purchase
                purchase_record = Purchase.objects.create(
                    product=product,
                    quantity=quantity
                )
                
                return Response({
                    "message": "Purchase successful",
                    "purchase_id": purchase_record.id,
                    "product_name": product.name,
                    "quantity": quantity,
                    "remaining_stock": product.stock
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "error": f"Insufficient stock. Available: {product.stock}, Requested: {quantity}"
                }, status=status.HTTP_400_BAD_REQUEST)

    except Product.DoesNotExist:
        return Response(
            {"error": "Product not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def checkout(request):
    """
    Challenge 03: Mini POS System
    POST /api/checkout/ - Process complete checkout with transactional integrity
    Uses transaction.atomic() to ensure all-or-nothing order processing
    """
    items = request.data.get('items', [])
    
    if not items:
        return Response(
            {"error": "Cart is empty"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        with transaction.atomic():
            # Create the order
            order = Order.objects.create(status='pending')
            total_amount = 0
            
            # Process each item in the cart
            for item in items:
                product_id = item.get('product_id')
                quantity = item.get('quantity', 1)
                
                # Get product with row-level lock
                product = Product.objects.select_for_update().get(id=product_id)
                
                # Check stock availability
                if product.stock < quantity:
                    raise ValueError(
                        f"Insufficient stock for {product.name}. "
                        f"Available: {product.stock}, Requested: {quantity}"
                    )
                
                # Deduct stock
                product.stock -= quantity
                product.save()
                
                # Calculate subtotal
                subtotal = product.price * quantity
                total_amount += subtotal
                
                # Create order item
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=product.price,
                    subtotal=subtotal
                )
            
            # Update order total
            order.total_amount = total_amount
            order.status = 'completed'
            order.save()
            
            return Response({
                "message": "Checkout successful",
                "order_id": order.id,
                "total_amount": order.total_amount,
                "items_count": len(items),
                "status": order.status
            }, status=status.HTTP_201_CREATED)
            
    except Product.DoesNotExist:
        return Response(
            {"error": "One or more products not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except ValueError as e:
        # Transaction will be rolled back automatically
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def analytics(request):
    """
    Challenge 02: Big Data Aggregation & Query Optimization
    GET /api/analytics/ - Returns daily revenue for 30 days and top 5 products
    Optimized to respond in under 500ms using database-level aggregation
    """
    try:
        # Get last 30 days data
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # Daily revenue aggregation using Django ORM (executed at DB level)
        daily_revenue = (
            OrderItem.objects
            .filter(order__created_at__gte=thirty_days_ago, order__status='completed')
            .extra(select={'day': 'DATE(created_at)'})
            .values('day')
            .annotate(revenue=Sum(F('subtotal')))
            .order_by('day')
        )
        
        # Top 5 products by quantity sold
        top_products = (
            OrderItem.objects
            .filter(order__created_at__gte=thirty_days_ago, order__status='completed')
            .values('product__id', 'product__name', 'product__price')
            .annotate(
                total_quantity=Sum('quantity'),
                total_revenue=Sum(F('subtotal'))
            )
            .order_by('-total_quantity')[:5]
        )
        
        # Calculate total revenue for the period
        total_revenue_period = sum(item['revenue'] for item in daily_revenue) if daily_revenue else 0
        
        return Response({
            "period": "Last 30 days",
            "total_revenue": total_revenue_period,
            "daily_revenue": list(daily_revenue),
            "top_5_products": list(top_products),
            "data_points": len(list(daily_revenue))
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_products(request):
    """
    GET /api/products/ - Get all available products for POS interface
    """
    products = Product.objects.all().values('id', 'name', 'price', 'stock')
    return Response({
        "products": list(products),
        "count": len(list(products))
    })


def home(request):
    from django.http import JsonResponse
    return JsonResponse({
        "message": "Purchase API working...",
        "endpoints": {
            "purchase": "/api/purchase/ (POST)",
            "checkout": "/api/checkout/ (POST)",
            "analytics": "/api/analytics/ (GET)",
            "products": "/api/products/ (GET)"
        }
    })