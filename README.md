# Boston Irish Dippers — Tide Height (NOAA)

A lightweight, mobile-friendly tide + conditions viewer for Boston.

- Pick a date (Boston local time)
- View the **full-day tide curve** (NOAA predictions)
- Drag/scrub on the plot to read tide height at any time
- See a **15-minute table** from 05:00 to 22:00 with:
  - time
  - **% of day max high** (relative to the highest high tide event that day)
  - height in **feet** and **meters**
- See **high/low tide event times**
- See latest **water temperature (Boston tide station, with offshore buoy for context)**, air temperature, and wind
- See **NWS forecast** for the selected date (only when within the next ~7 days)

Hosted via **GitHub Pages** (static HTML/JS, no backend).

---

## Live site

Enable GitHub Pages in repo settings (see setup below).  
Once enabled, your site will be available at:

`https://bioapps-6520.github.io/bostontides/`

---

## Data sources (NOAA / NWS)

This app pulls **public data** from the following official sources:

### 1) Tide predictions (NOAA CO-OPS / Tides & Currents)
**Station:** `8443970` — Boston, MA  
**Datum:** `MLLW`  
**Timezone:** local (Boston) via `time_zone=lst_ldt`  
**Units:** English (feet) via `units=english`

**A) Tide curve (every 6 minutes)**
- Endpoint: NOAA CO-OPS Datagetter
- Product: `predictions`
- Interval: `6` minutes

Used to draw the curve and compute tide height at the scrubbed time.

**B) High/low tide events**
- Endpoint: NOAA CO-OPS Datagetter
- Product: `predictions`
- Interval: `hilo`

Used to display the day’s High/Low tide times and to find the **highest high tide of the day** (used as 100% for the table).

> API base:
`https://api.tidesandcurrents.noaa.gov/api/prod/datagetter`

Example parameters used:
- `product=predictions`
- `station=8443970`
- `datum=MLLW`
- `time_zone=lst_ldt`
- `units=english`
- `format=json`
- `begin_date=YYYYMMDD 00:00`
- `end_date=YYYYMMDD 23:59`
- `interval=6` or `interval=hilo`

---

### 2) Coastal water temp (NOAA CO-OPS)
**Station:** `8443970` — Boston, MA (same station as the tides)  
Product `water_temperature`, `date=latest`. If Boston has no recent reading, the app falls back to `8418150` (Portland, ME) and labels the line accordingly.

---

### 3) Offshore water temp / wind / air temp (NDBC buoy via ERDDAP)
**Buoy:** `44013` (offshore; may differ from beach temperature)

Directly fetching `https://www.ndbc.noaa.gov/data/realtime2/44013.txt` is blocked by browser CORS on GitHub Pages.  
So this app uses a CORS-friendly **ERDDAP JSON** endpoint that includes:

- `WTMP` = water temp (°C)
- `ATMP` = air temp (°C)
- `WSPD` = wind speed (m/s)
- `WDIR` = wind direction (degrees)

**Endpoint used (latest row):**
`https://data.neracoos.org/erddap/tabledap/NDBC_44013.json?time,WTMP,ATMP,WSPD,WDIR&orderByMax("time")`

Displayed as:
- Water (offshore buoy, context only): °F and °C
- Air: °F and °C
- Wind: mph + direction

---

### 4) Weather forecast (NWS / weather.gov)
Uses the National Weather Service API for Boston coordinates.

**Point endpoint:**
`https://api.weather.gov/points/42.3601,-71.0589`

From that, the app reads:
- `forecast` (7-day daily periods)
- `forecastHourly` (hourly forecast; used for “next 12h” when the selected date is today)

Forecast is shown only when the selected date is within the next ~7 days.  
If not available, the app displays `—`.

---

## Files in this repo

- `index.html` — the full app (HTML + CSS + JavaScript)
- `seahorse.png` — logo used in the page header and as the favicon
- `README.md` — this file
- `LICENSE` — MIT License

No build step. No backend. Just static hosting.

---

## Setup (GitHub Pages)

1. Put these files in the repo root:
   - `index.html`
   - `seahorse.png`
   - `README.md`
   - `LICENSE`

2. Commit + push.

3. Enable Pages:
   - Repo → **Settings** → **Pages**
   - Source: **Deploy from a branch**
   - Branch: **main**
   - Folder: **/(root)**
   - Save

4. Wait a minute, then open your Pages URL.

---

## Troubleshooting

### The page updates on GitHub but I still see the old version
- Hard refresh:
  - Windows/Linux: `Ctrl + Shift + R`
  - Mac: `Cmd + Shift + R`
- Or open in a Private/Incognito window.
- GitHub Pages and your browser can cache files briefly.

### Water temperature shows `—`
Most common causes:
1) **Network blocked / offline**  
2) **ERDDAP temporary outage**  
3) A browser extension blocking requests

How to debug:
- Open browser DevTools Console:
  - Firefox: `Ctrl + Shift + K` (Console)
  - Chrome: `Ctrl + Shift + J`
- Reload and look for red errors mentioning `data.neracoos.org`.

Why we don’t fetch `ndbc.noaa.gov/...44013.txt` directly:
- Browsers block it due to **CORS** (no `Access-Control-Allow-Origin`), so GitHub Pages cannot read it from JS.

### Forecast shows `—` even though weather exists
Expected in these cases:
- Selected date is **more than ~7 days ahead**
- Selected date is **in the past**
- NWS API temporarily unavailable or rate-limited

Debug:
- Check Console for `api.weather.gov` errors.
- Try selecting **today** to confirm NWS is reachable.

### Tide curve is blank or table is empty
Usually means NOAA CO-OPS returned no data or the request failed.

Debug:
- Console errors mentioning `api.tidesandcurrents.noaa.gov`
- Try another date (today / tomorrow)
- Confirm station `8443970` is correct (Boston)

### Mobile scrolling/zoom feels weird
This app disables Plotly zoom and uses a transparent overlay to implement “scrub” behavior.
If it feels jumpy, try:
- A slower finger drag (scrub updates are frame-limited)
- Reload the page
- Ensure iOS “Reader” mode is off

---

## License

MIT License — see `LICENSE`.
