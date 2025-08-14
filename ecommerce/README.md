# Flask E-Commerce App

A simple multi-role e-commerce application built with Flask, SQLAlchemy, WTForms, Flask-Login, and Bootstrap.

## Features
- User authentication (register, login, logout) with password hashing
- Roles: Customer, Vendor, Admin
- Vendor registration and admin approval
- Product catalog with categories, search and filters
- Cart (guest session cart and persistent user cart)
- Checkout with shipping info and payment simulation
- Orders with statuses and email notifications (simulated)
- Dashboards for vendor and admin, including reports

## Tech
- Flask, SQLite (default), SQLAlchemy ORM
- Jinja2 templates with Bootstrap 5
- WTForms for forms, Flask-Login for auth
- Blueprints for `auth`, `shop`, `cart`, `vendor`, `admin`, `api`

## Quickstart

1. Create a virtual environment and install dependencies:
```bash
cd ecommerce
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the app:
```bash
python run.py
```
The app will create `ecommerce.db` and seed sample data on first run.

3. Open the app: `http://localhost:5000`

## Sample Accounts
- Admin: `admin@example.com` / `password`
- Vendor: `vendor@example.com` / `password` (already approved)
- Customer: `customer@example.com` / `password`

## Configuration
Override defaults via environment variables if desired (see `config.py`).
- `SECRET_KEY`, `DATABASE_URL`, `ADMIN_EMAIL`
- Email uses console simulation by default (`MAIL_SUPPRESS_SEND=true`).

## Notes
- For a real email delivery, configure Flask-Mail settings and set `MAIL_SUPPRESS_SEND=false`.
- This is a reference implementation; extend with pagination, image uploads, payments, and proper migrations for production.