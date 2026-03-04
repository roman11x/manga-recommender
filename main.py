import os
import threading
from db import Database
from api import JikanClient
from app import MediaApp
from generator import generate_recommendations

os.makedirs("data", exist_ok=True)
db = Database("data/manga.db")
db.setup()
client = JikanClient()

first_run = not db.has_consumed_liked_entries()
app = MediaApp(db, client, first_run=first_run)

if not first_run:
    def _bg_generate():
        result = generate_recommendations(db, client)
        if result == "network_error":
            try:
                from tkinter import messagebox
                app.after(0, lambda: messagebox.showwarning(
                    "No Internet Connection",
                    "Could not refresh recommendations.\n"
                    "Check your connection — you can regenerate them later from Settings.",
                ))
            except Exception:
                pass
    threading.Thread(target=_bg_generate, daemon=True).start()

app.mainloop()
