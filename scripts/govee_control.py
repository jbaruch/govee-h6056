"""
Govee Developer API v2 client for the H6056 Flow Plus light bars.

Ground truth (see tile rules):
- Physical segments: 0..11 only. API accepts 0..14 but 12..14 are phantom (200 OK, no light).
- Two physical bars, one API device:
    Yankee (top bar)    -> segments 0..5
    Golf   (bottom bar) -> segments 6..11
- Auth header is "Govee-API-Key" (not bearer).
- Discovery: GET /router/api/v1/user/devices (NOT mDNS).

If GOVEE_API_KEY is unset, this client runs in MOCK mode: logs intended calls instead of
hitting the network. Useful for CI and offline testing.
"""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from typing import Iterable

import requests


BASE = "https://openapi.api.govee.com"

# Physical ground truth — do not change without a hardware reason.
PHYSICAL_SEGMENTS = 12
YANKEE_SEGMENTS = list(range(0, 6))   # top bar
GOLF_SEGMENTS = list(range(6, 12))    # bottom bar
PHANTOM_SEGMENTS = {12, 13, 14}       # never address these


def rgb_int(r: int, g: int, b: int) -> int:
    """Pack 8-bit RGB into the int Govee expects."""
    return (int(r) << 16) | (int(g) << 8) | int(b)


def gradient_rgb(t: float) -> tuple[int, int, int]:
    """t in [0,1]: 0.0 -> red, 0.5 -> yellow, 1.0 -> green."""
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        return (255, int(255 * (t * 2)), 0)
    return (int(255 * (1 - (t - 0.5) * 2)), 255, 0)


@dataclass
class GoveeDevice:
    sku: str
    device: str  # MAC-like identifier returned by /user/devices


class GoveeAPI:
    """Thin wrapper around the Govee Developer API v2."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("GOVEE_API_KEY")
        self.mock = not self.api_key
        if self.mock:
            print("[govee] MOCK MODE — no GOVEE_API_KEY set. Calls will be logged only.")
        self.session = requests.Session()

    # ---- HTTP -----------------------------------------------------------

    def _headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Govee-API-Key": self.api_key or "MOCK",
        }

    def list_devices(self) -> list[dict]:
        if self.mock:
            print("[govee] MOCK list_devices → []")
            return []
        r = self.session.get(
            f"{BASE}/router/api/v1/user/devices",
            headers=self._headers(),
            timeout=10,
        )
        r.raise_for_status()
        return r.json().get("data", [])

    def control(
        self,
        sku: str,
        device: str,
        cap_type: str,
        cap_instance: str,
        value: dict,
    ) -> dict | None:
        payload = {
            "requestId": str(uuid.uuid4()),
            "payload": {
                "sku": sku,
                "device": device,
                "capability": {
                    "type": cap_type,
                    "instance": cap_instance,
                    "value": value,
                },
            },
        }
        if self.mock:
            print(f"[govee MOCK] {sku}/{device[:12]}… {cap_instance} = {value}")
            return {"mock": True}
        r = self.session.post(
            f"{BASE}/router/api/v1/device/control",
            headers=self._headers(),
            data=json.dumps(payload),
            timeout=10,
        )
        if not r.ok:
            print(f"[govee] control FAIL {r.status_code}: {r.text[:200]}")
            return None
        return r.json()

    # ---- High-level segment API ----------------------------------------

    def set_segments(
        self,
        device: GoveeDevice,
        segments: Iterable[int],
        rgb: tuple[int, int, int],
    ) -> dict | None:
        """
        Address a set of physical segments with a single RGB color.

        Silently drops phantom segments (12..14) to protect the caller.
        """
        safe = [s for s in segments if s not in PHANTOM_SEGMENTS and 0 <= s < PHYSICAL_SEGMENTS]
        if not safe:
            return None
        return self.control(
            device.sku,
            device.device,
            "devices.capabilities.segment_color_setting",
            "segmentedColorRgb",
            {"segment": safe, "rgb": rgb_int(*rgb)},
        )

    def yankee(self, device: GoveeDevice, rgb: tuple[int, int, int]) -> dict | None:
        return self.set_segments(device, YANKEE_SEGMENTS, rgb)

    def golf(self, device: GoveeDevice, rgb: tuple[int, int, int]) -> dict | None:
        return self.set_segments(device, GOLF_SEGMENTS, rgb)

    def all_off(self, device: GoveeDevice) -> dict | None:
        return self.set_segments(device, range(PHYSICAL_SEGMENTS), (0, 0, 0))


if __name__ == "__main__":
    api = GoveeAPI()
    print("Devices:", api.list_devices())
