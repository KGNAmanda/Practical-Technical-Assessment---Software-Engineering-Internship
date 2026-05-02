# Troubleshooting Guide

## 🔧 Common Issues and Solutions

### Issue 1: ImportError when running Django commands

**Error**:
```
ImportError: No module named 'rest_framework'
```

**Solution**:
```bash
pip install -r backend/requirements.txt
```

**Explanation**: Required packages not installed

---

### Issue 2: ModuleNotFoundError: No module named 'django_cors_headers'

**Error**:
```
ModuleNotFoundError: No module named 'django_cors_headers'
```

**Solution**:
```bash
pip install django-cors-headers
```

**Explanation**: CORS package not installed. It's in requirements.txt

---

### Issue 3: Port 8000 already in use

**Error**:
```
Address already in use: ('127.0.0.1', 8000)
```

**Solution**:
```bash
# Run on different port
python manage.py runserver 8001

# Then update frontend/index.html
# Change: const API_BASE_URL = 'http://localhost:8000/api';
# To: const API_BASE_URL = 'http://localhost:8001/api';
```

**Explanation**: Another process using port 8000. Use alternative port.

---

### Issue 4: Database not migrated

**Error**:
```
django.db.utils.ProgrammingError: table "shop_product" does not exist
```

**Solution**:
```bash
python manage.py makemigrations
python manage.py migrate
```

**Explanation**: Database tables not created. Migrations needed.

---

### Issue 5: No products available

**Error**:
```
Testing: POST /api/purchase/
Error: Product not found. Create one first!
```

**Solution**:
```bash
python manage.py shell
```

Then in the Python shell:
```python
from shop.models import Product

# Create a test product
Product.objects.create(
    name="Test Product",
    stock=50,
    price=99.99
)

# Verify
print(Product.objects.all())
exit()
```

**Explanation**: No products in database

---

### Issue 6: CORS errors in browser console

**Error**:
```
Access to XMLHttpRequest at 'http://localhost:8000/api/products/' from origin 
'file://...' has been blocked by CORS policy
```

**Solution**:
```bash
# Option 1: Serve frontend through a web server
python -m http.server 8080
# Then access: http://localhost:8080/frontend/index.html

# Option 2: Use browser extension to allow CORS (for testing only)
# Or update CORS settings in backend/settings.py:
CORS_ALLOWED_ORIGINS = [
    "file://",  # Already included
]
```

**Explanation**: CORS restrictions. Use HTTP server instead of file:// protocol

---

### Issue 7: Migration conflicts

**Error**:
```
django.core.exceptions.ImproperlyConfigured: Conflicting migrations detected
```

**Solution**:
```bash
# Show all migrations
python manage.py showmigrations

# If issues, reset migrations (WARNING: deletes data)
python manage.py migrate shop zero
python manage.py migrate purchase zero
python manage.py migrate

# Or remove pycache
rm -rf shop/__pycache__ purchase/__pycache__
```

**Explanation**: Migration conflicts. Reset or clear cache.

---

### Issue 8: Concurrent test fails to connect

**Error**:
```
ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
```

**Solution**:
```bash
# Make sure Django server is running in another terminal
python manage.py runserver

# Then run test in a separate terminal
python test_concurrent_purchases.py
```

**Explanation**: Django server not running when test tries to connect

---

### Issue 9: Analytics endpoint returns empty data

**Error**:
```json
{
    "period": "Last 30 days",
    "total_revenue": 0,
    "daily_revenue": [],
    "top_5_products": []
}
```

**Solution**:
```bash
# Seed database with test data
python manage.py seed --products 50 --orders 10000

# Then test analytics
curl http://localhost:8000/api/analytics/
```

**Explanation**: No data in database. Need to seed first.

---

### Issue 10: Frontend shows "Cart is empty" but can't add products

**Error**: Products don't load in the POS interface

**Solution**:
1. Check browser console (F12)
2. Verify Django server is running
3. Check API_BASE_URL is correct in frontend/index.html
4. Create at least one product:
   ```bash
   python manage.py shell
   from shop.models import Product
   Product.objects.create(name="Test", stock=50, price=99.99)
   exit()
   ```
5. Refresh browser

**Explanation**: Products not in database or API connection issue

---

### Issue 11: TypeError when importing models

**Error**:
```
TypeError: __init__() got an unexpected keyword argument 'default'
```

**Solution**:
```bash
# Update Django version
pip install --upgrade django

# Or check the model syntax is correct
# Make sure FloatField doesn't have 'default' parameter
```

**Explanation**: Django version compatibility issue

---

### Issue 12: Permission denied on test script

**Error**:
```
Permission denied: './test_concurrent_purchases.py'
```

**Solution (Windows)**:
```bash
python test_concurrent_purchases.py
```

**Solution (Linux/Mac)**:
```bash
chmod +x test_concurrent_purchases.py
python test_concurrent_purchases.py
```

**Explanation**: File permissions issue

---

### Issue 13: Receipt doesn't print correctly

**Error**: Receipt prints with wrong formatting

**Solution**:
1. Check browser print settings
2. Set paper size to custom (80mm)
3. Disable headers/footers in print dialog
4. Use PDF printer for better results

**Code**:
```javascript
// Already handles print dialog in frontend/index.html
function printReceipt() {
    const printWindow = window.open('', '', 'height=600,width=400');
    // Prints with 80mm-optimized styling
}
```

---

### Issue 14: Checkout returns "Insufficient stock" when stock is available

**Error**:
```json
{
    "error": "Insufficient stock for Product. Available: 5, Requested: 5"
}
```

**Possible Causes**:
1. Stock was reduced by concurrent purchase
2. Multiple checkout attempts happened simultaneously
3. Previous failed checkout deducted stock

**Solution**:
```bash
# Check current stock
python manage.py shell
from shop.models import Product
Product.objects.values('name', 'stock')
exit()

# Reset stock if needed
python manage.py shell
from shop.models import Product
p = Product.objects.get(id=1)
p.stock = 50
p.save()
exit()
```

---

### Issue 15: "AttributeError: 'NoneType' object has no attribute..."

**Error**:
```
AttributeError: 'NoneType' object has no attribute 'stock'
```

**Solution**: Product doesn't exist

```bash
# Check if products exist
python manage.py shell
from shop.models import Product
print(Product.objects.all())
exit()

# If empty, create products
python manage.py shell
from shop.models import Product
Product.objects.create(name="Test1", stock=50, price=99.99)
Product.objects.create(name="Test2", stock=30, price=49.99)
exit()
```

---

## ✅ Verification Checklist

### Before Running Tests
- [x] All dependencies installed: `pip install -r requirements.txt`
- [x] Migrations applied: `python manage.py migrate`
- [x] Django server running: `python manage.py runserver`
- [x] Products created in database
- [x] API accessible: `curl http://localhost:8000/api/`

### For Challenge 01
- [x] Product with stock=50 created
- [x] Server running on port 8000
- [x] Test script executed: `python test_concurrent_purchases.py`
- [x] Stock is 0 after test (or within reasonable range)

### For Challenge 02
- [x] Data seeded: `python manage.py seed --products 100 --orders 100000`
- [x] Analytics endpoint working: `curl http://localhost:8000/api/analytics/`
- [x] Response contains daily_revenue and top_5_products
- [x] Response time < 500ms

### For Challenge 03
- [x] Frontend file exists: `frontend/index.html`
- [x] Products load in POS interface
- [x] Can add items to cart
- [x] Checkout completes successfully
- [x] Receipt displays and prints

---

## 🔍 Debug Tips

### Check Django logs
```bash
# Run with verbose output
python manage.py runserver --verbosity 2
```

### Check database state
```bash
python manage.py shell
from shop.models import Product, Order, OrderItem
print(f"Products: {Product.objects.count()}")
print(f"Orders: {Order.objects.count()}")
print(f"Order Items: {OrderItem.objects.count()}")
exit()
```

### Check API responses manually
```bash
# Using curl
curl -v http://localhost:8000/api/products/

# Using Python
import requests
response = requests.get('http://localhost:8000/api/products/')
print(response.json())
```

### Enable Django debug toolbar
```python
# Add to settings.py
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']
```

### Check browser console
1. Press F12
2. Go to Console tab
3. Check for JavaScript errors
4. Check Network tab for failed requests

---

## 🆘 Still Having Issues?

### 1. Check if it's a Python environment issue
```bash
which python
python --version
pip list | grep -i django
```

### 2. Check if it's a database issue
```bash
rm db.sqlite3
python manage.py migrate
```

### 3. Check if it's a permissions issue
```bash
# Ensure files are readable
chmod -R 755 backend/
```

### 4. Start fresh
```bash
# In backend directory
rm db.sqlite3
rm -rf shop/__pycache__ purchase/__pycache__
python manage.py makemigrations
python manage.py migrate
python manage.py shell
from shop.models import Product
Product.objects.create(name="Test", stock=50, price=99.99)
exit()
python manage.py runserver
```

---

## 📊 Common Error Status Codes

| Status | Meaning | Likely Cause |
|--------|---------|--------------|
| 200 | OK | Success |
| 201 | Created | Successful POST |
| 400 | Bad Request | Invalid data or insufficient stock |
| 404 | Not Found | Product ID doesn't exist |
| 500 | Server Error | Code error or database issue |
| 503 | Service Unavailable | Server not running |

---

## 🚨 Emergency Reset

If everything is broken:

```bash
cd backend

# Remove database
rm db.sqlite3

# Clear Python cache
rm -rf __pycache__ shop/__pycache__ purchase/__pycache__

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Recreate database
python manage.py makemigrations
python manage.py migrate

# Create test data
python manage.py shell
from shop.models import Product
Product.objects.create(name="Emergency Test", stock=50, price=99.99)
exit()

# Start fresh
python manage.py runserver
```

---

**Last Updated**: May 2, 2026
**Most Common Issue**: Missing dependencies or Django server not running
