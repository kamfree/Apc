from decimal import Decimal
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import current_user, login_required
from ..extensions import db
from ..models import Product, CartItem, Order, OrderItem, ORDER_STATUS_PENDING
from ..forms import CheckoutForm
from ..utils import get_or_create_session_id
from ..email import send_email


cart_bp = Blueprint("cart", __name__, url_prefix="/cart", template_folder="../templates/cart")


def _get_cart_items():
    if current_user.is_authenticated:
        items = CartItem.query.filter_by(user_id=current_user.id).all()
    else:
        sid = get_or_create_session_id()
        items = CartItem.query.filter_by(session_id=sid).all()
    return items


def _cart_totals(items):
    subtotal = Decimal("0.00")
    for it in items:
        subtotal += it.product.price * it.quantity
    return subtotal


@cart_bp.route("/")
def view_cart():
    items = _get_cart_items()
    subtotal = _cart_totals(items)
    return render_template("cart/cart.html", items=items, subtotal=subtotal)


@cart_bp.route("/add/<int:product_id>", methods=["POST"]) 
def add_to_cart(product_id: int):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get("quantity", 1))
    if quantity <= 0:
        quantity = 1

    if current_user.is_authenticated:
        item = CartItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()
        if not item:
            item = CartItem(user_id=current_user.id, product_id=product.id, quantity=0)
            db.session.add(item)
    else:
        sid = get_or_create_session_id()
        item = CartItem.query.filter_by(session_id=sid, product_id=product.id).first()
        if not item:
            item = CartItem(session_id=sid, product_id=product.id, quantity=0)
            db.session.add(item)
    item.quantity += quantity
    db.session.commit()
    flash("Item added to cart.", "success")
    return redirect(request.referrer or url_for("shop.product_detail", product_id=product.id))


@cart_bp.route("/update/<int:item_id>", methods=["POST"]) 
def update_item(item_id: int):
    item = CartItem.query.get_or_404(item_id)
    quantity = int(request.form.get("quantity", 1))
    if quantity <= 0:
        db.session.delete(item)
    else:
        item.quantity = quantity
    db.session.commit()
    flash("Cart updated.", "info")
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/remove/<int:item_id>")
def remove_item(item_id: int):
    item = CartItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash("Item removed.", "info")
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/checkout", methods=["GET", "POST"]) 
@login_required
def checkout():
    items = _get_cart_items()
    if not items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("shop.product_list"))

    form = CheckoutForm()
    if form.validate_on_submit():
        order = Order(
            user_id=current_user.id,
            shipping_name=form.shipping_name.data,
            shipping_address=form.shipping_address.data,
            shipping_city=form.shipping_city.data,
            shipping_postal_code=form.shipping_postal_code.data,
            shipping_country=form.shipping_country.data,
            status=ORDER_STATUS_PENDING,
        )
        db.session.add(order)
        db.session.flush()

        # Create order items and adjust stock
        for ci in items:
            if ci.quantity > ci.product.stock:
                flash(f"Insufficient stock for {ci.product.title}", "danger")
                db.session.rollback()
                return redirect(url_for("cart.view_cart"))
            oi = OrderItem(order_id=order.id, product_id=ci.product.id, quantity=ci.quantity, unit_price=ci.product.price)
            ci.product.stock -= ci.quantity
            db.session.add(oi)
            db.session.delete(ci)

        order.compute_total()
        db.session.commit()

        # Send confirmation email
        send_email(to=current_user.email, subject="Order Confirmation", body=f"Thank you for your order #{order.id}. Total: ${order.total_amount}")

        return render_template("cart/order_confirmation.html", order=order)

    return render_template("cart/checkout.html", form=form, items=items, subtotal=_cart_totals(items))


@cart_bp.before_app_request
def merge_session_cart_after_login():
    # If a session cart exists and user logs in, merge it once
    if not current_user.is_authenticated:
        return
    sid = session.get("sid")
    if not sid:
        return
    session_items = CartItem.query.filter_by(session_id=sid).all()
    if not session_items:
        return
    for si in session_items:
        existing = CartItem.query.filter_by(user_id=current_user.id, product_id=si.product_id).first()
        if existing:
            existing.quantity += si.quantity
            db.session.delete(si)
        else:
            si.user_id = current_user.id
            si.session_id = None
    db.session.commit()
    session.pop("sid", None)