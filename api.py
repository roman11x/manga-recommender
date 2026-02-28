# JikanClient class; all HTTP calls; rate limiting
import requests
import time

class JikanClient:
    def __init__(self):
        self.base_url = "https://api.jikan.moe/v4"
        self._last_call = 0

    def _get(self, endpoint, params=None):
        now = time.time()
        elapsed = now - self._last_call
        if elapsed < 0.4: #rate limit: 3 requests/second
            time.sleep(0.4 - elapsed)
        self._last_call = time.time()
        response = requests.get(self.base_url + endpoint, params=params)
        response.raise_for_status()
        return response.json()

    #Full manga/anime data for one title
    def get_media(self, media_type, mal_id) -> dict | None:
        #https://api.jikan.moe/v4/manga/11/full
        endpoint = f"/{media_type}/{mal_id}/full"
        try:
            response = self._get(endpoint)
            return response["data"]
        except Exception:
            return None

    #Search media by name
    def search_media(self, media_type,title) -> dict | None:
        #https://api.jikan.moe/v4/manga?q=berserk&limit=1
        endpoint = f"/{media_type}"
        params = {"q": title, "limit": 1}
        try:
            response = self._get(endpoint, params)
            data = response["data"][0]
        except Exception:
            return None

        if not data:
            return None
        return data

    #Browse by genre
    def get_by_genres(self, media_type, genre_ids, page=1) -> list[dict] | None:
        #https://api.jikan.moe/v4/manga?genres=7&limit=5&page=1
        endpoint = f"/{media_type}"

        params = {"genres": ",".join(str(i) for i in genre_ids), "limit": 25, "page": page}
        try:
            response = self._get(endpoint, params)
            return response["data"]
        except Exception:
            return None

    # All media genres with numeric IDS
    def get_genres(self, media_type) -> dict[str,int]:
        #https://api.jikan.moe/v4/genres/manga
        endpoint = f"/genres/{media_type}"
        try:
            response = self._get(endpoint)
            return {item["name"]:item["mal_id"] for item in response["data"]}
        except Exception:
            return None

#Tag extraction helper
def extract_tags(media_data:dict) -> list[str]:
    genres = [g['name'] for g in media_data.get('genres', [])]
    themes = [t['name'] for t in media_data.get('themes', [])]
    return genres + themes