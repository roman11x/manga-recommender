import os
from db import Database
from api import JikanClient
from app import MediaApp

os.makedirs("data", exist_ok=True)
db = Database("data/manga.db")
db.setup()
client = JikanClient()

app = MediaApp(db, client, first_run=True)
app.mainloop()
