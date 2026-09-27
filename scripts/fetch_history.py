#!/usr/bin/env python3
"""Build data/water_history.json: daily water temperature (°C) per source for
the page's "Water temperature trend" chart.

Runs in the same daily GitHub Action as fetch_sst.py. Each run fetches the last
FETCH_DAYS days and merges them into the existing file, so the history grows
beyond a year over time (capped at KEEP_DAYS).

Sources (all daily means, °C):
  - Satellite at L Street: NASA JPL MUR (~1 km) and NOAA blended (~5 km)
  - Buoy 44013 (NDBC via NERACOOS ERDDAP), buoy A01 1 m (NERACOOS)
  - Portland, ME 8418150 (NOAA CO-OPS via the IOOS sensors ERDDAP)
"""
import json, math, os, sys, urllib.request, urllib.parse
from datetime import datetime, timezone

FETCH_DAYS = 365
KEEP_DAYS = 3 * 366
OUT = "data/water_history.json"

LST_MUR = (42.33, -71.02)        # same pixels as fetch_sst.py "lst"
LST_BLENDED = (42.325, -71.025)

SERIES = [
    {"key": "sat_mur_lst",     "name": "Satellite at L St (NASA MUR)",     "kind": "satellite"},
    {"key": "sat_blended_lst", "name": "Satellite at L St (NOAA blended)", "kind": "satellite"},
    {"key": "buoy44013",       "name": "Buoy 44013 (offshore)",            "kind": "sensor"},
    {"key": "a01",             "name": "Buoy A01 (Mass Bay, 1 m)",         "kind": "sensor"},
    {"key": "portland",        "name": "Portland, ME (coastal)",           "kind": "sensor"},
]

def get_json(url, timeout=180):
    req = urllib.request.Request(url, headers={"User-Agent": "bostontides-history/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)

def is_num(v):
    return v is not None and not (isinstance(v, float) and math.isnan(v))

def to_c(v, unit):
    return v - 273.15 if (unit or "").lower() in ("k", "kelvin", "degree_k", "degrees_k") else v

def griddap_daily(base, var, lat, lon, index_sel):
    q = f"{var}[{index_sel}][({lat})][({lon})]"
    t = get_json(f"{base}.json?{urllib.parse.quote(q, safe='()[],:')}")["table"]
    cols, units = t["columnNames"], t["columnUnits"]
    iv = cols.index(var)
    return {row[cols.index("time")][:10]: round(to_c(row[iv], units[iv]), 2)
            for row in t["rows"] if is_num(row[iv])}

def griddap_daily_chunked(base, var, lat, lon, days, chunk=30):
    """Some servers time out on long series; ask for `chunk` days at a time."""
    out = {}
    for start in range(0, days, chunk):
        hi, lo = start, min(start + chunk, days) - 1
        sel = f"last-{lo}:1:last" if hi == 0 else f"last-{lo}:1:last-{hi}"
        try:
            out.update(griddap_daily(base, var, lat, lon, sel))
        except Exception as e:
            print(f"  chunk {sel}: {e}", file=sys.stderr)
    return out

def tabledap_daily_mean(base, var, days):
    q = f"time,{var}&time>=now-{days}days&{var}!=NaN&orderByMean(\"time/1day\")"
    t = get_json(f"{base}.json?{urllib.parse.quote(q, safe='=,&-!/')}")["table"]
    cols = t["columnNames"]
    iv, it = cols.index(var), cols.index("time")
    return {row[it][:10]: round(row[iv], 2) for row in t["rows"] if is_num(row[iv])}

FETCHERS = {
    "sat_mur_lst": lambda: griddap_daily(
        "https://coastwatch.pfeg.noaa.gov/erddap/griddap/jplMURSST41", "analysed_sst",
        *LST_MUR, f"last-{FETCH_DAYS - 1}:1:last"),
    "sat_blended_lst": lambda: griddap_daily_chunked(
        "https://coastwatch.noaa.gov/erddap/griddap/noaacwBLENDEDsstDaily", "analysed_sst",
        *LST_BLENDED, FETCH_DAYS),
    "buoy44013": lambda: tabledap_daily_mean(
        "https://data.neracoos.org/erddap/tabledap/NDBC_44013", "WTMP", FETCH_DAYS),
    "a01": lambda: tabledap_daily_mean(
        "https://data.neracoos.org/erddap/tabledap/A01_ocean_001m", "temperature", FETCH_DAYS),
    "portland": lambda: tabledap_daily_mean(
        "https://erddap.sensors.ioos.us/erddap/tabledap/noaa_nos_co_ops_8418150",
        "sea_water_temperature", FETCH_DAYS),
}

def main():
    old = {}
    if os.path.exists(OUT):
        try:
            for s in json.load(open(OUT)).get("series", []):
                old[s["key"]] = dict(s.get("data", []))
        except Exception as e:
            print(f"ignoring unreadable {OUT}: {e}", file=sys.stderr)

    series_out, got_any = [], False
    for s in SERIES:
        data = dict(old.get(s["key"], {}))
        try:
            new = FETCHERS[s["key"]]()
            data.update(new)
            got_any = got_any or bool(new)
            print(f"{s['key']}: {len(new)} new days, {len(data)} total")
        except Exception as e:
            print(f"{s['key']}: fetch failed ({e}); keeping {len(data)} old days", file=sys.stderr)
        days = sorted(data)[-KEEP_DAYS:]
        series_out.append({**s, "unit": "C", "data": [[d, data[d]] for d in days]})

    if not got_any:
        print("No new data from any source; leaving the file unchanged.", file=sys.stderr)
        return 1
    with open(OUT, "w") as f:
        json.dump({"updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "series": series_out}, f, separators=(",", ":"))
        f.write("\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
