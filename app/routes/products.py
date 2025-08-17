import re
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from .. import db
from ..models import Product, Category, ProductImage, ProductVariant, Inventory

products_bp = Blueprint('products', __name__)


def _slugify(text: str) -> str:
	text = text.strip().lower()
	text = re.sub(r'[^a-z0-9\s-]', '', text)
	text = re.sub(r'[\s-]+', '-', text)
	return text


def _current_user_id() -> int:
	user_id = get_jwt_identity()
	return int(user_id) if user_id is not None else None


def _require_role(roles: list[str]) -> bool:
	claims = get_jwt() or {}
	return (claims.get('role') in roles)


@products_bp.get('')
def list_products():
	q = (request.args.get('q') or '').strip().lower()
	category_id = request.args.get('category_id', type=int)
	vendor_id = request.args.get('vendor_id', type=int)
	min_price = request.args.get('min_price', type=float)
	max_price = request.args.get('max_price', type=float)
	page = request.args.get('page', default=1, type=int)
	per_page = request.args.get('per_page', default=20, type=int)

	query = Product.query.filter_by(is_active=True)

	if q:
		pattern = f"%{q}%"
		query = query.filter(db.or_(Product.name.ilike(pattern), Product.description.ilike(pattern)))
	if category_id:
		query = query.filter(Product.category_id == category_id)
	if vendor_id:
		query = query.filter(Product.vendor_id == vendor_id)
	if min_price is not None:
		query = query.filter(Product.price >= min_price)
	if max_price is not None:
		query = query.filter(Product.price <= max_price)

	total = query.count()
	items = query.order_by(Product.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

	return jsonify({
		'items': [p.to_dict() for p in items],
		'meta': {'total': total, 'page': page, 'per_page': per_page}
	}), 200


@products_bp.get('/<int:product_id>')
def get_product(product_id: int):
	product = Product.query.get_or_404(product_id)
	return jsonify({'product': product.to_dict()}), 200


@products_bp.post('')
@jwt_required()
def create_product():
	if not _require_role(['vendor', 'admin']):
		return jsonify({'message': 'vendor or admin required'}), 403
	vendor_id = _current_user_id()

	data = request.get_json(silent=True) or {}
	name = (data.get('name') or '').strip()
	description = data.get('description')
	price = data.get('price', 0)
	currency = (data.get('currency') or 'USD').upper()
	category_id = data.get('category_id')
	images = data.get('images') or []
	variants = data.get('variants') or []
	quantity = data.get('quantity', 0)

	if not name:
		return jsonify({'message': 'name is required'}), 400

	slug = _slugify(name)
	# Ensure slug uniqueness
	existing = Product.query.filter_by(slug=slug).first()
	if existing:
		slug = f"{slug}-{existing.id + 1}"

	product = Product(
		vendor_id=vendor_id,
		category_id=category_id,
		name=name,
		slug=slug,
		description=description,
		price=price,
		currency=currency,
		is_active=True,
	)
	db.session.add(product)
	db.session.flush()  # get product.id

	# Images
	for idx, img in enumerate(images):
		if not isinstance(img, dict):
			continue
		url = img.get('url')
		if not url:
			continue
		image = ProductImage(product_id=product.id, url=url, is_primary=bool(img.get('is_primary')), sort_order=int(img.get('sort_order') or idx))
		db.session.add(image)

	created_variant_ids = []
	# Variants
	if variants:
		for v in variants:
			sku = (v.get('sku') or '').strip() or None
			vname = v.get('name')
			attributes = v.get('attributes') if isinstance(v.get('attributes'), dict) else None
			price_override = v.get('price_override')
			qty = int(v.get('quantity') or 0)
			if not sku:
				sku = f"SKU-{product.id}-{len(created_variant_ids)+1}"
			variant = ProductVariant(product_id=product.id, sku=sku, name=vname, attributes=attributes, price_override=price_override)
			db.session.add(variant)
			db.session.flush()
			inv = Inventory(variant_id=variant.id, quantity=qty)
			db.session.add(inv)
			created_variant_ids.append(variant.id)
	else:
		# Default variant
		sku = f"SKU-{product.id}-1"
		variant = ProductVariant(product_id=product.id, sku=sku, name=None, attributes=None, price_override=None)
		db.session.add(variant)
		db.session.flush()
		inv = Inventory(variant_id=variant.id, quantity=int(quantity or 0))
		db.session.add(inv)
		created_variant_ids.append(variant.id)

	db.session.commit()
	return jsonify({'message': 'product created', 'product': product.to_dict()}), 201


@products_bp.patch('/<int:product_id>')
@jwt_required()
def update_product(product_id: int):
	product = Product.query.get_or_404(product_id)
	claims = get_jwt() or {}
	user_id = _current_user_id()
	is_admin = claims.get('role') == 'admin'
	if not is_admin and product.vendor_id != user_id:
		return jsonify({'message': 'not authorized'}), 403

	data = request.get_json(silent=True) or {}
	for field in ['name', 'description', 'currency', 'is_active', 'category_id']:
		if field in data:
			setattr(product, field, data[field])
	if 'price' in data and data['price'] is not None:
		product.price = data['price']
	if 'name' in data:
		product.slug = _slugify(product.name)

	db.session.commit()
	return jsonify({'message': 'updated', 'product': product.to_dict()}), 200


@products_bp.delete('/<int:product_id>')
@jwt_required()
def delete_product(product_id: int):
	product = Product.query.get_or_404(product_id)
	claims = get_jwt() or {}
	user_id = _current_user_id()
	is_admin = claims.get('role') == 'admin'
	if not is_admin and product.vendor_id != user_id:
		return jsonify({'message': 'not authorized'}), 403

	db.session.delete(product)
	db.session.commit()
	return jsonify({'message': 'deleted'}), 200