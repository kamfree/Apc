from flask import request, jsonify, Blueprint, Response, render_template
from app import db
from app.models import OrderItem, Order, Product, Inventory, SKU, User, UserRoles
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.routes.vendor import role_required
from sqlalchemy import func
from datetime import datetime
import csv
import io
from weasyprint import HTML

reports_bp = Blueprint('reports', __name__)

def generate_pdf(title, headers, data):
    """Helper to generate a PDF from data."""
    html_out = render_template('report.html', title=title, headers=headers, data=data)
    pdf = HTML(string=html_out).write_pdf()
    return Response(pdf, mimetype='application/pdf', headers={'Content-Disposition': 'attachment;filename=report.pdf'})

def generate_csv(headers, data):
    """Helper to generate a CSV from data."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for row in data:
        writer.writerow(row)
    return Response(output.getvalue(), mimetype='text/csv', headers={'Content-Disposition': 'attachment;filename=report.csv'})

@reports_bp.route('/sales', methods=['GET'])
@jwt_required()
def sales_report():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()

    query = db.session.query(
        Product.name,
        func.sum(OrderItem.quantity).label('total_quantity_sold'),
        func.sum(OrderItem.quantity * OrderItem.price).label('total_revenue')
    ).join(OrderItem.sku).join(SKU.product).join(OrderItem.order)

    # Filter by date
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if start_date:
        query = query.filter(Order.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Order.created_at <= datetime.fromisoformat(end_date))

    # Role-based filtering
    if user.role == UserRoles.VENDOR:
        query = query.filter(Product.vendor_id == user.vendor_profile.id)
    elif user.role == UserRoles.ADMIN:
        vendor_id = request.args.get('vendor_id', type=int)
        if vendor_id:
            query = query.filter(Product.vendor_id == vendor_id)
    else: # Customer
        return jsonify({'message': 'Access forbidden'}), 403

    results = query.group_by(Product.name).all()

    headers = ['Product Name', 'Total Quantity Sold', 'Total Revenue']
    data = [[r.name, r.total_quantity_sold, f"{r.total_revenue:.2f}"] for r in results]

    # Export format
    export_format = request.args.get('format', 'json')
    if export_format == 'pdf':
        return generate_pdf('Sales Report', headers, data)
    if export_format == 'csv':
        return generate_csv(headers, data)

    return jsonify([dict(zip(headers, row)) for row in data]), 200


@reports_bp.route('/inventory/low-stock', methods=['GET'])
@jwt_required()
def low_stock_report():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()

    threshold = request.args.get('threshold', 10, type=int)

    query = db.session.query(
        Product.name,
        SKU.sku_code,
        Inventory.quantity
    ).join(SKU.product).join(Inventory)

    query = query.filter(Inventory.quantity <= threshold)

    # Role-based filtering
    if user.role == UserRoles.VENDOR:
        query = query.filter(Product.vendor_id == user.vendor_profile.id)
    elif user.role != UserRoles.ADMIN: # Only Admin and Vendor can access
        return jsonify({'message': 'Access forbidden'}), 403

    results = query.order_by(Inventory.quantity.asc()).all()

    headers = ['Product Name', 'SKU', 'Quantity Remaining']
    data = [[r.name, r.sku_code, r.quantity] for r in results]

    # Export format
    export_format = request.args.get('format', 'json')
    if export_format == 'pdf':
        return generate_pdf('Low Stock Report', headers, data)
    if export_format == 'csv':
        return generate_csv(headers, data)

    return jsonify([dict(zip(headers, row)) for row in data]), 200
