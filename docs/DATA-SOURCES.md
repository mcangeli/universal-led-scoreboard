# External data endpoints and user responsibility

**Inventory date:** October 20, 2026. These URLs reflect the ULS v0.8.0 source code at the time of review, not a guarantee that any provider will continue serving them.

## Sports endpoints currently used

| Sport / league | Scoreboard or schedule endpoint | Standings endpoint |
| --- | --- | --- |
| MLB | `https://statsapi.mlb.com/api/v1/schedule` | `https://statsapi.mlb.com/api/v1/standings` |
| NHL | `https://api-web.nhle.com/v1/score/{YYYY-MM-DD}` | `https://api-web.nhle.com/v1/standings/now` |
| NBA | `https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard` | `https://site.api.espn.com/apis/v2/sports/basketball/nba/standings` |
| WNBA | `https://site.api.espn.com/apis/site/v2/sports/basketball/wnba/scoreboard` | **Not confirmed by this inventory**; inspect WNBA standings integration before treating NBA standings URL as equivalent |
| NFL | `https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={YYYYMMDD}` | `https://site.api.espn.com/apis/v2/sports/football/nfl/standings` |
| MLS | `https://site.api.espn.com/apis/site/v2/sports/soccer/usa.1/scoreboard?dates={YYYYMMDD}` | `https://site.api.espn.com/apis/v2/sports/soccer/usa.1/standings` |
| NWSL | `https://site.api.espn.com/apis/site/v2/sports/soccer/usa.nwsl/scoreboard?dates={YYYYMMDD}` | `https://site.api.espn.com/apis/v2/sports/soccer/usa.nwsl/standings` |
| English Premier League | `https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard?dates={YYYYMMDD}` | `https://site.api.espn.com/apis/v2/sports/soccer/eng.1/standings` |
| EFL Championship | `https://site.api.espn.com/apis/site/v2/sports/soccer/eng.2/scoreboard?dates={YYYYMMDD}` | `https://site.api.espn.com/apis/v2/sports/soccer/eng.2/standings` |
| EFL League One | `https://site.api.espn.com/apis/site/v2/sports/soccer/eng.3/scoreboard?dates={YYYYMMDD}` | `https://site.api.espn.com/apis/v2/sports/soccer/eng.3/standings` |
| EFL League Two | `https://site.api.espn.com/apis/site/v2/sports/soccer/eng.4/scoreboard?dates={YYYYMMDD}` | `https://site.api.espn.com/apis/v2/sports/soccer/eng.4/standings` |

**Code references:** `universal_led/mlb_data.py`, `mlb_standings_feed.py`, `nhl_feed.py`, `nhl_standings_feed.py`, `nba_feed.py`, `nba_standings_feed.py`, `nfl_feed.py`, `nfl_standings_feed.py`, `soccer_data.py`, `mls_standings_feed.py`, `nwsl_standings_feed.py`, `football_standings_feed.py`. Scoreboard requests may add query parameters such as dates, seasons, or league identifiers. Some optional features may use additional detail endpoints not exhaustively captured in this table.

## Weather and news endpoints

| Feature | Current endpoint |
| --- | --- |
| Open-Meteo location search | `https://geocoding-api.open-meteo.com/v1/search` |
| Open-Meteo forecast/current | `https://api.open-meteo.com/v1/forecast` |
| OpenWeatherMap geocoding | `https://api.openweathermap.org/geo/1.0/zip`, `/geo/1.0/reverse` |
| OpenWeatherMap current weather | `https://api.openweathermap.org/data/2.5/weather` |
| OpenWeatherMap forecast | `https://api.openweathermap.org/data/2.5/forecast` |
| MLB headlines | `https://www.mlb.com/feeds/news/rss.xml` |
| General news | User-configured RSS/Atom source URLs; no universal fixed endpoint |

**Code references:** `universal_led/weather_feed.py`, `weather_openweathermap.py`, `mlb_news.py`, `news_feeds.py`.

## Important notice: external services and user discretion

Universal LED Scoreboard is an independent, unofficial open-source project. It is not affiliated with, endorsed by, sponsored by, or authorized by MLB, NHL, NBA, WNBA, NFL, MLS, NWSL, ESPN, the English football leagues, or any listed data provider.

**External endpoints may change, become unavailable, impose authentication, rate limits or fees, restrict access, or be discontinued at any time without notice.** ULS cannot guarantee endpoint availability, response formats, accuracy, timeliness, continued compatibility, or access rights. A provider's endpoint being publicly reachable does **not** establish permission for automated access, copying, redistribution, or commercial use.

**Users choose to enable and access third-party data sources at their own discretion and responsibility.** Before using a source, users should review and comply with its current terms of service, licenses, attribution requirements, usage limits, and applicable law. Users are responsible for obtaining any necessary permissions or API subscriptions. ULS's GPLv3 software license does not grant rights to third-party data, trademarks, logos, or content.

This notice is not legal advice and does not remove any obligations the project maintainers may have when distributing software or bundled content. Report broken endpoints or terms changes through the project issue tracker.

For licensing status and unresolved provenance questions, see [Third-party attribution and licensing audit](THIRD-PARTY-ATTRIBUTION.md).
