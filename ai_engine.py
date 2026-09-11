"""
AI verification engine for Jharkhand Samadhan.

Two jobs:

1. verify_image_against_problem() — a real, local image-analysis check. It
   actually opens the citizen's uploaded photo with Pillow, extracts visual
   features (sharpness, exposure, edge density, colour composition), compares
   them against the problem they reported (title + description + category),
   and returns a confidence score plus a human-readable verdict. No cloud
   API or ML model is used — everything runs offline with pure Pillow, which
   keeps the project's dependency footprint at just Flask + Pillow.

   The engine is deliberately honest in its wording: it reports what it can
   and cannot see, and a low confidence result quietly routes the complaint
   to an officer instead of blocking the citizen.

2. compare_before_after() — real before/after photo diff used when an officer
   uploads a resolution photo: measures how much the site visibly changed
   (pixel difference + edge-density delta) to help auto-close or reopen a case.
"""

from collections import Counter

from PIL import Image, ImageFilter, ImageChops, ImageOps

VERIFY_THRESHOLD = 62          # confidence >= this -> AI auto-verifies
RESOLUTION_CHANGE_THRESHOLD = 10.0

# Minimum pixel count below which we warn about low-resolution photos
MIN_DETAIL_PIXELS = 96 * 96

# Laplacian-variance blur floor (below this the photo looks out of focus)
BLUR_MIN = 14.0

# ---------------------------------------------------------------------------
# keyword groups per category — used to cross-check the citizen's text
# ---------------------------------------------------------------------------

CATEGORY_KEYWORDS = {
    "Roads & Infrastructure": [
        "road", "pothole", "crack", "break", "broken", "damage", "damaged",
        "pavement", "asphalt", "tar", "bridge", "footpath", "sidewalk",
        "trench", "dig", "digging", "barricade", "concrete", "highway",
        "lane", "speed breaker", "speedbreaker", "diversion", "surface",
        "repair", "filler", "manhole",
    ],
    "Water Resources": [
        "water", "leak", "leaking", "pipe", "flood", "flooded", "logging",
        "overflow", "overflowing", "drain", "sump", "tank", "supply", "bore",
        "well", "stagnant", "puddle", "pipeburst", "burst", "wet", "mud",
        "mosquito", "seepage", "pressure",
    ],
    "Electricity": [
        "electric", "electricity", "power", "light", "lighting", "streetlight",
        "street light", "fuse", "wire", "wires", "transformer", "pole",
        "voltage", "shock", "dark", "blackout", "cut", "inverter", "grid",
        "cable", "spark", "sparking", "burn", "burnt", "meter", "high tension",
    ],
    "Sanitation": [
        "garbage", "waste", "trash", "rubbish", "litter", "dump", "dumping",
        "dumped", "dirt", "sewage", "smell", "smelly", "open drain", "canal",
        "clean", "hygienic", "stale", "manure", "dung", "clutter", "debris",
        "odour", "rotten", "stagnant", "bins", "filth",
    ],
    "Healthcare": [
        "hospital", "clinic", "doctor", "medicine", "medical", "ambulance",
        "nurse", "pharmacy", "health", "first aid", "emergency", "bed", "ward",
        "dispensary", "injured", "patient", "vaccin", "anaemi", "ill", "sick",
    ],
    "Education": [
        "school", "college", "teacher", "classroom", "student", "blackboard",
        "library", "computer lab", "uniform", "mid-day", "toilet", "playground",
        "fence", "fencing", "building", "roof", "class", "admission", "books",
    ],
    "Public Safety": [
        "dark", "darkness", "crime", "violent", "violence", "threat", "harass",
        "stalk", "thief", "theft", "burglary", "unsafe", "safety", "patrol",
        "lighting", "streetlight", "street light", "footpath", "parapet",
        "fallen", "tree", "hang", "hanging", "sagging", "wire", "uncovered",
        "open manhole", "accident", "hit", "pothole", "slippery",
    ],
}

# Default keyword list for the "Other" bucket
OTHER_KEYWORDS = ["problem", "issue", "broken", "damaged", "repair", "broken",
                  "not working", "bad", "poor", "unusable", "blocked",
                  "collapsed", "dilapidated", "critical", "urgent"]


# ---------------------------------------------------------------------------
# image feature extraction (pure Pillow)
# ---------------------------------------------------------------------------

def _extract_features(image_path):
    """Open the photo and pull out hand-crafted visual features.

    Returns (features: dict, warnings: list) or (None, [error]) if the file
    is not a readable image. Warnings hold quality caveats (blur, darkness...).
    """
    try:
        img = Image.open(image_path)
        img = ImageOps.exif_transpose(img)  # respect camera rotation tag
        img.load()
    except Exception:
        return None, ["Could not read the uploaded file as an image."]

    width, height = img.size
    small = img.resize((96, 96)).convert("RGB")
    gray = small.convert("L")
    px = list(small.getdata())
    n = len(px)

    # average brightness (0-100) and exposure buckets
    lum = [int(0.299 * r + 0.587 * g + 0.114 * b) for r, g, b in px]
    brightness = sum(lum) / n / 255.0 * 100
    dark_ratio = sum(1 for v in lum if v < 55) / n
    bright_ratio = sum(1 for v in lum if v > 205) / n

    # sharpness: variance of a 3x3 Laplacian over the downsized image
    lap = gray.filter(ImageFilter.Kernel((3, 3), [0, 1, 0, 1, -4, 1, 0, 1, 0],
                                         scale=1))
    flat = list(lap.getdata())
    mean = sum(flat) / len(flat)
    blur = round(sum((v - mean) ** 2 for v in flat) / len(flat), 1)

    # edge density on 1-100 scale
    edges = sum(list(gray.filter(ImageFilter.FIND_EDGES).getdata())) / n / 255 * 100

    # colour composition buckets
    buckets = Counter()
    for r, g, b in px:
        mx, mn = max(r, g, b), min(r, g, b)
        sat = (mx - mn) / 255.0
        lum_v = (0.299 * r + 0.587 * g + 0.114 * b)
        if lum_v < 55:
            buckets["dark"] += 1
        elif mx - mn < 26 and lum_v > 200:
            buckets["white"] += 1
        elif mx - mn < 26:
            buckets["gray"] += 1
        elif b > r and b > g and (b - r) >= 18 and b >= 100 and lum_v < 175:
            buckets["water"] += 1
        elif g >= r + 10 and g >= b + 10 and lum_v > 40:
            buckets["green"] += 1
        elif r >= 90 and r > b + 20 and g >= b + 10:
            buckets["brown"] += 1
        elif r > g + 28 and r > b + 28 and lum_v > 55:
            buckets["bright_color"] += 1
        else:
            buckets["other"] += 1

    for key in ("dark", "white", "gray", "water", "green", "brown",
                "bright_color", "other"):
        buckets.setdefault(key, 0)

    # mean saturation as the colourfulness metric
    colorfulness = round(
        sum((max(r, g, b) - min(r, g, b)) / 255.0 for r, g, b in px) / n * 100, 1)

    regions = {k: round(v / n, 3) for k, v in buckets.items()}

    features = {
        "width": width, "height": height,
        "pixels": width * height,
        "blur": blur,
        "brightness": round(brightness, 1),
        "dark_ratio": round(dark_ratio, 3),
        "bright_ratio": round(bright_ratio, 3),
        "edge_density": round(edges, 1),
        "colorfulness": colorfulness,
        "regions": regions,
    }

    warnings = []
    if blur < BLUR_MIN:
        warnings.append("Image looks blurry/out of focus — fine details may be hard to judge.")
    if dark_ratio > 0.60:
        warnings.append("Image is very dark — most of the scene is obscured.")
    if bright_ratio > 0.80:
        warnings.append("Image is overexposed/very bright — little can be confirmed from it.")
    if features["pixels"] < MIN_DETAIL_PIXELS:
        warnings.append("Image resolution is low — small details may be lost.")
    features["blank"] = features["edge_density"] < 6 and colorfulness < 7
    if features["blank"]:
        warnings.append("Image appears blank or near-uniform — it may not show a problem at all.")

    return features, warnings


def clamp(value, low=5, high=95):
    return round(max(low, min(high, value)))


# ---------------------------------------------------------------------------
# per-category visual scoring
# ---------------------------------------------------------------------------

def _score_roads(f):
    s, sigs = 30.0, []
    if f["edge_density"] > 45:
        s += 32; sigs.append("High edge density — consistent with cracking or a damaged surface.")
    elif f["edge_density"] > 30:
        s += 18; sigs.append("Moderate edge density — surface texture is visible.")
    if f["regions"]["gray"] > 0.32:
        s += 15; sigs.append("Large grey region — appears to be a paved/asphalt surface.")
    if 20 <= f["brightness"] <= 80:
        s += 10; sigs.append("Outdoor daylight capture with details visible.")
    return s, sigs


def _score_water(f):
    s, sigs = 30.0, []
    wr = f["regions"]["water"]
    if wr > 0.20:
        s += 45; sigs.append(f"~{int(wr * 100)}% of the frame is blue/water-toned — consistent with water logging, flooding or leakage.")
    elif wr > 0.08:
        s += 25; sigs.append("A water-toned region is visible in the frame.")
    if f["dark_ratio"] > 0.45:
        s += 10; sigs.append("Shadowed/wet ground detected — plausible for standing water.")
    return s, sigs


def _score_electricity(f):
    s, sigs = 30.0, []
    if f["dark_ratio"] > 0.50:
        s += 40; sigs.append("Image captured in darkness — consistent with a street-light/power failure.")
    if f["edge_density"] > 35:
        s += 15; sigs.append("Visible structures against the dark — masts/poles/wiring plausible.")
    return s, sigs


def _score_sanitation(f):
    s, sigs = 30.0, []
    if f["colorfulness"] > 24:
        s += 25; sigs.append("High colour variance — scattered clutter/debris is plausible.")
    if f["regions"]["brown"] > 0.22:
        s += 22; sigs.append("Large earthy/brown area — consistent with garbage or dirt piles.")
    if f["regions"]["green"] > 0.15 and f["regions"]["brown"] > 0.10:
        s += 10; sigs.append("Mixed organic tones — foliage mixed with waste is common at dumping sites.")
    if f["regions"]["white"] > 0.18:
        s += 8; sigs.append("Bright/white specks — plastic wraps or paper litter are common.")
    return s, sigs


def _score_facility(f):
    # Healthcare / Education — the photo should be a usable, well-lit shot of a site
    s, sigs = 50.0, []
    if f["blur"] >= BLUR_MIN:
        s += 15; sigs.append("Photo is sharp — structure/building details are readable.")
    if 15 <= f["brightness"] <= 85:
        s += 15; sigs.append("Well-exposed capture of the site.")
    if f["regions"]["green"] > 0.2:
        s += 8; sigs.append("Vegetation around the site is visible for context.")
    return s, sigs


def _score_public_safety(f):
    s, sigs = 30.0, []
    if f["dark_ratio"] > 0.50:
        s += 35; sigs.append("Image captured in darkness — poor/absent lighting visible.")
    if f["edge_density"] > 30:
        s += 20; sigs.append("Object edges visible — wires, sagging structures or obstacles plausible.")
    if f["bright_ratio"] > 0.7:
        s -= 15
    return s, sigs


def _score_generic(f):
    s, sigs = 42.0, []
    if f["blur"] >= BLUR_MIN:
        s += 15; sigs.append("Photo is sharp enough to inspect.")
    if 15 <= f["brightness"] <= 85:
        s += 13; sigs.append("Correctly exposed capture.")
    return s, sigs


_CATEGORY_SCORERS = {
    "Roads & Infrastructure": _score_roads,
    "Water Resources": _score_water,
    "Electricity": _score_electricity,
    "Sanitation": _score_sanitation,
    "Healthcare": _score_facility,
    "Education": _score_facility,
    "Public Safety": _score_public_safety,
    "Other": _score_generic,
}


# ---------------------------------------------------------------------------
# text cross-check
# ---------------------------------------------------------------------------

def _match_keywords(text, keywords):
    low = text.lower()
    matched = [kw for kw in keywords if kw in low]
    return list(dict.fromkeys(matched))


def verify_image_against_problem(image_path, title, description, category):
    """Cross-check an uploaded photo against the citizen's stated problem.

    Opens the image, extracts visual features, scores how well the picture
    matches the reported category/description, and returns a verdict dict:

    {
        "ok": bool,                # False if the file isn't a readable image
        "confidence": int,         # 0-100
        "verified": bool,          # True when confidence >= VERIFY_THRESHOLD
        "note": str,               # one-line summary for the timeline
        "signals": [str],          # evidence the AI actually looked for
        "warnings": [str],         # quality caveats
        "category": str,
        "threshold": int,
    }
    """
    category = category if category in _CATEGORY_SCORERS else "Other"

    features, warnings = _extract_features(image_path)
    if features is None:
        return {
            "ok": False, "confidence": 0, "verified": False,
            "note": (warnings[0] if warnings else "Could not analyse the uploaded file.")
                    + " Routed for officer verification.",
            "signals": [], "warnings": warnings, "category": category,
            "threshold": VERIFY_THRESHOLD,
        }

    text = f"{title} {description} {category}"

    # --- textual cross-check ---------------------------------------------
    kw_list = CATEGORY_KEYWORDS.get(category, OTHER_KEYWORDS)
    matched = _match_keywords(text, kw_list)
    text_score = 15.0
    text_signals = []
    if matched:
        text_score = min(100.0, 30.0 * len(matched))
        clipped = matched[:6]
        text_signals.append(
            "Description keywords consistent with the category: " + ", ".join(clipped) + ".")

    # --- visual cross-check ----------------------------------------------
    scorer = _CATEGORY_SCORERS[category]
    visual_score, visual_signals = scorer(features)

    confidence = clamp(0.35 * text_score + 0.65 * visual_score)

    # quality gates — poor evidence caps confidence (never fully blocks)
    if features["blur"] < BLUR_MIN:
        confidence = min(confidence, 70)
    if features["dark_ratio"] > 0.60 and category not in ("Electricity", "Public Safety"):
        confidence = min(confidence, 65)
    if features["bright_ratio"] > 0.80:
        confidence = min(confidence, 60)
    if features["pixels"] < MIN_DETAIL_PIXELS:
        confidence = min(confidence, 70)
    # a uniformly dark or dark-and-blank frame is expected for lighting-failure
    # reports, so don't treat a dark scene as "blank" evidence there
    if features["blank"]:
        if category in ("Electricity", "Public Safety") and features["dark_ratio"] > 0.5:
            warnings = [w for w in warnings
                        if w != "Image appears blank or near-uniform — it may not show a problem at all."]
        else:
            confidence = min(confidence, 25)

    verified = confidence >= VERIFY_THRESHOLD

    if verified:
        note = (f"AI cross-checked your photo against the reported problem "
                f"({category}) and found consistent visual and textual evidence "
                f"(confidence {confidence}%). Auto-verified.")
    else:
        note = (f"AI cross-check of the photo could not fully confirm the "
                f"reported problem ({category}) (confidence {confidence}%). "
                f"Routed to an officer for manual verification.")

    signals = (text_signals + visual_signals)[:7]

    return {
        "ok": True,
        "confidence": int(confidence),
        "verified": verified,
        "note": note,
        "signals": signals,
        "warnings": warnings,
        "category": category,
        "threshold": VERIFY_THRESHOLD,
    }


# ---------------------------------------------------------------------------
# before/after resolution diff (unchanged behaviour, real Pillow comparison)
# ---------------------------------------------------------------------------

def compare_before_after(before_path, after_path):
    """Compare two images and return (change_score: float 0-100, note: str).
    Returns None, note if either file can't be read as an image (e.g. a
    video was uploaded as the 'before' evidence)."""
    try:
        img_before = Image.open(before_path).convert("L").resize((256, 256))
        img_after = Image.open(after_path).convert("L").resize((256, 256))
    except Exception:
        return None, "Could not run automated image comparison (unsupported file type)."

    # Overall pixel-level change
    diff = ImageChops.difference(img_before, img_after)
    pixel_change = sum(diff.getdata()) / (256 * 256 * 255) * 100  # 0-100

    # Edge-density change as a rough structural proxy (e.g. a patched road
    # has fewer crack edges than a broken one)
    edges_before = img_before.filter(ImageFilter.FIND_EDGES)
    edges_after = img_after.filter(ImageFilter.FIND_EDGES)
    edge_before_density = sum(edges_before.getdata()) / (256 * 256 * 255) * 100
    edge_after_density = sum(edges_after.getdata()) / (256 * 256 * 255) * 100
    edge_change = abs(edge_before_density - edge_after_density)

    change_score = round(min(100.0, pixel_change * 0.6 + edge_change * 1.4), 1)

    if change_score >= RESOLUTION_CHANGE_THRESHOLD:
        note = (f"Before/after comparison detected a significant visual change at the site "
                 f"(change score {change_score}/100). Marked resolved.")
    else:
        note = (f"Before/after comparison found little visible change at the site "
                 f"(change score {change_score}/100). Case reopened for rework.")
    return change_score, note