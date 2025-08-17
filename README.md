# Flask E-Commerce App

A local Flask + SQLite e-commerce API with JWT auth, vendors, products, cart, checkout/orders, reviews, reports, and simple Tailwind templates.

## Requirements
- Python 3.11+ (works on 3.13 here)

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run
Create `.env` as needed (optional). Then:
```bash
export FLASK_APP='app:create_app'
export FLASK_ENV=development
flask run
```
App runs at http://127.0.0.1:5000

## Features (API)
- Auth: `/api/auth/register`, `/api/auth/login`, `/api/auth/me`, `/api/auth/refresh`
- Vendor: `/api/vendor/request`, `/api/vendor/approve/<user_id>`, `/api/vendor/dashboard`
- Products: `/api/products` (GET/POST), `/api/products/<id>` (GET/PATCH/DELETE)
- Cart: `/api/cart` (GET), `/api/cart/add` (POST), `/api/cart/item/<id>` (PATCH/DELETE), `/api/cart/merge` (POST)
- Orders: `/api/orders/checkout`, `/api/orders` (GET), `/api/orders/<id>` (GET), `/api/orders/<id>/cancel` (POST), `/api/orders/<id>/items/<item_id>/fulfillment` (PATCH), `/api/orders/<id>/invoice.pdf` (GET)
- Reviews: `/api/reviews` (POST), `/api/reviews/product/<product_id>` (GET), `/api/reviews/pending` (GET admin), `/api/reviews/<id>/approve` (POST admin)
- Reports: `/api/reports/sales`, `/api/reports/low-stock`

## Templates (UI)
- `/` Home products grid
- `/product/<id>` Product detail with Add to Cart (guest)
- `/cart` Guest cart viewer
- `/checkout` Simple checkout form (requires `access_token` in localStorage)
- `/dashboard` Vendor dashboard demo (requires vendor token)

## Database
SQLite file at `app.db`. Use `flask shell` to inspect.

## Notes
- Payment is mocked.
- Stock deduction is atomic in checkout transaction.
- JWT subject is string user id.
- CORS enabled for `/api/*`.