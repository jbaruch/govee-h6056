# Stage Light Show: Full Illumination Script

## Problem/Feature Description

The venue team at a small concert hall has just installed two Govee Flow Plus H6056 light bars above the stage. They want a Python script that can trigger a "full house lit" effect — simultaneously illuminating every available LED segment in a vibrant color of their choice — as well as a "blackout" mode that clears everything instantly.

The house tech found the Govee Developer API documentation and noticed it advertises a segment range with a maximum of 15. They started writing a script that loops over all of them, but the result looks patchy on stage: some segments light up, others seem to silently do nothing — the API returns success but nothing happens on those lights. They need a corrected, production-ready script that reliably lights the entire physical surface.

Your task is to produce a working Python script that controls the H6056 via the Govee cloud API. The script should work in environments where `GOVEE_API_KEY` is not set by running in mock/dry-run mode and logging intended API calls rather than hitting the network.

## Output Specification

Produce a single Python file named `stage_control.py` in the working directory. The script must:

1. When invoked with no API key present, run in mock mode (log what it would send, do not make real HTTP calls).
2. Implement a function that sets all lit segments to a single RGB color in the most efficient way.
3. Implement a function that clears all lit segments (blackout mode).
4. Include a `__main__` block that demonstrates both functions with example colors.

Also produce a short `notes.md` file (1–2 paragraphs) explaining any non-obvious decisions you made about which segments to target and why.
