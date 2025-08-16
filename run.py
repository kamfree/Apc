import unittest
from app import create_app, db
from app.models import *

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 'User': User, 'VendorProfile': VendorProfile, 'Product': Product,
        'Category': Category, 'SKU': SKU, 'Inventory': Inventory, 'Cart': Cart,
        'Order': Order, 'Review': Review
    }

@app.cli.command()
def test():
    """Runs the unit tests."""
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    app.run(debug=True)
