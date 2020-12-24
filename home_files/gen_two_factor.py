import smtplib
import ssl
from email.message import EmailMessage
import random
import dialog

class GenerateTwoFactorAuth:
    def __init__(self, email):
        super().__init__()
        self._receiver_email = email
        self._code = self.generate_code()

        self.email_code()
    
    def email_config(self):
        with open("email.txt", "r") as f:
            return f.readline().split(":")

    def generate_code(self):
        return random.randint(9999,99999)

    def generate_message(self, sender, receiver):
        msg = EmailMessage()
        msg.set_content(f"Your authentication code is: {self._code}")
        msg["Subject"] = "Password Manager - 2FA"
        msg["From"] = sender
        msg["To"] = receiver
        return msg

    def email_code(self):
        port = 465 #SSL
        sender_email, password = self.email_config()

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(sender_email, password)
            server.send_message(self.generate_message(sender_email, self._receiver_email))

    @property
    def code(self):
        return self._code
