import sqlite3
import datetime
from contextlib import contextmanager
from .config import DB_PATH

_initialized = False

GENRES = ["fantasy", "sci-fi", "romance", "mystery", "horror", "literary", "any"]
LENGTHS = ["flash", "short", "novella"]
STYLES = ["lyrical", "spare", "cinematic", "epistolary"]
CRITIQUE_MODES = ["open", "workshop", "closed"]
WORKSHOP_PROMPTS = {
    "character": "Examine the characters: are their motivations clear and consistent?",
    "plot":      "Examine the plot: does the structure create momentum and payoff?",
    "world":     "Examine the world: does the setting feel lived-in and specific?",
    "writing":   "Examine the prose: does the writing style serve the story's tone?",
}


@contextmanager
def _conn():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA foreign_keys=ON")
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init_db():
    global _initialized
    with _conn() as con:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT NOT NULL UNIQUE,
                email       TEXT NOT NULL UNIQUE,
                password    TEXT NOT NULL,
                bio         TEXT NOT NULL DEFAULT '',
                avatar      TEXT NOT NULL DEFAULT '',
                created_at  TEXT NOT NULL DEFAULT (datetime('now')),
                level       INTEGER NOT NULL DEFAULT 0,
                xp          INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS stories (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                title         TEXT NOT NULL,
                author        TEXT NOT NULL DEFAULT 'Anonymous',
                user_id       INTEGER REFERENCES users(id) ON DELETE SET NULL,
                body          TEXT NOT NULL,
                genre         TEXT NOT NULL DEFAULT 'any',
                length        TEXT NOT NULL DEFAULT 'short',
                style         TEXT NOT NULL DEFAULT 'cinematic',
                critique_mode TEXT NOT NULL DEFAULT 'open',
                likes         INTEGER NOT NULL DEFAULT 0,
                created_at    TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS comments (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id   INTEGER NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
                author     TEXT NOT NULL DEFAULT 'Anonymous',
                user_id    INTEGER REFERENCES users(id) ON DELETE SET NULL,
                body       TEXT NOT NULL,
                lens       TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS usage_log (
                key        TEXT NOT NULL,
                date       TEXT NOT NULL,
                count      INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (key, date)
            );

            CREATE TABLE IF NOT EXISTS saved_work (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                kind       TEXT NOT NULL,
                title      TEXT NOT NULL DEFAULT '',
                content    TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
        """)

        if not con.execute("SELECT 1 FROM stories LIMIT 1").fetchone():
            con.execute("""
                INSERT INTO stories (title, author, body, genre, length, style, critique_mode) VALUES
                ('The Second Shadow', 'Demo Author',
                 'The city remembered its dead differently now — not with stone or bronze, but with living shadows that walked the alleys at dusk. Maren had learned to tell them apart from the living by the way they paused at corners, uncertain of a world that had moved on without them.',
                 'fantasy', 'flash', 'lyrical', 'open')
            """)
            con.execute("""
                INSERT INTO stories (title, author, body, genre, length, style, critique_mode) VALUES
                ('Signal, With Apology', 'Demo Author',
                 'The last transmission from Station Kepler-9 was not a distress call. It was a love letter — seventeen minutes of compressed audio addressed to no one the crew manifest listed, discovered only when the salvage team decoded the black box three years later.',
                 'sci-fi', 'flash', 'spare', 'workshop')
            """)
    _initialized = True


def _ensure():
    global _initialized
    if not _initialized:
        init_db()


def get_daily_usage(key: str) -> int:
    _ensure()
    today = datetime.date.today().isoformat()
    with _conn() as con:
        row = con.execute("SELECT count FROM usage_log WHERE key=? AND date=?", (key, today)).fetchone()
        return row["count"] if row else 0


def increment_daily_usage(key: str) -> int:
    _ensure()
    today = datetime.date.today().isoformat()
    with _conn() as con:
        existing = con.execute("SELECT count FROM usage_log WHERE key=? AND date=?", (key, today)).fetchone()
        if existing:
            new_count = existing["count"] + 1
            con.execute("UPDATE usage_log SET count=? WHERE key=? AND date=?", (new_count, key, today))
        else:
            new_count = 1
            con.execute("INSERT INTO usage_log (key, date, count) VALUES (?,?,?)", (key, today, 1))
        return new_count


def create_user(username: str, email: str, password: str) -> dict:
    _ensure()
    with _conn() as con:
        cur = con.execute("INSERT INTO users (username, email, password) VALUES (?,?,?)", (username, email, password))
        return dict(con.execute("SELECT * FROM users WHERE id=?", (cur.lastrowid,)).fetchone())


def get_user_by_email(email: str):
    _ensure()
    with _conn() as con:
        row = con.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        return dict(row) if row else None


def get_user_by_username(username: str):
    _ensure()
    with _conn() as con:
        row = con.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        return dict(row) if row else None


def get_user_by_id(uid: int):
    _ensure()
    with _conn() as con:
        row = con.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
        return dict(row) if row else None


def update_user(uid: int, bio: str = None, avatar: str = None):
    _ensure()
    with _conn() as con:
        if bio is not None:
            con.execute("UPDATE users SET bio=? WHERE id=?", (bio, uid))
        if avatar is not None:
            con.execute("UPDATE users SET avatar=? WHERE id=?", (avatar, uid))
        row = con.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
        return dict(row) if row else None


def add_xp(uid: int, amount: int):
    _ensure()
    LEVELS = [0, 100, 300, 700, 1500, 3000]
    with _conn() as con:
        user = con.execute("SELECT xp, level FROM users WHERE id=?", (uid,)).fetchone()
        if not user:
            return None
        new_xp = user["xp"] + amount
        new_level = user["level"]
        while new_level + 1 < len(LEVELS) and new_xp >= LEVELS[new_level + 1]:
            new_level += 1
        con.execute("UPDATE users SET xp=?, level=? WHERE id=?", (new_xp, new_level, uid))
        return {"xp": new_xp, "level": new_level}


def save_work(uid: int, kind: str, title: str, content: str) -> dict:
    _ensure()
    with _conn() as con:
        cur = con.execute("INSERT INTO saved_work (user_id, kind, title, content) VALUES (?,?,?,?)", (uid, kind, title, content))
        return dict(con.execute("SELECT * FROM saved_work WHERE id=?", (cur.lastrowid,)).fetchone())


def list_saved_work(uid: int, kind: str = None):
    _ensure()
    with _conn() as con:
        if kind:
            rows = con.execute("SELECT * FROM saved_work WHERE user_id=? AND kind=? ORDER BY created_at DESC", (uid, kind)).fetchall()
        else:
            rows = con.execute("SELECT * FROM saved_work WHERE user_id=? ORDER BY created_at DESC", (uid,)).fetchall()
        return [dict(r) for r in rows]


def delete_saved_work(uid: int, item_id: int) -> bool:
    _ensure()
    with _conn() as con:
        cur = con.execute("DELETE FROM saved_work WHERE id=? AND user_id=?", (item_id, uid))
        return cur.rowcount > 0


def list_stories(genre=None, length=None, style=None):
    _ensure()
    filters, params = [], []
    if genre and genre != "any":
        filters.append("genre=?"); params.append(genre)
    if length:
        filters.append("length=?"); params.append(length)
    if style:
        filters.append("style=?"); params.append(style)
    where = ("WHERE " + " AND ".join(filters)) if filters else ""
    with _conn() as con:
        rows = con.execute(
            f"SELECT id,title,author,genre,length,style,critique_mode,likes,created_at FROM stories {where} ORDER BY created_at DESC",
            params,
        ).fetchall()
        return [dict(r) for r in rows]


def get_story(sid: int):
    _ensure()
    with _conn() as con:
        row = con.execute("SELECT * FROM stories WHERE id=?", (sid,)).fetchone()
        if not row:
            return None
        story = dict(row)
        comments = con.execute("SELECT * FROM comments WHERE story_id=? ORDER BY created_at ASC", (sid,)).fetchall()
        story["comments"] = [dict(c) for c in comments]
        return story


def create_story(data: dict) -> dict:
    _ensure()
    with _conn() as con:
        cur = con.execute(
            "INSERT INTO stories (title, author, user_id, body, genre, length, style, critique_mode) VALUES (:title,:author,:user_id,:body,:genre,:length,:style,:critique_mode)",
            data,
        )
        return dict(con.execute("SELECT * FROM stories WHERE id=?", (cur.lastrowid,)).fetchone())


def like_story(sid: int) -> int:
    _ensure()
    with _conn() as con:
        con.execute("UPDATE stories SET likes=likes+1 WHERE id=?", (sid,))
        row = con.execute("SELECT likes FROM stories WHERE id=?", (sid,)).fetchone()
        return row["likes"] if row else 0


def add_comment(story_id: int, author: str, body: str, lens: str = None, user_id: int = None) -> dict:
    _ensure()
    with _conn() as con:
        cur = con.execute("INSERT INTO comments (story_id, author, user_id, body, lens) VALUES (?,?,?,?,?)", (story_id, author, user_id, body, lens))
        return dict(con.execute("SELECT * FROM comments WHERE id=?", (cur.lastrowid,)).fetchone())


def user_stories(uid: int):
    _ensure()
    with _conn() as con:
        rows = con.execute(
            "SELECT id,title,genre,length,style,critique_mode,likes,created_at FROM stories WHERE user_id=? ORDER BY created_at DESC",
            (uid,),
        ).fetchall()
        return [dict(r) for r in rows]
