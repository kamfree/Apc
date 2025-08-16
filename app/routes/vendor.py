from flask import request, jsonify, Blueprint
from app import db
from app.models import User, VendorProfile, UserRoles
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps

vendor_bp = Blueprint('vendor', __name__)

def role_required(required_role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_user_email = get_jwt_identity()
            user = User.query.filter_by(email=current_user_email).first()
            if not user or user.role != required_role:
                return jsonify({'message': 'Access forbidden: insufficient permissions'}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

@vendor_bp.route('/register', methods=['POST'])
@jwt_required()
def request_vendor_status():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    if user.vendor_profile:
        return jsonify({'message': 'Vendor profile already exists'}), 400

    data = request.get_json()
    if not data or not 'shop_name' in data:
        return jsonify({'message': 'Shop name is required'}), 400

    vendor_profile = VendorProfile(
        user_id=user.id,
        shop_name=data['shop_name'],
        description=data.get('description', '')
    )
    db.session.add(vendor_profile)
    db.session.commit()

    return jsonify({'message': 'Vendor registration request submitted. Waiting for approval.'}), 201

@vendor_bp.route('/approve/<int:user_id>', methods=['POST'])
@jwt_required()
@role_required(UserRoles.ADMIN)
def approve_vendor(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if not user.vendor_profile:
        return jsonify({'message': 'User has not applied to be a vendor'}), 400

    if user.vendor_profile.is_approved:
        return jsonify({'message': 'Vendor is already approved'}), 400

    user.vendor_profile.is_approved = True
    user.role = UserRoles.VENDOR
    db.session.commit()

    return jsonify({'message': f'Vendor {user.vendor_profile.shop_name} approved.'}), 200

from app.models import Product, Order, OrderItem, SKU, OrderItemStatus

@vendor_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@role_required(UserRoles.VENDOR)
def vendor_dashboard():
    # This is a placeholder. Full implementation requires Order and Product models.
    # TODO: Implement sales stats and low stock alerts.
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    return jsonify({
        'message': f'Welcome to your vendor dashboard, {user.vendor_profile.shop_name}!',
        'sales_stats': 'Not implemented',
        'low_stock_alerts': 'Not implemented'
    })

@vendor_bp.route('/orders', methods=['GET'])
@jwt_required()
@role_required(UserRoles.VENDOR)
def get_vendor_orders():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    vendor_profile = user.vendor_profile

    if not vendor_profile:
        return jsonify({'message': 'Vendor profile not found'}), 404

    # Find all orders containing items from this vendor
    orders = db.session.query(Order).join(Order.items).join(OrderItem.sku).join(SKU.product)\
        .filter(Product.vendor_id == vendor_profile.id).distinct().all()

    response_data = []
    for order in orders:
        order_data = {
            'id': order.id,
            'customer_email': order.user.email,
            'status': order.status.value,
            'date': order.created_at.isoformat(),
            'shipping_address': {
                'address_line_1': order.shipping_address.address_line_1,
                'city': order.shipping_address.city,
                'state': order.shipping_address.state,
                'zip_code': order.shipping_address.zip_code
            },
            'items': []
        }
        # Filter for items belonging to this vendor
        for item in order.items:
            if item.sku.product.vendor_id == vendor_profile.id:
                order_data['items'].append({
                    'id': item.id,
                    'product_name': item.sku.product.name,
                    'sku': item.sku.sku_code,
                    'quantity': item.quantity,
                    'fulfillment_status': item.fulfillment_status.value
                })
        response_data.append(order_data)

    return jsonify(response_data), 200

@vendor_bp.route('/order_items/<int:item_id>/status', methods=['PATCH'])
@jwt_required()
@role_required(UserRoles.VENDOR)
def update_order_item_status(item_id):
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    vendor_profile = user.vendor_profile

    data = request.get_json()
    new_status_str = data.get('status')
    if not new_status_str:
        return jsonify({'message': 'Status is required'}), 400

    try:
        new_status = OrderItemStatus[new_status_str.upper()]
    except KeyError:
        return jsonify({'message': 'Invalid status value'}), 400

    order_item = OrderItem.query.get_or_404(item_id)

    # Security check: ensure the item belongs to the vendor
    if order_item.sku.product.vendor_id != vendor_profile.id:
        return jsonify({'message': 'Access forbidden: this item does not belong to you'}), 403

    order_item.fulfillment_status = new_status
    db.session.commit()

    # Optional: Check if the parent order's status should be updated
    order = order_item.order
    if all(item.fulfillment_status == OrderItemStatus.SHIPPED for item in order.items):
        order.status = OrderStatus.SHIPPED
        db.session.commit()
    elif all(item.fulfillment_status == OrderItemStatus.DELIVERED for item in order.items):
        order.status = OrderStatus.DELIVERED
        db.session.commit()

    return jsonify({'message': f'Item {item_id} status updated to {new_status.value}'}), 200
