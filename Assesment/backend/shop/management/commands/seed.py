# shop/management/commands/seed.py
"""
Seed script for Challenge 02: Big Data Aggregation & Query Optimization
Populates database with 100,000 dummy transaction records from last 6 months
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from shop.models import Product, Order, OrderItem
import random

class Command(BaseCommand):
    help = 'Seed database with 100k dummy transaction records from last 6 months'

    def add_arguments(self, parser):
        parser.add_argument(
            '--products',
            type=int,
            default=100,
            help='Number of products to create'
        )
        parser.add_argument(
            '--orders',
            type=int,
            default=100000,
            help='Number of order items to create'
        )

    def handle(self, *args, **options):
        products_count = options['products']
        orders_count = options['orders']
        
        self.stdout.write(self.style.SUCCESS('Starting data seeding...'))
        
        # Step 1: Create Products
        self.stdout.write(f'Creating {products_count} products...')
        products = []
        
        # Clear existing products
        Product.objects.all().delete()
        
        for i in range(products_count):
            product = Product.objects.create(
                name=f"Product {i+1}",
                stock=random.randint(50, 500),
                price=round(random.uniform(10, 1000), 2)
            )
            products.append(product)
            
            if (i + 1) % 10000 == 0:
                self.stdout.write(f'  Created {i+1}/{products_count} products')
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {products_count} products'))
        
        # Step 2: Create Orders and OrderItems
        self.stdout.write(f'Creating {orders_count} order items from last 6 months...')
        
        # Clear existing orders
        Order.objects.all().delete()
        
        six_months_ago = timezone.now() - timedelta(days=180)
        
        # Batch create for performance
        order_items = []
        created_orders = 0
        
        for i in range(orders_count):
            # Create or get an order (simulate multiple items per order)
            order_created = i % 5 == 0  # Every 5 items = new order
            
            if order_created:
                # Random timestamp within last 6 months
                random_days = random.randint(0, 180)
                random_hours = random.randint(0, 23)
                random_minutes = random.randint(0, 59)
                
                order_date = six_months_ago + timedelta(
                    days=random_days,
                    hours=random_hours,
                    minutes=random_minutes
                )
                
                order = Order.objects.create(
                    status='completed',
                    total_amount=0,
                    created_at=order_date
                )
                created_orders += 1
            
            # Create order item
            product = random.choice(products)
            quantity = random.randint(1, 10)
            unit_price = product.price
            subtotal = quantity * unit_price
            
            order_item = OrderItem(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=subtotal
            )
            order_items.append(order_item)
            
            # Update order total
            order.total_amount += subtotal
            order.save()
            
            # Batch insert for performance
            if len(order_items) % 5000 == 0:
                OrderItem.objects.bulk_create(order_items)
                self.stdout.write(f'  Created {i+1}/{orders_count} order items ({created_orders} orders)')
                order_items = []
        
        # Insert remaining items
        if order_items:
            OrderItem.objects.bulk_create(order_items)
        
        self.stdout.write(self.style.SUCCESS(
            f'✓ Created {orders_count} order items across {created_orders} orders'
        ))
        
        # Summary statistics
        total_revenue = sum(
            item.subtotal for item in OrderItem.objects.all()
        )
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('SEEDING COMPLETE'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'Total Products: {Product.objects.count()}')
        self.stdout.write(f'Total Orders: {Order.objects.count()}')
        self.stdout.write(f'Total Order Items: {OrderItem.objects.count()}')
        self.stdout.write(f'Total Revenue: ${total_revenue:,.2f}')
        self.stdout.write(self.style.SUCCESS('='*60))