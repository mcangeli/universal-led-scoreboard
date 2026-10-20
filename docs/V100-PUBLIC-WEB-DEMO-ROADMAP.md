# v1.0 Public Web Demo Roadmap

**Target:** v1.0 planning milestone, not part of v0.8.0 or v0.9.0.

## Goal

Support a publicly accessible website where prospective users can see Universal LED Scoreboard running in a virtual 64×32 matrix preview, without Raspberry Pi hardware.

## Proposed scope

- Supported deployment instructions for a conventional Linux web server, preferably containerized and reverse-proxy friendly.
- Responsive, publicly viewable scoreboard demo with realistic sample data and optional permitted live data feeds.
- Curated sport/game scenarios that remain useful outside live-game windows.
- Separate read-only public preview and authenticated administration.
- If interactive visitor configuration is introduced, isolate each visitor's session and reset changes automatically.
- No public exposure of Wi-Fi, hotspot, system services, updater, credential management, file import, or privileged maintenance endpoints.
- Document resource limits, abuse protection, privacy, HTTPS, and provider branding/licensing restrictions.
- Keep the Raspberry Pi hardware installation and v0.8/v0.9 release scopes unaffected.

## Acceptance criteria (to refine during v1.0 planning)

1. A clean supported server deployment serves a working scoreboard preview over HTTPS.
2. Anonymous visitors cannot alter persistent settings or invoke privileged controls.
3. Demo data can show live, pregame, final, and idle rotations independent of actual sports schedules.
4. No visitor can see or modify another visitor's configuration or session.
5. Documentation covers deployment, maintenance, reset, and teardown.

**Status:** Roadmap proposal only; not implemented or committed to a specific architecture.
