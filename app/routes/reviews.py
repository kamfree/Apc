from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from .. import db
from ..models import Review, Order, OrderItem, Product

reviews_bp = Blueprint('reviews', __name__)


def _current_user_id():
	uid = get_jwt_identity()
	return int(uid) if uid is not None else None


def _require_role(roles: list[str]) -> bool:
	claims = get_jwt() or {}
	return (claims.get('role') in roles)


@reviews_bp.get('/product/<int:product_id>')
def list_product_reviews(product_id: int):
	page = request.args.get('page', 1, type=int)
	per_page = request.args.get('per_page', 20, type=int)
	query = Review.query.filter_by(product_id=product_id, is_approved=True)
	total = query.count()
	items = query.order_by(Review.created_at.desc()).offset((page-1)*per_page).limit(per_page).all()
	return jsonify({'items': [r.to_dict() for r in items], 'meta': {'total': total, 'page': page, 'per_page': per_page}}), 200


@reviews_bp.post('')
@jwt_required()
def create_review():
	user_id = _current_user_id()
	data = request.get_json(silent=True) or {}
	product_id = data.get('product_id')
	rating = int(data.get('rating') or 0)
	title = data.get('title')
	body = data.get('body')
	if not product_id or rating < 1 or rating > 5:
		return jsonify({'message': 'product_id and 1-5 rating required'}), 400

	# must have purchased product
	purchased = db.session.query(OrderItem.id).join(Order).filter(
		Order.user_id == user_id,
		Order.payment_status == 'paid',
		Order.status != 'cancelled',
		OrderItem.product_id == int(product_id)
	).first() is not None
	if not purchased:
		return jsonify({'message': 'purchase required to review'}), 403

	# one review per user per product
	existing = Review.query.filter_by(user_id=user_id, product_id=product_id).first()
	if existing:
		return jsonify({'message': 'review already exists'}), 409

	review = Review(user_id=user_id, product_id=product_id, rating=rating, title=title, body=body, is_approved=False)
	db.session.add(review)
	db.session.commit()
	return jsonify({'message': 'review submitted', 'review': review.to_dict()}), 201


@reviews_bp.get('/pending')
@jwt_required()
def list_pending():
	if not _require_role(['admin']):
		return jsonify({'message': 'admin required'}), 403
	items = Review.query.filter_by(is_approved=False).order_by(Review.created_at.desc()).limit(100).all()
	return jsonify({'items': [r.to_dict() for r in items]}), 200


@reviews_bp.post('/<int:review_id>/approve')
@jwt_required()
def approve_review(review_id: int):
	if not _require_role(['admin']):
		return jsonify({'message': 'admin required'}), 403
	review = Review.query.get_or_404(review_id)
	review.is_approved = True
	db.session.commit()
	return jsonify({'message': 'approved', 'review': review.to_dict()}), 200