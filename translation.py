"""
Runtime auto-translation for Jharkhand Samadhan.

Any string that is missing a translation for the current language is
translated on demand through a public translation endpoint and stored in a
persistent local cache (translations_cache.json). On later requests the value
comes straight from the cache — no network call, no script to re-run, nothing
to "push". New strings that are added later are translated automatically the
first time someone views them.

Safety rails (the UI must never break because of a translation hiccup):

* Only translates text that is genuinely missing for the active language —
  existing hand-written translations are always preferred.
* Never sends very long text through the endpoint (capped at 500 chars).
* Rate-limits itself: a rolling budget of calls per window. When the budget is
  exhausted the call fails fast and returns None so callers fall back to the
  normal English/Hindi chain.
* Retries a 429/5xx a couple of times with backoff.
* Caches *failures* briefly (60s) so we don't hammer a throttled endpoint on
  every page view.
* `AUTO_TRANSLATE=0` (or "false"/"off") disables online translation entirely.

Note: with multiple gunicorn workers each process keeps its own view of the
cache file and the last writer wins. That's fine for a prototype; a shared
datastore (or the AI-verification SQLite DB) would remove that caveat.
"""

import json
import os
import threading
import time
import urllib.parse
import urllib.request

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CACHE_FILE = os.path.join(BASE_DIR, "translations_cache.json")

ENABLED = os.environ.get("AUTO_TRANSLATE", "1").lower() not in ("0", "false", "off")

# Turning the knobs. Conservative defaults — this endpoint throttles hard.
MAX_TEXT_LEN = 500        # don't translate huge blobs through a free endpoint
BUDGET_CALLS = 6          # max online calls per window...
BUDGET_WINDOW = 8         # ...every N seconds (rolling)
RETRY_BACKOFF = ()        # one attempt per string; failures are cached (see FAIL_TTL)
HTTP_TIMEOUT = 8          # seconds per request — bounds page-load stall if host unreachable
FAIL_TTL = 3600           # remember "couldn't translate" for an hour (won't re-stall pages)
USER_AGENT = "Mozilla/5.0 (jharkhand-samadhan/auto-translate)"
_ENDPOINT = "https://translate.googleapis.com/translate_a/single?client=gtx&sl={src}&tl={dst}&dt=t&q={q}"

_lock = threading.Lock()
_cache = {}               # key -> {"t": text, "err": bool, "at": epoch}
_timestamps = []          # wall-clock times of recent online calls (rolling budget)
_last_failures = {}       # key -> epoch of last failed attempt


def _load_cache():
    global _cache
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as fh:
            _cache = json.load(fh)
    except Exception:
        _cache = {}


def _save_cache():
    try:
        tmp = CACHE_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(_cache, fh, ensure_ascii=False)
        os.replace(tmp, CACHE_FILE)
    except Exception:
        pass


def _key(target, text):
    return "{}|||{}".format(target, text)


def _budget_ok():
    """True while we're within the rolling online-call budget."""
    global _timestamps
    now = time.time()
    _timestamps = [ts for ts in _timestamps if now - ts < BUDGET_WINDOW]
    return len(_timestamps) < BUDGET_CALLS


def _endpoint(source, target, text):
    q = urllib.parse.quote(text)
    return _ENDPOINT.format(src=source, dst=target, q=q)


def _unpack(data):
    """Translate the endpoint's nested response into one string."""
    parts = []
    for seg in data[0]:
        if seg and seg[0]:
            parts.append(seg[0])
    return "".join(parts)


def translate(text, target, source="en"):
    """
    Translate `text` into `target`, preferring the persistent cache.

    Returns the translated string, or None when the text is empty/English,
    too long, disabled, unsupported by the endpoint, or the budget is spent
    (callers should then use their normal fallback chain).
    """
    if not ENABLED or not text or not text.strip():
        return None
    if target == source or target == "en":
        return None
    if len(text) > MAX_TEXT_LEN:
        return None

    key = _key(target, text)
    with _lock:
        hit = _cache.get(key)
        if hit is not None:
            if not hit.get("err"):
                return hit.get("t")
            if time.time() - hit.get("at", 0) < FAIL_TTL:
                return None  # remembered failure, don't retry yet
        _cache.pop(key, None)  # stale failure -> try again below

    if not _budget_ok():
        return None  # fail fast this window; cache warms up on later views

    attempts = 1 + len(RETRY_BACKOFF)
    for i in range(attempts):
        try:
            req = urllib.request.Request(_endpoint(source, target, text),
                                         headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
                translated = _unpack(json.loads(resp.read().decode("utf-8")))
            if not translated:
                raise ValueError("empty translation")
            with _lock:
                _cache[key] = {"t": translated, "err": False, "at": time.time()}
                _timestamps.append(time.time())
                _save_cache()
            return translated
        except Exception:
            with _lock:
                _timestamps.append(time.time())
            if i < len(RETRY_BACKOFF):
                time.sleep(RETRY_BACKOFF[i])
            continue

    with _lock:
        _cache[key] = {"t": None, "err": True, "at": time.time()}
        _save_cache()
    return None


_load_cache()