from api import JikanClient, extract_tags

client = JikanClient()

# Test get_media
manga = client.get_media("manga", 1)
print(manga["title"])

# Test extract_tags
print(extract_tags(manga))

# Test search_media
result = client.search_media("manga", "vagabond")
print(result["title"])

# Test get_by_genres
candidates = client.get_by_genres("manga", [1, 14], page=1)
print(len(candidates))
print(candidates[0]["title"])

# Test get_genres
genres = client.get_genres("manga")
print(genres)

# Test None handling
missing = client.get_media("manga", 999999999)
print(missing)