# CI/CD Build Status Visualizer

## Problem/Feature Description

A software team uses two Govee H6056 light bars mounted above their shared monitor wall to give the whole office an at-a-glance view of their CI pipeline health. They want the top bar to reflect the status of their frontend builds and the bottom bar to reflect their backend builds. Each bar should show a color gradient from red (failing) to green (passing) based on a confidence score (0.0–1.0) provided by their build system.

The team's previous attempt used a simple loop that sent one API call per bar per update, but it kept triggering HTTP 429 errors during busy push windows when both pipelines report status updates at the same time. They need a smarter solution. Additionally, they want the implementation to be maintainable and close to the reference patterns used by the team for this device — so future contributors understand which physical bar corresponds to which pipeline at a glance.

Your task is to write a Python script that, given two confidence scores (one for each pipeline), updates the two light bars to the appropriate gradient colors. The script must handle rate-limit responses gracefully without losing the update. It must work in mock mode when `GOVEE_API_KEY` is not set.

## Output Specification

Produce a single Python file named `build_status.py`. The script must:

1. Accept two float arguments (0.0–1.0) on the command line representing frontend and backend build confidence scores.
2. Map frontend score → top bar and backend score → bottom bar, using a red-to-green color gradient.
3. Handle rate-limit errors gracefully without dropping the update.
4. Include a `__main__` block showing example usage.
5. Work in mock mode (log intended API calls, no real HTTP) when `GOVEE_API_KEY` is absent.

Also produce a `design_notes.md` file explaining your mapping of pipeline → physical bar and the approach taken for API call efficiency.

## Input Files

A reference client exists in the project at `scripts/govee_control.py`. Import and use it as your starting point — do not reimplement the API client from scratch.
