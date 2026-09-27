#!/usr/bin/env python3
"""Fetch satellite sea-surface temperature just off L Street Beach (Boston)
and write data/sst.json for the page to read.

The satellite ERDDAP servers don't send CORS headers, so the browser can't
read them directly; a daily GitHub Action runs this script instead.

Sources, tried in order (first valid pixel wins for each):
  - NOAA CoastWatch blended SST, daily, ~5 km   (noaacwBLENDEDsstDaily)
  - NASA JPL MUR SST, daily, ~1 km              (jplMURSST41)
Pixels right at the shore are often blank, so a few nearby water points are
tried from closest to farthest.
"""
import json, math, sys, urllib.request, urllib.parse
from datetime import datetime, timezone

# Points in Dorchester Bay / off Pleasure Bay, closest to L Street first.
POINTS = [(42.33, -71.02), (42.325, -71.025), (42.32, -70.99), (42.34, -71.00)]

SOURCES = [
    {"key": "blended", "name": "NOAA blended SST (~5 km)",
     "url": "https://coastwatch.noaa.gov/erddap/griddap/noaacwBLENDEDsstDaily.json",
     "var": "analysed_sst"},
    {"key": "mur", "name": "NASA MUR SST (~1 km)",
     "url": "https://coastwatch.pfeg.noaa.gov/erddap/griddap/jplMURSST41.json",
     "var": "analysed_sst"},
]

def fetch_point(src, lat, lon):
    q = f"{src['var']}[(last)][({lat})][({lon})]"
    url = f"{src['url']}?{urllib.parse.quote(q, safe='()[],')}"
    req = urllib.request.Request(url, headers={"User-Agent": "bostontides-sst/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        t = json.load(r)["table"]
    cols, units, row = t["columnNames"], t["columnUnits"], t["rows"][0]
    v = row[cols.index(src["var"])]
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return None
    u = (units[cols.index(src["var"])] or "").lower()
    temp_c = v - 273.15 if u in ("k", "kelvin", "degree_k", "degrees_k") else v
    return {"time": row[cols.index("time")], "lat": row[cols.index("latitude")],
            "lon": row[cols.index("longitude")], "tempC": round(temp_c, 2)}

def main():
    out = {"updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "note": "Satellite estimate near L Street Beach; 1-2 days old, less reliable right at the shore.",
           "sources": []}
    for src in SOURCES:
        for lat, lon in POINTS:
            try:
                p = fetch_point(src, lat, lon)
            except Exception as e:
                print(f"{src['key']} {lat},{lon}: {e}", file=sys.stderr)
                continue
            if p:
                out["sources"].append({"key": src["key"], "name": src["name"], **p})
                print(f"{src['key']}: {p}")
                break
        else:
            print(f"{src['key']}: no valid pixel", file=sys.stderr)
    if not out["sources"]:
        print("No satellite data; leaving data/sst.json unchanged.", file=sys.stderr)
        return 1
    with open("data/sst.json", "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
