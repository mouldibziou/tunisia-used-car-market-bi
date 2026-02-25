# Data Collection

This folder contains all web scrapers used to build the project's raw datasets. Data was sourced from **three independent platforms** covering both the current Tunisian used car market (2025) and historical records dating back to 2007.

---

## Sources Overview

| Source | Platform | Period | Records | Notebook(s) |
|---|---|---|---|---|
| **automobile.tn** | Live marketplace | 2025 | ~2,000 | `large_scraper.ipynb`, `small_scraper.ipynb` |
| **tayara.tn** | Live marketplace | 2025 | ~3,000 | `tayara_tn_all_ads_scraped.ipynb`, `tayara_cars_data.ipynb` |
| **tunisie-annonce.com** | Wayback Machine archive | 2007–2024 | ~4,500 | `wayback/api_links.ipynb` |

---

## `automobile.tn/`

### `large_scraper.ipynb` — Link Harvester

Crawls all paginated listing pages on automobile.tn and collects individual ad URLs.

**Techniques used:**
- **Pagination detection**: dynamically reads the last page number from the site's `<ul class="pagination">` element, so the scraper auto-adjusts when new pages are added
- **MD5 content hashing** (`hashlib`): each ad's title, price, km, and year are hashed before storing; duplicate hashes are rejected in real time and persisted to `seen_ads.txt` across sessions
- **BeautifulSoup (lxml parser)**: targets `div.occasion-item-v2` containers to extract ad metadata
- **Polite crawling**: random `time.sleep(uniform(1, 3))` between page requests to avoid rate-limiting
- **Error handling**: `requests.exceptions.RequestException` is caught per page; parsing failures return an empty list so the scraper continues

**Output:** `car_links.csv` — one URL per row

---

### `small_scraper.ipynb` — Detail Extractor

Visits each URL collected by the link harvester and extracts the full ad specification sheet.

**Techniques used:**
- **User-Agent spoofing**: mimics a real Chrome browser to avoid bot-blocking
- **Adaptive CSS selector fallback**: if a primary class selector fails (e.g., `div.box.d-none.d-md-block`), the scraper logs all `box`-class divs found and falls back to alternative selectors — useful when the site updates its HTML
- **Defensive index-based spec extraction**: the 15 spec fields are accessed by known list positions (`spec_fields` tuple list) with explicit bounds-checking; missing indices emit a warning instead of crashing
- **HTML debug dump**: on parser failure, the raw response is saved to `debug_page.html` for manual inspection
- **Success rate tracking**: final print reports `total_links`, `successful_scrapes`, and `success_rate` (achieved ~91%)
- **`pd.concat` row-append pattern**: each scraped row is appended without pre-allocating the DataFrame

**Fields extracted:** title, price, brand, model, mileage, circulation-date, fuel, engine-size, gear, fiscal-power, body-type, ownership, publish-date, location, description, interior

**Output:** `cleaned_automobile_tn.csv`

---

## `tayara.tn/`

### `tayara_tn_all_ads_scraped.ipynb` — Link Harvester

Equivalent of the automobile.tn link harvester, adapted for tayara.tn's React-rendered markup.

**Techniques used:**
- **MD5 hashing** with a different key schema (`title-price-location`) stored in `seen_ads_tayara.txt`
- **Relative URL resolution**: `base_url + a_tag['href']` to build absolute URLs
- **Dynamic last-page detection**: pagination parsed from the live DOM on each request

**Output:** `links_tayara_csv.csv`

---

### `tayara_cars_data.ipynb` — Detail Extractor

Scrapes the full specification page for each tayara.tn listing.

**Techniques used:**
- **French label-to-English field mapping** (`label_mapping` dict): maps scraped French spec labels (e.g., *Kilométrage*, *Puissance fiscale*) to standardised English column names, making the dataset schema-compatible with automobile.tn output
- **Class-less container discovery**: since the description and specs divs carry no CSS class, the scraper iterates all sibling divs and identifies them by their `<h2>` heading text (`Description`, `Critères`)
- **Deleted ad detection**: responses containing `"Annonce supprimée"` are skipped before parsing
- **Extended HTTP headers**: includes `Accept`, `Accept-Language`, `Accept-Encoding`, and `Upgrade-Insecure-Requests` to reduce blocking probability
- **Success/failure/deleted counters** for final reporting

---

## `wayback/`

### `api_links.ipynb` — Wayback Machine Archival Scraper

Retrieves historical car listings from **tunisie-annonce.com** via the Internet Archive's CDX API, covering 2007–2024.

**Techniques used:**
- **CDX API query**: `http://web.archive.org/cdx/search/cdx?url=...&from=YYYY&to=YYYY&filter=statuscode:200&output=json` — filters only successfully-archived pages and returns timestamps with original URLs
- **Wayback URL construction**: `https://web.archive.org/web/{timestamp}/{original_url}` — each snapshot is accessed independently
- **`AnnoncesAuto.asp` suffix injection**: normalises URL variants (trailing slash, no path) so all variants point to the car listings page
- **Table-based HTML parsing**: the site used legacy table markup; `soup.find('table', width='767')` followed by `tr.Tableau1` row extraction
- **Vertical menu removal**: `MenuVertical` table is `.decompose()`-d before parsing to avoid picking up navigation links as ads
- **Odd-index trick**: `ad_details[1::2]` skips image cells and reads only text columns
- **`onmouseover` description extraction**: ad descriptions were embedded in JavaScript hover handlers; raw text is extracted with a regex strip and decoded via `html.unescape()` + `BeautifulSoup`
- **"Wanted" ad filter**: rows containing *cherche* or *recherche* in the description are discarded (buyers advertising wanted listings, not sellers)
- **Polite crawling**: `time.sleep(random.uniform(7, 15))` — longer delays due to the Wayback Machine's rate limits
- **Configurable date range**: `start` and `end` variables set at the call site; the full run used 2007–2024

**Output:** `wayback_data.csv`

---

## Libraries Used

| Library | Purpose |
|---|---|
| `requests` | HTTP requests with timeout and error handling |
| `beautifulsoup4` / `lxml` | HTML parsing |
| `hashlib` | MD5 deduplication hashing |
| `pandas` | DataFrame construction and CSV I/O |
| `re` | Regex for text cleaning |
| `html` | HTML entity decoding for wayback descriptions |
| `json` | CDX API response parsing |
| `csv` | Low-level CSV read/write |
| `time`, `random` | Polite crawl delays |
