import os
from db import Database
from api import JikanClient
from app import MediaApp

os.makedirs("data", exist_ok=True)
db = Database("data/manga.db")
db.setup()
client = JikanClient()

# first_run = True   # uncomment to test onboarding
first_run = not db.has_consumed_liked_entries()

app = MediaApp(db, client, first_run=first_run)
app.mainloop()
