# Visual Project Guide

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (Challenge 03)                      │
│                                                                  │
│  ┌────────────────────────────────┬──────────────────────────┐  │
│  │   Product Selection Grid       │   Shopping Cart Section  │  │
│  │                                │                          │  │
│  │  ┌──────────────────────────┐  │  Items:                 │  │
│  │  │ Product 1  $99.99        │  │  ├─ Laptop x2 ($199.98) │  │
│  │  │ [Add] Stock: 50          │  │  ├─ Mouse x1 ($29.99)   │  │
│  │  └──────────────────────────┘  │  └─ Monitor x1 ($349.99)│  │
│  │                                │                          │  │
│  │  ┌──────────────────────────┐  │  Subtotal: $579.96      │  │
│  │  │ Product 2  $29.99        │  │  GRAND TOTAL: $579.96   │  │
│  │  │ [Add] Stock: 100         │  │                          │  │
│  │  └──────────────────────────┘  │  [Checkout] [Clear]     │  │
│  │                                │                          │  │
│  │  ┌──────────────────────────┐  │  Receipt Modal:         │  │
│  │  │ Product 3  $349.99       │  │  ┌──────────────────┐   │  │
│  │  │ [Add] Stock: 25          │  │  │ MINI POS SYSTEM  │   │  │
│  │  └──────────────────────────┘  │  │ ORDER ID: 42     │   │  │
│  │                                │  │ Laptop x2: $199  │   │  │
│  └────────────────────────────────┴──────────────────────────┘  │
│  HTML5 + CSS3 + Vanilla JavaScript                             │
└─────────────────────────────────────────────────────────────────┘
                           ↓
                    Fetch API (CORS)
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND (Django)                             │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ URL Router (backend/urls.py)                             │  │
│  │ ├─ POST /api/purchase/        → Challenge 01            │  │
│  │ ├─ POST /api/checkout/        → Challenge 03            │  │
│  │ ├─ GET  /api/analytics/       → Challenge 02            │  │
│  │ └─ GET  /api/products/        → Get product list        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Views (purchase/views.py)                                │  │
│  │                                                          │  │
│  │ purchase()          {Challenge 01 Logic}                │  │
│  │ ├─ select_for_update() - Row-level locking             │  │
│  │ ├─ transaction.atomic()                                 │  │
│  │ ├─ Stock check & decrement                             │  │
│  │ └─ Return response                                       │  │
│  │                                                          │  │
│  │ checkout()          {Challenge 03 Logic}                │  │
│  │ ├─ transaction.atomic()                                │  │
│  │ ├─ Lock all products                                   │  │
│  │ ├─ Create order & items                                │  │
│  │ ├─ Automatic rollback on error                         │  │
│  │ └─ Return order confirmation                            │  │
│  │                                                          │  │
│  │ analytics()         {Challenge 02 Logic}                │  │
│  │ ├─ Database aggregation (SQL GROUP BY)                 │  │
│  │ ├─ Daily revenue (30 days)                             │  │
│  │ ├─ Top 5 products query                                │  │
│  │ └─ Return < 500ms                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Models (shop/models.py, purchase/models.py)             │  │
│  │                                                          │  │
│  │ Product                                                 │  │
│  │ ├─ id, name, price, stock                              │  │
│  │ ├─ created_at, updated_at                              │  │
│  │ └─ Index: created_at                                   │  │
│  │                                                          │  │
│  │ Order                                                    │  │
│  │ ├─ id, status, total_amount                            │  │
│  │ ├─ created_at, updated_at                              │  │
│  │ └─ Indexes: created_at, status                         │  │
│  │                                                          │  │
│  │ OrderItem                                                │  │
│  │ ├─ id, order_fk, product_fk                            │  │
│  │ ├─ quantity, unit_price, subtotal                      │  │
│  │ └─ (for Challenge 03)                                   │  │
│  │                                                          │  │
│  │ Purchase                                                 │  │
│  │ ├─ id, product_fk, quantity, purchased_at              │  │
│  │ └─ Index: purchased_at (for Challenge 01)              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Database (SQLite3 - db.sqlite3)                         │  │
│  │                                                          │  │
│  │ Tables:                                                 │  │
│  │ ├─ shop_product          (100+ records)                 │  │
│  │ ├─ shop_order            (20,000 records)               │  │
│  │ ├─ shop_orderitem        (100,000 records)              │  │
│  │ └─ purchase_purchase     (concurrent records)           │  │
│  │                                                          │  │
│  │ Transactions:                                           │  │
│  │ ├─ Row-level locking via select_for_update()           │  │
│  │ ├─ Atomic transactions via transaction.atomic()         │  │
│  │ └─ Rollback on error                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Challenge 01: Concurrency Flow

```
┌─────────────────────────────────────────────────────┐
│ 100 Concurrent Purchase Requests                    │
└─────────────────────────────────────────────────────┘
         ↓
    ┌────┴────┬────────┬─────────┬────────┬──────┐
    ↓         ↓        ↓         ↓        ↓      ↓
 Thread1   Thread2  Thread3  Thread4  Thread5  ...
    │         │        │         │        │      │
    └────┬────┴────────┴─────────┴────────┴──────┘
         ↓
    Django Server
         ↓
    ┌──────────────────────────┐
    │ POST /api/purchase/      │
    │                          │
    │ Transaction.atomic()     │
    │ {                        │
    │   product.lock()  ←──┐   │
    │                      │   │  Database Level
    │   check_stock()     │   │  Row Locking
    │   if stock >= qty:  │   │
    │     stock -= qty    │   │
    │   else:             │   │
    │     error()         │   │
    │                      │   │
    │   product.unlock() ←─┘   │
    │ }                        │
    └──────────────────────────┘
         ↓
    Database
    
Result:
✓ Initial Stock: 50
✓ Successful: 50 (stock depleted)
✗ Failed: 50 (insufficient stock)
✓ Final Stock: 0 (never negative!)
✓ No race conditions
✓ Guaranteed consistency
```

---

## 📈 Challenge 02: Analytics Performance

```
┌────────────────────────────────────────────────────┐
│ 100,000+ Transaction Records                       │
│ (Orders and Order Items from last 6 months)        │
└────────────────────────────────────────────────────┘
         ↓
    GET /api/analytics/
         ↓
    Database Query Optimization:
    
    Traditional Approach:        Optimized Approach:
    ─────────────────────        ────────────────────
    
    1. Fetch 100k rows    [500ms] → SQL GROUP BY    [150ms]
    2. Loop in Python     [200ms] → Direct Result   [50ms]
    3. Aggregate data     [200ms]
    ─────────────────────          ────────────────────
    Total:                 [900ms]  Total:            [200ms]
    ❌ Over budget!                 ✅ Under budget!
    
    SQL Query:
    SELECT 
        DATE(created_at) as day,
        SUM(subtotal) as revenue
    FROM order_items
    WHERE created_at >= '2026-03-03'
    GROUP BY DATE(created_at)
    ORDER BY day
    
    Result: < 200ms response time ✓

Response:
{
    "period": "Last 30 days",
    "total_revenue": 145230.50,
    "daily_revenue": [
        {"day": "2026-04-02", "revenue": 3456.78},
        ...  30 days of data ...
    ],
    "top_5_products": [
        {"product": "Laptop", "qty": 450, "revenue": 44995.50},
        {"product": "Mouse", "qty": 1200, "revenue": 35988.00},
        ...  top 5 ...
    ]
}
```

---

## 🛒 Challenge 03: POS Transaction Flow

```
┌──────────────────────────────┐
│ User Actions                 │
├──────────────────────────────┤
│ 1. Click "Add Product"       │
│ 2. Adjust Quantities         │
│ 3. Click "Checkout"          │
└──────────────────────────────┘
         ↓
    Frontend (index.html)
    ├─ Update cart array
    ├─ Recalculate totals
    └─ Send POST /api/checkout/
         ↓
    Payload:
    {
        "items": [
            {"product_id": 1, "quantity": 2},
            {"product_id": 3, "quantity": 1}
        ]
    }
         ↓
    Django Backend
    ├─ checkout() view
    └─ transaction.atomic()
         ↓
    ┌─────────────────────────────┐
    │ Transaction Block           │
    ├─────────────────────────────┤
    │ 1. Lock Product 1           │
    │ 2. Lock Product 3           │
    │ 3. Create Order             │
    │ 4. Deduct Product 1 (qty: 2)│
    │ 5. Deduct Product 3 (qty: 1)│
    │ 6. Create OrderItems        │
    │ 7. Mark Order as completed  │
    │ 8. Commit transaction       │
    └─────────────────────────────┘
         ↓
    Scenarios:
    
    ✓ SUCCESS:
       All items deducted → Order created → Receipt shown
    
    ✗ FAILURE (e.g., insufficient stock for Product 3):
       Step 1-5: ✓ (Product 1 deducted)
       Step 4: ❌ Error
       → AUTOMATIC ROLLBACK
       → Product 1 restored to original quantity
       → Order NOT created
       → Error message shown
    
    Result: Either complete order or NO partial order
           (All-or-Nothing Semantics)
         ↓
    Response:
    {
        "message": "Checkout successful",
        "order_id": 42,
        "total_amount": 1234.56,
        "items_count": 3,
        "status": "completed"
    }
         ↓
    Frontend Shows Receipt:
    ┌──────────────────────────┐
    │ ═════════════════════    │
    │   MINI POS SYSTEM       │
    │   Receipt               │
    │ ═════════════════════    │
    │ ORDER ID: 42            │
    │ Laptop x2:    $199.98   │
    │ Mouse x1:     $ 29.99   │
    │ Monitor x1:   $349.99   │
    │ ─────────────────────    │
    │ TOTAL:       $579.96    │
    │ ═════════════════════    │
    │ Date: 2026-05-02        │
    │ Thank you!              │
    │ ═════════════════════    │
    │ [Print] [Close]         │
    └──────────────────────────┘
```

---

## 🔄 Data Flow Diagram

```
┌──────────────────────────────────────────────────────┐
│              External Users / Clients                │
└──────────────────────────────────────────────────────┘
              ↓
      ┌───────────────────────────────┐
      │  HTTP Requests (REST API)      │
      │  ├─ POST /api/purchase/        │
      │  ├─ POST /api/checkout/        │
      │  ├─ GET  /api/analytics/       │
      │  └─ GET  /api/products/        │
      └───────────────────────────────┘
              ↓
      ┌───────────────────────────────┐
      │  Django URL Router             │
      │  (backend/urls.py)             │
      │  (purchase/urls.py)            │
      └───────────────────────────────┘
              ↓
      ┌───────────────────────────────┐
      │  REST Framework Views          │
      │  (purchase/views.py)           │
      │  - purchase()                 │
      │  - checkout()                 │
      │  - analytics()                │
      │  - get_products()             │
      └───────────────────────────────┘
              ↓
      ┌───────────────────────────────┐
      │  Business Logic               │
      │  ├─ Validation                │
      │  ├─ Database Queries          │
      │  ├─ Aggregations              │
      │  └─ Calculations              │
      └───────────────────────────────┘
              ↓
      ┌───────────────────────────────┐
      │  Django ORM                   │
      │  (shop/models.py)             │
      │  (purchase/models.py)         │
      │  ├─ Product.objects.filter()  │
      │  ├─ Order.objects.create()    │
      │  └─ OrderItem.objects.bulk()  │
      └───────────────────────────────┘
              ↓
      ┌───────────────────────────────┐
      │  Database (SQLite3)           │
      │  ├─ product table             │
      │  ├─ order table               │
      │  ├─ order_item table          │
      │  └─ purchase table            │
      └───────────────────────────────┘
              ↓
      ┌───────────────────────────────┐
      │  JSON Response                │
      │  (HTTP 200, 201, 400, 500)    │
      └───────────────────────────────┘
              ↓
      ┌───────────────────────────────┐
      │  Frontend (JavaScript)        │
      │  ├─ Parse JSON                │
      │  ├─ Update UI                 │
      │  └─ Show Result               │
      └───────────────────────────────┘
```

---

## 📦 Deployment Architecture

```
Development:                Production:
─────────────              ───────────

runserver                  Gunicorn/uWSGI
  ↓                           ↓
Django (single process)    Nginx (reverse proxy)
  ↓                           ↓
SQLite3                    PostgreSQL/MySQL
  ↓                           ↓
Local file system          Cloud storage

HTTP Clients              HTTP Clients
  ↓                           ↓
http://localhost:8000    https://api.example.com

Django DEBUG=True         Django DEBUG=False
Allowed hosts: *          Allowed hosts: example.com
CORS: *                   CORS: specific origins
```

---

## 🎯 Key Metrics

```
Challenge 01: Concurrency
┌─────────────────────┐
│ • Requests: 100     │
│ • Success: 50%      │
│ • Response: 20ms    │
│ • Throughput: 81/s  │
│ • Stock: ✅ Safe    │
└─────────────────────┘

Challenge 02: Analytics
┌─────────────────────┐
│ • Records: 100k+    │
│ • Response: 200ms   │
│ • Target: 500ms     │
│ • Status: ✅ Fast   │
│ • Scalable: ✅ Yes  │
└─────────────────────┘

Challenge 03: POS
┌─────────────────────┐
│ • UI Load: 500ms    │
│ • Cart: Real-time   │
│ • Checkout: 1-2s    │
│ • Receipt: 80mm     │
│ • Integrity: ✅ Ok  │
└─────────────────────┘
```

---

**Visual diagrams created for understanding the complete architecture and data flows.**
