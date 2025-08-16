from flask import request, jsonify, Blueprint, render_template, make_response
from app import db
from app.models import (
    Address, ShippingMethod, Order, OrderItem, Payment, Cart, Inventory, User,
    OrderStatus, PaymentStatus, SKU
)
from flask_jwt_extended import jwt_required, get_jwt_identity
from weasyprint import HTML
import uuid

orders_bp = Blueprint('orders', __name__)

# --- Address Management ---
@orders_bp.route('/addresses', methods=['POST'])
@jwt_required()
def add_address():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    data = request.get_json()

    address = Address(
        user_id=user.id,
        address_line_1=data['address_line_1'],
        city=data['city'],
        state=data['state'],
        zip_code=data['zip_code'],
        country=data['country']
    )
    db.session.add(address)
    db.session.commit()
    return jsonify({'message': 'Address added successfully'}), 201

@orders_bp.route('/addresses', methods=['GET'])
@jwt_required()
def get_addresses():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    addresses = Address.query.filter_by(user_id=user.id).all()
    return jsonify([{
        'id': a.id,
        'address_line_1': a.address_line_1,
        'city': a.city,
        'state': a.state,
        'zip_code': a.zip_code,
        'country': a.country
    } for a in addresses]), 200

# --- Shipping ---
@orders_bp.route('/shipping_methods', methods=['GET'])
def get_shipping_methods():
    # In a real app, you'd populate this from a table
    methods = [
        {'id': 1, 'name': 'Standard Shipping', 'price': 5.00},
        {'id': 2, 'name': 'Express Shipping', 'price': 15.00}
    ]
    # Let's ensure these exist in the DB for FK constraints
    for method_data in methods:
        method = ShippingMethod.query.get(method_data['id'])
        if not method:
            method = ShippingMethod(**method_data)
            db.session.add(method)
    db.session.commit()

    return jsonify(methods), 200

# --- Checkout ---
@orders_bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    data = request.get_json()

    required_fields = ['shipping_address_id']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Shipping address is required'}), 400

    cart = Cart.query.filter_by(user_id=user.id).first()
    if not cart or not cart.items:
        return jsonify({'message': 'Your cart is empty'}), 400

    shipping_address = Address.query.filter_by(id=data['shipping_address_id'], user_id=user.id).first()
    if not shipping_address:
        return jsonify({'message': 'Invalid shipping address'}), 400

    # Use a transaction for the whole process
    try:
        with db.session.begin_nested():
            # 1. Check stock and calculate total
            subtotal = 0
            for item in cart.items:
                # Lock inventory row for this SKU
                inventory = Inventory.query.filter_by(sku_id=item.sku_id).with_for_update().first()
                if not inventory or inventory.quantity < item.quantity:
                    raise ValueError(f'Not enough stock for SKU {item.sku.sku_code}')
                subtotal += item.sku.price * item.quantity

            # For now, let's assume a fixed shipping cost.
            shipping_cost = 5.0
            total_amount = subtotal + shipping_cost

            # 2. Create Order
            order = Order(
                user_id=user.id,
                total_amount=total_amount,
                shipping_address_id=shipping_address.id,
                status=OrderStatus.PENDING
            )
            db.session.add(order)
            db.session.flush() # Get order ID

            # 3. Create OrderItems and decrease stock
            for item in cart.items:
                inventory = Inventory.query.get(item.sku.inventory.id)
                inventory.quantity -= item.quantity

                order_item = OrderItem(
                    order_id=order.id,
                    sku_id=item.sku_id,
                    quantity=item.quantity,
                    price=item.sku.price
                )
                db.session.add(order_item)

            # 4. Mock Payment
            payment = Payment(
                order_id=order.id,
                amount=total_amount,
                status=PaymentStatus.SUCCESS, # Mock success
                transaction_id=f'txn_{uuid.uuid4()}'
            )
            db.session.add(payment)

            # 5. Update Order status
            order.status = OrderStatus.PAID

            # 6. Clear the cart
            for item in cart.items:
                db.session.delete(item)

        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred during checkout.', 'error': str(e)}), 500

    return jsonify({'message': 'Order created successfully', 'order_id': order.id}), 201

from app.models import OrderItemStatus, UserRoles

# --- Customer Order Management ---
@orders_bp.route('/history', methods=['GET'])
@jwt_required()
def get_order_history():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()

    # This could be more detailed, but let's keep it simple for now
    return jsonify([{
        'id': o.id,
        'total_amount': o.total_amount,
        'status': o.status.value,
        'date': o.created_at.isoformat()
    } for o in orders]), 200

@orders_bp.route('/<int:order_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_order(order_id):
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    order = Order.query.get_or_404(order_id)

    if order.user_id != user.id:
        return jsonify({'message': 'Access forbidden'}), 403

    # Only cancellable if not yet shipped
    if order.status not in [OrderStatus.PENDING, OrderStatus.PAID]:
        return jsonify({'message': f'Cannot cancel order with status: {order.status.value}'}), 400

    try:
        with db.session.begin_nested():
            order.status = OrderStatus.CANCELED
            # Restock items
            for item in order.items:
                item.fulfillment_status = OrderItemStatus.CANCELED
                inventory = Inventory.query.filter_by(sku_id=item.sku_id).first()
                if inventory:
                    inventory.quantity += item.quantity

            # Update payment status if applicable
            if order.payment:
                order.payment.status = PaymentStatus.FAILED # Or 'REFUNDED' in a real system

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred while canceling the order.', 'error': str(e)}), 500

    return jsonify({'message': 'Order canceled successfully'}), 200


# --- Invoice ---
@orders_bp.route('/<int:order_id>/invoice', methods=['GET'])
@jwt_required()
def get_invoice(order_id):
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    order = Order.query.get_or_404(order_id)

    if order.user_id != user.id and user.role != UserRoles.ADMIN:
        return jsonify({'message': 'Access forbidden'}), 403

    # Render HTML template
    html_out = render_template('invoice.html', order=order)

    # Generate PDF
    pdf = HTML(string=html_out).write_pdf()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=invoice_{order.id}.pdf'

    return response
