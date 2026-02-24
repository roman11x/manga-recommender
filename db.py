# Database class; all SQL; nothing else touches sqlite3
import sqlite3

class database:
    def __init__(self, path):
        self.path = path

    def setup(self):
        with sqlite3.connect(self.path) as con:
            con.executescript("""
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
                value TEXT NOT NULL)
            """)