import json
from tests.base import BaseTestCase
from app.models import User, Product, Category, VendorProfile, SKU, Inventory, UserRoles
from app import db

class CheckoutTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        # Create a user
        self.user = User(email='customer@example.com', role=UserRoles.CUSTOMER)
        self.user.set_password('password')
        db.session.add(self.user)

        # Create a vendor
        vendor_user = User(email='vendor@example.com', role=UserRoles.VENDOR)
        vendor_user.set_password('password')
        self.vendor_profile = VendorProfile(user=vendor_user, shop_name='Test Shop', is_approved=True)
        db.session.add(vendor_user)
        db.session.add(self.vendor_profile)

        # Create a category
        self.category = Category(name='Electronics')
        db.session.add(self.category)

        # Create a product
        self.product = Product(name='Test Product', description='A product for testing',
                               vendor=self.vendor_profile, category=self.category)
        db.session.add(self.product)

        # Create a SKU and Inventory
        self.sku = SKU(product=self.product, sku_code='TEST01', price=10.00)
        self.inventory = Inventory(sku=self.sku, quantity=5)
        db.session.add(self.sku)
        db.session.add(self.inventory)

        db.session.commit()

        # Login the user to get a token
        response = self.client.post('/api/auth/login',
                                    data=json.dumps({'email': 'customer@example.com', 'password': 'password'}),
                                    content_type='application/json')
        self.token = json.loads(response.get_data(as_text=True))['access_token']
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

    def test_successful_checkout(self):
        """Test a successful checkout process."""
        # 1. Add item to cart
        response = self.client.post('/api/cart/items', headers=self.headers,
                                    json={'sku_id': self.sku.id, 'quantity': 2})
        self.assertEqual(response.status_code, 200)

        # 2. Create an address
        address_data = {'address_line_1': '123 Test St', 'city': 'Testville', 'state': 'TS', 'zip_code': '12345', 'country': 'Testland'}
        self.client.post('/api/orders/addresses', headers=self.headers, json=address_data)

        # 3. Checkout
        checkout_data = {'shipping_address_id': 1}
        response = self.client.post('/api/orders', headers=self.headers, json=checkout_data)

        # 4. Verify results
        self.assertEqual(response.status_code, 201)
        self.assertIn('Order created successfully', response.get_data(as_text=True))

        # Check that inventory was reduced
        inventory = Inventory.query.get(self.inventory.id)
        self.assertEqual(inventory.quantity, 3)

    def test_add_to_cart_insufficient_stock(self):
        """Test adding item to cart fails due to insufficient stock."""
        # Try to add more items than are in stock
        response = self.client.post('/api/cart/items', headers=self.headers,
                                    json={'sku_id': self.sku.id, 'quantity': 10})

        # Verify failure
        self.assertEqual(response.status_code, 400)
        self.assertIn('Not enough stock available', response.get_data(as_text=True))

        # Check that inventory was NOT reduced
        inventory = Inventory.query.get(self.inventory.id)
        self.assertEqual(inventory.quantity, 5)
