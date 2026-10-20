# Third-party attribution and licensing audit

**Status:** in progress, **not a certification of compliance**. Updated October 19, 2026.

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

## Closeout procedure

1. Search source and packaged assets for copied upstream code, included third-party files, fonts, team badges and logos. Record exact file paths and provenance.
2. For each actual dependency or reused asset, record upstream repository/URL, license identifier/version, required attribution or license text, modifications and redistribution conditions.
3. Preserve copyright notices and provide license text where required. Investigate unknown provenance rather than assuming a GitHub-hosted asset is free to redistribute.
4. Verify that team/league logos and data-provider trademarks are used consistently with their terms. Attribution is not a license.
5. Update this register with reviewed evidence and outstanding exceptions before approving a public release.

No upstream licenses or provider permissions have been independently confirmed by this document. Do not mark the release's licensing gate complete until the inventory and review are performed.
