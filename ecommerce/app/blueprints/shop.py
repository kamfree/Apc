from flask import Blueprint, render_template, request
from sqlalchemy import or_, and_
from ..extensions import db
from ..models import Product, Category


shop_bp = Blueprint("shop", __name__, url_prefix="/shop", template_folder="../templates/shop")


@shop_bp.route("/")
@shop_bp.route("/products")
def product_list():
    query = Product.query.filter_by(is_active=True)

    keyword = request.args.get("q", type=str, default="").strip()
    category_id = request.args.get("category", type=int)
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)

    if keyword:
        like = f"%{keyword}%"
        query = query.filter(or_(Product.title.ilike(like), Product.description.ilike(like)))

    if category_id:
        query = query.filter(Product.category_id == category_id)

    if min_price is not None and max_price is not None:
        query = query.filter(and_(Product.price >= min_price, Product.price <= max_price))
    elif min_price is not None:
        query = query.filter(Product.price >= min_price)
    elif max_price is not None:
        query = query.filter(Product.price <= max_price)

    products = query.order_by(Product.created_at.desc()).all()
    categories = Category.query.order_by(Category.name).all()
    return render_template("shop/product_list.html", products=products, categories=categories)


@shop_bp.route("/product/<int:product_id>")
def product_detail(product_id: int):
    product = Product.query.get_or_404(product_id)
    return render_template("shop/product_detail.html", product=product)