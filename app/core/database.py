from typing import Dict, List

fake_db = {
    "users": [],
    "clients": [],
    "trainers": [],
    "services": [],
    "workouts": [],
    "attendances": [],
    "workout_bookings": [],
}

class Database:
    def __init__(self):
        self.db = fake_db

db = Database()
