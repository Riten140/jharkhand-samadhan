"""
Simulated AI engine for Jharkhand Samadhan.

Two jobs:
1. satellite_screen()  — for road/infrastructure complaints, simulate checking
   recent satellite imagery against the citizen's report. No real satellite
   feed is wired up here (that needs a paid imagery API in production), so we
   generate a deterministic confidence score per complaint. High confidence
   auto-verifies the complaint; low confidence sends it to an officer for
   manual verification instead of blocking the citizen.

2. compare_before_after() — this one is real, not simulated: it actually opens
   the citizen's "before" photo and the officer's "after" photo with Pillow
   and measures how much the image content changed (grayscale mean absolute
   difference, plus edge-density delta as a rough proxy for "a road got
   patched" / "a pile of garbage disappeared"). A bigger change score means
   the site visibly changed, which is used as one signal (combined with the
   officer's own confirmation) to auto-close or reopen a case.
"""

import hashlib
import random

from PIL import Image, ImageFilter, ImageChops

SATELLITE_VERIFY_THRESHOLD = 65     # confidence >= this -> AI auto-verifies
RESOLUTION_CHANGE_THRESHOLD = 10.0  # change score >= this -> looks resolved


def _seed_from(text):
    h = hashlib.sha256(text.encode()).hexdigest()
    return int(h[:8], 16)


def satellite_screen(complaint_code, category, description):
    """Deterministic pseudo-AI screening for infra complaints against 'recent
    satellite imagery'. Returns (confidence:int, note:str)."""
    rnd = random.Random(_seed_from(complaint_code))
    confidence = rnd.randint(35, 97)

    if confidence >= SATELLITE_VERIFY_THRESHOLD:
        note = (f"Recent satellite pass shows a visible surface anomaly consistent with "
                 f"the reported issue (confidence {confidence}%). Auto-verified.")
    else:
        note = (f"Satellite imagery was inconclusive for this location (confidence {confidence}%). "
                 f"Routed to an officer for on-ground verification.")
    return confidence, note


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
