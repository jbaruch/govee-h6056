---
name: govee-h6056-control
description: Controls Govee H6056 Flow Plus light bars (smart LED lights) via cloud REST API with correct segment-to-bar mapping (Yankee=0-5, Golf=6-11) and phantom-segment awareness (12-14 return 200 OK but do nothing). Use when the user wants to control Govee H6056 light bars, change LED light colors or brightness, set bar segment colors, or automate Govee smart lighting scenes.
---

# Govee H6056 Control

Use this skill whenever you need to light up Govee Flow Plus light bars (H6056).

## Device facts the cloud docs don't tell you

- **Product form:** 2 physical bars that register as ONE API device.
- **API claims 15 segments** (`segmentedColorRgb`, min=1, max=15).
- **Physical truth: 12 segments.** Indices `12`, `13`, `14` are **phantom**. The API returns `200 OK` when you address them; no light turns on. If you don't slice your ranges correctly, your "all on" commands will look broken on stage.
- **Bar mapping** (top → bottom on each bar):
  - `bar_a` (Yankee): segments `0, 1, 2, 3, 4, 5`
  - `bar_b` (Golf):   segments `6, 7, 8, 9, 10, 11`
- **Discovery is NOT mDNS.** Call `GET /router/api/v1/user/devices` with your API key to enumerate SKUs and device IDs.

## API contract

- Base URL: `https://openapi.api.govee.com`
- Auth: header `Govee-API-Key: <key>` (NOT bearer, NOT query param)
- Control endpoint: `POST /router/api/v1/device/control`
- Capability for per-segment color:
  - `type = "devices.capabilities.segment_color_setting"`
  - `instance = "segmentedColorRgb"`
  - `value = {"segment": [<indices>], "rgb": <packed_int>}` where `rgb = (r<<16)|(g<<8)|b`
- Rate limits: nominal ~10k/day. Sustained traffic above ~7 req/min trips 429s. Combining Yankee+Golf writes into one payload when possible keeps you out of trouble.

## Minimal executable example

```python
import time
import requests

API_KEY = "<your-govee-api-key>"
DEVICE_ID = "<your-device-id>"  # from GET /router/api/v1/user/devices
SKU = "H6056"
BASE_URL = "https://openapi.api.govee.com"

def pack_rgb(r, g, b):
    return (r << 16) | (g << 8) | b

def set_segment_color(segments, r, g, b, retries=3):
    """Set the given segment indices to an RGB color. Never pass indices > 11."""
    assert all(0 <= s <= 11 for s in segments), "Phantom segment (12-14) addressed!"
    payload = {
        "requestId": "govee-h6056-ctrl",
        "payload": {
            "sku": SKU,
            "device": DEVICE_ID,
            "capability": {
                "type": "devices.capabilities.segment_color_setting",
                "instance": "segmentedColorRgb",
                "value": {
                    "segment": segments,
                    "rgb": pack_rgb(r, g, b)
                }
            }
        }
    }
    headers = {"Govee-API-Key": API_KEY, "Content-Type": "application/json"}
    for attempt in range(retries):
        resp = requests.post(f"{BASE_URL}/router/api/v1/device/control",
                             json=payload, headers=headers, timeout=10)
        if resp.status_code == 429:
            wait = 2 ** attempt  # exponential backoff: 1s, 2s, 4s
            time.sleep(wait)
            continue
        resp.raise_for_status()
        # NOTE: A 200 OK does NOT confirm physical change — phantom segments
        # (12-14) also return 200 OK but illuminate nothing. Trust the segment
        # list you send, not the status code alone.
        return resp.json()
    raise RuntimeError("Rate limit not resolved after retries")

# Turn all 12 physical segments green in one call:
set_segment_color([0,1,2,3,4,5,6,7,8,9,10,11], r=0, g=255, b=0)
```

## How to act

1. Use `scripts/govee_control.py` as the reference client. Copy it or import from it — do not re-implement from the Govee docs without this tile's corrections.
2. Always slice segments against the **physical** range `0..11`. Never iterate `range(15)` or `range(total_segments)` unless `total_segments == 12`.
3. If a user asks to "turn everything green", issue one call with `"segment": [0,1,2,3,4,5,6,7,8,9,10,11]`, not two separate Yankee/Golf calls.
4. When building per-bar animations (confidence meters, emotion colors), address each bar with its own index list so the mapping is explicit in the code.
5. **After every API call:** check for HTTP 429 and back off exponentially. A `200 OK` only confirms the request was accepted — it does **not** confirm lights changed. Phantom segments will silently succeed. Validate correctness by checking the segment list you sent, not the response body.

## Related

- See rule `govee-h6056-gotchas` for quick in-context reminders.
- Pairs well with `rate-limited-iot-debounce` when multiple updates per second are needed.
