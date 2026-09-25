# Boston Irish Dippers — Tide Height (NOAA)

A lightweight, mobile-friendly tide + conditions viewer for Boston.

- Pick a date (Boston local time)
- View the **full-day tide curve** (NOAA predictions)
- Drag/scrub on the plot to read tide height at any time
- See an **hourly table** from 05:00 to 22:00 with:
  - time
  - **% of day max high** (relative to the highest high tide event that day)
  - height in **feet** and **meters**
- See **high/low tide event times**
- See latest **wind and air temperature at Castle Island**, **water temperature** (Portland ME coastal station, Gallops Island once it reports, plus offshore buoy)
- See **NWS forecast** for the selected date (only when within the next ~7 days)
- **Beach bacteria warning**: shows rain at Logan over the last 48h and a warning at 0.5 in or more (higher bacteria risk at harbor beaches from Quincy to Castle Island), plus links to the Mass DPH beach dashboard (summer only), BWSC sewer overflow alerts, and Save the Harbor's report card

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

### 2) Local conditions and coastal water temp
**Castle Island `8444069` (NOAA PORTS, CO-OPS)**, 1.8 km from L Street: latest `air_temperature` (`units=english`, °F) and `wind` (`units=metric`, m/s, shown in mph with direction and gusts).

**Gallops Island tide gauge `SLL-2699` (Stone Living Lab, via NERACOOS ERDDAP):** `water_temperature` (°F). The sensor went in August 2026 but has not reported water temperature yet, so this line only appears once there is a reading from the last 24 hours.

**Portland, ME `8418150` (CO-OPS)** `water_temperature`, `date=latest`. In winter, Portland has tracked Boston beach temperatures more closely than the offshore buoy, which can read 5°F or more warmer.

Note: the Boston tide station `8443970` has no water temperature sensor.

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

### 4) Rain at Logan (Iowa Environmental Mesonet)
Hourly routine METAR precipitation (`p01i`, inches) for station `BOS`, summed over the last 48 hours:

`https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?station=BOS&data=p01i&report_type=3&format=onlycomma&tz=UTC&sts=...&ets=...`

This endpoint sends `Access-Control-Allow-Origin: *`, so the static page can read it. At 0.5 in or more, the Beach bacteria line turns into a warning, following Boston public health guidance to avoid harbor water for 48 hours after heavy rain.

---

### 5) Weather forecast (NWS / weather.gov)
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
- `seahorse.png` — logo used in the page header
- `manifest.webmanifest`, `icon-192.png`, `icon-512.png`, `icon-maskable-512.png`, `apple-touch-icon.png` — home-screen app setup and icons (square versions of the seahorse)
- `README.md` — this file
- `LICENSE` — MIT License

No build step. No backend. Just static hosting.

---

## Setup (GitHub Pages)

1. Put these files in the repo root:
   - `index.html`
   - `seahorse.png`
   - `manifest.webmanifest` and the `icon-*.png` / `apple-touch-icon.png` files
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

## Search engines

`index.html` has `<meta name="robots" content="noindex, nofollow">`, so Google and other search engines drop the page from results the next time they crawl it. Anyone with the link can still open it.

---

## Add to Home Screen

The page can be installed like an app, with the seahorse icon and no browser bars:
- **iPhone (Safari):** Share button → **Add to Home Screen**
- **Android (Chrome):** ⋮ menu → **Add to Home screen** / **Install app**

There is deliberately no offline service worker, so the installed app always loads the latest version and live data.

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
