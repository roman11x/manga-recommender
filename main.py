import os
from db import Database
from api import JikanClient
from app import MediaApp
from generator import generate_recommendations
import tkinter as tk
from tkinter import messagebox

os.makedirs("data", exist_ok=True)
db = Database("data/manga.db")
db.setup()
client = JikanClient()

first_run = not db.has_consumed_liked_entries()

if not first_run:
   result = generate_recommendations(db, client)
   if result == "network_error":
       root = tk.Tk()
       root.withdraw() #hide empty root window
       messagebox.showwarning("No Internet Connection",
                             "Could not fetch recommendations.\nCheck your connection — you can generate them later from Settings.")
       root.destroy()

app = MediaApp(db, client, first_run=first_run)
app.mainloop()