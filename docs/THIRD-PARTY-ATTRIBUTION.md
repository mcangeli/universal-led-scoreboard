# Third-party attribution and licensing audit

**Status:** in progress, **not a certification of compliance**. Updated October 20, 2026.

The repository distributes its own [GPLv3 license](../LICENSE). That alone does not determine the provenance or redistribution permissions of each incorporated asset or third-party component. This register separates acknowledgments from a verified dependency and asset inventory.

| Project / provider | Relationship to review | Audit status |
| --- | --- | --- |
| [MLB LED Scoreboard](https://github.com/MLB-LED-Scoreboard/mlb-led-scoreboard) | Original scoreboard inspiration and potential implementation lineage | Attribution in README; copied-code provenance and license compatibility not independently verified |
| [NBA LED Scoreboard](https://github.com/m0ranwa/nba-led-scoreboard) | Original NBA scoreboard inspiration | Attribution present; reuse audit pending |
| [NFL LED Scoreboard](https://github.com/mikemountain/nfl-led-scoreboard) | Original NFL scoreboard inspiration | Attribution present; reuse audit pending |
| [MLS LED Scoreboard](https://github.com/alexanderthebadatcoding/mls-led-scoreboard) | Original MLS scoreboard inspiration | Attribution present; reuse audit pending |
| [NHL LED Scoreboard](https://github.com/falkyre/nhl-led-scoreboard) | Original NHL scoreboard inspiration | Attribution present; reuse audit pending |
| [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) | Hardware driver dependency | Attribution present; review installed/bundled driver version and applicable notices |
| Sports data, news/RSS and weather providers | Live external data, names and branding | Provider terms, display/redistribution restrictions and trademark review pending |
| Fonts, team/league logos and artwork | May have independent copyright/trademark restrictions | Inventory files and source/provenance before redistribution |

## Initial source-tree findings (October 19, 2026)

- The `universal_led/` directory contains Python source modules; the initial directory inventory did not expose a standalone bundled logo/image/font directory. **This is not a full recursive asset audit.**
- `universal_led/mlb_classic.py` explicitly describes its MLB 64×32 layout as an independent clean-room implementation rather than a port of upstream artwork. This is an author statement, not independent proof of provenance.
- `universal_led/mlb_team_marks.py` describes its compact letterform marks as original symbolic marks rather than official MLB logos. The source uses team abbreviations and colors, so trademark/branding review remains relevant.
- `scripts/install-system.sh` provisions a physical matrix mode, but installed driver sources and their notices must be checked on a device or in the driver provisioning scripts. A repository directory listing alone does not establish the exact driver license/version deployed.
- No conclusion has yet been drawn about upstream code similarity, third-party Python packages, provider terms, or graphics embedded as source constants. These require file-level review.

## Recursive source-tree inventory (October 20, 2026)

- Inspected the Git tree at commit `3ecdd158908ad7716157f946d9aa5888fbe1c5ed` (596 entries). No standalone files ending in `.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.ttf`, `.otf`, `.woff`, `.ico` or `.bmp` were found. This does **not** rule out embedded pixel art, base64 payloads, generated artwork or externally fetched assets.
- `universal_led/mlb_team_marks.py` contains inline pixel mark and sprite dictionaries. Its comments describe these as original symbolic marks; source ownership and trademark treatment remain subject to review.
- `scripts/install-system.sh` clones `hzeller/rpi-rgb-led-matrix` into the installer user’s local source directory for physical mode. The driver is an externally installed dependency rather than a copied repository asset. The script does not pin a specific driver commit; reproducibility and installed-version provenance remain open.
- `docs/RGB-MATRIX-DRIVER.md` identifies the driver as GPL-2.0-or-later and documents compatibility with GPLv3; verify against the precise upstream revision actually installed before declaring the license review complete.
- Physical Pi 3 operator check (October 20, 2026): upstream driver `14464b3` (2026-10-10), clean working tree, `uls-matrix.service` enabled/active, frame fresh at 1 second, web health OK. Treat this as a **known-working Pi 3 candidate** for a future pinned install, not cross-device certification. Resolve its full commit SHA and check license notices before pinning; do not silently replace installed drivers.
- No redistribution clearance is implied by the absence of binary assets. Code lineage, embedded fonts, provider terms, and notices still require inspection.

## Source-level font and feed findings (October 20, 2026)

- `universal_led/display.py` defines a 5×7 pixel glyph dictionary inline. No external font file is bundled, but the glyph designs' provenance is not independently established. Other font tables or encoded assets still require a recursive source-content scan.
- Confirmed source endpoints include MLB StatsAPI (`universal_led/mlb_data.py`), NHL API (`universal_led/nhl_feed.py`), and ESPN-hosted NBA and NFL scoreboards (`universal_led/nba_feed.py`, `universal_led/nfl_feed.py`). `universal_led/news_feeds.py` consumes configurable RSS/Atom feeds. These are observations of code endpoints, **not** findings that commercial or public redistribution is authorized.
- Review each provider's current terms, permitted caching/rate limits, attribution and branding restrictions before release. NHL and ESPN feed access should not be represented as an official partnership or endorsement.
- Upstream scoreboard inspirations remain acknowledged, but source-level derivation and copied-code provenance have not been established. Do not infer either copying or independent creation solely from similar score layouts.

## Weather and headlines provider inventory (October 20, 2026)

| Source | Code location | Release concern |
| --- | --- | --- |
| Open-Meteo geocoding and forecast | `universal_led/weather_feed.py` | Confirm noncommercial/commercial usage conditions, attribution, and request limits for the deployment context |
| OpenWeatherMap geocoding, current weather and forecast | `universal_led/weather_openweathermap.py` | User-supplied API key is required; confirm account tier, display attribution and caching/redistribution conditions |
| MLB public RSS news | `universal_led/mlb_news.py` | Feed visibility does not establish rights to redistribute headline text or MLB branding |
| User-configured RSS/Atom | `universal_led/news_feeds.py` | Permissions vary by publisher; preserve source identity and avoid implying universal redistribution rights |

These are verified source-code references, not legal conclusions or current provider terms. ULS should document source attribution and responsible rate limits without representing itself as an official service of any league or weather provider. Do not mark provider-terms review complete without examining authoritative current terms.

## Confirmed upstream terms (reviewed October 20, 2026)

- **RGB matrix driver:** The upstream project explicitly identifies its license as GPL-2.0-or-later, copyright Henner Zeller, and states that use under GPLv3 is permitted. Source: https://github.com/hzeller/rpi-rgb-led-matrix (README and COPYING). ULS installs the dependency from upstream in physical mode; it does not bundle a binary in this repository. Preserve driver license/copyright notices in any redistribution and verify the exact deployed commit before claiming a reproducible dependency set.
- **Open-Meteo:** https://open-meteo.com/en/terms specifies that its free API is for noncommercial use, with limits of fewer than 10,000 calls/day, 5,000/hour and 600/minute. https://open-meteo.com/en/pricing says a commercial subscription uses a separate customer API endpoint/key and that data attribution under CC BY 4.0 is required. ULS currently calls the free geocoding and forecast endpoints. Do not imply the free endpoint is approved for a commercial website, product, or promotional deployment.
- **Scope of verification:** These are confirmed statements from the providers' published upstream documentation, not a legal opinion or blanket certification for all dependencies. Other sports, RSS, weather, logos, and code lineage reviews remain open.

## Sports-provider and OpenWeather terms review (October 20, 2026)

| Provider | Published primary source | Finding / unresolved constraint |
| --- | --- | --- |
| NHL | https://www.nhl.com/info/terms-of-service | NHL's terms restrict content access/use to noncommercial, informational, personal purposes, and prohibit unauthorized automated harvesting. Public score endpoint availability does **not** grant a redistribution or commercial API license. |
| MLB | https://www.mlb.com/official-information/terms-of-use | MLB Digital Properties are subject to substantial copying/redistribution and commercial-use restrictions. The exact StatsAPI data license and applicability to each ULS call remain unresolved; do not claim API licensing approval. |
| ESPN | https://disneytermsofuse.com/ and https://www.espn.com/ | ULS calls undocumented ESPN-hosted JSON score endpoints; no supported developer license or redistribution authorization was verified. Terms applicable to API access require additional confirmation. |
| OpenWeather | https://openweathermap.org/faq and https://openweathermap.org/price | Published attribution is required for applicable free/self-service tiers. Subscription and data-license conditions vary; verify the particular API key's plan and current terms. |

**Release consequence:** A personal hobby scoreboard and a public/commercial demo are different use cases. Do not infer permitted commercial redistribution from successful requests or an open-source ULS code license. Provider permissions, trademarks and content licenses are independent of GPLv3. These findings document risks; they are not legal clearance.

## Published endpoint inventory

The [data sources and endpoint inventory](DATA-SOURCES.md) lists current score/schedule and standings URLs by sport, weather and news endpoints, and the explicit notice that external services may change without notice and users access them at their own discretion and responsibility. This improves transparency but **does not** resolve provider permission, embedded asset provenance, or distribution obligations.

## Embedded font and mark source review (October 20, 2026)

Directly inspected `universal_led/display.py`, `universal_led/mlb_classic.py` and `universal_led/mlb_team_marks.py` on the v0.8.0 feature branch:

- `display.py` embeds a 5×7 monochrome pixel-glyph dictionary (`FONT`) and draws the startup splash procedurally; there is no referenced external font file or splash bitmap in this module.
- `mlb_classic.py` embeds a separate 3×5 glyph dictionary (`SMALL`) for compact labels and numbers; its module header describes the screen as an independent implementation.
- `mlb_team_marks.py` embeds a team-color/letter mapping and five 11×9 pixel sprite definitions (MIL, LAD, ATL, CLE, TBR). These are source constants, not separately bundled official image files. Their shapes, colors and team associations may nevertheless implicate branding rights.
- **Important limitation:** module comments calling the marks or layouts “original” are claims by the code authors, not independent evidence of who designed each glyph/sprite. The two font dictionaries and five sprites therefore remain provenance exceptions pending author confirmation or documented replacement with clearly licensed assets. Similarity to upstream scoreboard projects was not exhaustively assessed.
- The previous recursive tree inventory found no standalone image or font files. This targeted inspection does not prove that no other module embeds artwork.

**Disposition:** No files were deleted or altered in this review. Do not mark the bundled-artwork/provenance release gate complete on this evidence alone.

## Closeout procedure

1. Search source and packaged assets for copied upstream code, included third-party files, fonts, team badges and logos. Record exact file paths and provenance.
2. For each actual dependency or reused asset, record upstream repository/URL, license identifier/version, required attribution or license text, modifications and redistribution conditions.
3. Preserve copyright notices and provide license text where required. Investigate unknown provenance rather than assuming a GitHub-hosted asset is free to redistribute.
4. Verify that team/league logos and data-provider trademarks are used consistently with their terms. Attribution is not a license.
5. Update this register with reviewed evidence and outstanding exceptions before approving a public release.

No upstream licenses or provider permissions have been independently confirmed by this document. Do not mark the release's licensing gate complete until the inventory and review are performed.
