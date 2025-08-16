from flask import request, jsonify, Blueprint
from app import db
from app.models import Product, Category, VendorProfile, SKU, ProductImage, Inventory, User, UserRoles
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.routes.vendor import role_required

products_bp = Blueprint('products', __name__)

def get_product_details(product):
    """Helper function to serialize product details."""
    skus = []
    for sku in product.skus:
        skus.append({
            'id': sku.id,
            'sku_code': sku.sku_code,
            'price': sku.price,
            'attributes': sku.attributes,
            'quantity': sku.inventory.quantity if sku.inventory else 0
        })

    images = [{'id': img.id, 'url': img.image_url, 'alt': img.alt_text} for img in product.images]

    return {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'category': product.category.name,
        'vendor': product.vendor.shop_name,
        'images': images,
        'skus': skus
    }

@products_bp.route('', methods=['GET'])
def list_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = Product.query

    # Filtering
    category_id = request.args.get('category_id', type=int)
    if category_id:
        query = query.filter(Product.category_id == category_id)

    vendor_id = request.args.get('vendor_id', type=int)
    if vendor_id:
        query = query.filter(Product.vendor_id == vendor_id)

    # Searching
    search_term = request.args.get('search')
    if search_term:
        query = query.filter(Product.name.ilike(f'%{search_term}%') | Product.description.ilike(f'%{search_term}%'))

    paginated_products = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'products': [get_product_details(p) for p in paginated_products.items],
        'total': paginated_products.total,
        'pages': paginated_products.pages,
        'current_page': paginated_products.page
    }), 200

@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(get_product_details(product)), 200

@products_bp.route('', methods=['POST'])
@jwt_required()
@role_required(UserRoles.VENDOR)
def create_product():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()

    if not user.vendor_profile or not user.vendor_profile.is_approved:
        return jsonify({'message': 'Only approved vendors can create products'}), 403

    data = request.get_json()
    # Basic validation
    required_fields = ['name', 'description', 'category_id', 'skus']
    if not all(field in data for field in required_fields):
        return jsonify({'message': f'Missing fields. Required: {required_fields}'}), 400

    # Create product
    product = Product(
        name=data['name'],
        description=data['description'],
        category_id=data['category_id'],
        vendor_id=user.vendor_profile.id
    )
    db.session.add(product)
    db.session.flush() # Flush to get the product ID for relations

    # Create SKUs and Inventory
    for sku_data in data['skus']:
        sku = SKU(
            product_id=product.id,
            sku_code=sku_data['sku_code'],
            price=sku_data['price'],
            attributes=sku_data.get('attributes')
        )
        db.session.add(sku)
        db.session.flush() # Flush to get SKU ID
        inventory = Inventory(sku_id=sku.id, quantity=sku_data.get('quantity', 0))
        db.session.add(inventory)

    # Create Product Images
    if 'images' in data:
        for img_data in data['images']:
            image = ProductImage(
                product_id=product.id,
                image_url=img_data['url'],
                alt_text=img_data.get('alt')
            )
            db.session.add(image)

    db.session.commit()
    return jsonify(get_product_details(product)), 201

@products_bp.route('/<int:product_id>', methods=['PUT', 'PATCH'])
@jwt_required()
@role_required(UserRoles.VENDOR)
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()

    if product.vendor_id != user.vendor_profile.id:
        return jsonify({'message': 'You can only edit your own products'}), 403

    data = request.get_json()
    # Update fields
    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.category_id = data.get('category_id', product.category_id)
    # More complex updates for relations (SKUs, images) would go here

    db.session.commit()
    return jsonify(get_product_details(product)), 200

@products_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
@role_required(UserRoles.VENDOR)
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()

    if product.vendor_id != user.vendor_profile.id:
        return jsonify({'message': 'You can only delete your own products'}), 403

    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'}), 200
