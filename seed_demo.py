"""One-shot demo seed: downloads real topical photos (Wikimedia Commons,
picsum fallback) into uploads/ and files 6 addressed dummy complaints for
the demo citizen (citizen@example.com). Idempotent — skips if seed rows or
photo files already exist. Run: venv\\Scripts\\python.exe seed_demo.py"""
import io
import json
import os
import sqlite3
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)
import db
from PIL import Image

UA = {"User-Agent": "jharkhand-samadhan/demo-seed"}
UPLOADS = os.path.join(BASE_DIR, "uploads")

PHOTOS = {
    "pothole": ["pothole road india", "pothole road"],
    "road_fixed": ["asphalt paver road construction", "road construction site"],
    "handpump": ["handpump india", "hand pump water"],
    "street_dark": ["dark empty street night", "street at night"],
    "street_lit": ["street lamp illuminated night", "street light pole night"],
    "garbage": ["garbage pile india", "solid waste dump"],
    "pipe": ["water pipe leak repair", "burst water pipe"],
    "school": ["school toilet india", "rural school classroom india"],
}


def commons_candidates(query):
    params = urllib.parse.urlencode({
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": query + " filetype:bitmap", "gsrnamespace": 6, "gsrlimit": 6,
        "prop": "imageinfo", "iiprop": "url|size", "iiurlwidth": 800,
    })
    req = urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + params, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    out = []
    for p in ((data.get("query") or {}).get("pages") or {}).values():
        ii = (p.get("imageinfo") or [{}])[0]
        url = ii.get("thumburl") or ii.get("url")
        if url and (ii.get("width") or 0) >= 500:
            out.append(url)
    return out


def fetch_bytes(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def save_photo(name):
    dest = os.path.join(UPLOADS, "seed_%s.jpg" % name)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        print("photo %s: cached" % name)
        return "seed_%s.jpg" % name
    urls = []
    try:
        for q in PHOTOS[name]:
            try:
                urls += commons_candidates(q)
            except Exception as e:
                print("photo %s: search %r failed (%s)" % (name, q, e))
    except Exception as e:
        print("photo %s: commons failed (%s)" % (name, e))
    urls.append("https://picsum.photos/seed/jsamadhan-%s/800/600" % name)
    for url in urls:
        try:
            raw = fetch_bytes(url)
            img = Image.open(io.BytesIO(raw)).convert("RGB")
            if img.width < 400:
                continue
            img.thumbnail((1000, 1000))
            img.save(dest, "JPEG", quality=82)
            print("photo %s: ok (%s)" % (name, url[:70]))
            return "seed_%s.jpg" % name
        except Exception as e:
            print("photo %s: download %s failed (%s)" % (name, url[:70], e))
    raise RuntimeError("no usable photo for " + name)


def days_ago(n):
    return (datetime.utcnow() - timedelta(days=n)).isoformat()


def main():
    # plain connection (no flask context needed)
    conn = sqlite3.connect(db.DB_PATH)
    conn.row_factory = sqlite3.Row
    if conn.execute("SELECT 1 FROM complaints WHERE photo_filename LIKE 'seed_%' LIMIT 1").fetchone():
        print("seed complaints already present — nothing to do")
        return
    citizen = conn.execute("SELECT * FROM users WHERE email=?", ("citizen@example.com",)).fetchone()
    verma = conn.execute("SELECT * FROM users WHERE email=?", ("officer1@jsamadhan.gov",)).fetchone()
    kujur = conn.execute("SELECT * FROM users WHERE email=?", ("officer2@jsamadhan.gov",)).fetchone()
    assert citizen and verma and kujur, "demo users missing — reset the DB first"

    photos = {name: save_photo(name) for name in PHOTOS}

    items = [
        dict(title="Deep potholes on Main Road near Daily Market",
             description="Multiple deep potholes outside the Daily Market gate. Two-wheeler riders are skidding, especially after rain. Needs urgent re-carpeting.",
             category="Roads & Infrastructure", district="Ranchi",
             location_text="Main Road, near Daily Market", location_address="Main Road",
             location_city="Ranchi", pincode="834001", latitude=23.3648, longitude=85.3345,
             photo=photos["pothole"], status="Resolved", officer=verma,
             created=days_ago(18), accepted=days_ago(17), deadline=days_ago(12), resolved=days_ago(10),
             resolution=photos["road_fixed"],
             resolution_note="Potholed stretch re-carpeted with fresh bitumen; confirmed against the after photo."),
        dict(title="Handpump dry for three weeks in Bank More",
             description="The only handpump on our lane has gone completely dry. Around 40 families depend on it for drinking water.",
             category="Water Resources", district="Dhanbad",
             location_text="Lane 6, Bank More", location_address="Lane 6, Bank More",
             location_city="Dhanbad", pincode="826001", latitude=23.7957, longitude=86.4304,
             photo=photos["handpump"], status="Accepted by Officer", officer=kujur,
             created=days_ago(3), accepted=days_ago(2), deadline=(datetime.utcnow() + timedelta(days=4)).isoformat()),
        dict(title="All four streetlights dead on Sector 4 market road",
             description="The whole 200-metre stretch near the market goes pitch dark after sunset. Women and schoolchildren feel unsafe walking here.",
             category="Electricity", district="Bokaro",
             location_text="Sector 4 market road", location_address="Sector 4",
             location_city="Bokaro Steel City", pincode="827004", latitude=23.6693, longitude=86.1511,
             photo=photos["street_dark"], status="Resolved", officer=verma,
             created=days_ago(14), accepted=days_ago(13), deadline=days_ago(8), resolved=days_ago(6),
             resolution=photos["street_lit"],
             resolution_note="Faulty underground cable replaced; all four LED streetlights glowing at night."),
        dict(title="Garbage pile rotting near Matwari Road crossing",
             description="Municipal van has not come for ten days. The pile now blocks half the footpath and stray dogs scatter it every night.",
             category="Sanitation", district="Hazaribagh",
             location_text="Matwari Road crossing", location_address="Matwari Road",
             location_city="Hazaribagh", pincode="825301", latitude=23.9929, longitude=85.3617,
             photo=photos["garbage"], status="Pending Officer Review", officer=None, created=days_ago(5)),
        dict(title="Drinking water pipeline leaking day and night",
             description="Clean drinking water has been gushing from a burst joint since yesterday morning. A tanker of water is being wasted every day.",
             category="Water Resources", district="East Singhbhum",
             location_text="Boulevard Road, Sakchi", location_address="Boulevard Road, Sakchi",
             location_city="Jamshedpur", pincode="831001", latitude=22.8046, longitude=86.2029,
             photo=photos["pipe"], status="Submitted", officer=None, created=days_ago(2)),
        dict(title="Girls' toilet door broken at middle school",
             description="The only girls' toilet in the school has no door latch and no water connection. Many girls skip school during those days.",
             category="Education", district="Deoghar",
             location_text="Rajkiya Madhya Vidyalaya, Tower Chowk", location_address="Tower Chowk",
             location_city="Deoghar", pincode="814112", latitude=24.4838, longitude=86.6978,
             photo=photos["school"], status="Submitted", officer=None, created=days_ago(1)),
    ]

    for it in items:
        code = db.new_complaint_code(conn)
        fields = dict(code=code, title=it["title"], description=it["description"],
                      category=it["category"], district=it["district"],
                      location_text=it["location_text"], location_address=it["location_address"],
                      location_city=it["location_city"], pincode=it["pincode"],
                      latitude=it["latitude"], longitude=it["longitude"],
                      photo_filename=it["photo"], is_photo_video=0,
                      citizen_id=citizen["id"], status=it["status"], created_at=it["created"])
        if it.get("officer") is not None:
            fields["officer_id"] = it["officer"]["id"]
        if it.get("accepted"):
            fields["accepted_at"] = it["accepted"]
        if it.get("deadline"):
            fields["deadline"] = it["deadline"]
        if it.get("resolved"):
            fields["resolved_at"] = it["resolved"]
        if it.get("resolution"):
            fields["resolution_filename"] = it["resolution"]
        if it.get("resolution_note"):
            fields["resolution_note"] = it["resolution_note"]
        cid = db.create_complaint(conn, **fields)
        logs = [("Submitted", "Report filed by citizen.", it["created"])]
        if it.get("accepted"):
            logs.append(("Accepted by Officer",
                         "Accepted by %s." % it["officer"]["name"], it["accepted"]))
        if it.get("resolved"):
            logs.append(("Resolved", "Resolution evidence uploaded and verified.", it["resolved"]))
        for status, note, ts in logs:
            conn.execute("INSERT INTO complaint_logs (complaint_id, status, note, timestamp) VALUES (?,?,?,?)",
                         (cid, status, note, ts))
        conn.commit()
        print("seeded %s (%s)" % (code, it["status"]))
    conn.close()
    print("DONE: 6 demo complaints filed")


if __name__ == "__main__":
    main()
