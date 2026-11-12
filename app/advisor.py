"""Advisory engine: local knowledge base + Gemini with live Google Search / Google Maps grounding."""
import hashlib
import json
import time
from datetime import date

from . import db, dictionary
from .config import (
    CACHE_HOURS, COUNTRY, FALLBACK_MODELS, GEMINI_API_KEY, GEMINI_MODEL, SARVAM_API_KEY, SARVAM_MODEL, SARVAM_URL,
)

SEGMENTS = {
    "farmer": "farmer / agri-producer",
    "msme": "micro, small or medium enterprise (MSME)",
    "startup": "startup founder",
    "company": "established company / enterprise",
    "retail": "shopkeeper, kirana or street vendor",
    "artisan": "artisan / craftsperson / weaver",
}

MODES = {
    "quick": (
        "Give a short, practical answer (max ~250 words): the direct answer first, then 3-5 numbered action "
        "steps. Use simple words a person with primary-school education understands."
    ),
    "research": (
        "Do thorough research with multiple Google searches and write a structured advisory report with these "
        "sections as markdown headings: Summary; Market & demand (current prices/trends with numbers and dates); "
        "Costs, pricing & profit estimate (a small table in local currency); Government schemes, finance & "
        "licences; Competition & opportunities; Risks and how to reduce them; 30-60-90 day action plan. "
        "Be specific to the location and segment."
    ),
    "nearby": (
        "Focus on places near the user: markets/mandis, suppliers, wholesalers, banks, government offices, "
        "training centres, buyers or service providers that are relevant to the question. List each with what "
        "it is useful for, and finish with practical next steps."
    ),
}

_client = None


def ai_enabled():
    return bool(GEMINI_API_KEY or SARVAM_API_KEY)


def _get_client():
    global _client
    if _client is None:
        from google import genai
        from google.genai import types
        # No SDK-level retries (they back off up to 60s per call); _call_gemini/_generate do fast fallbacks instead.
        _client = genai.Client(api_key=GEMINI_API_KEY, http_options=types.HttpOptions(
            timeout=120_000, retry_options=types.HttpRetryOptions(attempts=1),
        ))
    return _client


# When Google says the key has no quota for search/maps grounding, skip those tools for a while.
_tools_blocked_until = 0.0
TOOLS_BLOCK_SECONDS = 15 * 60


def _system_instruction(profile, mode):
    seg = SEGMENTS.get(profile.get("segment"), "business owner") if profile else "business owner"
    language = (profile or {}).get("language") or "English"
    return f"""You are "Vyapar Mitra", a trusted hyper-local business advisor for {COUNTRY}. You advise farmers,
artisans, shopkeepers, MSMEs, startups and established companies. The current user is a {seg}.
Today's date is {date.today().isoformat()}.

Rules:
- ALWAYS research with Google Search for anything time-sensitive: prices, mandi rates, weather, demand,
  scheme amounts, deadlines, interest rates, tax rules, regulations, competitors. Do not rely on memory for these.
- Make advice local: use the user's location, state and business. Mention specific markets, schemes, portals and numbers.
- Show money in local currency. Give realistic numbers with the date/source they come from.
- If the local knowledge base below is relevant, use it, but correct it if your search finds newer figures.
- Be honest about uncertainty; never invent schemes, prices or phone numbers. Tell the user to verify amounts on the official portal.
- Consider risk: never push loans the user cannot repay; mention cheaper alternatives first.
- Reply entirely in {language} (keep scheme names and URLs as they are). Use markdown.

{MODES.get(mode, MODES['quick'])}"""


def _profile_block(profile):
    if not profile:
        return "No profile given."
    fields = [
        ("Name", "name"), ("Segment", "segment"), ("Business / crops / products", "business"),
        ("Location", "location"), ("State", "state"), ("Stage", "stage"),
        ("Turnover / scale", "turnover"), ("Other details", "details"),
    ]
    return "\n".join(f"- {label}: {profile[key]}" for label, key in fields if profile.get(key))


def _kb_block(entries):
    if not entries:
        return "(no matching local entries)"
    parts = []
    for e in entries:
        parts.append(
            f"* {e['title']} [{e['segment']}/{e['category']}]: {e['summary']}"
            + (f" Eligibility: {e['eligibility']}" if e.get("eligibility") else "")
            + (f" Benefits: {e['benefits']}" if e.get("benefits") else "")
            + (f" Apply: {e['how_to_apply']}" if e.get("how_to_apply") else "")
            + (f" ({e['url']})" if e.get("url") else "")
        )
    return "\n".join(parts)


def _dict_block(question):
    try:
        found = dictionary.lookup_for_question(question, limit=4)
    except Exception:
        return "(dictionary unavailable)"
    if not found:
        return "(no matching dictionary terms)"
    return "\n".join(
        f"* {e['term']} ({e.get('category','')}): {e.get('meaning_simple','')} Use: {e.get('use_it','')}"
        for e in found
    )


def _offline_answer(question, profile, kb):
    lines = [
        "**Offline mode** - no Gemini API key is configured, so this answer comes only from the local knowledge base. "
        "Add `GEMINI_API_KEY` to `.env` for live researched advice.\n",
        f"Most relevant entries for: *{question}*\n",
    ]
    for e in kb[:5]:
        lines.append(f"### {e['title']}\n{e['summary']}")
        if e.get("eligibility"):
            lines.append(f"- **Who can apply:** {e['eligibility']}")
        if e.get("benefits"):
            lines.append(f"- **Benefits:** {e['benefits']}")
        if e.get("how_to_apply"):
            lines.append(f"- **How:** {e['how_to_apply']}")
        lines.append("")
    if not kb:
        lines.append("No matching entries. Try different words or add your own entry in the Knowledge tab.")
    return "\n".join(lines)


def _extract_grounding(response):
    sources, queries, widget = [], [], ""
    seen = set()
    for cand in response.candidates or []:
        gm = getattr(cand, "grounding_metadata", None)
        if not gm:
            continue
        queries.extend(gm.web_search_queries or [])
        if gm.search_entry_point and gm.search_entry_point.rendered_content:
            widget = gm.search_entry_point.rendered_content
        for chunk in gm.grounding_chunks or []:
            src = chunk.web or chunk.maps
            if src and src.uri and src.uri not in seen:
                seen.add(src.uri)
                sources.append({"title": src.title or src.uri, "url": src.uri, "kind": "maps" if chunk.maps else "web"})
    return sources, queries, widget


NO_SEARCH_NOTE = (
    "IMPORTANT: Live Google Search is NOT available for this answer. Do not claim you searched or that figures "
    "are live. Give the latest figures you know with their approximate date, and tell the user to check current "
    "prices and scheme amounts on the official portal or local mandi."
)


def _generate(contents, config):
    """Try the configured model, then the fallbacks when a model is retired (404), overloaded (5xx) or unreachable."""
    import httpx
    from google.genai import errors

    client = _get_client()
    last_err = None
    for model in dict.fromkeys([GEMINI_MODEL, *FALLBACK_MODELS]):
        try:
            # Short network drops (DNS failure, dropped connection) are retried on the same model.
            for attempt in range(3):
                try:
                    return model, client.models.generate_content(model=model, contents=contents, config=config)
                except (httpx.ConnectError, httpx.RemoteProtocolError):
                    if attempt == 2:
                        raise
                    time.sleep(2 * (attempt + 1))
        except (errors.ServerError, httpx.TransportError) as e:
            last_err = e
        except errors.ClientError as e:
            if getattr(e, "code", None) != 404:
                raise
            last_err = e
    raise last_err


def _call_gemini(contents, system, mode, lat=None, lng=None):
    """Returns (model, response, grounded). Degrades Maps -> Search -> no tools when the key lacks quota for a tool."""
    global _tools_blocked_until
    from google.genai import errors, types

    # Research reports are long; quick answers should fail over to the next model fast.
    http = types.HttpOptions(timeout=120_000 if mode == "research" else 40_000)
    no_search = types.GenerateContentConfig(system_instruction=f"{system}\n\n{NO_SEARCH_NOTE}", http_options=http)
    if time.time() < _tools_blocked_until:
        return (*_generate(contents, no_search), False)

    attempts = []
    if mode == "nearby" and lat is not None and lng is not None:
        attempts.append(([types.Tool(google_maps=types.GoogleMaps())], types.ToolConfig(
            retrieval_config=types.RetrievalConfig(lat_lng=types.LatLng(latitude=lat, longitude=lng))
        )))
    attempts.append(([types.Tool(google_search=types.GoogleSearch())], None))

    for tools, tool_config in attempts:
        config = types.GenerateContentConfig(
            system_instruction=system, tools=tools, tool_config=tool_config, http_options=http,
        )
        try:
            model, response = _generate(contents, config)
            return model, response, True
        except errors.ClientError as e:
            # 429 = no quota for grounding on this key's plan, 400 = tool not supported: try the next option.
            if getattr(e, "code", None) not in (400, 429):
                raise
    _tools_blocked_until = time.time() + TOOLS_BLOCK_SECONDS

    return (*_generate(contents, no_search), False)


def _short_error(e):
    code = getattr(e, "code", None)
    reasons = {429: "quota used up", 503: "servers busy", 500: "server error", 400: "request rejected"}
    if code in reasons:
        return reasons[code]
    name = type(e).__name__
    return "network problem" if "Connect" in name or "Timeout" in name or "Protocol" in name else name


def _call_sarvam(turns, system, mode):
    """Sarvam AI chat completion (OpenAI-compatible v2). turns = [(role, text), ...] with role user/assistant."""
    import httpx

    messages = [{"role": "system", "content": f"{system}\n\n{NO_SEARCH_NOTE}"}]
    messages += [{"role": role, "content": text} for role, text in turns]
    payload = {
        "model": SARVAM_MODEL, "messages": messages, "temperature": 0.4,
        # sarvam-105b reasons before answering (~1.5k tokens), so the budget must cover thinking + answer.
        "max_tokens": 12000 if mode == "research" else 5000,
    }
    headers = {"Authorization": f"Bearer {SARVAM_API_KEY}"}
    for attempt in range(3):
        try:
            r = httpx.post(SARVAM_URL, json=payload, headers=headers, timeout=180 if mode == "research" else 90)
            break
        except (httpx.ConnectError, httpx.RemoteProtocolError):
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))
    r.raise_for_status()
    text = (r.json()["choices"][0]["message"].get("content") or "").strip()
    # Some reasoning models inline their thinking; keep only the final answer.
    if "</think>" in text:
        text = text.split("</think>", 1)[1].strip()
    if not text:
        raise RuntimeError("Sarvam returned an empty answer")
    return text


def ask(question, profile=None, mode="quick", lat=None, lng=None):
    question = question.strip()
    segment = profile.get("segment") if profile else None
    kb = db.search_knowledge(f"{question} {profile.get('business', '') if profile else ''}", segment, limit=6)

    if not ai_enabled():
        return {
            "answer": _offline_answer(question, profile, kb),
            "sources": [{"title": e["title"], "url": e["url"], "kind": "local"} for e in kb if e.get("url")],
            "search_queries": [], "search_widget": "", "model": "offline-knowledge-base", "cached": False,
        }

    cache_key = hashlib.sha256(json.dumps(
        [question.lower(), mode, segment, profile and profile.get("location"), profile and profile.get("language"),
         profile and profile.get("business"), round(lat or 0, 2), round(lng or 0, 2)]
    ).encode()).hexdigest()
    cached = db.cache_get(cache_key, CACHE_HOURS)
    if cached:
        return {**cached, "cached": True}

    # Recent turns give the model conversational memory for follow-up questions.
    turns = []
    if profile:
        for past in reversed(db.history(profile["id"], limit=3)):
            turns += [("user", past["question"]), ("assistant", past["answer"][:2500])]

    prompt = f"""User profile:
{_profile_block(profile)}

Local knowledge base (may be outdated - verify with search):
{_kb_block(kb)}

Business dictionary (plain-language meanings from dictionary/ - use these to explain jargon simply):
{_dict_block(question)}

Question: {question}"""
    turns.append(("user", prompt))
    system = _system_instruction(profile, mode)
    local_sources = [{"title": e["title"], "url": e["url"], "kind": "local"} for e in kb[:3] if e.get("url")]

    # 1) Gemini (with Google Search when quota allows). 2) Sarvam AI if Gemini fails or has no key.
    gemini_error = None
    if GEMINI_API_KEY:
        from google.genai import types

        contents = [
            types.Content(role="model" if role == "assistant" else "user", parts=[types.Part(text=text)])
            for role, text in turns
        ]
        try:
            model, response, grounded = _call_gemini(contents, system, mode, lat, lng)
            if not response.text:
                raise RuntimeError("Gemini returned an empty answer")
        except Exception as e:
            if not SARVAM_API_KEY:
                raise
            gemini_error = e

    if not GEMINI_API_KEY or gemini_error:
        answer = (
            "> **Answered by Sarvam AI (fallback), not live-researched:** Gemini was unavailable"
            + (f" ({_short_error(gemini_error)})" if gemini_error else "")
            + ". Verify prices and dates before acting.\n\n" + _call_sarvam(turns, system, mode)
        )
        result = {
            "answer": answer, "sources": local_sources, "search_queries": [], "search_widget": "",
            "model": f"sarvam:{SARVAM_MODEL} (fallback)",
        }
        return {**result, "cached": False}

    sources, queries, widget = _extract_grounding(response)
    answer = response.text
    if not grounded:
        answer = (
            "> **Not live-researched:** Google Search grounding has no quota on this API key's plan, so this answer "
            "uses Gemini's own knowledge and the local database. Verify prices and dates before acting.\n\n" + answer
        )
    result = {
        "answer": answer, "sources": sources + local_sources, "search_queries": queries, "search_widget": widget,
        "model": model if grounded else f"{model} (no search)",
    }
    # Only cache researched answers, so they refresh as soon as search quota is available.
    if grounded:
        db.cache_put(cache_key, result)
    return {**result, "cached": False}
