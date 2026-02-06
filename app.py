from flask import Flask, render_template, request, redirect, url_for, flash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Email configuration
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# File to store contact messages (backup)
MESSAGES_FILE = "contact_messages.json"

def save_message(name, email, message):
    """Save message to local file as backup"""
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, 'r') as f:
            messages = json.load(f)
    else:
        messages = []
    
    messages.append({
        "name": name,
        "email": email,
        "message": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    with open(MESSAGES_FILE, 'w') as f:
        json.dump(messages, f, indent=2)

def send_gmail(name, sender_email, message):
    """Send email notification via Gmail SMTP"""
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'🚀 New Portfolio Contact: {name}'
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_USER
    
    # Plain text version
    text = f"""
New Contact Form Submission
===========================

Name: {name}
Email: {sender_email}

Message:
{message}

---
Sent from your Portfolio Contact Form
    """
    
    # HTML version
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px 15px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 24px;">📬 New Contact Message</h1>
        </div>
        <div style="background: #1a1a2e; padding: 30px; border-radius: 0 0 15px 15px; color: #e0e0e0;">
            <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <p style="margin: 5px 0;"><strong style="color: #667eea;">👤 Name:</strong> {name}</p>
                <p style="margin: 5px 0;"><strong style="color: #667eea;">📧 Email:</strong> <a href="mailto:{sender_email}" style="color: #a78bfa;">{sender_email}</a></p>
            </div>
            <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px;">
                <p style="margin: 0 0 10px 0;"><strong style="color: #667eea;">💬 Message:</strong></p>
                <p style="margin: 0; line-height: 1.6; white-space: pre-wrap;">{message}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(text, 'plain'))
    msg.attach(MIMEText(html, 'html'))
    
    # Connect and send
    print(f"📧 Connecting to Gmail SMTP...")
    print(f"   Email: {EMAIL_USER}")
    print(f"   Password length: {len(EMAIL_PASS) if EMAIL_PASS else 0} chars")
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
    
    print("✅ Email sent successfully!")

@app.route("/")
def home():
    return render_template("mainpage.html")

@app.route("/contact", methods=["POST"])
def contact():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()
    
    if not name or not email or not message:
        flash("Please fill in all fields", "error")
        return redirect(url_for("home") + "#contact")
    
    # Save to file as backup
    save_message(name, email, message)
    print(f"📬 Message saved from: {name} ({email})")
    
    # Try to send Gmail
    try:
        send_gmail(name, email, message)
        flash("Message sent successfully! I'll get back to you soon.", "success")
    except Exception as e:
        print(f"❌ Gmail error: {e}")
        flash("Message saved! (Email notification pending)", "success")
    
    return redirect(url_for("home") + "#contact")

@app.route("/messages")
def view_messages():
    """View saved messages"""
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, 'r') as f:
            messages = json.load(f)
    else:
        messages = []
    
    messages.reverse()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Contact Messages</title>
        <style>
            body { font-family: Arial; max-width: 800px; margin: 40px auto; padding: 20px; background: #0a0a1a; color: #e0e0e0; }
            h1 { color: #00d4ff; }
            .msg { background: rgba(255,255,255,0.05); padding: 20px; margin: 15px 0; border-radius: 10px; border-left: 4px solid #00d4ff; }
            .meta { color: #888; font-size: 14px; }
            a { color: #00d4ff; }
        </style>
    </head>
    <body>
        <h1>📬 Contact Messages</h1>
        <p><a href="/">← Back to Portfolio</a></p>
    """
    
    if not messages:
        html += '<p>No messages yet!</p>'
    else:
        for msg in messages:
            html += f"""
            <div class="msg">
                <div class="meta"><strong>{msg['name']}</strong> ({msg['email']}) - {msg['timestamp']}</div>
                <p>{msg['message']}</p>
            </div>
            """
    
    html += "</body></html>"
    return html

if __name__ == "__main__":
    print("🚀 Starting Portfolio Server...")
    print(f"📧 Gmail: {EMAIL_USER}")
    print(f"🔑 Password: {'*' * len(EMAIL_PASS) if EMAIL_PASS else 'NOT SET'}")
    print(f"📂 Backup file: {MESSAGES_FILE}")
    app.run(debug=True)
