# Database class; all SQL; nothing else touches sqlite3
import sqlite3

class Database:
    def __init__(self, path):
        self.path = path
        self.con = sqlite3.connect(path, check_same_thread=False)
        self.con.row_factory = sqlite3.Row
    def setup(self):
        with self.con as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS media(
            mal_id INTEGER NOT NULL,
            media_type TEXT NOT NULL,
            title TEXT NOT NULL,
            status TEXT NOT NULL,
            liked INTEGER,
            added_at TEXT DEFAULT (datetime('now')),
                PRIMARY KEY (mal_id, media_type)
                );
                CREATE TABLE IF NOT EXISTS tags(
                mal_id INTEGER NOT NULL,
                media_type TEXT NOT NULL,
                tag TEXT NOT NULL,
                FOREIGN KEY (mal_id,media_type) REFERENCES media(mal_id,media_type)
                    );
                CREATE TABLE IF NOT EXISTS recommendations(
                mal_id INTEGER NOT NULL,
                media_type TEXT NOT NULL,
                title TEXT NOT NULL,
                score REAL,
                'state' text NOT NULL,
                cover_url TEXT,
                synopsis TEXT,
                mal_score REAL,
                generated_at TEXT DEFAULT (datetime('now')),
                    PRIMARY KEY (mal_id, media_type)
                    );
                CREATE TABLE IF NOT EXISTS recommendation_tags(
                    mal_id INTEGER NOT NULL,
                    media_type TEXT NOT NULL,
                    tag TEXT NOT NULL,
                    'matched' integer NOT NULL,
                    FOREIGN KEY (mal_id, media_type) REFERENCES recommendations(mal_id,media_type)
                    );
                    CREATE TABLE IF NOT EXISTS blacklisted_tags
                    (
                        tag TEXT NOT NULL,
                        media_type TEXT NOT NULL,
                        PRIMARY KEY (tag, media_type)
                    );
                CREATE TABLE IF NOT EXISTS settings(
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL);
            """)
    def add_media(self,mal_id,media_type,title,status, tags, liked=None):
        cursor = self.con.cursor()
        cursor.execute('''
        INSERT INTO media(mal_id,media_type,title,status,liked) values (?,?,?,?,? )''', (mal_id,media_type,title,status,liked))

        for tag in tags:
            cursor.execute('''
            INSERT OR IGNORE INTO tags(mal_id,media_type,tag) values (?,?,?)''', (mal_id,media_type,tag))
        self.con.commit()

    def delete_media(self, mal_id, media_type):
        cursor = self.con.cursor()
        cursor.execute("DELETE FROM media WHERE mal_id = ? AND media_type = ?", (mal_id, media_type))
        cursor.execute("DELETE FROM tags WHERE mal_id = ? AND media_type = ?", (mal_id, media_type))
        self.con.commit()

    def get_all_media(self, media_type = None) -> list[dict] :
        query = "SELECT * FROM media WHERE status != 'blacklisted'"
        params = []
        if media_type is not None:
            query += " AND media_type = ?"
            params.append(media_type)
        cursor = self.con.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


    def get_media(self, mal_id, media_type) -> dict | None:
        cursor = self.con.cursor()
        cursor.execute('''
        Select * from media WHERE mal_id =? and media_type = ?''', (mal_id, media_type))
        row = cursor.fetchone()
        if row is None:
            return None
        return dict(row)

    def update_status(self, mal_id, media_type, status):
        cursor = self.con.cursor()
        cursor.execute('''
        UPDATE media SET status = ? WHERE mal_id =? and media_type = ?''', (status, mal_id, media_type))
        self.con.commit()

    def update_liked(self, mal_id, media_type, liked):
        cursor = self.con.cursor()
        cursor.execute('''
        UPDATE media SET liked = ? WHERE mal_id =? and media_type = ?''', (liked, mal_id, media_type))
        self.con.commit()
    # Does the user have a taste so that we can look for recommendations
    def has_consumed_liked_entries(self) -> bool:
        cursor = self.con.cursor()
        cursor.execute('''
        SELECT COUNT(*) FROM media WHERE liked = 1 AND status = 'consumed' ''')
        return cursor.fetchone()[0] > 0

    def get_tag_weights(self, media_type) -> dict[str, int]:
        cursor = self.con.cursor()
        cursor.execute('''
        SELECT tags.tag, COUNT(*) FROM TAGS  
        JOIN media ON tags.mal_id = media.mal_id AND tags.media_type = media.media_type 
        WHERE status = 'consumed' AND liked = 1 AND media.media_type = ?
        GROUP BY tags.tag''', (media_type,))
        # Extract the tag (index 0) and the count (index 1) to build the dictionary
        return {row[0] : row[1] for row in cursor.fetchall()}

    # get consumed media for filtering returns [(mal_id,mediatype)[
    def get_library_ids (self, media_type) -> set[tuple]:
        cursor = self.con.cursor()
        cursor.execute('''
        SELECT mal_id, media_type FROM media WHERE status != 'blacklisted' AND media_type = ? ''', (media_type,))
        return {(row[0], row[1]) for row in cursor.fetchall()}

    # get blacklisted media for filtering returns [(mal_id,mediatype)]
    def get_blacklist_ids(self, media_type) -> set[tuple]:
        cursor = self.con.cursor()
        cursor.execute('''
        SELECT mal_id, media_type FROM media WHERE status = 'blacklisted' AND media_type = ? ''', (media_type,))
        return {(row[0], row[1]) for row in cursor.fetchall()}

    def add_blacklisted_tag(self,tag,media_type):
        cursor = self.con.cursor()
        cursor.execute('''
        INSERT INTO blacklisted_tags(tag,media_type) values (?,?)''', (tag,media_type))
        self.con.commit()

    def remove_blacklisted_tag(self,tag,media_type):
        cursor = self.con.cursor()
        cursor.execute('''
        DELETE FROM blacklisted_tags WHERE tag = ? AND media_type = ?''', (tag,media_type))
        self.con.commit()

    def get_blacklisted_tags(self,media_type) -> set[str]:
        cursor = self.con.cursor()
        cursor.execute('''
        SELECT tag FROM blacklisted_tags WHERE media_type = ? OR media_type ='both' ''', (media_type,))
        return {row[0] for row in cursor.fetchall()}
    # return all blackisted tags with their media for gui
    def get_all_blacklisted_tags(self) -> list[dict]:
        cursor = self.con.cursor()
        cursor.execute("SELECT tag, media_type FROM blacklisted_tags ORDER BY tag")
        return [{"tag": row[0], "media_type": row[1]} for row in cursor.fetchall()]

    def save_recommendation(self, item_dict):
        cursor = self.con.cursor()
        cursor.execute('''
        INSERT OR IGNORE INTO recommendations(mal_id,media_type,title,score, state, cover_url,synopsis,mal_score) 
        VALUES (?,?,?,?,?,?,?,?) '''
                       ,(item_dict.get("mal_id"), item_dict.get("media_type"), item_dict.get("title"), item_dict.get("score"), "pending", item_dict.get("cover_url"), item_dict.get("synopsis"), item_dict.get("mal_score")))

        for tag in item_dict['tags']:
            cursor.execute('''
            INSERT OR IGNORE INTO recommendation_tags(mal_id,media_type,tag, matched) VALUES (?,?,?,?)''',
                           (item_dict.get("mal_id"), item_dict.get("media_type"), tag['name'], tag['matched']))

        self.con.commit()

    def get_pending_recommendations(self, media_type = None) -> list[dict]:
        query = "SELECT * FROM recommendations WHERE state = 'pending'"
        params = []
        if media_type is not None:
            query += " AND media_type = ?"
            params.append(media_type)
        cursor = self.con.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_saved_recommendations(self, media_type = None) -> list[dict]:
        query = "SELECT * FROM recommendations WHERE state = 'saved'"
        params = []
        if media_type is not None:
            query += " AND media_type = ?"
            params.append(media_type)
        cursor = self.con.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_recommendation_tags(self, mal_id, media_type) -> list[str]:
        cursor = self.con.cursor()
        cursor.execute('''
                       SELECT tag
                       FROM recommendation_tags
                       WHERE mal_id = ?
                         AND media_type = ?
                       ''', (mal_id, media_type))
        return [row[0] for row in cursor.fetchall()]

    def move_recommendation_to_saved(self, mal_id, media_type):
        cursor = self.con.cursor()
        cursor.execute('''
        UPDATE recommendations SET state = 'saved' WHERE mal_id = ? and media_type = ?''', (mal_id, media_type))
        self.con.commit()
    def remove_recommendation(self, mal_id, media_type):
        cursor = self.con.cursor()
        cursor.execute('''
        DELETE FROM recommendations WHERE mal_id = ? and media_type = ?''', (mal_id, media_type))
        cursor.execute('''
        DELETE FROM recommendation_tags WHERE mal_id = ? and media_type = ?''', (mal_id, media_type))
        self.con.commit()
    def clear_pending_recommendations(self, media_type):
        cursor = self.con.cursor()
        cursor.execute('''
        DELETE FROM recommendations WHERE state = 'pending' AND media_type = ?  ''', (media_type,))
        self.con.commit()

    def get_setting(self, key) -> str | None:
        cursor = self.con.cursor()
        cursor.execute('''
        SELECT value FROM settings WHERE key = ?''', (key,))
        row = cursor.fetchone()
        if row is  None:
            return None
        return row[0]

    def set_setting(self, key, value):
        cursor = self.con.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO settings(key, value) VALUES (?,?)''', (key, value))
        self.con.commit()

    def get_active_media_types(self) -> list[str]:
        value = self.get_setting('active_media_types')
        if value is None:
            return []
        return value.split(',')


