from db import Database

db = Database("data/media.db")
db.setup()

# Two manga
db.add_media(1, "manga", "Berserk", "consumed", ["Action", "Dark Fantasy", "Seinen", "Gore"], liked=1)
db.add_media(11, "manga", "Naruto", "consumed", ["Action", "Adventure", "Fantasy", "Shounen"], liked=1)

# One anime
db.add_media(1, "anime", "Berserk (2016)", "consuming", ["Action", "Dark Fantasy", "Seinen"], liked=None)

# One blacklisted manga
db.add_media(13, "manga", "Doraemon", "blacklisted", ["Comedy", "Shounen", "Sci-Fi"])

# One recommendation
rec = {
    "mal_id": 2,
    "media_type": "manga",
    "title": "Vagabond",
    "score": 42.5,
    "cover_url": "https://cdn.myanimelist.net/images/manga/1/259070.jpg",
    "synopsis": "Based on the novel Musashi, Vagabond portrays a fictionalized account of the life of Miyamoto Musashi.",
    "mal_score": 9.5,
    "tags": [
        {"name": "Action", "matched": 1},
        {"name": "Seinen", "matched": 1},
        {"name": "Historical", "matched": 0}
    ]
}

print("getting all media")
print(db.get_all_media())
print("getting just manga")
print(db.get_all_media("manga"))
print(db.get_all_media("anime"))
print("getting existing media")
print(db.get_media(1, "manga"))
print("getting non existent media")
print(db.get_media(50, "manga"))
print("testing get_tag_weights for manga then anime")
print(db.get_tag_weights("manga"))
print(db.get_tag_weights("anime"))

print("updating status for berserk: consuming")
db.update_status(1, "manga", "consuming")
db.update_liked(1, "manga", 0)
print(db.get_media(1, "manga"))
print("testing get_library ids, manga then anime")
print(db.get_library_ids("manga"))
print(db.get_library_ids("anime"))
print("testing get blacklisted ids manga first then anime")
print(db.get_blacklist_ids("manga"))
print(db.get_blacklist_ids("anime"))
print("adding blacklisted tags: gore&test")
db.add_blacklisted_tag("gore", "manga")
db.add_blacklisted_tag("test", "anime")
print("getting blacklisted tags")
print(db.get_blacklisted_tags("manga"))
print(db.get_blacklisted_tags("anime"))
print("removing blacklisted tag: test")
db.remove_blacklisted_tag("test", "anime")
print("testing getting blacklisted tags")
db.get_blacklisted_tags("manga")
print("testing settings")
db.set_setting("active_media_types", "manga,anime")
print(db.get_setting("active_media_types"))
print("before removing Naruto from consumed")
print(db.has_consumed_liked_entries())

print("after remove Naruto form consumed")
db.update_status(11, "manga", "consuming")
db.update_liked(11, "manga", 0)
print(db.has_consumed_liked_entries())

print("recommendation test")
db.save_recommendation(rec)
print("test get pending")
print(db.get_pending_recommendations("manga"))
print("move to saved")
db.move_recommendation_to_saved(2,"manga")
print(db.get_saved_recommendations("manga"))
print("removing from saved")
db.remove_recommendation(2, "manga")
print(db.get_saved_recommendations("manga"))







