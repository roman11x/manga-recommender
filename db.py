# Database class; all SQL; nothing else touches sqlite3
import sqlite3

class Database:
    def __init__(self, path):
        self.path = path
        self.con = sqlite3.connect(path)
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
                synopsis TEXT NOT NULL,
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