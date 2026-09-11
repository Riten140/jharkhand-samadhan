# Jharkhand Samadhan — Citizen Complaint Verification Platform (v2)

Three real logins — **Citizen**, **Officer**, **Admin** — with actual file
uploads and a real SQLite database (no more dummy in-memory data). Citizens
report a problem with a required photo/video. Road & infrastructure reports
get an automatic simulated satellite screening; everything else is verified
by an officer. Once accepted, an officer has a resolution deadline, and
uploading an "after" photo triggers a **real** before/after image comparison
(via Pillow) that decides whether the case auto-closes or reopens.

Only two dependencies: **Flask** and **Pillow**. No ORM, no login-manager
library — auth uses Flask's own session cookies, and the database layer is
plain `sqlite3` (see `db.py`).

## Run it

```bash
cd jsamadhan
pip install -r requirements.txt
python app.py
```

Open **http://localhost:5000**. A `jsamadhan.db` SQLite file and an
`uploads/` folder are created automatically on first run.

## Demo accounts (seeded automatically)

| Role    | Email                     | Password    |
|---------|---------------------------|-------------|
| Admin   | admin@jsamadhan.gov       | admin123    |
| Officer | officer1@jsamadhan.gov    | officer123  |
| Officer | officer2@jsamadhan.gov    | officer123  |
| Citizen | citizen@example.com       | citizen123  |

Citizens can also self-register from the landing page.

## Language support

A language switcher sits in the top-right of every page. The UI is built
around two fully-translated primary languages, plus a wide selectable list
covering Jharkhand's own languages and other major Indian languages:

- **Primary (fully translated):** English, Hindi
- **Jharkhand regional/tribal languages:** Nagpuri, Khortha, Panchpargania,
  Santali, Ho, Mundari, Kurukh (Oraon), Kharia
- **Other Indian languages:** Bengali, Odia, Marathi, Gujarati, Punjabi,
  Tamil, Telugu, Kannada, Malayalam, Urdu, Assamese

**How it works:** `i18n.py` defines every language with a fallback chain
(e.g. Nagpuri → Hindi → English, Tamil → English). Core navigation, buttons,
and status labels are translated for every language in the list; anything
not yet translated for a given language falls back along that chain instead
of breaking or showing a raw key. Switching language is instant (stored in
the session) and persists across the whole visit, including after logging
in.

**Being upfront about coverage:** English and Hindi are complete. The other
languages currently cover the most-used vocabulary (login, navigation,
status names, role names) rather than every sentence on every page — that's
enough to demo the feature honestly. Real deployment, especially for
Jharkhand's tribal languages (Santali, Ho, Mundari, Kurukh, Kharia), should
get full translations reviewed by native speakers before going live —
inaccurate machine-style translation of indigenous languages can do more
harm than good. Extending coverage for any language is just adding more
keys to its dictionary in `i18n.py` — no template changes needed.

## The complaint lifecycle

1. **Citizen reports a problem** — title, description, category, district,
   location, and a **required** photo or video. Their name/email/phone are
   pulled from their account automatically (no re-typing).
2. **Automatic AI screening** (simulated):
   - If category = *Roads & Infrastructure* → a simulated "recent satellite
     imagery" check runs (`ai_engine.satellite_screen`), producing a
     confidence score. High confidence → **AI Verified**. Low confidence →
     **Pending Officer Review**.
   - Any other category → skips straight to **Pending Officer Review**
     (satellite imagery isn't useful for, say, a healthcare complaint).
3. **Officer verifies** — from their queue, an officer can *Accept* (for
   AI-verified or manually-reviewed cases) or *Reject* with a reason.
   Accepting starts a **5-day resolution deadline**.
4. **Officer resolves** — uploads an "after" photo of the same site. This
   triggers `ai_engine.compare_before_after`, which really opens both images
   with Pillow and measures (a) overall pixel-level change and (b) edge-
   density change (a rough proxy for "the crack/pile/damage is gone").
   - Score above threshold → **Resolved**, case closes.
   - Score below threshold → **Reopened**, officer must try again.
   - If either photo is actually a video, automated comparison is skipped
     and the case is resolved on the officer's confirmation alone.
5. **Citizen tracks progress** any time from "My Complaints" — full status
   timeline, before/after photos side by side, and the AI's reasoning at
   each step.
6. **Admin** sees every complaint, KPIs (total / open / resolved / overdue),
   can create new officer accounts, and can manually assign or reassign a
   complaint to a specific officer (which also (re)starts their deadline).

## What's genuinely real vs. simulated

| 🟢 Real | 🟡 Simulated |
|---|---|
| File uploads (photo/video), saved to disk | Satellite imagery screening (no real satellite API wired in) |
| SQLite persistence — survives restarts | — |
| Session-based login per role | — |
| Before/after image comparison (Pillow: pixel diff + edge-density diff) | The specific 65%/10-point thresholds, tuned for demo purposes |
| Deadline tracking or overdue detection | — |
| Full status timeline / audit log per complaint | — |

## Project structure

```
jsamadhan/
├── app.py            # Routes, auth, upload handling, AI hooks
├── db.py              # sqlite3 schema + queries + row hydration
├── ai_engine.py        # Simulated satellite screen + real image diff
├── i18n.py              # Languages, translations, fallback chains
├── requirements.txt
├── templates/           # citizen / officer / admin views + shared layout
├── static/css/style.css # design system
├── static/js/main.js
└── uploads/              # uploaded photos/videos land here (auto-created)
```

## Extending it for real

Swap `ai_engine.satellite_screen()` for a real satellite-imagery / change-
detection API (e.g. Sentinel Hub, Planet, Bhuvan ISRO imagery) keyed by GPS
coordinates instead of a random seed. `compare_before_after()` already does
genuine image analysis — you could upgrade it to a trained CV model (e.g. a
crack/pothole segmentation model) for a sharper resolved/not-resolved call.
For production, move from SQLite to PostgreSQL and put uploads in cloud
object storage (S3 / GCS) instead of local disk.
