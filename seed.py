from app import create_app, db
from app.models import User, VendorProfile, Category, Product, SKU, Inventory, UserRoles

def seed_data():
    app = create_app()
    with app.app_context():
        print("Clearing old data...")
        db.drop_all()
        db.create_all()

        print("Seeding new data...")

        # --- Users ---
        admin_user = User(email='admin@example.com', role=UserRoles.ADMIN)
        admin_user.set_password('adminpass')

        vendor_user = User(email='vendor@example.com', role=UserRoles.VENDOR)
        vendor_user.set_password('vendorpass')

        customer_user = User(email='customer@example.com', role=UserRoles.CUSTOMER)
        customer_user.set_password('customerpass')

        db.session.add_all([admin_user, vendor_user, customer_user])
        db.session.commit()
        print("Users created: admin@example.com, vendor@example.com, customer@example.com")

        # --- Vendor Profile ---
        vendor_profile = VendorProfile(user_id=vendor_user.id, shop_name="Jules's Gadgets", is_approved=True)
        db.session.add(vendor_profile)
        db.session.commit()

        # --- Categories ---
        cat_electronics = Category(name='Electronics')
        cat_books = Category(name='Books')
        db.session.add_all([cat_electronics, cat_books])
        db.session.commit()

        # --- Products ---
        prod1 = Product(name='Quantum Laptop', description='A laptop from the future.', vendor_id=vendor_profile.id, category_id=cat_electronics.id)
        prod2 = Product(name='Advanced AI Programming', description='The definitive guide to AI.', vendor_id=vendor_profile.id, category_id=cat_books.id)
        prod3 = Product(name='Smart Mug', description='Keeps your coffee at the perfect temperature.', vendor_id=vendor_profile.id, category_id=cat_electronics.id)
        db.session.add_all([prod1, prod2, prod3])
        db.session.commit()

        # --- SKUs & Inventory ---
        sku1 = SKU(product_id=prod1.id, sku_code='QL-2024', price=1299.99, attributes={'color': 'silver', 'storage': '1TB'})
        sku2 = SKU(product_id=prod2.id, sku_code='BK-AI-42', price=49.99, attributes={'format': 'hardcover'})
        sku3 = SKU(product_id=prod3.id, sku_code='SM-BLK', price=89.99, attributes={'color': 'black'})
        sku4 = SKU(product_id=prod3.id, sku_code='SM-WHT', price=89.99, attributes={'color': 'white'})
        db.session.add_all([sku1, sku2, sku3, sku4])
        db.session.commit()

        inv1 = Inventory(sku_id=sku1.id, quantity=10)
        inv2 = Inventory(sku_id=sku2.id, quantity=50)
        inv3 = Inventory(sku_id=sku3.id, quantity=25)
        inv4 = Inventory(sku_id=sku4.id, quantity=0) # Low stock example
        db.session.add_all([inv1, inv2, inv3, inv4])
        db.session.commit()

        print("Seeding complete!")

if __name__ == '__main__':
    seed_data()
