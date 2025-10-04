import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==========================================================
# 🛑🛑🛑 YAHAN APNE CREDENTIALS ZAROOR DAALO 🛑🛑🛑
# ==========================================================
GMAIL_USER = "dynoc845@gmail.com"        # <-- Apni Gmail ID
GMAIL_APP_PASSWORD = "bfwy axdd xwdl nimn" # <-- Google ka 16-digit App Password
# ==========================================================

def send_confirmation_email_via_gmail(recipient_email, booking_details):
    # Gmail ka standard SMTP server aur port 587 (TLS security ke liye)
    smtp_server = "smtp.gmail.com" 
    smtp_port = 587 

    msg = MIMEMultipart()
    msg['Subject'] = 'TravelEase: Aapki Booking Confirm Ho Gayi Hai! ✈️'
    msg['From'] = GMAIL_USER
    msg['To'] = recipient_email

    # Email Body (HTML format)
    body = f"""
    <html>
        <body>
            <p>Priya Grahak,</p>
            <p>Aapki TravelEase flight booking safaltapoorvak <b>CONFIRMED</b> ho gayi hai!</p>
            <hr>
            <p><b>Booking Reference:</b> {booking_details.get('booking_reference')}</p>
            <p><b>Flight:</b> {booking_details.get('flight')}</p>
            <p><b>Total Amount Paid:</b> ₹{booking_details.get('price')}</p>
            <p><b>Transaction ID:</b> {booking_details.get('transaction_id')}</p>
            <hr>
            <p>TravelEase chunne ke liye dhanyawad.</p>
            <p>Aabhar,<br>TravelEase Team</p>
        </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"*** REAL EMAIL SENT SUCCESS: Confirmation sent to {recipient_email} via Gmail ***")
        return True
    
    except smtplib.SMTPAuthenticationError:
        print("!!! AUTH ERROR: Login failed. Check App Password and Gmail ID.")
        return False
    except Exception as e:
        print(f"!!! EMAIL SEND FAILED: {e}")
        return False