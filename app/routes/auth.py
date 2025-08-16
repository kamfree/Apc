from flask import request, jsonify, Blueprint
from app import db
from app.models import User
from flask_jwt_extended import create_access_token, create_refresh_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not 'email' in data or not 'password' in data:
        return jsonify({'message': 'Email and password are required'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'User already exists'}), 400

    user = User(email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

from app.models import Cart, CartItem

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not 'email' in data or not 'password' in data:
        return jsonify({'message': 'Email and password are required'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if user is None or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401

    # --- Cart Merging Logic ---
    session_id = request.headers.get('X-Cart-Session-ID')
    guest_cart = None
    if session_id:
        guest_cart = Cart.query.filter_by(session_id=session_id).first()

    if guest_cart:
        user_cart = Cart.query.filter_by(user_id=user.id).first()
        if not user_cart:
            # If user has no cart, just assign the guest cart to them
            guest_cart.user_id = user.id
            guest_cart.session_id = None
            db.session.commit()
        else:
            # Merge guest cart into user's cart
            for guest_item in guest_cart.items:
                user_item = CartItem.query.filter_by(cart_id=user_cart.id, sku_id=guest_item.sku_id).first()
                if user_item:
                    user_item.quantity += guest_item.quantity
                else:
                    # Move item to user's cart
                    guest_item.cart_id = user_cart.id

            # Delete the now-empty guest cart
            db.session.delete(guest_cart)
            db.session.commit()
    # --- End Cart Merging Logic ---

    access_token = create_access_token(identity=user.email)
    refresh_token = create_refresh_token(identity=user.email)

    return jsonify(access_token=access_token, refresh_token=refresh_token), 200
