from flask import request, jsonify, Blueprint
from app import db
from app.models import Review, Product, User, Order, OrderItem, SKU, OrderStatus
from flask_jwt_extended import jwt_required, get_jwt_identity

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('/products/<int:product_id>/reviews', methods=['POST'])
@jwt_required()
def create_review(product_id):
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    data = request.get_json()

    if not data or 'rating' not in data:
        return jsonify({'message': 'Rating is required'}), 400

    # 1. Check if product exists
    product = Product.query.get_or_404(product_id)

    # 2. Check if user has already reviewed this product
    existing_review = Review.query.filter_by(user_id=user.id, product_id=product_id).first()
    if existing_review:
        return jsonify({'message': 'You have already reviewed this product'}), 400

    # 3. Check if user has purchased this product
    has_purchased = db.session.query(OrderItem.id)\
        .join(Order).join(SKU)\
        .filter(
            Order.user_id == user.id,
            SKU.product_id == product_id,
            Order.status.in_([OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.DELIVERED])
        ).first()

    if not has_purchased:
        return jsonify({'message': 'You can only review products you have purchased'}), 403

    review = Review(
        user_id=user.id,
        product_id=product_id,
        rating=data['rating'],
        comment=data.get('comment')
    )
    db.session.add(review)
    db.session.commit()

    return jsonify({'message': 'Review submitted and is pending approval'}), 201

@reviews_bp.route('/products/<int:product_id>/reviews', methods=['GET'])
def get_reviews_for_product(product_id):
    product = Product.query.get_or_404(product_id)
    reviews = Review.query.filter_by(product_id=product.id, is_approved=True).order_by(Review.created_at.desc()).all()

    return jsonify([{
        'id': r.id,
        'rating': r.rating,
        'comment': r.comment,
        'author': r.user.email, # In a real app, you might want a username instead of email
        'date': r.created_at.isoformat()
    } for r in reviews]), 200
