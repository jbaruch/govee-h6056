# govee-h6056

A [Tessl](https://tessl.io) plugin encoding ground truth for the **Govee Flow Plus light bars (H6056)** — a 2-bar product that registers as a single API device and has three phantom segments the cloud docs don't warn you about.

## What this plugin provides

| Kind | Name | Purpose |
|---|---|---|
| Skill | `govee-h6056-control` | How to address segments safely, with a runnable Python example. |
| Rule  | `govee-h6056-gotchas` | Concise in-context reminder card. |
| Script | `scripts/govee_control.py` | Reference client that silently drops phantom segments. |

## Why it exists

The Govee Developer API reports 15 segments for the H6056. Segments `12`, `13`, `14`
return `200 OK` for every call but do **nothing** in hardware. The real physical range
is `0..11`, split across two bars:

- **Yankee (top bar):** segments `0..5`
- **Golf (bottom bar):** segments `6..11`

The plugin encodes those constraints so agents using it do not ship broken demos.

## Install

```bash
tessl install jbaruch/govee-h6056
```

Or pull directly from this repo:

```bash
tessl install github:jbaruch/govee-h6056
```

## Usage (quick)

```python
from scripts.govee_control import GoveeAPI, GoveeDevice, YANKEE_SEGMENTS, GOLF_SEGMENTS

api = GoveeAPI()              # reads GOVEE_API_KEY from env, else MOCK mode
devices = api.list_devices()
dev = GoveeDevice(sku=devices[0]["sku"], device=devices[0]["device"])

api.set_segments(dev, YANKEE_SEGMENTS, (0, 255, 0))   # top bar green
api.set_segments(dev, GOLF_SEGMENTS, (255, 0, 0))     # bottom bar red
```

See `skills/govee-h6056-control/SKILL.md` for the full API contract and
`rules/govee-h6056-gotchas.md` for the short version.

## License

MIT — see `LICENSE`.
