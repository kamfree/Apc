import csv
import io
from datetime import datetime
from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt
from weasyprint import HTML

from .. import db
from ..models import Order, OrderItem, Product, ProductVariant, Inventory, User

reports_bp = Blueprint('reports', __name__)


def _require_admin() -> bool:
	claims = get_jwt() or {}
	return claims.get('role') == 'admin'


@reports_bp.get('/sales')
@jwt_required()
def sales_report():
	if not _require_admin():
		return jsonify({'message': 'admin required'}), 403
	group_by = (request.args.get('group_by') or 'date').lower()
	start = request.args.get('start')
	end = request.args.get('end')
	fmt = (request.args.get('format') or 'json').lower()

	filters = [Order.payment_status == 'paid']
	if start:
		filters.append(Order.created_at >= datetime.fromisoformat(start))
	if end:
		filters.append(Order.created_at <= datetime.fromisoformat(end))

	rows = []
	if group_by == 'vendor':
		q = db.session.query(OrderItem.vendor_id, db.func.coalesce(db.func.sum(OrderItem.total_price), 0.0).label('total')) \
			.join(Order, OrderItem.order_id == Order.id) \
			.filter(*filters) \
			.group_by(OrderItem.vendor_id) \
			.order_by(db.desc('total'))
		for vendor_id, total in q:
			rows.append({'vendor_id': vendor_id, 'vendor_email': (User.query.get(vendor_id).email if vendor_id else None), 'total': float(total or 0)})
	elif group_by == 'product':
		q = db.session.query(OrderItem.product_id, db.func.coalesce(db.func.sum(OrderItem.total_price), 0.0).label('total')) \
			.join(Order, OrderItem.order_id == Order.id) \
			.filter(*filters) \
			.group_by(OrderItem.product_id) \
			.order_by(db.desc('total'))
		for product_id, total in q:
			name = (Product.query.get(product_id).name if product_id else None)
			rows.append({'product_id': product_id, 'product_name': name, 'total': float(total or 0)})
	else:
		# date grouping
		q = db.session.query(db.func.date(Order.created_at).label('date'), db.func.coalesce(db.func.sum(Order.total_amount), 0.0).label('total')) \
			.filter(*filters) \
			.group_by(db.func.date(Order.created_at)) \
			.order_by(db.func.date(Order.created_at))
		for date, total in q:
			rows.append({'date': str(date), 'total': float(total or 0)})

	if fmt == 'csv':
		buf = io.StringIO()
		writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()) if rows else ['date','total'])
		writer.writeheader()
		for r in rows:
			writer.writerow(r)
		resp = make_response(buf.getvalue())
		resp.headers['Content-Type'] = 'text/csv'
		resp.headers['Content-Disposition'] = 'attachment; filename=sales.csv'
		return resp
	elif fmt == 'pdf':
		# simple HTML table
		html = '<h1>Sales Report</h1><table border="1" cellspacing="0" cellpadding="4">'
		if rows:
			html += '<tr>' + ''.join(f'<th>{k}</th>' for k in rows[0].keys()) + '</tr>'
			for r in rows:
				html += '<tr>' + ''.join(f'<td>{v}</td>' for v in r.values()) + '</tr>'
		html += '</table>'
		pdf = HTML(string=html).write_pdf()
		resp = make_response(pdf)
		resp.headers['Content-Type'] = 'application/pdf'
		resp.headers['Content-Disposition'] = 'attachment; filename=sales.pdf'
		return resp
	else:
		return jsonify({'rows': rows, 'group_by': group_by}), 200


@reports_bp.get('/low-stock')
@jwt_required()
def low_stock():
	if not _require_admin():
		return jsonify({'message': 'admin required'}), 403
	threshold = request.args.get('threshold', 5, type=int)
	q = db.session.query(Product, ProductVariant, Inventory).join(ProductVariant, ProductVariant.product_id == Product.id) \
		.join(Inventory, Inventory.variant_id == ProductVariant.id) \
		.filter(Inventory.quantity <= threshold)
	rows = []
	for prod, variant, inv in q.limit(200).all():
		rows.append({'product_id': prod.id, 'product_name': prod.name, 'variant_id': variant.id, 'sku': variant.sku, 'quantity': inv.quantity})
	return jsonify({'rows': rows, 'threshold': threshold}), 200