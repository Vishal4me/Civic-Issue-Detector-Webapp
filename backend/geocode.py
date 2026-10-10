"""
Reverse geocoding via OpenStreetMap's Nominatim (free, no API key).

Nominatim's usage policy requires a descriptive User-Agent and asks for at
most ~1 request/second from a single app, which is fine for a demo/project
volume. For a real deployment, read their usage policy and consider a paid
provider (Google Maps, Mapbox) for higher volume / better accuracy.
"""
import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
HEADERS = {"User-Agent": "automata-civic-issue-project/1.0 (student project)"}


def reverse_geocode(latitude: float, longitude: float, timeout: float = 5.0) -> str:
    """Return a human-readable address, or a lat/lon string if lookup fails."""
    try:
        resp = requests.get(
            NOMINATIM_URL,
            params={"lat": latitude, "lon": longitude, "format": "json", "zoom": 18},
            headers=HEADERS,
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("display_name") or f"{latitude:.5f}, {longitude:.5f}"
    except Exception:
        # Never let a geocoding hiccup block a report from being saved.
        return f"{latitude:.5f}, {longitude:.5f} (address lookup unavailable)"
