import os
from db import Database
from api import JikanClient
from app import MediaApp
from generator import generate_recommendations

os.makedirs("data", exist_ok=True)
db = Database("data/manga.db")
db.setup()
client = JikanClient()

first_run = not db.has_consumed_liked_entries()

if not first_run:
    generate_recommendations(db, client)

app = MediaApp(db, client, first_run=first_run)
app.mainloop()