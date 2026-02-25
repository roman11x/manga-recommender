from db import Database

db = Database("data/media.db")
db.setup()

db.add_media(11, "manga", "Naruto", "consumed", ["Action", "Adventure", "Fantasy"], liked=1)
db.add_media(1, "manga", "Berserk", "consuming", ["Action", "Dark Fantasy", "Seinen"])

print(db.get_all_media())
print(db.get_all_media("manga"))
print(db.get_media(11, "manga"))
print(db.get_media(99, "manga"))  # should return None