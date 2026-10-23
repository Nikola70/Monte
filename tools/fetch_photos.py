# -*- coding: utf-8 -*-
"""Download the freely licensed Wikimedia Commons photos used on the Things to Do cards.

Reads the file titles below, asks the Commons API for author and licence, downloads a 1000 px
version, resizes it to about 900 px wide and writes images/Places/<id>.jpg plus
tools/activities_photos.json (author, licence and file page, used for the credits list).
Photos under CC0 or public domain need no credit; set credit=False for them.
Run from the repo root:  python tools/fetch_photos.py
"""
import io
import json
import os
import re
import time
import urllib.parse
import urllib.request

from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
UA = {"User-Agent": "monte-hotel-site-build/1.0 (contact: info@montegudauri.com)"}

# place id -> (Commons file title, optional crop box as fractions (left, top, right, bottom))
PHOTOS = {
    "ananuri": ("File:Ananuri Fortress 01.jpg", None),
    "rafting": ("File:Aragvi confluence Gruzia 2019 2.jpg", None),
    "lessons": ("File:Gudauri (9).jpg", None),
    "heliski": ("File:Gudauri (14).jpg", None),
    "paragliding": ("File:Гудаури - panoramio (19).jpg", None),
    "travertine": ("File:Jvari Overpass Travertine Gruzia 2019 2.jpg", None),
    "gudauri-lake": ("File:2024-08-04 White Rabbit Wakeboard Park in Gudauri Recreational Area.jpg", None),
    "horse": ("File:Field with Wildflowers and Horse - Road to Gergeti Trinity Church - Outside Kazbegi - Georgia (18578101811).jpg", None),
    "truso": ("File:Truso Valley views 24.jpg", None),
    "sioni": ("File:Sioni, Khevi, Bell tower, Georgia.jpg", None),
    "sno-castle": ("File:Sno Fortress.jpg", None),
    "gergeti": ("File:Gergeti Trinity Church and Mt. Kazbeg 01.jpg", None),
    "kazbek": ("File:Mount Kazbek from peak 3219 m.jpg", None),
    "gveleti": ("File:Gveleti waterfall.jpg", None),
    "juta": ("File:A view from the trail from Juta to Chaukhi Pass 2023-07-29-18.jpg", None),
}


def clean(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()


def api(params):
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))


def main():
    os.makedirs(os.path.join(ROOT, "images", "Places"), exist_ok=True)
    prev_path = os.path.join(HERE, "activities_photos.json")
    prev = json.load(open(prev_path, encoding="utf-8")) if os.path.exists(prev_path) else {}
    out = {k: v for k, v in prev.items() if v.get("own")}  # photos supplied by the hotel are kept as they are
    for pid, (title, crop) in PHOTOS.items():
        data = api({"action": "query", "format": "json", "titles": title, "prop": "imageinfo",
                    "iiprop": "url|extmetadata|size", "iiurlwidth": 1000})
        page = next(iter(data["query"]["pages"].values()))
        if "imageinfo" not in page:
            print("NOT FOUND", pid, title)
            continue
        ii = page["imageinfo"][0]
        md = ii["extmetadata"]
        lic = clean(md.get("LicenseShortName", {}).get("value"))
        raw = urllib.request.urlopen(urllib.request.Request(ii["thumburl"], headers=UA), timeout=90).read()
        im = ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
        if crop:
            w, h = im.size
            im = im.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h)))
        im.thumbnail((900, 900), Image.LANCZOS)
        path = os.path.join(ROOT, "images", "Places", pid + ".jpg")
        im.save(path, "JPEG", quality=80, optimize=True, progressive=True)
        needs_credit = not re.search(r"CC0|public domain|^PD", lic, re.I)
        out[pid] = {
            "title": title[5:], "author": clean(md.get("Artist", {}).get("value")), "license": lic,
            "license_url": clean(md.get("LicenseUrl", {}).get("value")),
            "page": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_")),
            "credit": needs_credit, "w": im.size[0], "h": im.size[1],
        }
        print("%-18s %-14s credit=%-5s %dx%d %4d KB  %s" % (pid, lic, needs_credit, im.size[0], im.size[1], os.path.getsize(path) // 1024, out[pid]["author"][:40]))
        time.sleep(0.4)
    with open(os.path.join(HERE, "activities_photos.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
