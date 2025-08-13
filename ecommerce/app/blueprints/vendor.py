from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Vendor, Product, OrderItem
from ..forms import ProductForm
from ..utils import role_required


vendor_bp = Blueprint("vendor", __name__, template_folder="../templates/vendor")


def _require_vendor():
    if not current_user.is_authenticated or not current_user.is_vendor:
        abort(403)
    if not current_user.vendor or not current_user.vendor.approved:
        abort(403)


@vendor_bp.route("/")
@login_required
@role_required("vendor")
def dashboard():
    if not current_user.vendor or not current_user.vendor.approved:
        flash("Your vendor account is pending approval.", "warning")
        return redirect(url_for("shop.product_list"))

    vendor = current_user.vendor
    products = Product.query.filter_by(vendor_id=vendor.id).all()

    # Simple sales stats
    order_items = (
        OrderItem.query.join(Product, OrderItem.product_id == Product.id)
        .filter(Product.vendor_id == vendor.id)
        .all()
    )
    total_sales = sum([oi.unit_price * oi.quantity for oi in order_items])
    total_items_sold = sum([oi.quantity for oi in order_items])

    return render_template("vendor/dashboard.html", vendor=vendor, products=products, total_sales=total_sales, total_items_sold=total_items_sold)


@vendor_bp.route("/products")
@login_required
@role_required("vendor")
def products():
    _require_vendor()
    products = Product.query.filter_by(vendor_id=current_user.vendor.id).all()
    return render_template("vendor/products.html", products=products)


@vendor_bp.route("/products/new", methods=["GET", "POST"]) 
@login_required
@role_required("vendor")
def product_new():
    _require_vendor()
    form = ProductForm()
    # populate categories select
    from ..models import Category
    form.category_id.choices = [(0, "-- None --")] + [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]

    if form.validate_on_submit():
        category_id = form.category_id.data or None
        if category_id == 0:
            category_id = None
        p = Product(
            vendor_id=current_user.vendor.id,
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            stock=form.stock.data,
            image_url=form.image_url.data or None,
            category_id=category_id,
        )
        db.session.add(p)
        db.session.commit()
        flash("Product created.", "success")
        return redirect(url_for("vendor.products"))

    return render_template("vendor/product_form.html", form=form, action="New")


@vendor_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"]) 
@login_required
@role_required("vendor")
def product_edit(product_id: int):
    _require_vendor()
    product = Product.query.filter_by(id=product_id, vendor_id=current_user.vendor.id).first_or_404()
    form = ProductForm(obj=product)
    from ..models import Category
    form.category_id.choices = [(0, "-- None --")] + [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]

    if form.validate_on_submit():
        product.title = form.title.data
        product.description = form.description.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.image_url = form.image_url.data or None
        category_id = form.category_id.data or None
        if category_id == 0:
            category_id = None
        product.category_id = category_id
        db.session.commit()
        flash("Product updated.", "success")
        return redirect(url_for("vendor.products"))

    return render_template("vendor/product_form.html", form=form, action="Edit")


@vendor_bp.route("/products/<int:product_id>/delete", methods=["POST"]) 
@login_required
@role_required("vendor")
def product_delete(product_id: int):
    _require_vendor()
    product = Product.query.filter_by(id=product_id, vendor_id=current_user.vendor.id).first_or_404()
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted.", "info")
    return redirect(url_for("vendor.products"))


@vendor_bp.route("/orders")
@login_required
@role_required("vendor")
def orders():
    _require_vendor()
    # Show order items related to vendor's products
    order_items = (
        OrderItem.query.join(Product, OrderItem.product_id == Product.id)
        .filter(Product.vendor_id == current_user.vendor.id)
        .order_by(OrderItem.id.desc())
        .all()
    )
    return render_template("vendor/orders.html", order_items=order_items)