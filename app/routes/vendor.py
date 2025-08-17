from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from .. import db
from ..models import User, VendorProfile

vendor_bp = Blueprint('vendor', __name__)


def _get_current_user():
	user_id = get_jwt_identity()
	return User.query.get(int(user_id))


def _require_role(user: User, roles: list[str]):
	if not user or user.role not in roles:
		return False
	return True


@vendor_bp.post('/request')
@jwt_required()
def request_vendor():
	user = _get_current_user()
	if not user:
		return jsonify({'message': 'user not found'}), 404

	payload = request.get_json(silent=True) or {}
	company_name = payload.get('company_name')
	bio = payload.get('bio')

	if not company_name:
		return jsonify({'message': 'company_name is required'}), 400

	profile = user.vendor_profile
	if not profile:
		profile = VendorProfile(user=user)
		db.session.add(profile)

	profile.company_name = company_name
	profile.bio = bio
	profile.is_approved = False
	db.session.commit()

	return jsonify({'message': 'vendor request submitted', 'profile': {
		'id': profile.id,
		'company_name': profile.company_name,
		'bio': profile.bio,
		'is_approved': profile.is_approved,
	}}), 201


@vendor_bp.post('/approve/<int:user_id>')
@jwt_required()
def approve_vendor(user_id: int):
	admin_user = _get_current_user()
	if not _require_role(admin_user, ['admin']):
		return jsonify({'message': 'admin privileges required'}), 403

	vendor_user = User.query.get(user_id)
	if not vendor_user:
		return jsonify({'message': 'user not found'}), 404

	profile = vendor_user.vendor_profile
	if not profile:
		return jsonify({'message': 'vendor profile not found'}), 404

	profile.is_approved = True
	vendor_user.role = 'vendor'
	db.session.commit()

	return jsonify({'message': 'vendor approved', 'user': vendor_user.to_dict(), 'profile': {
		'id': profile.id,
		'is_approved': profile.is_approved,
	}}), 200


@vendor_bp.get('/dashboard')
@jwt_required()
def vendor_dashboard():
	user = _get_current_user()
	if not _require_role(user, ['vendor']):
		return jsonify({'message': 'vendor privileges required'}), 403
	if not user.vendor_profile or not user.vendor_profile.is_approved:
		return jsonify({'message': 'vendor not approved'}), 403

	# Placeholder metrics until product and order models are implemented in later steps
	sales_stats = {
		'total_sales': 0.0,
		'orders_count': 0,
	}
	low_stock_alerts = []

	# Attempt to compute real metrics if models exist
	try:
		from .. import models as models_module
		Product = getattr(models_module, 'Product', None)
		Inventory = getattr(models_module, 'Inventory', None)
		OrderItem = getattr(models_module, 'OrderItem', None)

		if Product is not None and Inventory is not None and OrderItem is not None:
			# Low stock: products owned by this vendor with inventory below threshold
			threshold = int((request.args.get('low_stock_threshold') or 5))
			low_stock = db.session.query(Product).join(Inventory).filter(
				Product.vendor_id == user.id,
				Inventory.quantity <= threshold
			).limit(20).all()
			low_stock_alerts = [
				{'product_id': p.id, 'name': p.name} for p in low_stock
			]

			# Sales stats: sum of order items total for this vendor
			result = db.session.query(db.func.coalesce(db.func.sum(OrderItem.total_price), 0.0), db.func.count(OrderItem.id)) \
				.join(Product, Product.id == OrderItem.product_id) \
				.filter(Product.vendor_id == user.id).first()
			sales_stats = {
				'total_sales': float(result[0] or 0.0),
				'orders_count': int(result[1] or 0),
			}
	except Exception:
		# Keep placeholders if models or tables are not ready yet
		pass

	return jsonify({'sales_stats': sales_stats, 'low_stock_alerts': low_stock_alerts}), 200