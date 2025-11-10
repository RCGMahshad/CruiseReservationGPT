# cruiseReservationGPT
AI-powered onboard marketplace for cruise lines

## Automated booking (Selenium)

A small helper script `selenium_booking.py` is included to run configurable browser automation steps for booking flows. It uses `selenium` and `webdriver-manager` to auto-install a Chrome driver.

Quick usage:

1. Install dependencies (preferably in a virtualenv):

```bash
python -m pip install -r requirements.txt
```

2. Create a `steps.json` describing the actions. Example `steps.json`:

```json
[
	{"action": "click", "by": "css", "selector": "#cookie-accept"},
	{"action": "click", "by": "css", "selector": ".search-cruise"},
	{"action": "fill", "by": "css", "selector": "#departure-port", "value": "Miami"},
	{"action": "fill", "by": "css", "selector": "#departure-date", "value": "2026-05-01"},
	{"action": "click", "by": "xpath", "selector": "//button[contains(., 'Search') ]"},
	{"action": "wait", "seconds": 2},
	{"action": "click", "by": "css", "selector": ".select-sail"},
	{"action": "select", "by": "css", "selector": "#cabin-type", "select_by": "visible_text", "value": "Balcony"},
	{"action": "fill", "by": "css", "selector": "#passenger-name", "value": "Jane Traveler"},
	{"action": "click", "by": "css", "selector": "#book-now"}
]
```

3. Run the script pointing at the site and steps file:

```bash
python selenium_booking.py --url "https://example-cruise-booking.example" --steps steps.json
```

Notes:
- The script is intentionally generic: provide accurate selectors for the target site.
- Start with `--no-quit` to keep the browser open and debug selectors interactively.
- Automated booking may violate site terms; make sure you have permission before running.

