from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ..models import Order


account_bp = Blueprint("account", __name__, url_prefix="/account", template_folder="../templates/account")


@account_bp.route("/orders")
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template("account/orders.html", orders=orders)