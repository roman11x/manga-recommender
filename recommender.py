# scoring and ranking (pure functions, no classes)


# Score = sum of tag_weight for each tag the candidate shares with your library. tag_weight is the count of how many times that tag appears in your read-and-liked list.
# A manga that shares your most-read tags scores much higher than one that shares obscure tags.
def score_candidates(candidates, tag_weights, library_ids, blacklist_ids, blacklisted_tags) -> list[dict]:
    results = []
    for candidate in candidates:
        if (candidate["mal_id"],candidate["media_type"]) in library_ids:
            continue
        if (candidate["mal_id"], candidate["media_type"]) in blacklist_ids:
            continue
        if any (tag in blacklisted_tags for tag in candidate["tags"]):
            continue
        score = sum(tag_weights.get(tag,0) for tag in candidate["tags"])
        if score == 0:
            continue
        results.append({**candidate,'score':score})

    return sorted(results, key=lambda x: x['score'], reverse=True)

def get_tag_weights_from_db(db,media_type) -> dict[str, int]:
    return db.get_tag_weights(media_type)
