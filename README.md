# Flask E-commerce API & Frontend

This is a complete e-commerce web application built with Python and Flask. It includes a full-featured REST API backend and a dynamic frontend that interacts with it.

## Features

*   **Backend API**:
    *   JWT-based authentication (login, register).
    *   Role-based access control (Customer, Vendor, Admin).
    *   Vendor management system (application and approval).
    *   Complete product catalog with categories, variants (SKUs), and inventory.
    *   Shopping cart for both registered users and guests (guest cart merges on login).
    *   Transactional order checkout with atomic stock reduction.
    *   Order management for customers, vendors, and admins.
    *   PDF invoice generation.
    *   Product reviews and ratings with an admin approval system.
    *   Sales and inventory reporting with JSON, CSV, and PDF export.
*   **Frontend**:
    *   A dynamic, responsive UI built with Tailwind CSS.
    *   Client-side rendering of data from the API.
    *   Pages for home, product detail, cart, login, and registration.
*   **Database**:
    *   Uses SQLite for simplicity and local execution.
    *   Managed with Flask-Migrate for database schema migrations.
*   **Testing**:
    *   Unit test suite covering critical functionality like authentication and stock control.

## Technologies Used

*   **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-JWT-Extended, Flask-CORS
*   **Database**: SQLite
*   **PDF Generation**: WeasyPrint
*   **Frontend**: HTML, Tailwind CSS (via Play CDN), vanilla JavaScript

## Local Setup and Execution

Follow these steps to get the application running locally.

### 1. Prerequisites

*   Python 3.8+
*   `pip` package manager

### 2. Installation

Clone the repository and navigate into the project directory.

Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 3. Database Setup

Before running the application for the first time, you need to set up the database.

First, set the Flask application environment variable:
```bash
export FLASK_APP=run.py
# On Windows Command Prompt, use `set FLASK_APP=run.py`
# On Windows PowerShell, use `$env:FLASK_APP="run.py"`
```

Apply the database migrations to create the tables:
```bash
flask db upgrade
```

### 4. Seed the Database (Optional but Recommended)

To populate the database with demo data (users, products, etc.), run the seed script:
```bash
python seed.py
```
This will create the following user accounts:
*   **Admin**: `admin@example.com` (password: `adminpass`)
*   **Vendor**: `vendor@example.com` (password: `vendorpass`)
*   **Customer**: `customer@example.com` (password: `customerpass`)

### 5. Run the Application

Start the Flask development server:
```bash
flask run
```
The application will be available at `http://127.0.0.1:5000`. You can now open this URL in your web browser to use the application.

### 6. Running Tests

To run the unit test suite, use the custom `test` command:
```bash
flask test
```
