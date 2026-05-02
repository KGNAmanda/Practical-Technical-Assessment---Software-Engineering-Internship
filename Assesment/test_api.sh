#!/usr/bin/env bash
# API Testing Guide - Micronsoft Solutions Assessment
# Run this script to test all endpoints

BASE_URL="http://localhost:8000"

echo "======================================================"
echo "Micronsoft Solutions - API Testing Guide"
echo "======================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test 1: Check server status
echo -e "${BLUE}Test 1: Server Status${NC}"
echo "Testing: GET /"
curl -s "${BASE_URL}/" | python -m json.tool
echo ""

# Test 2: List products
echo -e "${BLUE}Test 2: Get Products${NC}"
echo "Testing: GET /api/products/"
curl -s "${BASE_URL}/api/products/" | python -m json.tool
echo ""

# Test 3: Create a test product via Django shell first
echo -e "${BLUE}Test 3: Purchase Product${NC}"
echo "Testing: POST /api/purchase/"
echo "Payload:"
echo '{
  "product_id": 1,
  "quantity": 1
}'
echo ""
curl -X POST "${BASE_URL}/api/purchase/" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 1}' | python -m json.tool 2>/dev/null || echo "Error: Product not found. Create one first!"
echo ""

# Test 4: Checkout
echo -e "${BLUE}Test 4: Checkout (Create Order)${NC}"
echo "Testing: POST /api/checkout/"
echo "Payload:"
echo '{
  "items": [
    {"product_id": 1, "quantity": 1}
  ]
}'
echo ""
curl -X POST "${BASE_URL}/api/checkout/" \
  -H "Content-Type: application/json" \
  -d '{"items": [{"product_id": 1, "quantity": 1}]}' | python -m json.tool 2>/dev/null || echo "Error: Could not complete checkout"
echo ""

# Test 5: Analytics
echo -e "${BLUE}Test 5: Analytics (Requires seeded data)${NC}"
echo "Testing: GET /api/analytics/"
curl -s "${BASE_URL}/api/analytics/" | python -m json.tool | head -30
echo "..."
echo ""

echo -e "${GREEN}======================================================"
echo "Testing Complete!"
echo "======================================================${NC}"
echo ""
echo "Setup Instructions:"
echo "1. Install dependencies: pip install -r backend/requirements.txt"
echo "2. Apply migrations: python manage.py migrate"
echo "3. Create product: python manage.py shell"
echo "   >>> from shop.models import Product"
echo "   >>> Product.objects.create(name='Test', stock=50, price=99.99)"
echo "   >>> exit()"
echo "4. Start server: python manage.py runserver"
echo "5. Run tests: bash test_api.sh"
echo ""
