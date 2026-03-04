# generator.py — recommendation generation pipeline
from api import extract_tags
from recommender import score_candidates

GENRE_IDS = {
    "Action": 1, "Adventure": 2, "Drama": 8, "Fantasy": 10,
    "Horror": 14, "Mystery": 7, "Romance": 22, "Sci-Fi": 24,
    "Slice of Life": 36, "Supernatural": 37, "Seinen": 42,
    "Shounen": 27, "Shoujo": 25, "Comedy": 4, "Psychological": 18,
    "Thriller": 41,
}

def get_genre_ids_for_tags(tags: list[str]) -> list[int]:
    return [GENRE_IDS[t] for t in tags if t in GENRE_IDS]

def generate_recommendations(db, client) -> str:
    active_types = db.get_active_media_types()
    if not active_types:
        active_types = list({e["media_type"] for e in db.get_all_media()})
    network_ok = False
    for media_type in active_types:
        tag_weights = db.get_tag_weights(media_type)

        if not tag_weights:
            continue
        top_tags = sorted(tag_weights, key=tag_weights.get, reverse=True)[:5]
        genre_ids = get_genre_ids_for_tags(top_tags)

        if not genre_ids:
            continue

        library_ids = db.get_library_ids(media_type)
        blacklist_ids = db.get_blacklist_ids(media_type)
        blacklisted_tags = db.get_blacklisted_tags(media_type)

        seen_ids = set()
        candidates = []
        for genre_id in genre_ids:
            for page in range(1, 3):
                page_results = client.get_by_genres(media_type, [genre_id], page=page)
                if page_results is None: #network error
                    break;
                network_ok = True #got a real response

                if not page_results:
                    break
                for item in page_results:
                    if item["mal_id"] in seen_ids:
                        continue
                    seen_ids.add(item["mal_id"])
                    candidates.append({
                        "mal_id":     item["mal_id"],
                        "media_type": media_type,
                        "title":      item["title"],
                        "cover_url":  (item.get("images") or {}).get("jpg", {}).get("large_image_url"),
                        "synopsis":   item.get("synopsis"),
                        "mal_score":  item.get("score"),
                        "tags":       extract_tags(item),
                    })


        scored = score_candidates(candidates, tag_weights, library_ids, blacklist_ids, blacklisted_tags)


        db.clear_pending_recommendations(media_type)
        for item in scored[:20]:
            tag_dicts = [{"name": t, "matched": 1 if t in tag_weights else 0} for t in item["tags"]]
            db.save_recommendation({**item, "tags": tag_dicts})
    return "ok" if network_ok else "network_error"