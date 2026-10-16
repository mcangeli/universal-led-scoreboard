# NHL module architecture — v0.2.0

## Scope and isolation

Implement NHL as an optional sport module without changing MLB's rendering or configuration semantics. The production v0.1.0 installation remains the stable baseline. NHL work happens on `feature/0.2.0-nhl`; do not deploy to the production Pi until the tests and hardware preview are approved.

## Data model (first implementation milestone)

Define a provider-independent game snapshot with: game ID, UTC start time, away/home team abbreviations and names, scores (nullable before puck drop), status (scheduled, live, final, postponed, unknown), period number and ordinal label, clock time remaining, intermission flag, and optional shootout state. Normalize absent API fields safely. Keep API payloads out of renderer code.

The NHL adapter should use the official NHL public schedule/score endpoints, with bounded timeouts, explicit failure handling, a short-lived cache, and deterministic fixtures for tests. Do not depend on live internet access in the unit test suite.

## 64×32 screens

- Pregame: logos or compact team marks, opponent abbreviations, start time.
- Live: scores, current period, clock remaining; distinguish intermission and overtime/shootout.
- Final: final scores with OT/SO designation when applicable.
- Off-day: a graceful no-game display.

Respect the existing RGB matrix framebuffer and original sport-specific visual style. Favor legibility over fitting excessive statistics on the matrix.

## Configurator and rotation

NHL team selection and screen eligibility should follow the existing shared sport configuration and rotation patterns wherever possible. An enabled favorite NHL team's live game should receive the same priority behavior as an enabled favorite MLB team's live game, without hijacking MLB-only settings. Introduce UI options only after model/adapter tests pass.

## Milestone sequence

1. Inventory existing sport registration, MLB adapter, shared settings, renderer and test conventions. Introduce NHL data types, API adapter, fixtures, and tests.
2. Implement NHL pregame/live/final/off-day 64×32 renderers and emulator previews with pixel/layout tests.
3. Connect NHL to screen rotation, team preferences, and the web configurator, with isolation/regression tests.
4. Validate on the development Pi and physical matrix, run full suite, document release and deployment steps.

A passing test report approves proceeding to the next milestone; failed tests require correction before advancement.
