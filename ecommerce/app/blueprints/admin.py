from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import func
from ..extensions import db
from ..models import User, Vendor, Product, Order, OrderItem, ROLE_ADMIN, ORDER_STATUSES
from ..forms import VendorApprovalForm, OrderStatusForm
from ..utils import role_required


admin_bp = Blueprint("admin", __name__, template_folder="../templates/admin")


@admin_bp.before_request
@login_required
@role_required(ROLE_ADMIN)
def require_admin():
    pass


@admin_bp.route("/")
def dashboard():
    users_count = User.query.count()
    vendors_count = Vendor.query.count()
    products_count = Product.query.count()
    orders_count = Order.query.count()

    # Revenue
    revenue = db.session.query(func.coalesce(func.sum(Order.total_amount), 0)).scalar() or 0

    return render_template("admin/dashboard.html", users_count=users_count, vendors_count=vendors_count, products_count=products_count, orders_count=orders_count, revenue=revenue)


@admin_bp.route("/users")
def users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users)


@admin_bp.route("/vendors", methods=["GET", "POST"]) 
def vendors():
    vendors = Vendor.query.all()
    return render_template("admin/vendors.html", vendors=vendors)


@admin_bp.route("/vendors/<int:vendor_id>/approve", methods=["POST"]) 
def approve_vendor(vendor_id: int):
    vendor = Vendor.query.get_or_404(vendor_id)
    vendor.approved = True
    db.session.commit()
    flash("Vendor approved.", "success")
    return redirect(url_for("admin.vendors"))


@admin_bp.route("/products")
def products():
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template("admin/products.html", products=products)


@admin_bp.route("/orders", methods=["GET", "POST"]) 
def orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template("admin/orders.html", orders=orders)


@admin_bp.route("/orders/<int:order_id>", methods=["GET", "POST"]) 
def order_detail(order_id: int):
    order = Order.query.get_or_404(order_id)
    form = OrderStatusForm(status=order.status)
    if form.validate_on_submit():
        order.status = form.status.data
        db.session.commit()
        # Email notification to customer
        from ..email import send_email
        send_email(to=order.user.email, subject=f"Order #{order.id} status updated", body=f"Your order status is now: {order.status}")
        flash("Order status updated.", "success")
        return redirect(url_for("admin.order_detail", order_id=order.id))
    return render_template("admin/order_detail.html", order=order, form=form)


@admin_bp.route("/reports")
def reports():
    # Total sales
    total_sales = db.session.query(func.coalesce(func.sum(Order.total_amount), 0)).scalar() or 0

    # Sales per vendor
    sales_per_vendor = db.session.query(
        Vendor.name,
        func.coalesce(func.sum(OrderItem.unit_price * OrderItem.quantity), 0)
    ).join(Product, Product.vendor_id == Vendor.id).join(OrderItem, OrderItem.product_id == Product.id).group_by(Vendor.id).all()

    # Best-selling products
    best_selling = db.session.query(
        Product.title,
        func.sum(OrderItem.quantity).label("qty")
    ).join(OrderItem, OrderItem.product_id == Product.id).group_by(Product.id).order_by(func.sum(OrderItem.quantity).desc()).limit(10).all()

    # Monthly revenue (last 12 months)
    monthly = db.session.query(
        func.strftime('%Y-%m', Order.created_at).label('month'),
        func.coalesce(func.sum(Order.total_amount), 0)
    ).group_by('month').order_by('month').all()

    return render_template("admin/reports.html", total_sales=total_sales, sales_per_vendor=sales_per_vendor, best_selling=best_selling, monthly=monthly)