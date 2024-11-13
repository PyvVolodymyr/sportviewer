import sqlite3

# Connect to the database (this will create it if it doesn't exist)
conn = sqlite3.connect('sports_events.db')
cursor = conn.cursor()

# Create users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number TEXT UNIQUE,
    favorite_team TEXT,
    timezone TEXT
)
''')

# Create events table
cursor.execute('''
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team1 TEXT,
    team2 TEXT,
    sport TEXT,
    start_time DATETIME,
    status TEXT,
    score TEXT
)
''')

# Create subscriptions table
cursor.execute('''
CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    sport TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database tables created successfully.")
