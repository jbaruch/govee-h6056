# Automated Lighting Controller with Clean Exit

## Problem/Feature Description

A small escape room venue uses Govee H6056 light bars for ambient effects during their game sessions. The game master runs a Python script that cycles through lighting patterns during the hour-long session. The problem: when the session ends (or the script crashes), the lights sometimes stay on in whatever color they were last set to. Guests leaving the room are confused by the lingering colored lights, and the staff has to manually power-cycle the bars each time.

The venue owner wants a controller script that handles exit cleanly: no matter how the script ends — normal completion, keyboard interrupt, or exception — all light bars must be visibly dark when the process exits. A previous attempt at a shutdown function didn't work reliably; the lights would sometimes remain on even after the script claimed to have cleared them.

Your task is to build a Python script that runs a short timed lighting sequence (pick any colors/pattern you like for the sequence) and then guarantees a clean visual shutdown when it finishes or is interrupted. The script should operate in mock mode when `GOVEE_API_KEY` is not set, logging what it would send instead of making real API calls.

## Output Specification

Produce a single Python file named `session_controller.py`. The script must:

1. Run a lighting sequence of at least 3 distinct color states across the bars.
2. Guarantee that all segments are visually cleared when the script exits, whether the exit is clean or caused by an unexpected error or interruption.
3. Work in mock/dry-run mode when `GOVEE_API_KEY` is absent.
4. Include a brief inline comment or docstring explaining the shutdown strategy chosen and why you chose the specific shutdown approach and what hardware behavior informed the decision.
