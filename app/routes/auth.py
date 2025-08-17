from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
	create_access_token,
	create_refresh_token,
	get_jwt_identity,
	jwt_required,
)

from .. import db
from ..models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.post('/register')
def register():
	data = request.get_json(silent=True) or {}
	email = (data.get('email') or '').strip().lower()
	password = data.get('password')
	first_name = data.get('first_name')
	last_name = data.get('last_name')

	if not email or not password:
		return jsonify({'message': 'email and password are required'}), 400

	if User.query.filter_by(email=email).first():
		return jsonify({'message': 'email already registered'}), 409

	user = User(email=email, role='customer', first_name=first_name, last_name=last_name)
	user.set_password(password)
	db.session.add(user)
	db.session.commit()

	return jsonify({'message': 'registration successful', 'user': user.to_dict()}), 201


@auth_bp.post('/login')
def login():
	data = request.get_json(silent=True) or {}
	email = (data.get('email') or '').strip().lower()
	password = data.get('password')

	if not email or not password:
		return jsonify({'message': 'email and password are required'}), 400

	user = User.query.filter_by(email=email).first()
	if not user or not user.check_password(password):
		return jsonify({'message': 'invalid credentials'}), 401

	additional_claims = {'role': user.role}
	access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
	refresh_token = create_refresh_token(identity=str(user.id), additional_claims=additional_claims)

	# Optional: merge guest cart into user cart if provided
	guest_session_id = data.get('guest_session_id')
	if guest_session_id:
		try:
			from ..models import Cart
			from .. import db
			user_cart = Cart.query.filter_by(user_id=user.id, status='active').first()
			guest_cart = Cart.query.filter_by(session_id=guest_session_id, status='active').first()
			if not user_cart and guest_cart:
				guest_cart.user_id = user.id
				db.session.commit()
			elif guest_cart and user_cart and guest_cart.id != user_cart.id:
				user_cart.merge_from(guest_cart)
				db.session.commit()
		except Exception:
			pass

	return jsonify({
		'user': user.to_dict(),
		'access_token': access_token,
		'refresh_token': refresh_token,
	}), 200


@auth_bp.post('/refresh')
@jwt_required(refresh=True)
def refresh():
	user_id = get_jwt_identity()
	user = User.query.get(int(user_id))
	if not user:
		return jsonify({'message': 'user not found'}), 404
	additional_claims = {'role': user.role}
	new_access = create_access_token(identity=str(user.id), additional_claims=additional_claims)
	return jsonify({'access_token': new_access}), 200


@auth_bp.get('/me')
@jwt_required()
def me():
	user_id = get_jwt_identity()
	user = User.query.get(int(user_id))
	if not user:
		return jsonify({'message': 'user not found'}), 404
	return jsonify({'user': user.to_dict()}), 200