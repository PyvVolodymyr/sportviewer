# populate_db.py
import sqlite3
import random
from datetime import datetime, timedelta

# Підключення до бази даних
conn = sqlite3.connect('sports_events.db')
cursor = conn.cursor()

# Функція для генерації випадкової дати і часу
def random_date(start, end):
    return start + timedelta(
        seconds=random.randint(0, int((end - start).total_seconds()))
    )

# Списки для генерації даних
sports = ['Футбол', 'Баскетбол', 'Теніс', 'Хокей']
football_teams = ['Динамо Київ', 'Шахтар Донецьк', 'Зоря Луганськ', 'Ворскла Полтава', 'Десна Чернігів']
basketball_teams = ['Будівельник', 'Хімік', 'Дніпро', 'Київ-Баскет', 'Запоріжжя']
tennis_players = ['Світоліна Е.', 'Ястремська Д.', 'Костюк М.', 'Цуренко Л.', 'Марченко І.']
hockey_teams = ['Донбас', 'Сокіл Київ', 'Білий Барс', 'Кременчук', 'Дніпро']

# Додавання користувачів
users = [
    ('+380991234567', 'Динамо Київ', '+2'),
    ('+380997654321', 'Будівельник', '+2'),
    ('+380993216547', 'Світоліна Е.', '+3'),
]

cursor.executemany('INSERT OR IGNORE INTO users (phone_number, favorite_team, timezone) VALUES (?, ?, ?)', users)

# Додавання подій
events = []
start_date = datetime.now()
end_date = start_date + timedelta(days=30)

for _ in range(20):
    sport = random.choice(sports)
    if sport == 'Футбол':
        team1, team2 = random.sample(football_teams, 2)
    elif sport == 'Баскетбол':
        team1, team2 = random.sample(basketball_teams, 2)
    elif sport == 'Теніс':
        team1, team2 = random.sample(tennis_players, 2)
    else:  # Хокей
        team1, team2 = random.sample(hockey_teams, 2)
    
    start_time = random_date(start_date, end_date)
    status = random.choice(['scheduled', 'live', 'finished'])
    score = f"{random.randint(0, 5)}:{random.randint(0, 5)}" if status in ['live', 'finished'] else None
    
    events.append((team1, team2, sport, start_time, status, score))

cursor.executemany('INSERT INTO events (team1, team2, sport, start_time, status, score) VALUES (?, ?, ?, ?, ?, ?)', events)

# Додавання підписок
subscriptions = [
    (1, 'Футбол'),
    (1, 'Баскетбол'),
    (2, 'Баскетбол'),
    (3, 'Теніс'),
]

cursor.executemany('INSERT OR IGNORE INTO subscriptions (user_id, sport) VALUES (?, ?)', subscriptions)

# Збереження змін та закриття з'єднання
conn.commit()
conn.close()

print("База даних успішно заповнена тестовими даними.")
