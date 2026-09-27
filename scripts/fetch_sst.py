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

Also writes a HISTORY_DAYS daily history (both satellites at their chosen
pixel, plus the daily mean of offshore buoy 44013) for the page's
"Satellite water temp at L Street" table.
"""
import json, math, sys, urllib.request, urllib.parse
from collections import defaultdict
from datetime import datetime, timezone

HISTORY_DAYS = 14
BUOY_URL = "https://data.neracoos.org/erddap/tabledap/NDBC_44013.json"

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

def get_table(url):
    req = urllib.request.Request(url, headers={"User-Agent": "bostontides-sst/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)["table"]

def to_c(v, unit):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return None
    u = (unit or "").lower()
    return v - 273.15 if u in ("k", "kelvin", "degree_k", "degrees_k") else v

def fetch_series(src, lat, lon, time_sel):
    """Rows of {time, lat, lon, tempC} at one pixel; time_sel e.g. '(last)'."""
    q = f"{src['var']}[{time_sel}][({lat})][({lon})]"
    t = get_table(f"{src['url']}?{urllib.parse.quote(q, safe='()[],:')}")
    cols, units = t["columnNames"], t["columnUnits"]
    iv = cols.index(src["var"])
    out = []
    for row in t["rows"]:
        c = to_c(row[iv], units[iv])
        if c is not None:
            out.append({"time": row[cols.index("time")], "lat": row[cols.index("latitude")],
                        "lon": row[cols.index("longitude")], "tempC": round(c, 2)})
    return out

def fetch_point(src, lat, lon):
    rows = fetch_series(src, lat, lon, "(last)")
    return rows[0] if rows else None

def fetch_buoy_daily_means(days):
    """Daily mean water temp (°C) of buoy 44013, keyed by UTC date."""
    q = f"time,WTMP&time>=now-{days + 1}days"
    t = get_table(f"{BUOY_URL}?{urllib.parse.quote(q, safe='=,&-')}")
    cols = t["columnNames"]
    by_day = defaultdict(list)
    for row in t["rows"]:
        v = row[cols.index("WTMP")]
        if v is not None and not (isinstance(v, float) and math.isnan(v)):
            by_day[row[cols.index("time")][:10]].append(v)
    return {d: round(sum(v) / len(v), 2) for d, v in by_day.items()}

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

    # Daily history at each source's chosen pixel, plus the buoy's daily mean.
    history = defaultdict(dict)
    for s in out["sources"]:
        src = next(x for x in SOURCES if x["key"] == s["key"])
        try:
            for r in fetch_series(src, s["lat"], s["lon"], f"last-{HISTORY_DAYS - 1}:1:last"):
                history[r["time"][:10]][s["key"]] = r["tempC"]
        except Exception as e:
            print(f"{s['key']} history: {e}", file=sys.stderr)
    try:
        buoy = fetch_buoy_daily_means(HISTORY_DAYS)
        for d in list(history):
            if d in buoy:
                history[d]["buoy"] = buoy[d]
    except Exception as e:
        print(f"buoy history: {e}", file=sys.stderr)
    out["history"] = [{"date": d, **history[d]}
                      for d in sorted(history, reverse=True)[:HISTORY_DAYS]]
    print(f"history: {len(out['history'])} days")
    with open("data/sst.json", "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
