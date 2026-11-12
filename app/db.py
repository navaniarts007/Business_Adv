"""Local SQLite storage: profiles, Q&A history, knowledge base (with FTS5 search) and a research cache."""
import json
import re
import sqlite3
from contextlib import contextmanager

from .config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS profiles (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    segment     TEXT NOT NULL,            -- farmer | msme | startup | company | retail | artisan
    business    TEXT DEFAULT '',          -- what they grow / make / sell
    location    TEXT DEFAULT '',          -- village / town / district
    state       TEXT DEFAULT '',
    language    TEXT DEFAULT 'English',
    stage       TEXT DEFAULT '',          -- idea | running | growing ...
    turnover    TEXT DEFAULT '',
    details     TEXT DEFAULT '',
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS conversations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id  INTEGER REFERENCES profiles(id) ON DELETE CASCADE,
    mode        TEXT NOT NULL,
    question    TEXT NOT NULL,
    answer      TEXT NOT NULL,
    sources     TEXT DEFAULT '[]',
    search_queries TEXT DEFAULT '[]',
    model       TEXT DEFAULT '',
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS knowledge (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    segment      TEXT NOT NULL,           -- a segment or 'all'
    category     TEXT NOT NULL,           -- scheme | finance | compliance | market | practice
    title        TEXT NOT NULL UNIQUE,
    summary      TEXT NOT NULL,
    eligibility  TEXT DEFAULT '',
    benefits     TEXT DEFAULT '',
    how_to_apply TEXT DEFAULT '',
    url          TEXT DEFAULT '',
    tags         TEXT DEFAULT '',
    custom       INTEGER DEFAULT 0
);

CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(
    title, summary, eligibility, benefits, tags,
    content='knowledge', content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS knowledge_ai AFTER INSERT ON knowledge BEGIN
    INSERT INTO knowledge_fts(rowid, title, summary, eligibility, benefits, tags)
    VALUES (new.id, new.title, new.summary, new.eligibility, new.benefits, new.tags);
END;
CREATE TRIGGER IF NOT EXISTS knowledge_ad AFTER DELETE ON knowledge BEGIN
    INSERT INTO knowledge_fts(knowledge_fts, rowid, title, summary, eligibility, benefits, tags)
    VALUES ('delete', old.id, old.title, old.summary, old.eligibility, old.benefits, old.tags);
END;
CREATE TRIGGER IF NOT EXISTS knowledge_au AFTER UPDATE ON knowledge BEGIN
    INSERT INTO knowledge_fts(knowledge_fts, rowid, title, summary, eligibility, benefits, tags)
    VALUES ('delete', old.id, old.title, old.summary, old.eligibility, old.benefits, old.tags);
    INSERT INTO knowledge_fts(rowid, title, summary, eligibility, benefits, tags)
    VALUES (new.id, new.title, new.summary, new.eligibility, new.benefits, new.tags);
END;

CREATE TABLE IF NOT EXISTS research_cache (
    key         TEXT PRIMARY KEY,
    payload     TEXT NOT NULL,
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


@contextmanager
def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    from .seed import KNOWLEDGE

    with connect() as conn:
        conn.executescript(SCHEMA)
        # Seed entries are upserted by title so edits to seed.py reach existing databases.
        for k in KNOWLEDGE:
            conn.execute(
                """INSERT INTO knowledge (segment, category, title, summary, eligibility, benefits, how_to_apply, url, tags)
                   VALUES (:segment, :category, :title, :summary, :eligibility, :benefits, :how_to_apply, :url, :tags)
                   ON CONFLICT(title) DO UPDATE SET
                     segment=excluded.segment, category=excluded.category, summary=excluded.summary,
                     eligibility=excluded.eligibility, benefits=excluded.benefits,
                     how_to_apply=excluded.how_to_apply, url=excluded.url, tags=excluded.tags
                   WHERE custom = 0""",
                {"eligibility": "", "benefits": "", "how_to_apply": "", "url": "", "tags": "", **k},
            )


def rows(cur):
    return [dict(r) for r in cur.fetchall()]


# ---------- profiles ----------

PROFILE_FIELDS = ("name", "segment", "business", "location", "state", "language", "stage", "turnover", "details")


def list_profiles():
    with connect() as conn:
        return rows(conn.execute("SELECT * FROM profiles ORDER BY id DESC"))


def get_profile(pid):
    with connect() as conn:
        r = conn.execute("SELECT * FROM profiles WHERE id = ?", (pid,)).fetchone()
        return dict(r) if r else None


def save_profile(data, pid=None):
    values = {f: (data.get(f) or "") for f in PROFILE_FIELDS}
    with connect() as conn:
        if pid:
            sets = ", ".join(f"{f} = :{f}" for f in PROFILE_FIELDS)
            conn.execute(f"UPDATE profiles SET {sets} WHERE id = :id", {**values, "id": pid})
        else:
            cols = ", ".join(PROFILE_FIELDS)
            params = ", ".join(f":{f}" for f in PROFILE_FIELDS)
            pid = conn.execute(f"INSERT INTO profiles ({cols}) VALUES ({params})", values).lastrowid
    return get_profile(pid)


def delete_profile(pid):
    with connect() as conn:
        conn.execute("DELETE FROM profiles WHERE id = ?", (pid,))


# ---------- conversations ----------

def add_conversation(profile_id, mode, question, answer, sources, search_queries, model):
    with connect() as conn:
        cid = conn.execute(
            """INSERT INTO conversations (profile_id, mode, question, answer, sources, search_queries, model)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (profile_id, mode, question, answer, json.dumps(sources), json.dumps(search_queries), model),
        ).lastrowid
        return cid


def history(profile_id, limit=50):
    with connect() as conn:
        out = rows(conn.execute(
            "SELECT * FROM conversations WHERE profile_id IS ? ORDER BY id DESC LIMIT ?",
            (profile_id, limit),
        ))
    for r in out:
        r["sources"] = json.loads(r["sources"] or "[]")
        r["search_queries"] = json.loads(r["search_queries"] or "[]")
    return out


def delete_conversation(cid):
    with connect() as conn:
        conn.execute("DELETE FROM conversations WHERE id = ?", (cid,))


# ---------- knowledge base ----------

def _fts_query(text):
    words = [w for w in re.findall(r"\w+", text.lower()) if len(w) > 2]
    return " OR ".join(f'"{w}"*' for w in words[:12])


def search_knowledge(query="", segment=None, limit=8):
    seg_filter = "AND k.segment IN (?, 'all')" if segment else ""
    seg_args = [segment] if segment else []
    with connect() as conn:
        match = _fts_query(query) if query else ""
        if match:
            found = rows(conn.execute(
                f"""SELECT k.* FROM knowledge_fts f JOIN knowledge k ON k.id = f.rowid
                    WHERE knowledge_fts MATCH ? {seg_filter}
                    ORDER BY bm25(knowledge_fts) LIMIT ?""",
                [match, *seg_args, limit],
            ))
            if found:
                return found
        where = "WHERE k.segment IN (?, 'all')" if segment else ""
        return rows(conn.execute(
            f"SELECT k.* FROM knowledge k {where} ORDER BY k.segment = 'all', k.category, k.title LIMIT ?",
            [*seg_args, limit if query else 500],
        ))


def add_knowledge(data):
    fields = ("segment", "category", "title", "summary", "eligibility", "benefits", "how_to_apply", "url", "tags")
    values = {f: (data.get(f) or "") for f in fields}
    with connect() as conn:
        kid = conn.execute(
            f"INSERT INTO knowledge ({', '.join(fields)}, custom) VALUES ({', '.join(':' + f for f in fields)}, 1)",
            values,
        ).lastrowid
        return dict(conn.execute("SELECT * FROM knowledge WHERE id = ?", (kid,)).fetchone())


def delete_knowledge(kid):
    with connect() as conn:
        conn.execute("DELETE FROM knowledge WHERE id = ? AND custom = 1", (kid,))


# ---------- research cache ----------

def cache_get(key, max_age_hours):
    if max_age_hours <= 0:
        return None
    with connect() as conn:
        r = conn.execute(
            "SELECT payload FROM research_cache WHERE key = ? AND created_at >= datetime('now', ?)",
            (key, f"-{max_age_hours} hours"),
        ).fetchone()
    return json.loads(r["payload"]) if r else None


def cache_put(key, payload):
    with connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO research_cache (key, payload, created_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
            (key, json.dumps(payload)),
        )
