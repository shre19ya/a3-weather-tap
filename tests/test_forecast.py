"""Synthetic offline regression checks; not fresh-install or live evidence."""
import importlib.util
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/a3-nws-weather/scripts/forecast.py'
spec = importlib.util.spec_from_file_location('forecast', SCRIPT)
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)

class WeatherTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 12, 20, tzinfo=timezone.utc)
        self.url = 'https://api.weather.gov/gridpoints/LOX/155,45/forecast'

    def result(self, age=1, periods=None):
        payload = {'properties': {
            'updateTime': (self.now - timedelta(hours=age)).isoformat(),
            'periods': periods if periods is not None else [
                {'name': 'Synthetic daytime', 'startTime': '2026-11-12T12:00:00Z',
                 'endTime': '2026-11-13T00:00:00Z', 'detailedForecast': 'Synthetic sunny fixture.'},
                {'name': 'Expired', 'startTime': '2026-11-11T00:00:00Z',
                 'endTime': '2026-11-12T00:00:00Z', 'detailedForecast': 'Must not appear.'}]}}
        def fetch(url):
            return {'properties': {'forecast': self.url}} if '/points/' in url else payload
        return f.Weather(fetch).forecast(self.now)

    def test_current_excludes_expired(self):
        result = self.result()
        self.assertEqual(result['source'], self.url)
        self.assertEqual(result['summary'], 'Synthetic daytime: Synthetic sunny fixture.')

    def test_stale_rejected(self):
        with self.assertRaises(ValueError): self.result(age=19)

    def test_future_rejected(self):
        with self.assertRaises(ValueError): self.result(age=-1)

    def test_empty_rejected(self):
        with self.assertRaises(ValueError): self.result(periods=[])

    def test_unapproved_urls_fail_before_network(self):
        with patch.object(f.urllib.request, 'build_opener') as build:
            for url in ['http://api.weather.gov/x', 'https://example.com/x',
                        'https://api.weather.gov.evil.example/x',
                        'https://user:pass@api.weather.gov/x',
                        'https://api.weather.gov:444/x']:
                with self.subTest(url=url), self.assertRaises(ValueError): f.public_json(url)
            build.assert_not_called()

    def test_response_size_limit(self):
        with patch.object(f.urllib.request, 'build_opener') as build:
            response = build.return_value.open.return_value.__enter__.return_value
            response.read.return_value = b'x' * 2_000_001
            with self.assertRaises(ValueError): f.public_json(self.url)

    def test_redirect_handler_rejects(self):
        with patch.object(f.urllib.request, 'build_opener') as build:
            build.return_value.open.return_value.__enter__.return_value.read.return_value = b'{}'
            f.public_json(self.url)
            handlers = build.call_args.args
            handler = next(x for x in handlers if isinstance(x, f.urllib.request.HTTPRedirectHandler))
            with self.assertRaises(ValueError): handler.redirect_request(None, None, 302, '', {}, self.url)
            proxy = next(x for x in handlers if isinstance(x, f.urllib.request.ProxyHandler))
            self.assertEqual(proxy.proxies, {})

    def test_cli_failure_is_nonzero_and_redacted(self):
        import io, json
        from contextlib import redirect_stdout
        output = io.StringIO()
        with patch.object(f.Weather, 'forecast', side_effect=ValueError('private detail')):
            with redirect_stdout(output): code = f.main()
        result = json.loads(output.getvalue())
        self.assertEqual(code, 1)
        self.assertEqual(result['status'], 'unavailable')
        self.assertEqual(result['error_type'], 'ValueError')
        self.assertNotIn('private detail', output.getvalue())

if __name__ == '__main__': unittest.main()
