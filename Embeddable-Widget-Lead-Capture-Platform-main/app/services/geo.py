import logging
from dataclasses import dataclass

import httpx

from app.core.config import Settings


logger = logging.getLogger(__name__)


# ============================================================
# Geo Result
# ============================================================

@dataclass
class GeoResult:
    country: str | None
    city: str | None
    provider: str | None


# ============================================================
# Base Geo Provider
# ============================================================

class GeoProvider:
    name = "base"

    def lookup(self, ip: str) -> GeoResult:
        raise NotImplementedError


# ============================================================
# Provider A
# ============================================================

class ProviderA(GeoProvider):
    name = "provider_a"

    def __init__(self, settings: Settings):
        self.s = settings

    def lookup(self, ip):
        if self.s.geo_provider_a_mode == "mock_down":
            raise RuntimeError("Provider A mock failure")

        if self.s.geo_provider_a_mode == "mock_up":
            return GeoResult(
                "India",
                "Bengaluru",
                self.name
            )

        with httpx.Client(
            timeout=self.s.geo_timeout_seconds
        ) as client:
            r = client.get(
                self.s.geo_provider_a_url.format(ip=ip)
            )
            r.raise_for_status()
            d = r.json()

        if d.get("status") == "fail":
            raise RuntimeError("Provider A rejected lookup")

        return GeoResult(
            d.get("country"),
            d.get("city"),
            self.name
        )


# ============================================================
# Provider B
# ============================================================

class ProviderB(GeoProvider):
    name = "provider_b"

    def __init__(self, settings: Settings):
        self.s = settings

    def lookup(self, ip):
        if self.s.geo_provider_b_mode == "mock_down":
            raise RuntimeError("Provider B mock failure")

        if self.s.geo_provider_b_mode == "mock_up":
            return GeoResult(
                "India",
                "Bengaluru",
                self.name
            )

        with httpx.Client(
            timeout=self.s.geo_timeout_seconds
        ) as client:
            r = client.get(
                self.s.geo_provider_b_url.format(ip=ip)
            )
            r.raise_for_status()
            d = r.json()

        if d.get("error"):
            raise RuntimeError("Provider B rejected lookup")

        return GeoResult(
            d.get("country_name"),
            d.get("city"),
            self.name
        )


# ============================================================
# Geo Service
# ============================================================

class GeoService:

    def __init__(self, settings: Settings):
        self.providers = [
            ProviderA(settings),
            ProviderB(settings)
        ]

    def enrich(self, ip: str) -> GeoResult:

        for p in self.providers:
            try:
                return p.lookup(ip)

            except Exception as exc:
                logger.warning(
                    "Geo provider failed: %s",
                    exc
                )

        return GeoResult(
            None,
            None,
            None
        )