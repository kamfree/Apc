from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from ..models import Product, Order


api_bp = Blueprint("api", __name__)


@api_bp.get("/products")
def api_products():
    products = Product.query.filter_by(is_active=True).all()
    return jsonify([
        {
            "id": p.id,
            "title": p.title,
            "price": float(p.price),
            "stock": p.stock,
            "image_url": p.image_url,
        }
        for p in products
    ])


@api_bp.get("/orders/me")
@login_required
def api_my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return jsonify([
        {
            "id": o.id,
            "status": o.status,
            "created_at": o.created_at.isoformat(),
            "total_amount": float(o.total_amount),
        }
        for o in orders
    ])