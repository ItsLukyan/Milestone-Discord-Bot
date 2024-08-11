import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name='pr_bot.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Create the users table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                discord_id TEXT PRIMARY KEY, 
                                username TEXT)''')
        # Create the prs table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS prs (
                                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                discord_id TEXT, 
                                event TEXT, 
                                pr_value TEXT, 
                                date TEXT)''')
        # Create the events table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS events (
                                event_name TEXT PRIMARY KEY)''')
        
        # Insert predefined events into the events table
        predefined_events = [
            "2 Mile Run", 
            "5 Mile Run", 
            "Hand Release Push-Ups", 
            "Strict Dead-Hang Pull-Ups", 
            "Plank", 
            "Squat 1RM", 
            "Bench 1RM", 
            "Deadlift 1RM"
        ]
        for event in predefined_events:
            self.cursor.execute('INSERT OR IGNORE INTO events (event_name) VALUES (?)', (event,))
        
        self.conn.commit()
        
    def get_event(self, event):
        self.cursor.execute('SELECT * FROM events WHERE event_name = ?', (event,))
        return self.cursor.fetchone()

    def add_user(self, discord_id, username):
        self.cursor.execute("INSERT INTO users (discord_id, username) VALUES (?, ?)", (discord_id, username))
        self.conn.commit()
        
    def get_user(self, discord_id):
        self.cursor.execute('SELECT * FROM users WHERE discord_id = ?', (discord_id,))
        return self.cursor.fetchone()

    def add_pr(self, discord_id, event, pr_value):
        self.cursor.execute("INSERT INTO prs (discord_id, event, pr_value, date) VALUES (?, ?, ?, ?)", 
                            (discord_id, event, pr_value, str(datetime.now())))
        self.conn.commit()

    def get_user_prs(self, discord_id, event):
        self.cursor.execute("SELECT pr_value, date FROM prs WHERE discord_id = ? AND event = ? ORDER BY date", 
                            (discord_id, event))
        return self.cursor.fetchall()

    def get_event_leaderboard(self, event):
        timed_events = ["2 Mile Run", "5 Mile Run"]

        if event in timed_events:
            self.cursor.execute('''
                SELECT users.username, prs.pr_value, prs.discord_id, MAX(prs.date) as most_recent_date
                FROM prs 
                JOIN users ON prs.discord_id = users.discord_id 
                WHERE prs.event = ? 
                GROUP BY prs.discord_id 
                ORDER BY CAST(prs.pr_value AS REAL) ASC, most_recent_date ASC
            ''', (event,))
        else:
            self.cursor.execute('''
                SELECT users.username, prs.pr_value, prs.discord_id, MAX(prs.date) as most_recent_date
                FROM prs 
                JOIN users ON prs.discord_id = users.discord_id 
                WHERE prs.event = ? 
                GROUP BY prs.discord_id 
                ORDER BY CAST(prs.pr_value AS REAL) DESC, most_recent_date ASC
            ''', (event,))
    
        return self.cursor.fetchall()



    def close(self):
        self.conn.close()
