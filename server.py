from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('sports_events.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/live_events', methods=['GET'])
def get_live_events():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events WHERE status='live' ORDER BY start_time DESC")
    events = cursor.fetchall()
    conn.close()
    return jsonify([dict(event) for event in events])

@app.route('/scheduled_events', methods=['GET'])
def get_scheduled_events():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events WHERE status='scheduled' ORDER BY start_time")
    events = cursor.fetchall()
    conn.close()
    return jsonify([dict(event) for event in events])

@app.route('/user_subscriptions/<int:user_id>', methods=['GET'])
def get_user_subscriptions(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT sport FROM subscriptions WHERE user_id = ?", (user_id,))
    subscriptions = cursor.fetchall()
    conn.close()
    return jsonify([dict(sub) for sub in subscriptions])

@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.json
    user_id = data['user_id']
    sport = data['sport']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO subscriptions (user_id, sport) VALUES (?, ?)", (user_id, sport))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": f"Subscribed to {sport}"})

@app.route('/user_settings/<int:user_id>', methods=['GET', 'PUT'])
def user_settings(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'GET':
        cursor.execute("SELECT favorite_team, timezone FROM users WHERE id = ?", (user_id,))
        settings = cursor.fetchone()
        conn.close()
        return jsonify(dict(settings) if settings else {"error": "User not found"})
    elif request.method == 'PUT':
        data = request.json
        favorite_team = data.get('favorite_team')
        timezone = data.get('timezone')
        cursor.execute("UPDATE users SET favorite_team = ?, timezone = ? WHERE id = ?", 
                       (favorite_team, timezone, user_id))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Settings updated"})

@app.route('/statistics', methods=['GET'])
def get_statistics():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT sport, COUNT(*) as count FROM events GROUP BY sport ORDER BY count DESC LIMIT 1")
    most_popular_sport = cursor.fetchone()
    cursor.execute("SELECT team1, COUNT(*) as count FROM events GROUP BY team1 ORDER BY count DESC LIMIT 1")
    most_active_team = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) as count FROM events WHERE status='live'")
    live_events_count = cursor.fetchone()['count']
    conn.close()
    return jsonify({
        "most_popular_sport": dict(most_popular_sport),
        "most_active_team": dict(most_active_team),
        "live_events_count": live_events_count
    })


@app.route('/initialize_user', methods=['POST']) # -----------------------------------
def initialize_user():
    data = request.json
    user_id = data['user_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Перевірка, чи існує вже користувач
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    existing_user = cursor.fetchone()
    
    if not existing_user:
        # Якщо користувача немає в базі, додаємо нового
        cursor.execute("INSERT INTO users (id) VALUES (?)", (user_id,))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "User initialized"})
    
    conn.close()
    return jsonify({"status": "already_exists", "message": "User already exists"})

if __name__ == '__main__':
    app.run(debug=True)