from flask import current_app
from flask_mail import Message
from .extensions import mail


def init_email(app):
    # No special init for now; placeholder for future configuration
    pass


def send_email(to: str, subject: str, body: str) -> None:
    if current_app.config.get("MAIL_SUPPRESS_SEND", True):
        print("--- Simulated Email ---")
        print(f"To: {to}")
        print(f"Subject: {subject}")
        print("Body:\n" + body)
        print("-----------------------")
        return
    msg = Message(subject=subject, recipients=[to], body=body)
    mail.send(msg)