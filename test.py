from recommender import score_candidates

tag_weights = {'Action': 5, 'Horror': 4, 'Seinen': 3}

candidates = [
    {'mal_id': 1, 'media_type': 'manga', 'title': 'A', 'tags': ['Action', 'Horror']},
    {'mal_id': 2, 'media_type': 'manga', 'title': 'B', 'tags': ['Romance', 'Shoujo']},
    {'mal_id': 3, 'media_type': 'manga', 'title': 'C', 'tags': ['Seinen', 'Action']},
]

results = score_candidates(candidates, tag_weights, set(), set(), set())
print(results[0]['title'])  # A (score 9)
print(results[1]['title'])  # C (score 8)
# B not in results (score 0)

# Test blacklisted tag
results2 = score_candidates(candidates, tag_weights, set(), set(), {'Action'})
print(results2)  # empty — both A and C contain Action