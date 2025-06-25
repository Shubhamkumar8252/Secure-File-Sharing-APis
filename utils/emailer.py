import smtplib
from os import getenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email, subject, html_body):
    msg = MIMEMultipart()
    msg["From"] = getenv("EMAIL_USER")
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(getenv("EMAIL_HOST"), int(getenv("EMAIL_PORT"))) as server:
        server.starttls()
        server.login(getenv("EMAIL_USER"), getenv("EMAIL_PASS"))
        server.sendmail(msg["From"], msg["To"], msg.as_string())
