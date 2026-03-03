from db import Database
db = Database("data/manga.db")
print(db.get_setting("active_media_types"))
print(db.get_active_media_types())