from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from .. import db
from ..models import Cart, CartItem, ProductVariant

cart_bp = Blueprint('cart', __name__)


def _current_user_id():
	uid = get_jwt_identity()
	return int(uid) if uid is not None else None


def _get_or_create_cart(user_id=None, session_id=None) -> Cart:
	query = Cart.query.filter_by(status='active')
	if user_id:
		cart = query.filter_by(user_id=user_id).first()
		if cart:
			return cart
		cart = Cart(user_id=user_id, status='active')
		db.session.add(cart)
		db.session.commit()
		return cart
	elif session_id:
		cart = query.filter_by(session_id=session_id).first()
		if cart:
			return cart
		cart = Cart(session_id=session_id, status='active')
		db.session.add(cart)
		db.session.commit()
		return cart
	return None


@cart_bp.get('')
@jwt_required(optional=True)
def get_cart():
	user_id = _current_user_id()
	session_id = request.args.get('session_id')
	if not user_id and not session_id:
		return jsonify({'message': 'session_id required for guests'}), 400
	cart = _get_or_create_cart(user_id=user_id, session_id=session_id)
	return jsonify({'cart': cart.to_dict()}), 200


@cart_bp.post('/add')
@jwt_required(optional=True)
def add_item():
	user_id = _current_user_id()
	data = request.get_json(silent=True) or {}
	session_id = data.get('session_id')
	variant_id = data.get('variant_id')
	quantity = int(data.get('quantity') or 1)
	if not user_id and not session_id:
		return jsonify({'message': 'session_id required for guests'}), 400
	if not variant_id or quantity <= 0:
		return jsonify({'message': 'variant_id and positive quantity required'}), 400

	cart = _get_or_create_cart(user_id=user_id, session_id=session_id)
	variant = ProductVariant.query.get_or_404(int(variant_id))
	# Price from variant effective price
	unit_price = variant.effective_price()

	# Check if item exists
	existing = CartItem.query.filter_by(cart_id=cart.id, variant_id=variant.id).first()
	if existing:
		existing.quantity += quantity
		item = existing
	else:
		item = CartItem(cart_id=cart.id, variant_id=variant.id, quantity=quantity, unit_price=unit_price)
		db.session.add(item)

	db.session.commit()
	return jsonify({'message': 'item added', 'cart': cart.to_dict()}), 201


@cart_bp.patch('/item/<int:item_id>')
@jwt_required(optional=True)
def update_item(item_id: int):
	user_id = _current_user_id()
	data = request.get_json(silent=True) or {}
	session_id = data.get('session_id')
	quantity = int(data.get('quantity') or 0)
	if not user_id and not session_id:
		return jsonify({'message': 'session_id required for guests'}), 400
	item = CartItem.query.get_or_404(item_id)
	cart = Cart.query.get(item.cart_id)
	if user_id and cart.user_id != user_id:
		return jsonify({'message': 'not authorized'}), 403
	if not user_id and cart.session_id != session_id:
		return jsonify({'message': 'not authorized'}), 403
	if quantity <= 0:
		db.session.delete(item)
	else:
		item.quantity = quantity
	db.session.commit()
	return jsonify({'message': 'updated', 'cart': cart.to_dict()}), 200


@cart_bp.delete('/item/<int:item_id>')
@jwt_required(optional=True)
def remove_item(item_id: int):
	user_id = _current_user_id()
	session_id = request.args.get('session_id')
	if not user_id and not session_id:
		return jsonify({'message': 'session_id required for guests'}), 400
	item = CartItem.query.get_or_404(item_id)
	cart = Cart.query.get(item.cart_id)
	if user_id and cart.user_id != user_id:
		return jsonify({'message': 'not authorized'}), 403
	if not user_id and cart.session_id != session_id:
		return jsonify({'message': 'not authorized'}), 403
	db.session.delete(item)
	db.session.commit()
	return jsonify({'message': 'removed', 'cart': cart.to_dict()}), 200


@cart_bp.post('/merge')
@jwt_required()
def merge_guest_cart():
	user_id = _current_user_id()
	data = request.get_json(silent=True) or {}
	session_id = data.get('session_id')
	if not session_id:
		return jsonify({'message': 'session_id required'}), 400
	user_cart = _get_or_create_cart(user_id=user_id)
	guest_cart = Cart.query.filter_by(session_id=session_id, status='active').first()
	if guest_cart and guest_cart.id != user_cart.id:
		user_cart.merge_from(guest_cart)
		db.session.commit()
	return jsonify({'message': 'merged', 'cart': user_cart.to_dict()}), 200