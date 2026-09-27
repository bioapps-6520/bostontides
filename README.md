# Boston Irish Dippers — Tide Height (NOAA)

A lightweight, mobile-friendly tide + conditions viewer for Boston.

- Pick a date (Boston local time)
- View the **full-day tide curve** (NOAA predictions)
- Drag/scrub on the plot to read tide height at any time
- See the **moon**: a strip above the sun strip showing when the moon is up, with moonrise/moonset times and phase emoji, and a Moon line with phase, % lit, rise/set and a spring/neap tide hint (spring tides around new and full moon, neap around the quarters). Calculated in the page (main lunar terms; within about 3 minutes of USNO)
- See **sunrise and sunset**: a day/night strip above the tide curve (night, twilight, daylight with 🌅/🌇 times), faint shading of dark hours on the curve, and a Sun line with sunrise, sunset, daylight length and first/last light. Calculated in the page for Boston (standard solar formulas; within 1–2 minutes of the US Naval Observatory), no extra data source
- See an **hourly table** from 05:00 to 22:00 with:
  - time
  - **% of day max high** (relative to the highest high tide event that day)
  - height in **feet** and **meters**
- See **high/low tide event times**
- See a **water temperature trend** chart (1 week, 2 weeks, 5 weeks, 3 months, 1 year): satellite at L Street (NASA MUR and NOAA blended), buoys 44013 and A01, and Portland ME as daily averages, with a table of latest value, change over the range and low–high (tap a row to hide or show a line); club thermometer readings appear as dots once the Google Form is set up
- See a **tide calendar heatmap** (days × hours, 05:00–22:00, 2 weeks by default or 5 weeks) with Sunday 10:00 meets outlined and a "now" marker; color by **% of day max high** (default; each day's highest high tide = 100%) or by **height**, and the tooltip shows both, plus a **Sunday 10:00 meets** table for the next 8 Sundays (tide at 10:00, rising/falling, % of day max high, high/low times). Tap a day in either to open it in the main plot.
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
**Castle Island `8444069` (NOAA PORTS, CO-OPS)**, 1.8 km from L Street: latest `air_temperature` (`units=english`, °F) and `wind` (`units=metric`, m/s, shown in mph with direction and gusts). When it is 50°F or colder with wind over 3 mph, the line adds **feels like** (NWS wind chill from the measured air temperature and wind); the NWS forecast line does the same from forecast values.

**Gallops Island tide gauge `SLL-2699` (Stone Living Lab, via NERACOOS ERDDAP):** `water_temperature` (°F). The sensor went in August 2026 but has not reported water temperature yet, so this line only appears once there is a reading from the last 24 hours.

**Portland, ME `8418150` (CO-OPS)** `water_temperature`, `date=latest`. In winter, Portland has tracked Boston beach temperatures more closely than the offshore buoy, which can read 5°F or more warmer.

**Satellite water temp at L Street (trial):** a daily GitHub Action (`.github/workflows/satellite-sst.yml`) runs `scripts/fetch_sst.py`, which reads satellite sea-surface temperature for the water just off L Street and commits it to `data/sst.json`. The satellite ERDDAP servers don't allow browser (CORS) access, so the page reads that file from the site instead. It uses NOAA CoastWatch blended SST (`noaacwBLENDEDsstDaily`, ~5 km, preferred) and NASA JPL MUR SST (`jplMURSST41`, ~1 km). It's an estimate, 1–2 days old, and less reliable right at the shoreline, so compare it with your thermometer over the winter. The line is hidden if the reading is more than 5 days old. The job also reads the satellite at Dorchester Bay (Tenean / Malibu), Quincy Bay (Wollaston) and at buoy 44013 itself. Satellite minus buoy at the same spot shows how far off the satellite runs; the page shows the 14-day average. NOAA blended pixels are ~5 km, so Dorchester Bay usually falls in the same pixel as L Street and is marked that way. The file also keeps a 14-day daily history (both satellites plus buoy 44013's daily average), shown in the **Satellite water temp at L Street** table at the bottom of the page with a "blended − buoy" column for the winter comparison. To refresh on demand, go to **Actions → Satellite water temp (L Street) → Run workflow**.

**Danvers River at Beverly Pier `USGS-423223070531001` (USGS Water Data API):** water temperature from a shallow tidal estuary about 26 km north of L Street, via `https://api.waterdata.usgs.gov/ogcapi/v0/collections/latest-continuous/items?monitoring_location_id=USGS-423223070531001&parameter_code=00010` (CORS-friendly). It's shown only if the reading is under 24 hours old. Shallow near-shore water may track winter beach temperatures better than the offshore buoy. The other USGS temperature sensors nearby are Cambridge's drinking-water reservoirs and streams (Fresh Pond, Stony Brook, Hobbs Brook), which aren't swimming water. The Charles, Mystic and Neponset have no live USGS temperature sensors.

**Water temperature sensors table (bottom of the page):** only sensors that measure the water directly, nearest to L Street first, with type, distance, latest °F/°C and time (hidden if older than 24 h): Gallops Island gauge (Stone Living Lab, not reporting yet), Fresh Pond buoy (USGS, freshwater reservoir), Danvers River at Beverly Pier (USGS, estuary), buoy 44013, buoy A01 (NERACOOS `A01_ocean_001m`, 1 m), buoy 44090 (Cape Cod Bay), and Portland ME (CO-OPS). All are read directly by the browser (NERACOOS ERDDAP, USGS Water Data API, CO-OPS).

**Water temperature history (`data/water_history.json`):** the same daily Action runs `scripts/fetch_history.py`, which collects daily averages in °C for the trend chart: NASA MUR and NOAA blended at L Street (NOAA fetched in 30-day chunks, since longer requests time out), buoy 44013 and A01 (NERACOOS ERDDAP, `orderByMean("time/1day")`), and Portland ME (CO-OPS via the IOOS sensors ERDDAP). Each run fetches the last 365 days and merges them into the file, so history keeps growing (capped at about 3 years). The job commits only when a reading changes, not just the timestamp.

Note: the Boston tide station `8443970` has no water temperature sensor.

The **Coastal Water Temperature** table and map at the bottom list the satellite estimate at L Street (from `data/sst.json`, below), buoy `44013` (same ERDDAP feed as below) alongside the CO-OPS stations (Portland, Bar Harbor, Woods Hole, Nantucket).

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
- `scripts/fetch_sst.py`, `scripts/fetch_history.py`, `.github/workflows/satellite-sst.yml`, `data/sst.json`, `data/water_history.json` — daily satellite and water temperature history fetch, and their output
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

## Shore thermometer log (Google Form)

Club members log water temperatures measured at the beach. The latest reading from the last 7 days is shown first in Conditions, and the last 10 are listed in the **Shore thermometer log** section. The section stays hidden until it's set up.

**Setup (one time):**
1. Create a Google Form with these questions:
   - **Water temperature (°F)**: short answer, required. Under ⋮ → Response validation, choose Number, between 28 and 90.
   - **Beach**: dropdown, required. For example: L Street, M Street, City Point, Pleasure Bay / Castle Island, Carson, Tenean, Malibu, Savin Hill, Wollaston, Other.
   - **Your name (optional)**: short answer. First name or initials are enough; it will be visible on the page.
   - **Notes (optional)**: short answer.
2. In the form, go to **Responses → Link to Sheets** to create the responses sheet.
3. In the sheet, choose **File → Share → Publish to web**, pick the responses tab, choose **Comma-separated values (.csv)**, then click **Publish**. Copy the link.
4. In `index.html`, set `THERMO_FORM_URL` to the form's share link and `THERMO_CSV_URL` to the published CSV link.

Columns are matched by the question wording ("temp", "beach", "name", "note"), so small wording changes are fine. Readings outside 25–95°F are ignored as typos. The published CSV can be opened by anyone who has its link, so don't collect anything private.

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
