# v0.9.x roadmap: Dynamic team and division discovery

**Status:** planned for v0.9.x; not in v0.8.0.

## Goal

Allow league/provider plugins to discover current teams, stable provider IDs, league/division membership and season changes without hardcoding rosters in ULS. Handle expansion teams (for example, a future Atlanta NWSL club), renamed/relocated teams and annual promotion/relegation.

## Proposed design

- Each sports provider plugin exposes a versioned team/competition discovery interface, including provider-qualified stable IDs, names, abbreviations, optional branding metadata and season-specific league/division membership.
- Maintain a cached team registry that survives empty schedules, network failures and offseasons; update it from provider feeds with appropriate refresh limits.
- Prefer stable provider IDs for favorites. Migrate existing abbreviation-based favorites safely; preserve unresolved selections and provide clear reconciliation when an ID changes.
- Populate the dashboard's favorite-team and division selectors from the registry, with sensible fallback entries before a season begins.
- Treat league membership as season-scoped; preserve historical records across expansion, promotion, relegation, rebranding and contraction.
- Handle duplicate abbreviations and cross-league club identities without collisions.
- Support tests with simulated expansion, division changes, team renames, missing teams, provider outages and partial payloads.

## Release boundaries

Do not add this to the v0.8.0 release. Revisit during v0.9.x provider/plugin architecture work; avoid making the dynamic registry a prerequisite for unrelated plugin features.

## Acceptance criteria

1. A newly introduced team appears in game rotation and the dashboard selector when the provider supplies its identity.
2. Existing favorites survive a team's name or abbreviation change when its stable ID remains unchanged.
3. Promotion/relegation updates current-season league membership without deleting historical identities.
4. Empty or temporarily broken provider feeds do not erase known teams or favorites.
5. Duplicate abbreviations in different leagues/providers cannot select the wrong team.
