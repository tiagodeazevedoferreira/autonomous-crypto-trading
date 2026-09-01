from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass
class TradingCentralClient:
    """Read-only Trading Central API boundary.

    Endpoint paths intentionally remain explicit/configurable because access
    entitlements and API versions are provider-account dependent. No order
    execution is exposed by this client.
    """

    base_url: str
    api_token: str | None = None
    timeout: float = 15.0

    @classmethod
    def from_env(cls) -> "TradingCentralClient":
        return cls(
            base_url=os.environ.get("TRADING_CENTRAL_API_BASE_URL", "").rstrip("/"),
            api_token=os.environ.get("TRADING_CENTRAL_API_TOKEN"),
            timeout=float(os.environ.get("TRADING_CENTRAL_TIMEOUT", "15")),
        )

    def _request(self, path: str, params: dict[str, str] | None = None) -> Any:
        if not self.base_url:
            raise RuntimeError("TRADING_CENTRAL_API_BASE_URL is not configured")
        query = ""
        if params:
            from urllib.parse import urlencode

            query = "?" + urlencode({k: v for k, v in params.items() if v is not None})
        request = urllib.request.Request(self.base_url + path + query, method="GET")
        request.add_header("Accept", "application/json")
        if self.api_token:
            request.add_header("Authorization", f"Bearer {self.api_token}")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Trading Central API HTTP {exc.code}: {body[:500]}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Trading Central API connection error: {exc.reason}") from exc

    def technical_summary(self, **params: str) -> Any:
        return self._request("/technicalsummaries/v3", params)

    def support_resistance(self, **params: str) -> Any:
        return self._request("/supportandresistance/v3", params)

    def instrument_events(self, instrument_id: str, **params: str) -> Any:
        return self._request(f"/instrumentevents/v3/{instrument_id}", params)

    def article_sentiment(self, **params: str) -> Any:
        return self._request("/article-sentiments/v5/entities", params)

    def article_analytics(self, entity: str, **params: str) -> Any:
        return self._request(f"/article-analytics/v4/entities/{entity}", params)

    def latest_articles(self, **params: str) -> Any:
        return self._request("/latest-articles/v4", params)

    def economic_events(self, **params: str) -> Any:
        return self._request("/economicevents/v3", params)

    def anticipated_events(self, instrument_id: str, **params: str) -> Any:
        return self._request(f"/anticipatedevents/v3/{instrument_id}", params)

    def stops(self, **params: str) -> Any:
        return self._request("/stops/v3", params)
