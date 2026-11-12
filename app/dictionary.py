"""Dictionary loader: reads dictionary/*.json (built from the Business_Adv knowledge base)
and serves plain-language business terms + startup playbooks. No extra dependency."""
import json
import re
from pathlib import Path

DICT_DIR = Path(__file__).resolve().parent.parent / "dictionary"

_terms = None
_playbooks = None


def _load_json(name):
    path = DICT_DIR / name
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def terms():
    global _terms
    if _terms is None:
        _terms = _load_json("business_terms.json").get("entries", []) or []
    return _terms


def playbooks():
    global _playbooks
    if _playbooks is None:
        _playbooks = _load_json("startup_playbook.json").get("playbooks", []) or []
    return _playbooks


def search(query="", category="", limit=50):
    query = (query or "").strip().lower()
    words = [w for w in re.findall(r"\w+", query) if len(w) > 2]
    out = []
    for e in terms():
        if category and e.get("category") != category:
            continue
        if not words:
            out.append((0, e))
            continue
        hay = f"{e.get('term','')} {e.get('meaning_simple','')} {e.get('use_it','')} {' '.join(e.get('related', []))}".lower()
        score = sum(1 for w in words if w in hay)
        # boost exact-term matches so "gst" finds "GST" first
        if query and query in e.get("term", "").lower():
            score += 3
        if score:
            out.append((score, e))
    out.sort(key=lambda t: -t[0])
    return [e for _, e in out[:limit]]


def lookup_for_question(question, limit=4):
    """Terms relevant to a question - injected into the advisor prompt."""
    return search(question, limit=limit)
