# -*- coding: utf-8 -*-
"""Measure the drive from the hotel to every place on the Things to Do page.

Uses the public OSRM demo router (OpenStreetMap data, free-flow car estimates), so times are
optimistic in winter. Writes tools/activities_distances.json, which build_activities.py reads.
Run:  python tools/compute_distances.py
"""
import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from activities_data import HOTEL, PLACES

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "activities_distances.json")


def route(dest):
    url = "http://router.project-osrm.org/route/v1/driving/%f,%f;%f,%f?overview=false" % (
        HOTEL[1], HOTEL[0], dest[1], dest[0])
    req = urllib.request.Request(url, headers={"User-Agent": "monte-hotel-site-build"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    leg = data["routes"][0]
    snap = data["waypoints"][1]["distance"]
    return leg["distance"] / 1000.0, leg["duration"] / 60.0, snap


def main():
    result = {}
    for p in PLACES:
        if "km_fixed" in p:  # starts at the hotel itself
            result[p["id"]] = {"km": p["km_fixed"], "min": 0}
            print("%-20s fixed" % p["id"])
            continue
        dest = p.get("route") or p["ll"]
        for attempt in range(3):
            try:
                km, minutes, snap = route(dest)
                break
            except Exception as exc:  # network hiccup: retry
                print("retry", p["id"], exc)
                time.sleep(2)
        else:
            raise SystemExit("could not route " + p["id"])
        result[p["id"]] = {"km": round(km, 1), "min": int(round(minutes))}
        print("%-20s %6.1f km %4d min  snap %5.0f m%s" % (p["id"], km, minutes, snap, "  <-- far from a road" if snap > 400 else ""))
        time.sleep(0.4)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1, ensure_ascii=False)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
