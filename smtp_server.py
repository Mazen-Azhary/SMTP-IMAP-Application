import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()
"""
this script uses SMTP : simple mail transfer protocol to send emails through my gmail account
by creating an email object with a subject and body , then authenticating with my gmail credentials
and sending the email to a specified recipient

I used an environment file to hide my credentials for security

the script handles plain text emails and ensures the connection is secured using
TLS (transport layer security) before sending any data over the network
"""
class smtp_server:
    def __init__(self):
        #initialization
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.username = os.getenv("EMAIL_USERNAME")
        self.password = os.getenv("EMAIL_PASSWORD")
        self.sender_email = self.username
    def send_email(self, to_email, subject, body):
        try:
            # Create the email object
            message = MIMEText(body, "plain")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = to_email
            
            # Connect and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Secure the connection
                server.login(self.username, self.password)  # Log in to SMTP server
                server.sendmail(self.sender_email, to_email, message.as_string())  # Send email
            # print(f"Email sent successfully to {to_email}")
            return True
        
        except Exception as e:
            # print(f"Error sending email: {e}")
            return False



if __name__ == "__main__":
    mailer = smtp_server()
    
    # Send email with parameters
    mailer.send_email(
        to_email=os.getenv("RECEIVER_EMAIL"),
        subject="Test Email from Python",
        body="Hello, this is a test email sent using Python!"
    )
    
   