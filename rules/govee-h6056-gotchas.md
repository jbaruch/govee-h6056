# Govee H6056 Gotchas

When working with Govee Flow Plus light bars (H6056), remember:

- **Segments 12, 13, 14 are phantom.** API returns 200 OK, nothing lights. Physical range is `0..11` only. Never send commands targeting 12+.
- **Two physical bars = one API device.** The bar-to-segment mapping is:
  - Yankee (top bar) → segments `0..5`
  - Golf (bottom bar) → segments `6..11`
  - Top-to-bottom within each bar matches the natural index order.
- **Discovery is `GET /router/api/v1/user/devices` with header `Govee-API-Key`.** Not mDNS, not Bluetooth.
- **Capability name is verbose:** `devices.capabilities.segment_color_setting` / `segmentedColorRgb`. `rgb` is a packed int: `(r<<16)|(g<<8)|b`.
- **Rate limit reality:** ~7 req/min sustained is the ceiling. Pair with the `rate-limited-iot-debounce` plugin if you're emitting more than one update per second.

See the full skill at `skills/govee-h6056-control/SKILL.md` and the reference client at `scripts/govee_control.py`.
