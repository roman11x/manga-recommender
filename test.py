from db import Database

db = Database("data/media.db")
db.setup()

db.add_media(11, "manga", "Naruto", "consumed", ["Action", "Adventure", "Fantasy"], liked=1)
db.add_media(1, "manga", "Berserk", "consumed", ["Action", "Dark Fantasy", "Seinen"], liked=1)

print(db.get_tag_weights("manga"))
# {'Action': 2, 'Adventure': 1, 'Fantasy': 1, 'Dark Fantasy': 1, 'Seinen': 1}