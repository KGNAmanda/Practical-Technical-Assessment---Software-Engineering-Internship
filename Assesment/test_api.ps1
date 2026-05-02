# API Testing Guide - Windows PowerShell Version
# Micronsoft Solutions Assessment

$BASE_URL = "http://localhost:8000"

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "Micronsoft Solutions - API Testing Guide (PowerShell)" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Check server status
Write-Host "Test 1: Server Status" -ForegroundColor Blue
Write-Host "Testing: GET /" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BASE_URL/" -Method Get
    $response.Content | ConvertFrom-Json | ConvertTo-Json | Write-Host
} catch {
    Write-Host "Error: Could not connect to server. Is it running?" -ForegroundColor Red
}
Write-Host ""

# Test 2: List products
Write-Host "Test 2: Get Products" -ForegroundColor Blue
Write-Host "Testing: GET /api/products/" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BASE_URL/api/products/" -Method Get
    $response.Content | ConvertFrom-Json | ConvertTo-Json | Write-Host
} catch {
    Write-Host "Error: Could not fetch products" -ForegroundColor Red
}
Write-Host ""

# Test 3: Purchase Product
Write-Host "Test 3: Purchase Product" -ForegroundColor Blue
Write-Host "Testing: POST /api/purchase/" -ForegroundColor Yellow
Write-Host "Payload:" -ForegroundColor Gray
Write-Host '{
  "product_id": 1,
  "quantity": 1
}'
Write-Host ""

try {
    $body = @{
        product_id = 1
        quantity = 1
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "$BASE_URL/api/purchase/" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body

    $response.Content | ConvertFrom-Json | ConvertTo-Json | Write-Host
} catch {
    Write-Host "Error: Product not found. Create one first!" -ForegroundColor Red
}
Write-Host ""

# Test 4: Checkout
Write-Host "Test 4: Checkout (Create Order)" -ForegroundColor Blue
Write-Host "Testing: POST /api/checkout/" -ForegroundColor Yellow
Write-Host "Payload:" -ForegroundColor Gray
Write-Host '{
  "items": [
    {"product_id": 1, "quantity": 1}
  ]
}'
Write-Host ""

try {
    $items = @(
        @{
            product_id = 1
            quantity = 1
        }
    )
    
    $body = @{
        items = $items
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "$BASE_URL/api/checkout/" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body

    $response.Content | ConvertFrom-Json | ConvertTo-Json | Write-Host
} catch {
    Write-Host "Error: Could not complete checkout" -ForegroundColor Red
}
Write-Host ""

# Test 5: Analytics
Write-Host "Test 5: Analytics (Requires seeded data)" -ForegroundColor Blue
Write-Host "Testing: GET /api/analytics/" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BASE_URL/api/analytics/" -Method Get
    $analytics = $response.Content | ConvertFrom-Json
    $analytics | ConvertTo-Json | Write-Host
} catch {
    Write-Host "Error: Could not fetch analytics" -ForegroundColor Red
}
Write-Host ""

Write-Host "======================================================" -ForegroundColor Green
Write-Host "Testing Complete!" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
Write-Host ""

Write-Host "Setup Instructions:" -ForegroundColor Yellow
Write-Host "1. Install dependencies: pip install -r backend/requirements.txt"
Write-Host "2. Apply migrations: python manage.py migrate"
Write-Host "3. Create product in Django shell:"
Write-Host "   - python manage.py shell"
Write-Host "   - from shop.models import Product"
Write-Host "   - Product.objects.create(name='Test', stock=50, price=99.99)"
Write-Host "   - exit()"
Write-Host "4. Start server: python manage.py runserver"
Write-Host "5. Run tests: powershell -ExecutionPolicy Bypass .\test_api.ps1"
Write-Host ""
