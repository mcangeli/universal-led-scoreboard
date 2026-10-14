# Universal LED Scoreboard startup splash

**Status:** design specification; renderer and artwork are not yet implemented.

## Visual design

- Native 64x32 pixel composition, legible at normal viewing distance.
- Near-black background, bright white `UNIVERSAL`, warm gold `LED SCOREBOARD`.
- Restrained colored indicator pixels referencing the multi-sport concept without requiring protected league logos.
- Use bitmap/pixel fonts and integer coordinates; avoid downscaling large artwork at runtime.
- Optional subtle animation, with a static fallback for low-power devices.

## Lifecycle

1. Display splash as soon as the matrix driver is ready.
2. Continue startup while loading configuration, plugins and data sources.
3. Show a short, legible progress or error state when initialization is slow or fails.
4. Transition to the selected sport's **Classic** layout once a screen is ready.
5. Allow users to disable the splash or adjust its minimum duration in the web configurator.

## Tests

Verify 64x32 bounds, text clipping, emulator screenshots, slow/offline startup, and plugin failure behavior. Splash must not block service readiness or hang restart.
