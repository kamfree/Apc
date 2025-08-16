from flask import request, jsonify, Blueprint
from app import db
from app.models import Cart, CartItem, User, SKU
from flask_jwt_extended import get_jwt_identity, jwt_required
import uuid

cart_bp = Blueprint('cart', __name__)

def serialize_cart(cart):
    """Helper to serialize a cart and its items."""
    if not cart:
        return None

    total_price = 0
    items_data = []
    for item in cart.items:
        item_total = item.sku.price * item.quantity
        total_price += item_total
        items_data.append({
            'id': item.id,
            'sku_id': item.sku_id,
            'quantity': item.quantity,
            'name': item.sku.product.name,
            'price': item.sku.price,
            'item_total': item_total,
            'attributes': item.sku.attributes
        })

    return {
        'id': cart.id,
        'user_id': cart.user_id,
        'session_id': cart.session_id,
        'items': items_data,
        'total_price': total_price
    }

def get_current_cart():
    """
    Identifies and returns the correct cart for the current session.
    Handles both authenticated users and guests.
    Returns a tuple (cart, new_session_id) where new_session_id is only present for new guests.
    """
    new_session_id = None
    current_user_email = get_jwt_identity()

    if current_user_email:
        # Logged-in user
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            # This case should ideally not happen if token is valid
            return None, None
        cart = Cart.query.filter_by(user_id=user.id).first()
        if not cart:
            cart = Cart(user_id=user.id)
            db.session.add(cart)
            db.session.commit()
    else:
        # Guest user
        session_id = request.headers.get('X-Cart-Session-ID')
        if session_id:
            cart = Cart.query.filter_by(session_id=session_id).first()
        else:
            cart = None

        if not cart:
            new_session_id = str(uuid.uuid4())
            cart = Cart(session_id=new_session_id)
            db.session.add(cart)
            db.session.commit()

    return cart, new_session_id

@cart_bp.route('', methods=['GET'])
@jwt_required(optional=True)
def view_cart():
    cart, new_session_id = get_current_cart()
    response_data = serialize_cart(cart)

    if not response_data:
        return jsonify({'message': 'Cart not found'}), 404

    response = jsonify(response_data)
    if new_session_id:
        response.headers['X-Cart-Session-ID'] = new_session_id

    return response, 200

@cart_bp.route('/items', methods=['POST'])
@jwt_required(optional=True)
def add_item_to_cart():
    data = request.get_json()
    if not data or 'sku_id' not in data or 'quantity' not in data:
        return jsonify({'message': 'sku_id and quantity are required'}), 400

    sku_id = data['sku_id']
    quantity = data['quantity']

    sku = SKU.query.get(sku_id)
    if not sku:
        return jsonify({'message': 'SKU not found'}), 404

    # Check stock
    if not sku.inventory or sku.inventory.quantity < quantity:
        return jsonify({'message': 'Not enough stock available'}), 400

    cart, new_session_id = get_current_cart()

    # Check if item is already in cart
    cart_item = CartItem.query.filter_by(cart_id=cart.id, sku_id=sku_id).first()

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(cart_id=cart.id, sku_id=sku_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()

    response = jsonify(serialize_cart(cart))
    if new_session_id:
        response.headers['X-Cart-Session-ID'] = new_session_id

    return response, 200

@cart_bp.route('/items/<int:item_id>', methods=['PUT'])
@jwt_required(optional=True)
def update_cart_item(item_id):
    data = request.get_json()
    if 'quantity' not in data:
        return jsonify({'message': 'Quantity is required'}), 400

    quantity = data['quantity']
    if quantity <= 0:
        return jsonify({'message': 'Quantity must be positive'}), 400

    cart, _ = get_current_cart()
    cart_item = CartItem.query.with_parent(cart).filter_by(id=item_id).first()

    if not cart_item:
        return jsonify({'message': 'Item not found in cart'}), 404

    # Check stock
    if not cart_item.sku.inventory or cart_item.sku.inventory.quantity < quantity:
        return jsonify({'message': 'Not enough stock available'}), 400

    cart_item.quantity = quantity
    db.session.commit()

    return jsonify(serialize_cart(cart)), 200

@cart_bp.route('/items/<int:item_id>', methods=['DELETE'])
@jwt_required(optional=True)
def remove_cart_item(item_id):
    cart, _ = get_current_cart()
    cart_item = CartItem.query.with_parent(cart).filter_by(id=item_id).first()

    if not cart_item:
        return jsonify({'message': 'Item not found in cart'}), 404

    db.session.delete(cart_item)
    db.session.commit()

    return jsonify(serialize_cart(cart)), 200
