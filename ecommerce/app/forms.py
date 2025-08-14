from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DecimalField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional


class RegistrationForm(FlaskForm):
    name = StringField("Name", validators=[Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    register_as_vendor = BooleanField("Register as Vendor")
    vendor_name = StringField("Vendor Name", validators=[Optional(), Length(max=120)])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class ProductForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Description")
    price = DecimalField("Price", validators=[DataRequired(), NumberRange(min=0)], places=2)
    stock = IntegerField("Stock", validators=[DataRequired(), NumberRange(min=0)])
    image_url = StringField("Image URL", validators=[Optional(), Length(max=500)])
    category_id = SelectField("Category", coerce=int, validators=[Optional()])
    submit = SubmitField("Save")


class CategoryForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    parent_id = SelectField("Parent Category", coerce=int, validators=[Optional()])
    submit = SubmitField("Save")


class CheckoutForm(FlaskForm):
    shipping_name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    shipping_address = StringField("Address", validators=[DataRequired(), Length(max=255)])
    shipping_city = StringField("City", validators=[DataRequired(), Length(max=120)])
    shipping_postal_code = StringField("Postal Code", validators=[DataRequired(), Length(max=20)])
    shipping_country = StringField("Country", validators=[DataRequired(), Length(max=120)])
    submit = SubmitField("Place Order")


class VendorApprovalForm(FlaskForm):
    approved = BooleanField("Approved")
    submit = SubmitField("Update")


class OrderStatusForm(FlaskForm):
    status = SelectField("Status", choices=[
        ("Pending", "Pending"),
        ("Processing", "Processing"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ], validators=[DataRequired()])
    submit = SubmitField("Update Status")