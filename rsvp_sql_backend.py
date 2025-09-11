from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
import sqlite3
import yagmail
import os
from dotenv import load_dotenv


load_dotenv()
app = Flask(__name__)
CORS(app)

# Load environment variables from .env file
load_dotenv()

DB_FILE = 'rsvp_data.db'
EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASS = os.environ.get('EMAIL_PASS')
GOOGLE_FORM_LINK = os.environ.get('GOOGLE_FORM_LINK')

# Initialize database
with sqlite3.connect(DB_FILE) as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS rsvp (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        guests INTEGER,
        faction TEXT,
        message TEXT
    )''')

@app.route('/rsvp', methods=['POST'])
def rsvp():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    guests = data.get('guests')
    faction = data.get('faction')
    message = data.get('message')

    # Store in SQLite
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute('INSERT INTO rsvp (name, email, guests, faction, message) VALUES (?, ?, ?, ?, ?)',
                         (name, email, guests, faction, message))
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Database error: {e}'}), 500

    # Send email to user using yagmail and generate WhatsApp link
    try:
        subject = "Your AniCos Booking Confirmation"
        whatsapp_message = f"Hi {name}, thank you for booking your ticket for AniCos! Here is your booking info: Name: {name}, Email: {email}, Guests: {guests}, Faction: {faction}. To complete your registration, please fill out this Google Form: {GOOGLE_FORM_LINK}"
        whatsapp_link = f"https://wa.me/?text={whatsapp_message.replace(' ', '%20')}"
        body = f"""
        Hi {name},<br><br>
        Thank you for booking your ticket for AniCos!<br><br>
        <b>Here is your booking info:</b><br>
        Name: {name}<br>
        Email: {email}<br>
        Guests: {guests}<br>
        Faction: {faction}<br>
        Message: {message}<br><br>
        To complete your registration, please fill out this Google Form: <a href='{GOOGLE_FORM_LINK}'>{GOOGLE_FORM_LINK}</a><br><br>
        <b>Send yourself a WhatsApp confirmation:</b> <a href='{whatsapp_link}'>Click here</a><br><br>
        See you at the event!<br>
        AniCos Team
        """
        yag = yagmail.SMTP(EMAIL_USER, EMAIL_PASS)
        yag.send(to=email, subject=subject, contents=body)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Email error: {e}'}), 500

    return jsonify({'status': 'success', 'whatsapp_link': whatsapp_link})

    return jsonify({'status': 'success'})


# View all RSVP entries
@app.route('/rsvp/all', methods=['GET'])
def rsvp_all():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.execute('SELECT id, name, email, guests, faction, message FROM rsvp')
            rows = cursor.fetchall()
            data = [
                {
                    'id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'guests': row[3],
                    'faction': row[4],
                    'message': row[5]
                }
                for row in rows
            ]
        return jsonify(data)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


 # http://127.0.0.1:5000/rsvp/all   pip install yagmail