from decimal import Decimal
from flask import Blueprint, request, jsonify, make_response, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from weasyprint import HTML

from .. import db
from ..models import Cart, CartItem, Order, OrderItem, Payment, Address, ShippingMethod, ProductVariant, Product

orders_bp = Blueprint('orders', __name__)


def _current_user_id():
	uid = get_jwt_identity()
	return int(uid) if uid is not None else None


def _require_role(roles: list[str]) -> bool:
	claims = get_jwt() or {}
	return (claims.get('role') in roles)


def _ensure_shipping_methods():
	if ShippingMethod.query.count() == 0:
		basic = ShippingMethod(name='Standard', price=Decimal('9.99'), estimated_days=5, is_active=True)
		db.session.add(basic)
		db.session.commit()


@orders_bp.post('/checkout')
@jwt_required()
def checkout():
	user_id = _current_user_id()
	payload = request.get_json(silent=True) or {}

	# Addresses
	shipping_address_id = payload.get('shipping_address_id')
	billing_address_id = payload.get('billing_address_id')
	shipping_address_data = payload.get('shipping_address') or {}
	billing_address_data = payload.get('billing_address') or {}
	shipping_method_id = payload.get('shipping_method_id')

	cart = Cart.query.filter_by(user_id=user_id, status='active').first()
	if not cart or not cart.items:
		return jsonify({'message': 'cart is empty'}), 400

	_ensure_shipping_methods()
	shipping_method = ShippingMethod.query.get(shipping_method_id) if shipping_method_id else ShippingMethod.query.filter_by(is_active=True).first()
	if not shipping_method:
		return jsonify({'message': 'invalid shipping method'}), 400

	# Create or load addresses
	def upsert_address(addr_id, data):
		if addr_id:
			addr = Address.query.get(addr_id)
			if not addr or addr.user_id != user_id:
				return None
			return addr
		data = data or {}
		if not data.get('line1') or not data.get('city') or not data.get('postal_code'):
			return None
		addr = Address(user_id=user_id,
			full_name=data.get('full_name'),
			line1=data.get('line1'), line2=data.get('line2'), city=data.get('city'),
			state=data.get('state'), postal_code=data.get('postal_code'), country=(data.get('country') or 'US'))
		db.session.add(addr)
		db.session.flush()
		return addr

	shipping_address = upsert_address(shipping_address_id, shipping_address_data)
	billing_address = upsert_address(billing_address_id, billing_address_data or shipping_address_data)
	if not shipping_address or not billing_address:
		return jsonify({'message': 'invalid addresses'}), 400

	# Begin transactional checkout
	try:
		with db.session.begin_nested():
			order = Order(user_id=user_id, status='pending', payment_status='pending', currency='USD', shipping_method_id=shipping_method.id,
				shipping_address_id=shipping_address.id, billing_address_id=billing_address.id, total_amount=Decimal('0.00'))
			db.session.add(order)
			db.session.flush()

			total = Decimal('0.00')
			for item in cart.items:
				variant = ProductVariant.query.get(item.variant_id)
				if not variant or not variant.inventory or variant.inventory.quantity < item.quantity:
					raise ValueError('insufficient stock')

				product = Product.query.get(variant.product_id)
				unit_price = Decimal(str(item.unit_price))
				tline = unit_price * Decimal(item.quantity)
				order_item = OrderItem(order_id=order.id, product_id=product.id, variant_id=variant.id,
					vendor_id=product.vendor_id, quantity=item.quantity, unit_price=unit_price, total_price=tline,
					fulfillment_status='pending')
				db.session.add(order_item)
				total += tline

				# Reduce stock
				variant.inventory.quantity = int(variant.inventory.quantity) - int(item.quantity)
				if variant.inventory.quantity < 0:
					raise ValueError('stock underflow')

			total += Decimal(str(shipping_method.price or 0))
			order.total_amount = total

			# Mock payment processing
			payment = Payment(order_id=order.id, provider='mock', amount=total, currency='USD', status='paid', transaction_id='MOCK-TXN-OK')
			db.session.add(payment)

			order.status = 'paid'
			order.payment_status = 'paid'

			# Mark cart as ordered
			cart.status = 'ordered'
		db.session.commit()
	except ValueError as ve:
		db.session.rollback()
		return jsonify({'message': str(ve)}), 409
	except Exception as e:
		db.session.rollback()
		return jsonify({'message': 'checkout failed'}), 500

	return jsonify({'message': 'order placed', 'order': order.to_dict()}), 201


@orders_bp.get('')
@jwt_required()
def list_orders():
	user_id = _current_user_id()
	if _require_role(['admin']):
		orders = Order.query.order_by(Order.created_at.desc()).limit(100).all()
		return jsonify({'items': [o.to_dict() for o in orders]}), 200
	elif _require_role(['vendor']):
		# Orders containing this vendor's items
		orders = Order.query.join(OrderItem).filter(OrderItem.vendor_id == user_id).order_by(Order.created_at.desc()).limit(100).all()
		return jsonify({'items': [o.to_dict() for o in orders]}), 200
	else:
		orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).limit(100).all()
		return jsonify({'items': [o.to_dict() for o in orders]}), 200


@orders_bp.get('/<int:order_id>')
@jwt_required()
def get_order(order_id: int):
	user_id = _current_user_id()
	order = Order.query.get_or_404(order_id)
	if _require_role(['admin']):
		pass
	elif _require_role(['vendor']):
		if all(item.vendor_id != user_id for item in order.items):
			return jsonify({'message': 'not authorized'}), 403
	else:
		if order.user_id != user_id:
			return jsonify({'message': 'not authorized'}), 403
	return jsonify({'order': order.to_dict()}), 200


@orders_bp.post('/<int:order_id>/cancel')
@jwt_required()
def cancel_order(order_id: int):
	user_id = _current_user_id()
	order = Order.query.get_or_404(order_id)
	if not _require_role(['admin']) and order.user_id != user_id:
		return jsonify({'message': 'not authorized'}), 403
	if order.status in ['shipped', 'delivered']:
		return jsonify({'message': 'cannot cancel shipped or delivered orders'}), 400
	if order.status == 'cancelled':
		return jsonify({'message': 'already cancelled'}), 400

	# Restock items and cancel
	with db.session.begin_nested():
		for item in order.items:
			variant = ProductVariant.query.get(item.variant_id)
			if variant and variant.inventory:
				variant.inventory.quantity += int(item.quantity)
		order.status = 'cancelled'
		order.payment_status = 'refunded'
		db.session.add(Payment(order_id=order.id, provider='mock', amount=order.total_amount, currency=order.currency, status='refunded', transaction_id='MOCK-REFUND'))
	db.session.commit()
	return jsonify({'message': 'cancelled', 'order': order.to_dict()}), 200


@orders_bp.patch('/<int:order_id>/items/<int:item_id>/fulfillment')
@jwt_required()
def update_fulfillment(order_id: int, item_id: int):
	user_id = _current_user_id()
	if not _require_role(['vendor', 'admin']):
		return jsonify({'message': 'not authorized'}), 403
	item = OrderItem.query.get_or_404(item_id)
	if item.order_id != order_id:
		return jsonify({'message': 'item not in order'}), 400
	if not _require_role(['admin']) and item.vendor_id != user_id:
		return jsonify({'message': 'not authorized'}), 403
	data = request.get_json(silent=True) or {}
	status = data.get('fulfillment_status')
	if status not in ['pending', 'fulfilled', 'shipped']:
		return jsonify({'message': 'invalid status'}), 400
	item.fulfillment_status = status
	db.session.commit()
	return jsonify({'message': 'updated', 'item': item.to_dict()}), 200


@orders_bp.get('/<int:order_id>/invoice.pdf')
@jwt_required()
def invoice_pdf(order_id: int):
	user_id = _current_user_id()
	order = Order.query.get_or_404(order_id)
	if not _require_role(['admin']):
		if order.user_id != user_id and not (_require_role(['vendor']) and any(i.vendor_id == user_id for i in order.items)):
			return jsonify({'message': 'not authorized'}), 403

	html = render_template('invoice.html', order=order)
	pdf = HTML(string=html).write_pdf()
	response = make_response(pdf)
	response.headers['Content-Type'] = 'application/pdf'
	response.headers['Content-Disposition'] = f'attachment; filename=invoice-{order.id}.pdf'
	return response