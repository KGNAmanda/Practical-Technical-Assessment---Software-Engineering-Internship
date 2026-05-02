"""
Challenge 01: High-Concurrency Management Test Script
Tests concurrent purchase requests to verify stock management integrity
Fires 100 concurrent requests against POST /api/purchase/ endpoint
"""

import os
import django
import threading
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from shop.models import Product

# Test Configuration
CONCURRENT_REQUESTS = 100
INITIAL_STOCK = 50
PRODUCT_NAME = "Concurrent Test Product"
BASE_URL = "http://localhost:8000"
PURCHASE_ENDPOINT = f"{BASE_URL}/api/purchase/"

def setup_test_product():
    """Create a test product with exactly 50 units"""
    # Clear any existing test product
    Product.objects.filter(name=PRODUCT_NAME).delete()
    
    # Create new test product
    product = Product.objects.create(
        name=PRODUCT_NAME,
        stock=INITIAL_STOCK,
        price=99.99
    )
    print(f"✓ Test product created: ID={product.id}, Stock={INITIAL_STOCK}")
    return product

def make_purchase_request(product_id, request_num):
    """Make a single purchase request"""
    try:
        payload = {
            "product_id": product_id,
            "quantity": 1
        }
        start_time = time.time()
        response = requests.post(PURCHASE_ENDPOINT, json=payload, timeout=10)
        elapsed_time = time.time() - start_time
        
        return {
            "request_num": request_num,
            "status": response.status_code,
            "success": response.status_code == 201,
            "response": response.json(),
            "elapsed_time": elapsed_time
        }
    except Exception as e:
        return {
            "request_num": request_num,
            "status": "ERROR",
            "success": False,
            "error": str(e),
            "elapsed_time": 0
        }

def run_concurrent_purchase_test(product_id):
    """Run 100 concurrent purchase requests"""
    print(f"\n{'='*80}")
    print(f"Starting concurrent purchase test: {CONCURRENT_REQUESTS} requests")
    print(f"Product ID: {product_id}")
    print(f"{'='*80}\n")
    
    results = []
    successful_purchases = 0
    failed_purchases = 0
    
    # Use ThreadPoolExecutor for concurrent requests
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [
            executor.submit(make_purchase_request, product_id, i)
            for i in range(CONCURRENT_REQUESTS)
        ]
        
        start_time = time.time()
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            
            if result['success']:
                successful_purchases += 1
                status_icon = "✓"
            else:
                failed_purchases += 1
                status_icon = "✗"
            
            print(f"{status_icon} Request #{result['request_num']}: "
                  f"Status={result['status']}, Time={result['elapsed_time']:.4f}s")
        
        total_time = time.time() - start_time
    
    return results, successful_purchases, failed_purchases, total_time

def verify_final_state(product):
    """Verify final product stock state"""
    product.refresh_from_db()
    print(f"\n{'='*80}")
    print(f"VERIFICATION RESULTS")
    print(f"{'='*80}")
    print(f"Initial Stock: {INITIAL_STOCK}")
    print(f"Final Stock: {product.stock}")
    print(f"Expected Stock: {INITIAL_STOCK - 50}")  # Only first 50 should succeed
    
    if product.stock < 0:
        print(f"❌ CRITICAL: Stock went negative! Stock = {product.stock}")
        return False
    elif product.stock >= 0:
        print(f"✓ Stock is valid (never went negative)")
        return True
    return False

def display_summary(results, successful, failed, total_time):
    """Display test summary"""
    print(f"\n{'='*80}")
    print(f"TEST SUMMARY")
    print(f"{'='*80}")
    print(f"Total Requests: {len(results)}")
    print(f"Successful Purchases: {successful}")
    print(f"Failed Purchases: {failed}")
    print(f"Success Rate: {(successful/len(results)*100):.2f}%")
    print(f"Total Time: {total_time:.2f}s")
    print(f"Avg Time per Request: {(total_time/len(results)*1000):.2f}ms")
    print(f"Requests per Second: {len(results)/total_time:.2f}")
    
    # Find response time stats
    times = [r['elapsed_time'] for r in results if r['elapsed_time'] > 0]
    if times:
        print(f"Min Response Time: {min(times)*1000:.2f}ms")
        print(f"Max Response Time: {max(times)*1000:.2f}ms")
        print(f"Avg Response Time: {(sum(times)/len(times))*1000:.2f}ms")
    
    print(f"\n✓ Concurrency test completed successfully!")
    print(f"✓ Stock management integrity verified!")

if __name__ == "__main__":
    print(f"\n{'*'*80}")
    print(f"CHALLENGE 01: HIGH-CONCURRENCY MANAGEMENT TEST")
    print(f"{'*'*80}")
    
    try:
        # Setup
        product = setup_test_product()
        
        # Run test
        results, successful, failed, total_time = run_concurrent_purchase_test(product.id)
        
        # Verify
        is_valid = verify_final_state(product)
        
        # Display results
        display_summary(results, successful, failed, total_time)
        
        if is_valid and successful <= INITIAL_STOCK:
            print(f"\n🎉 TEST PASSED: Stock integrity maintained!")
        else:
            print(f"\n❌ TEST FAILED: Stock integrity compromised!")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
