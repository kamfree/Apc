from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from ..extensions import db
from ..forms import RegistrationForm, LoginForm
from ..models import User, Vendor, ROLE_VENDOR, ROLE_CUSTOMER


auth_bp = Blueprint("auth", __name__, template_folder="../templates/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("shop.product_list"))
    form = RegistrationForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data.lower()).first()
        if existing:
            flash("Email already registered.", "danger")
            return redirect(url_for("auth.register"))
        role = ROLE_CUSTOMER
        user = User(email=form.email.data.lower(), name=form.name.data or form.email.data.split("@")[0])
        user.set_password(form.password.data)
        if form.register_as_vendor.data:
            role = ROLE_VENDOR
        user.role = role
        db.session.add(user)
        db.session.flush()
        if role == ROLE_VENDOR:
            vendor_name = form.vendor_name.data or f"Vendor {user.name}"
            vendor = Vendor(user_id=user.id, name=vendor_name, approved=False)
            db.session.add(vendor)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("shop.product_list"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash("Logged in successfully.", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("shop.product_list"))
        flash("Invalid credentials.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("shop.product_list"))