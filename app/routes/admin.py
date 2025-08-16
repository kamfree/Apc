from flask import request, jsonify, Blueprint
from app import db
from app.models import Order, OrderStatus, User, UserRoles, Review
from flask_jwt_extended import jwt_required
from app.routes.vendor import role_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/orders', methods=['GET'])
@jwt_required()
@role_required(UserRoles.ADMIN)
def admin_get_all_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify([{
        'id': o.id,
        'user_id': o.user_id,
        'customer_email': o.user.email,
        'total_amount': o.total_amount,
        'status': o.status.value,
        'date': o.created_at.isoformat()
    } for o in orders]), 200

@admin_bp.route('/orders/<int:order_id>', methods=['GET'])
@jwt_required()
@role_required(UserRoles.ADMIN)
def admin_get_order_details(order_id):
    order = Order.query.get_or_404(order_id)

    items_data = []
    for item in order.items:
        items_data.append({
            'id': item.id,
            'product_name': item.sku.product.name,
            'quantity': item.quantity,
            'price': item.price,
            'fulfillment_status': item.fulfillment_status.value,
            'vendor_id': item.sku.product.vendor_id
        })

    return jsonify({
        'id': order.id,
        'customer_email': order.user.email,
        'status': order.status.value,
        'total_amount': order.total_amount,
        'items': items_data,
        'shipping_address': {
            'address_line_1': order.shipping_address.address_line_1,
            'city': order.shipping_address.city,
            'state': order.shipping_address.state
        }
    }), 200

@admin_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@jwt_required()
@role_required(UserRoles.ADMIN)
def admin_update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    data = request.get_json()
    new_status_str = data.get('status')

    if not new_status_str:
        return jsonify({'message': 'Status is required'}), 400

    try:
        new_status = OrderStatus[new_status_str.upper()]
    except KeyError:
        return jsonify({'message': 'Invalid status value'}), 400

    order.status = new_status
    db.session.commit()

    return jsonify({'message': f'Order {order_id} status updated to {new_status.value}'}), 200

# --- Review Management ---
@admin_bp.route('/reviews/pending', methods=['GET'])
@jwt_required()
@role_required(UserRoles.ADMIN)
def get_pending_reviews():
    pending_reviews = Review.query.filter_by(is_approved=False).order_by(Review.created_at.asc()).all()
    return jsonify([{
        'id': r.id,
        'product_id': r.product_id,
        'product_name': r.product.name,
        'author_email': r.user.email,
        'rating': r.rating,
        'comment': r.comment,
        'date': r.created_at.isoformat()
    } for r in pending_reviews]), 200

@admin_bp.route('/reviews/<int:review_id>/approve', methods=['POST'])
@jwt_required()
@role_required(UserRoles.ADMIN)
def approve_review(review_id):
    review = Review.query.get_or_404(review_id)
    review.is_approved = True
    db.session.commit()
    return jsonify({'message': f'Review {review_id} has been approved.'}), 200

@admin_bp.route('/reviews/<int:review_id>', methods=['DELETE'])
@jwt_required()
@role_required(UserRoles.ADMIN)
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    return jsonify({'message': f'Review {review_id} has been deleted.'}), 200
