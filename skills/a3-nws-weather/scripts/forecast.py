"""Standalone adaptation of assignment3.services public_json and Weather.
AI assistance: ChatGPT/Codex extracted the student project's weather code and
added this CLI. No Google, messaging, account, or assignment package dependency.
API contract: https://www.weather.gov/documentation/services-web-api
"""
import json
from datetime import datetime, timezone
from urllib.parse import urlsplit
import urllib.request

def public_json(url):
    parts = urlsplit(url)
    if (parts.scheme != 'https' or parts.hostname != 'api.weather.gov'
            or parts.port not in (None, 443) or parts.username or parts.password):
        raise ValueError('Unapproved weather source')
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            raise ValueError('Weather redirects are disabled')
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    request = urllib.request.Request(url, headers={'User-Agent': 'assignment3-synthetic-assistant',
                                                  'Accept': 'application/geo+json'})
    with opener.open(request, timeout=15) as response:
        data = response.read(2_000_001)
    if len(data) > 2_000_000:
        raise ValueError('Weather response too large')
    return json.loads(data)


class Weather:
    def __init__(self, fetch=public_json):
        self.fetch = fetch

    def forecast(self, now):
        # Fictional profile location is central Los Angeles, never a home address.
        points = self.fetch('https://api.weather.gov/points/34.0522,-118.2437')
        url = points['properties']['forecast']
        data = self.fetch(url)
        from datetime import datetime, timedelta
        updated = datetime.fromisoformat(data['properties']['updateTime'].replace('Z', '+00:00'))
        if now - updated > timedelta(hours=18) or updated - now > timedelta(minutes=10):
            raise ValueError('Forecast is stale or timestamp is invalid')
        periods = data['properties']['periods']
        selected = [p for p in periods if
                    datetime.fromisoformat(p['endTime'].replace('Z', '+00:00')) > now
                    and datetime.fromisoformat(p['startTime'].replace('Z', '+00:00')) <now + timedelta(hours=24)]
        if not selected:
            raise ValueError('No current forecast periods')
        return {'source': url, 'updated': updated.isoformat(),
                'summary': '; '.join(f"{p['name']}: {p['detailedForecast']}" for p in selected[:2])}


def main():
    now = datetime.now(timezone.utc)
    try:
        result = {"status": "verified", "checked_utc": now.isoformat(),
                  **Weather().forecast(now)}
        exit_code = 0
    except Exception as error:
        result = {"status": "unavailable", "checked_utc": now.isoformat(),
                  "error_type": type(error).__name__}
        exit_code = 1
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
