"""Native LAN configurator and shared scoreboard emulator."""
from __future__ import annotations
import os
import argparse
import json
import secrets
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from .config_store import read_config,save_config
from .mlb_classic import BaseballGame
from .mlb_palette_v11 import MLBPaletteScreen
from .mlb_data import MLBFeed
from .mlb_runtime import BackgroundMLBFeed,select_games
from .web_preview import HTML as BOARD_HTML
from .auth import Sessions, verify_password, configure_cli
from .release import display_version
from .matrix_settings import load_matrix_settings, validate_matrix_settings, matrix_service_label

LOGIN_HTML='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Scoreboard Login</title><style>body{font:16px system-ui;background:#0c1624;color:#e9eef5;max-width:400px;margin:12vh auto;padding:24px}form{background:#18283b;border:1px solid #34445b;border-radius:12px;padding:24px}input,button{box-sizing:border-box;width:100%;padding:12px;margin:8px 0;border-radius:6px}button{background:#d7b46d;border:0;font-weight:bold;cursor:pointer}.login-error{padding:12px;border:1px solid #d98989;border-radius:8px;background:#49262b;color:#fff0f0}input{background:#f8fafc;color:#111827;border:1px solid #a6b4c5}input:focus-visible,button:focus-visible{outline:3px solid #e8c985;outline-offset:2px}
</style></head><body><form method="post" action="/login"><h2>Universal LED Scoreboard</h2><p>Administrator login</p>__LOGIN_ERROR__<label>Password<input name="password" type="password" autocomplete="current-password" required></label><button type="submit">Sign In</button><p>Use HTTPS before accessing outside a trusted LAN.</p></form></body></html>'''

HTML='''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Universal LED Scoreboard | Configurator</title>
<style>
[hidden]{display:none!important} nav{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px} nav a.board-button{display:inline-flex;align-items:center;gap:8px;background:#d7b46d;color:#142033;padding:11px 17px;border:0;border-radius:7px;font-weight:bold;text-decoration:none;line-height:normal;box-sizing:border-box} nav a.board-button:hover,nav button:hover{background:#ebc987} nav a.board-button:focus-visible{outline:3px solid #fff;outline-offset:3px} input,select{padding:6px;border-radius:5px} body{margin:0;background:#0c1624;color:#e9eef5;font:15px system-ui}
header{padding:18px 24px;background:#152439;border-bottom:1px solid #34445b}
h1{margin:0;font-size:23px} main{max-width:1000px;margin:auto;padding:24px}
section{background:#18283b;border:1px solid #34445b;border-radius:12px;padding:20px;margin:0 0 18px}
canvas{width:100%;max-width:768px;image-rendering:pixelated;background:black;border:5px solid #304054}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(205px,1fr));gap:12px}
.item{display:flex;align-items:center;gap:12px;background:#22354a;padding:9px;border-radius:8px}
.item label{flex:1} input[type=color]{width:55px;height:37px;border:0;background:none;cursor:pointer}
button{background:#d7b46d;color:#142033;padding:11px 17px;border:0;border-radius:7px;font-weight:bold;cursor:pointer}
button:disabled{opacity:.5} .muted{color:#b6c5d5} #status{min-height:24px}

/* Preview 9: visual shell inspired by the original MLB Configurator. */
:root{color-scheme:dark;--surface:#101827;--edge:#263650;--muted:#91a0b7}
*{box-sizing:border-box}
body{background:#0a0f18;color:#e8edf5;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
header{min-height:86px;padding:16px 28px;background:#101827;border-bottom:1px solid #243047;display:flex;align-items:center;justify-content:space-between;gap:20px}
header h1{font-size:24px;margin:2px 0 4px}.eyebrow{font-size:11px;letter-spacing:.16em;color:#8fa4c7;font-weight:700}.header-note{color:#91a0b7;font-size:13px}
.shell{display:grid;grid-template-columns:245px minmax(0,1fr);min-height:calc(100vh - 86px)}
aside{padding:20px 14px;background:#0e1623;border-right:1px solid #243047;display:flex;flex-direction:column;gap:14px}
.side-title{font-size:12px;letter-spacing:.09em;font-weight:700;color:#8fa4bf;padding:0 12px}
aside nav{display:flex;flex-direction:column;gap:4px;margin:0}
aside .nav-item{width:100%;text-align:left;background:transparent;border:1px solid transparent;color:#dbe5f3;padding:12px;border-radius:8px;font-weight:600}
aside .nav-item:hover{background:#1a2940}aside .nav-item.active{background:#1c2940;border-color:#354968;color:#fff}
.sidebar-footer{margin-top:auto;display:grid;gap:10px;border-top:1px solid #26344d;padding-top:18px}
aside .board-button{justify-content:center;text-align:center}aside .signout{background:#182234;color:#e8edf5;border:1px solid #354968}
main{max-width:1500px;width:100%;margin:0 auto;padding:28px;min-width:0}
section{background:#101827;border:1px solid #263650;border-radius:12px;padding:22px;margin-bottom:18px}
section h2{margin-top:0}section h3{color:#d9e6f7}
input:not([type=color]),select{background:#0e1623;color:#e8edf5;border:1px solid #31415e;border-radius:7px;padding:9px;max-width:100%}
button{border:1px solid #354968}button:focus-visible,aside a:focus-visible{outline:2px solid #5aa2ff;outline-offset:2px}
.item{background:#182234;border:1px solid #263650}
.muted{color:#91a0b7}
@media(max-width:800px){.shell{grid-template-columns:1fr}aside{border-right:0;border-bottom:1px solid #243047}aside nav{flex-direction:row;flex-wrap:wrap}aside .nav-item{width:auto}.sidebar-footer{display:flex;flex-wrap:wrap}main{padding:16px}header{padding:16px}.header-note{display:none}}
.dashboard-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin:14px 0 22px}.dashboard-tile{background:#0e1623;border:1px solid #263650;border-radius:9px;padding:15px;min-width:0}.dashboard-tile h3{font-size:13px;text-transform:uppercase;letter-spacing:.05em;color:#aebed1;margin:0 0 9px}.dashboard-tile p{margin:0;overflow-wrap:anywhere;line-height:1.5}.status-dot{display:inline-block;width:9px;height:9px;border-radius:50%;background:#91a0b7;margin-left:5px}.status-dot[data-state="healthy"]{background:#4cc98a}.status-dot[data-state="error"]{background:#f07b72}.sidebar-footer .board-button{display:block;text-align:center;background:#1769d2;color:white;border-radius:7px;padding:11px 12px;text-decoration:none;font-weight:700}.sidebar-footer .board-button:hover{background:#287be0}.favorite-fieldset{border:1px solid #34445b;border-radius:9px;padding:14px;margin:12px 0}.favorite-team-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:9px;max-height:310px;overflow:auto;padding:8px}.favorite-team-grid label{display:flex;align-items:center;gap:9px;padding:7px;border-radius:5px;background:#101d2c;cursor:pointer}.favorite-team-grid input{accent-color:#d7b46d}.favorite-fieldset legend{font-weight:700}.color-editor{display:grid;grid-template-columns:1fr auto auto;gap:8px 12px;align-items:center}.color-editor .color-name{font-weight:700;min-width:0;overflow-wrap:anywhere}.color-editor .color-hex{font:12px ui-monospace,monospace;color:#d7b46d}.color-channels{grid-column:1/-1;display:grid;gap:6px;width:100%}.color-channel{display:grid;grid-template-columns:44px minmax(0,1fr) 32px;align-items:center;gap:7px;font-size:12px}.color-channel input[type=range]{width:100%;min-width:0;accent-color:#d7b46d}.color-channel output{text-align:right;font-variant-numeric:tabular-nums}.color-editor input[type=color]{width:42px;height:32px}/* v0.4.5 Preview 1: dashboard hierarchy and shared shell rhythm. */
:root{--space-1:6px;--space-2:12px;--space-3:18px;--space-4:24px;--radius-card:12px;--gold:#d7b46d}
main{padding:clamp(16px,2.2vw,32px)}section{padding:clamp(18px,2vw,28px)}
section h2{font-size:clamp(21px,1.6vw,26px);line-height:1.25;margin:0 0 18px}
.page-heading{display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap;margin-bottom:24px}
.page-heading h2{margin:2px 0 8px}.page-heading p{margin:0}.page-kicker{font-size:11px;text-transform:uppercase;letter-spacing:.13em;color:#9db5d4;font-weight:700}
.dashboard-board-link{display:inline-flex;align-items:center;justify-content:center;padding:11px 16px;background:#1c304a;border:1px solid #385373;border-radius:8px;color:#e9f1ff;text-decoration:none;font-weight:700;white-space:nowrap}
.dashboard-board-link:hover{background:#263e5e}.dashboard-board-link:focus-visible{outline:2px solid #5aa2ff;outline-offset:3px}
.dashboard-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:0 0 22px}
.dashboard-tile{padding:18px;min-height:116px;display:flex;flex-direction:column;gap:8px}.dashboard-tile h3{margin:0;color:#aebed1}.dashboard-tile p{font-size:14px;line-height:1.65}
.dashboard-tile-primary{background:#142035;border-color:#344b6c;min-height:142px}.dashboard-tile-primary p{font-size:15px;color:#e8edf5}
.dashboard-actions{display:flex;justify-content:space-between;align-items:center;gap:22px;border-top:1px solid var(--edge);padding-top:22px}
.dashboard-actions h3{margin:0 0 6px;font-size:15px}.dashboard-actions p{margin:0;line-height:1.55;max-width:690px}
.dashboard-actions button{flex-shrink:0}.dashboard-page #restart-status:empty{display:none}
@media(max-width:680px){.dashboard-grid{grid-template-columns:1fr}.dashboard-tile,.dashboard-tile-primary{min-height:0}.dashboard-actions{align-items:stretch;flex-direction:column}.dashboard-actions button{width:100%}.dashboard-board-link{width:100%}}

/* v0.4.5 Preview 2: task-oriented sport settings navigation. */
.sports-subnav{display:flex;flex-wrap:wrap;gap:8px;margin:20px 0;border-bottom:1px solid #31415e;padding-bottom:12px}
.sports-subnav button{background:#19263a;color:#c9d6e7;border:1px solid #354968}.sports-subnav button.active{background:#d7b46d;color:#142033;border-color:#d7b46d}
.sports-overview-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:12px;margin:16px 0}
.sport-choice{display:flex;flex-direction:column;align-items:flex-start;gap:10px;text-align:left;background:#152237;color:#edf3fc;border:1px solid #344b6c;border-radius:10px;padding:18px}
.sport-choice:hover{background:#1d3049}.sport-choice span{font-size:12px;color:#b5c5d8}
.sports-view[hidden],.sport-config-panel[hidden]{display:none!important}.sports-view>h3{margin-top:0}
#sport-picker{margin:10px 0 20px;min-width:170px}.sports-savebar{display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin-top:20px;padding-top:20px;border-top:1px solid #31415e}
.rotation-summary{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px}.rotation-summary .item{display:block;line-height:1.65}
</style></head><body>
<header><div><div class="eyebrow">UNIVERSAL LED SCOREBOARD</div><h1>Scoreboard Configurator</h1><span class="muted">__PREVIEW_VERSION__</span></div><span class="header-note">64 × 32 Display Manager</span></header>
<div class="shell"><aside><div class="side-title">DISPLAY</div><nav aria-label="Configurator navigation"><button class="nav-item" type="button" onclick="showPage('dashboard')">◫ Dashboard</button> <button class="nav-item" type="button" onclick="showPage('sports')">⚾ Sports</button> <button class="nav-item" type="button" onclick="showPage('display')">▦ Display</button> <button class="nav-item" type="button" onclick="showPage('colors')">◉ Colors</button> <button class="nav-item" type="button" onclick="showPage('news')">▤ Content &amp; News</button> <button class="nav-item" type="button" onclick="showPage('wifi')">◈ Wi-Fi</button> <button class="nav-item" type="button" onclick="showPage('matrix-settings')">▦ Matrix Hardware</button> <button class="nav-item" type="button" onclick="showPage('plugins')">▧ Plugins</button> <button class="nav-item" type="button" onclick="showPage('system')">⚙ System</button></nav><div class="sidebar-footer"><a class="board-button" href="/board" target="_blank" rel="noopener">Open Board View ↗</a><button type="button" class="signout" onclick="logout()">Sign Out</button></div></aside><main><section data-page="dashboard" class="dashboard-page"><div class="page-heading"><div><p class="page-kicker">Board overview</p><h2>Dashboard</h2><p class="muted">Your current display configuration and feed health at a glance.</p></div></div><div class="dashboard-grid"><div class="dashboard-tile dashboard-tile-primary"><h3>Active Configuration</h3><p id="summary">Loading settings…</p></div><div class="dashboard-tile dashboard-tile-primary"><h3>Current Game</h3><p id="current-game" class="muted">Waiting for game information…</p></div><div class="dashboard-tile"><h3>MLB Feed Diagnostics <span id="feed-indicator" class="status-dot" aria-hidden="true"></span></h3><p id="feed-status" class="muted" role="status">MLB feed loading…</p></div><div class="dashboard-tile"><h3>Feed Refresh</h3><p id="last-refresh" class="muted">Last feed update: pending</p></div></div><h3>Rotation selection</h3><div class="dashboard-tile"><h3>Selected sport &amp; priority</h3><p id="dashboard-rotation" class="muted">Checking rotation…</p><p class="muted">Shows the scheduler selection, not scoring alerts, final handoffs, or supplemental screens.</p></div><h3>System overview</h3><div class="dashboard-grid"><div class="dashboard-tile"><h3>Host &amp; Service</h3><p id="dashboard-host" class="muted" role="status">Checking device…</p></div><div class="dashboard-tile"><h3>Hardware &amp; Resources</h3><p id="dashboard-hardware" class="muted">Checking hardware…</p></div></div><h3>Configured sports</h3><p class="muted">Read-only configuration summary. Feed activity is shown only when available.</p><p id="dashboard-sports-summary" class="muted" role="status">Checking sport feed health…</p><div id="dashboard-sports" class="sports-overview-grid" aria-live="polite">Loading sports…</div><div class="dashboard-actions"><div><h3>Management</h3><p class="muted">Configuration and service actions live on their dedicated pages.</p></div><button type="button" onclick="showPage('system')">System Details</button><button type="button" onclick="showPage('sports')">Sports &amp; Rotation</button></div><details class="dashboard-maintenance"><summary>Maintenance tools (restart, export and import)</summary><div class="dashboard-actions"><div><h3>Scoreboard controls</h3><p class="muted">Board view updates independently every second. Restarting shows the startup splash without rebooting the Pi.</p></div><button type="button" id="restart-scoreboard" onclick="restartScoreboard()">Restart Scoreboard</button></div><p id="restart-status" class="muted" role="status" aria-live="polite"></p><div class="dashboard-actions"><div><h3>Portable Configuration Backup</h3><p class="muted">Download application settings and team colors. Hardware, Wi-Fi and credentials are excluded.</p></div><button type="button" id="download-backup" onclick="downloadBackup()">Download Backup</button></div><p id="backup-status" class="muted" role="status" aria-live="polite"></p><div class="dashboard-actions"><div><h3>Import Portable Backup</h3><p class="muted">Choose a ZIP, preview the changes, then explicitly restore selected sections. Device settings stay local.</p><input id="import-backup-file" type="file" accept=".zip,application/zip" onchange="previewBackup()"/></div></div><div id="import-backup-preview" class="muted" role="status" aria-live="polite"></div><button type="button" id="apply-backup" onclick="applyBackup()" hidden>Restore Selected Sections</button></details></section><section data-page="sports" hidden><h2>Sports &amp; Rotation</h2><p class="muted">Manage active leagues, configure favorites, and review per-sport timing without scrolling through every team.</p><div class="sports-subnav" role="group" aria-label="Sports configuration views"><button type="button" data-sports-view="overview" onclick="showSportsView('overview')">Overview</button><button type="button" data-sports-view="configure" onclick="showSportsView('configure')">Configure Sport</button><button type="button" data-sports-view="rotation" onclick="showSportsView('rotation')">Rotation</button></div><div id="sports-overview" class="sports-view"><h3>Available sports</h3><div class="sports-overview-grid"><button type="button" class="sport-choice" onclick="selectSport('mlb')"><strong>MLB</strong><span id="sport-state-mlb">Configure →</span></button><button type="button" class="sport-choice" onclick="selectSport('nhl')"><strong>NHL</strong><span id="sport-state-nhl">Configure →</span></button><button type="button" class="sport-choice" onclick="selectSport('nba')"><strong>NBA</strong><span id="sport-state-nba">Configure →</span></button><button type="button" class="sport-choice" onclick="selectSport('wnba')"><strong>WNBA</strong><span id="sport-state-wnba">Configure →</span></button><button type="button" class="sport-choice" onclick="selectSport('nfl')"><strong>NFL</strong><span id="sport-state-nfl">Configure →</span></button><button type="button" class="sport-choice" onclick="selectSport('mls')"><strong>MLS</strong><span id="sport-state-mls">Configure →</span></button><button type="button" class="sport-choice" onclick="selectSport('nwsl')"><strong>NWSL</strong><span id="sport-state-nwsl">Configure →</span></button><button type="button" class="sport-choice" onclick="selectSport('english')"><strong>English Football</strong><span id="sport-state-english">Configure →</span></button></div><p class="muted">Choose a sport to edit its settings. Enable and disable sports within Configure Sport.</p></div><div id="sports-configure" class="sports-view" hidden><label for="sport-picker">Sport to configure</label> <select id="sport-picker" onchange="selectSport(this.value)"><option value="mlb">MLB</option><option value="nhl">NHL</option><option value="nba">NBA</option><option value="wnba">WNBA</option><option value="nfl">NFL</option><option value="mls">MLS</option><option value="nwsl">NWSL</option><option value="english">English Football</option></select><div class="sport-config-panel" data-sport-panel="mlb" hidden><fieldset class="favorite-fieldset"><legend>MLB configuration</legend><p><label><input type="checkbox" id="mlb-enabled"> Enable MLB</label></p><h3>MLB standings divisions</h3><p class="muted">Select divisions for standings pages. Independent of MLB game coverage; requires Standings Pages enabled under Content/News.</p><div id="mlb-standings-divisions" class="favorite-team-grid"><label><input type="checkbox" value="AL_EAST"> AL East</label><label><input type="checkbox" value="AL_CENTRAL"> AL Central</label><label><input type="checkbox" value="AL_WEST"> AL West</label><label><input type="checkbox" value="NL_EAST"> NL East</label><label><input type="checkbox" value="NL_CENTRAL"> NL Central</label><label><input type="checkbox" value="NL_WEST"> NL West</label></div><h3>Favorite MLB teams</h3><p class="muted">Select one or more teams. Games featuring any favorite will be included.</p><div id="favorite-teams" class="favorite-team-grid"><label><input type="checkbox" value="ARI"> Arizona Diamondbacks</label><label><input type="checkbox" value="ATL"> Atlanta Braves</label><label><input type="checkbox" value="BAL"> Baltimore Orioles</label><label><input type="checkbox" value="BOS"> Boston Red Sox</label><label><input type="checkbox" value="CHC"> Chicago Cubs</label><label><input type="checkbox" value="CWS"> Chicago White Sox</label><label><input type="checkbox" value="CIN"> Cincinnati Reds</label><label><input type="checkbox" value="CLE"> Cleveland Guardians</label><label><input type="checkbox" value="COL"> Colorado Rockies</label><label><input type="checkbox" value="DET"> Detroit Tigers</label><label><input type="checkbox" value="HOU"> Houston Astros</label><label><input type="checkbox" value="KCR"> Kansas City Royals</label><label><input type="checkbox" value="LAA"> Los Angeles Angels</label><label><input type="checkbox" value="LAD"> Los Angeles Dodgers</label><label><input type="checkbox" value="MIA"> Miami Marlins</label><label><input type="checkbox" value="MIL"> Milwaukee Brewers</label><label><input type="checkbox" value="MIN"> Minnesota Twins</label><label><input type="checkbox" value="NYM"> New York Mets</label><label><input type="checkbox" value="NYY"> New York Yankees</label><label><input type="checkbox" value="OAK"> Athletics</label><label><input type="checkbox" value="PHI"> Philadelphia Phillies</label><label><input type="checkbox" value="PIT"> Pittsburgh Pirates</label><label><input type="checkbox" value="SDP"> San Diego Padres</label><label><input type="checkbox" value="SFG"> San Francisco Giants</label><label><input type="checkbox" value="SEA"> Seattle Mariners</label><label><input type="checkbox" value="STL"> St. Louis Cardinals</label><label><input type="checkbox" value="TBR"> Tampa Bay Rays</label><label><input type="checkbox" value="TEX"> Texas Rangers</label><label><input type="checkbox" value="TOR"> Toronto Blue Jays</label><label><input type="checkbox" value="WSN"> Washington Nationals</label></div><p id="favorite-summary" class="muted" aria-live="polite"></p><p><label>MLB game selection <select id="mode"><option value="favorite">Favorites only</option><option value="fallback">Favorites, otherwise all</option><option value="all">All games</option></select></label></p><p id="mode-help" class="muted" aria-live="polite"></p><p><label>MLB rotation seconds <input id="rotation" type="number" min="1" max="3600" value="12"></label> <label>MLB feed refresh seconds <input id="refresh" type="number" min="1" max="3600" value="60"></label></p><h3>MLB live screen rotation</h3><p class="muted">Percent of each live game interval. Last Play uses the remaining time. Classic must be at least 1%.</p><p><label>Classic % <input id="live-classic" type="number" min="1" max="100" step="1" value="50"></label> <label>Matchup % <input id="live-matchup" type="number" min="0" max="99" step="1" value="25"></label></p><p id="live-play-share" class="muted" aria-live="polite">Last Play: 25%</p></fieldset></div><div class="sport-config-panel" data-sport-panel="nhl" hidden><fieldset class="favorite-fieldset"><legend>NHL configuration</legend>
<p><label><input type="checkbox" id="nhl-enabled"> Enable NHL</label></p>
<h3>NHL standings</h3><p class="muted">Select divisions and Wild Card races for idle-time standings. Enable standings globally under Content/News.</p><div id="nhl-standings-divisions" class="favorite-team-grid"><label><input type="checkbox" value="Atlantic"> Atlantic</label><label><input type="checkbox" value="Metropolitan"> Metropolitan</label><label><input type="checkbox" value="Central"> Central</label><label><input type="checkbox" value="Pacific"> Pacific</label></div><h3>NHL Wild Card standings</h3><p class="muted">Choose conference Wild Card tables independently. Each displays the five leading contenders.</p><div id="nhl-standings-wild-cards" class="favorite-team-grid"><label><input type="checkbox" value="Eastern_Wild_Card"> Eastern Conference</label><label><input type="checkbox" value="Western_Wild_Card"> Western Conference</label></div><h3>Favorite NHL teams</h3><p class="muted">Select one or more teams, just like MLB.</p><p><button type="button" onclick="setNHLFavorites(NHL_TEAMS.map(team=>team[0]))">Select all</button> <button type="button" onclick="setNHLFavorites([])">Clear all</button></p><div id="nhl-teams" class="favorite-team-grid"><label><input type="checkbox" value="ANA"> Anaheim Ducks</label><label><input type="checkbox" value="BOS"> Boston Bruins</label><label><input type="checkbox" value="BUF"> Buffalo Sabres</label><label><input type="checkbox" value="CGY"> Calgary Flames</label><label><input type="checkbox" value="CAR"> Carolina Hurricanes</label><label><input type="checkbox" value="CHI"> Chicago Blackhawks</label><label><input type="checkbox" value="COL"> Colorado Avalanche</label><label><input type="checkbox" value="CBJ"> Columbus Blue Jackets</label><label><input type="checkbox" value="DAL"> Dallas Stars</label><label><input type="checkbox" value="DET"> Detroit Red Wings</label><label><input type="checkbox" value="EDM"> Edmonton Oilers</label><label><input type="checkbox" value="FLA"> Florida Panthers</label><label><input type="checkbox" value="LAK"> Los Angeles Kings</label><label><input type="checkbox" value="MIN"> Minnesota Wild</label><label><input type="checkbox" value="MTL"> Montréal Canadiens</label><label><input type="checkbox" value="NSH"> Nashville Predators</label><label><input type="checkbox" value="NJD"> New Jersey Devils</label><label><input type="checkbox" value="NYI"> New York Islanders</label><label><input type="checkbox" value="NYR"> New York Rangers</label><label><input type="checkbox" value="OTT"> Ottawa Senators</label><label><input type="checkbox" value="PHI"> Philadelphia Flyers</label><label><input type="checkbox" value="PIT"> Pittsburgh Penguins</label><label><input type="checkbox" value="SJS"> San Jose Sharks</label><label><input type="checkbox" value="SEA"> Seattle Kraken</label><label><input type="checkbox" value="STL"> St. Louis Blues</label><label><input type="checkbox" value="TBL"> Tampa Bay Lightning</label><label><input type="checkbox" value="TOR"> Toronto Maple Leafs</label><label><input type="checkbox" value="UTA"> Utah Mammoth</label><label><input type="checkbox" value="VAN"> Vancouver Canucks</label><label><input type="checkbox" value="VGK"> Vegas Golden Knights</label><label><input type="checkbox" value="WSH"> Washington Capitals</label><label><input type="checkbox" value="WPG"> Winnipeg Jets</label></div><p id="nhl-favorite-summary" class="muted" aria-live="polite"></p>
<p><label>NHL game selection <select id="nhl-mode"><option value="favorite">Favorites only</option><option value="fallback">Favorites, otherwise all</option><option value="all">All games</option></select></label></p><p id="nhl-mode-help" class="muted" aria-live="polite"></p>
<p><label>NHL rotation seconds <input id="nhl-rotation" type="number" min="5" max="3600" value="12"></label>
<label>NHL feed refresh seconds <input id="nhl-refresh" type="number" min="5" max="3600" value="60"></label></p>
</fieldset></div><div class="sport-config-panel" data-sport-panel="nba" hidden><fieldset class="favorite-fieldset"><legend>NBA configuration</legend><p><label><input type="checkbox" id="nba-enabled"> Enable NBA</label></p><h3>NBA conference standings</h3><p class="muted">Select idle-time conference tables. Global standings controls are under Content/News.</p><div id="nba-standings-conferences" class="favorite-team-grid"><label><input type="checkbox" value="Eastern"> Eastern Conference</label><label><input type="checkbox" value="Western"> Western Conference</label></div><h3>Favorite NBA teams</h3><div id="nba-teams" class="favorite-team-grid"><label><input type="checkbox" value="ATL"> Atlanta Hawks</label><label><input type="checkbox" value="BOS"> Boston Celtics</label><label><input type="checkbox" value="BKN"> Brooklyn Nets</label><label><input type="checkbox" value="CHA"> Charlotte Hornets</label><label><input type="checkbox" value="CHI"> Chicago Bulls</label><label><input type="checkbox" value="CLE"> Cleveland Cavaliers</label><label><input type="checkbox" value="DAL"> Dallas Mavericks</label><label><input type="checkbox" value="DEN"> Denver Nuggets</label><label><input type="checkbox" value="DET"> Detroit Pistons</label><label><input type="checkbox" value="GSW"> Golden State Warriors</label><label><input type="checkbox" value="HOU"> Houston Rockets</label><label><input type="checkbox" value="IND"> Indiana Pacers</label><label><input type="checkbox" value="LAC"> LA Clippers</label><label><input type="checkbox" value="LAL"> Los Angeles Lakers</label><label><input type="checkbox" value="MEM"> Memphis Grizzlies</label><label><input type="checkbox" value="MIA"> Miami Heat</label><label><input type="checkbox" value="MIL"> Milwaukee Bucks</label><label><input type="checkbox" value="MIN"> Minnesota Timberwolves</label><label><input type="checkbox" value="NOP"> New Orleans Pelicans</label><label><input type="checkbox" value="NYK"> New York Knicks</label><label><input type="checkbox" value="OKC"> Oklahoma City Thunder</label><label><input type="checkbox" value="ORL"> Orlando Magic</label><label><input type="checkbox" value="PHI"> Philadelphia 76ers</label><label><input type="checkbox" value="PHX"> Phoenix Suns</label><label><input type="checkbox" value="POR"> Portland Trail Blazers</label><label><input type="checkbox" value="SAC"> Sacramento Kings</label><label><input type="checkbox" value="SAS"> San Antonio Spurs</label><label><input type="checkbox" value="TOR"> Toronto Raptors</label><label><input type="checkbox" value="UTA"> Utah Jazz</label><label><input type="checkbox" value="WSH"> Washington Wizards</label></div><p><label>NBA game selection <select id="nba-mode"><option value="favorite">Favorites only</option><option value="fallback">Favorites, otherwise all</option><option value="all">All games</option></select></label></p><p id="nba-mode-help" class="muted" aria-live="polite"></p><p><label>NBA rotation seconds <input id="nba-rotation" type="number" min="5" max="3600" value="12"></label> <label>NBA feed refresh seconds <input id="nba-refresh" type="number" min="5" max="3600" value="60"></label></p></fieldset></div><div class="sport-config-panel" data-sport-panel="wnba" hidden><fieldset class="favorite-fieldset"><legend>WNBA configuration</legend><p><label><input type="checkbox" id="wnba-enabled"> Enable WNBA</label></p><p><label><input type="checkbox" id="wnba-standings-enabled"> Show WNBA standings when idle</label></p><h3>Favorite WNBA teams</h3><div id="wnba-teams" class="favorite-team-grid"><label><input type="checkbox" value="ATL"> Atlanta Dream</label><label><input type="checkbox" value="CHI"> Chicago Sky</label><label><input type="checkbox" value="CON"> Connecticut Sun</label><label><input type="checkbox" value="DAL"> Dallas Wings</label><label><input type="checkbox" value="GSV"> Golden State Valkyries</label><label><input type="checkbox" value="IND"> Indiana Fever</label><label><input type="checkbox" value="LVA"> Las Vegas Aces</label><label><input type="checkbox" value="LAS"> Los Angeles Sparks</label><label><input type="checkbox" value="MIN"> Minnesota Lynx</label><label><input type="checkbox" value="NYL"> New York Liberty</label><label><input type="checkbox" value="PHX"> Phoenix Mercury</label><label><input type="checkbox" value="SEA"> Seattle Storm</label><label><input type="checkbox" value="WAS"> Washington Mystics</label><label><input type="checkbox" value="POR"> Portland Fire</label><label><input type="checkbox" value="TOR"> Toronto Tempo</label></div><p><label>WNBA game selection <select id="wnba-mode"><option value="favorite">Favorites only</option><option value="fallback">Favorites, otherwise all</option><option value="all">All games</option></select></label></p><p id="wnba-mode-help" class="muted" aria-live="polite"></p><p><label>WNBA rotation seconds <input id="wnba-rotation" type="number" min="5" max="3600" value="12"></label> <label>WNBA feed refresh seconds <input id="wnba-refresh" type="number" min="5" max="3600" value="60"></label></p></fieldset></div><div class="sport-config-panel" data-sport-panel="nfl" hidden><fieldset class="favorite-fieldset"><legend>NFL configuration</legend>
<p><label><input type="checkbox" id="nfl-enabled"> Enable NFL</label></p>
<h3>NFL division standings</h3><p class="muted">Choose divisions for idle-time standings. Enable Standings Pages under Content &amp; News.</p><div id="nfl-standings-divisions" class="favorite-team-grid"><label><input type="checkbox" value="AFC East"> AFC East</label><label><input type="checkbox" value="AFC North"> AFC North</label><label><input type="checkbox" value="AFC South"> AFC South</label><label><input type="checkbox" value="AFC West"> AFC West</label><label><input type="checkbox" value="NFC East"> NFC East</label><label><input type="checkbox" value="NFC North"> NFC North</label><label><input type="checkbox" value="NFC South"> NFC South</label><label><input type="checkbox" value="NFC West"> NFC West</label></div><h3>Favorite NFL teams</h3>
<div id="nfl-teams" class="favorite-team-grid"></div>
<p><label>NFL game selection <select id="nfl-mode"><option value="favorite">Favorites only</option><option value="fallback">Favorites, otherwise all</option><option value="all">All games</option></select></label></p><p id="nfl-mode-help" class="muted" aria-live="polite"></p>
<p><label>NFL rotation seconds <input id="nfl-rotation" type="number" min="5" max="3600" value="12"></label>
<label>NFL feed refresh seconds <input id="nfl-refresh" type="number" min="5" max="3600" value="60"></label></p></fieldset></div><div class="sport-config-panel" data-sport-panel="mls" hidden><fieldset class="favorite-fieldset"><legend>MLS configuration</legend><p><label><input type="checkbox" id="mls-enabled"> Enable MLS</label></p><h3>MLS standings conferences</h3><p class="muted">Select conferences for idle-time standings. Enable Standings Pages under Content &amp; News.</p><div id="mls-standings-conferences" class="favorite-team-grid"><label><input type="checkbox" value="Eastern Conference"> Eastern Conference</label><label><input type="checkbox" value="Western Conference"> Western Conference</label></div><h3>Favorite MLS teams</h3><p class="muted">Select one or more teams. Games featuring your favorites are prioritized.</p><div id="mls-teams" class="favorite-team-grid"></div><p><label>Game selection <select id="mls-mode"><option value="favorite">Favorites only</option><option value="fallback">Favorites, otherwise all</option><option value="all">All matches</option></select></label></p><p id="mls-mode-help" class="muted" aria-live="polite"></p><p><label>Data source <select id="mls-provider"><option value="league_first">League first, ESPN fallback</option><option value="espn_only">ESPN only</option><option value="league_only">League only (requires native endpoint)</option></select></label></p><p><label>Rotation seconds <input id="mls-rotation" type="number" min="5" max="3600" value="12"></label><label>Refresh seconds <input id="mls-refresh" type="number" min="5" max="3600" value="60"></label></p></fieldset></div><div class="sport-config-panel" data-sport-panel="nwsl" hidden><fieldset class="favorite-fieldset"><legend>NWSL configuration</legend><p><label><input type="checkbox" id="nwsl-enabled"> Enable NWSL</label></p><p><label><input type="checkbox" id="nwsl-standings-enabled"> Show NWSL standings when idle</label></p><h3>Favorite NWSL teams</h3><p class="muted">Select one or more teams. Games featuring your favorites are prioritized.</p><div id="nwsl-teams" class="favorite-team-grid"></div><p><label>Game selection <select id="nwsl-mode"><option value="favorite">Favorites only</option><option value="fallback">Favorites, otherwise all</option><option value="all">All matches</option></select></label></p><p id="nwsl-mode-help" class="muted" aria-live="polite"></p><p><label>Data source <select id="nwsl-provider"><option value="league_first">League first, ESPN fallback</option><option value="espn_only">ESPN only</option><option value="league_only">League only (requires native endpoint)</option></select></label></p><p><label>Rotation seconds <input id="nwsl-rotation" type="number" min="5" max="3600" value="12"></label><label>Refresh seconds <input id="nwsl-refresh" type="number" min="5" max="3600" value="60"></label></p></fieldset></div><div class="sport-config-panel" data-sport-panel="english" hidden><fieldset class="favorite-fieldset"><legend>English football configuration</legend><p><label><input type="checkbox" id="english-enabled"> Enable English football</label></p><h3>Divisions</h3><div id="english-leagues" class="favorite-team-grid"><label><input type="checkbox" value="EPL"> Premier League</label><label><input type="checkbox" value="CHAMPIONSHIP"> Championship</label><label><input type="checkbox" value="LEAGUE_ONE"> League One</label><label><input type="checkbox" value="LEAGUE_TWO"> League Two</label></div><p id="english-game-coverage-summary" class="muted" aria-live="polite"></p><h3>Standings pages</h3><p class="muted">Choose which English divisions appear in idle-time standings. Game coverage is controlled separately above.</p><div id="english-standings-leagues" class="favorite-team-grid"><label><input type="checkbox" value="EPL"> Premier League</label><label><input type="checkbox" value="CHAMPIONSHIP"> Championship</label><label><input type="checkbox" value="LEAGUE_ONE"> League One</label><label><input type="checkbox" value="LEAGUE_TWO"> League Two</label></div><p id="english-standings-coverage-summary" class="muted" aria-live="polite"></p><h3>Favorite clubs</h3><p><label>Search clubs <input id="english-team-search" type="search" placeholder="Search all four divisions" oninput="filterEnglishClubs()"></label></p><div id="english-teams" class="favorite-team-grid"></div><p id="english-team-filter-summary" class="muted" role="status" aria-live="polite"></p><p id="english-team-status" class="muted">Loading club directory…</p><p><label>Game selection <select id="english-mode"><option value="favorite">Favorites only</option><option value="fallback">Favorites, otherwise all</option><option value="all">All matches</option></select></label></p><p id="english-mode-help" class="muted" aria-live="polite"></p><p><label>Rotation seconds <input id="english-rotation" type="number" min="5" max="3600" value="12"></label><label>Refresh seconds <input id="english-refresh" type="number" min="5" max="3600" value="60"></label></p><p class="muted">ESPN is the current data source. Club favorites remain selected when a club changes division.</p></fieldset></div><div id="sports-rotation" class="sports-view" hidden><h3>Rotation behavior</h3><p>Each sport currently has its own game rotation and feed refresh timing. Use Configure Sport to adjust those values for the selected league.</p><div class="rotation-summary" id="sports-rotation-summary"></div><p class="muted">Shared clock, weather, and countdown rotation settings remain under Display. A separate global rotation priority control is not supported by the current configuration schema.</p></div><div class="sports-savebar"><button id="save-settings">Save Sport Settings</button><span id="settings-status" role="status" aria-live="polite"></span></div></section><section data-page="display" hidden><h2>Shared Display Settings</h2><fieldset class="favorite-fieldset"><legend>Time &amp; Weather</legend><label><input id="clock-enabled" type="checkbox"> Enable clock rotation</label><label>Time zone <select id="clock-timezone"><option value="America/New_York">Eastern (ET)</option><option value="America/Chicago">Central (CT)</option><option value="America/Denver">Mountain (MT)</option><option value="America/Phoenix">Arizona (MST, no DST)</option><option value="America/Los_Angeles">Pacific (PT)</option><option value="America/Anchorage">Alaska (AKT)</option><option value="Pacific/Honolulu">Hawaii (HST)</option><option value="UTC">UTC</option><option value="Europe/London">London (UK)</option><option value="Europe/Paris">Central Europe</option><option value="Asia/Tokyo">Japan</option><option value="Australia/Sydney">Sydney</option></select></label><label>Time format <select id="clock-format"><option value="12h">12-hour</option><option value="24h">24-hour</option></select></label><label>Clock every N non-live slots <input id="clock-interval" type="number" min="1" max="20" value="5"></label><label><input id="weather-enabled" type="checkbox"> Enable weather display</label><label>Weather location <input id="weather-location" type="text" placeholder="City or ZIP"></label><label>Temperature unit <select id="weather-unit"><option value="fahrenheit">Fahrenheit</option><option value="celsius">Celsius</option></select></label><label>Weather provider <select id="weather-provider"><option value="open-meteo">Open-Meteo (no key)</option><option value="openweathermap">OpenWeatherMap (API key)</option></select></label><label>OpenWeatherMap API key <input id="weather-key" type="password" autocomplete="new-password" placeholder="Leave blank to keep saved key"></label><button type="button" onclick="saveClockSettings()">Save Time &amp; Weather</button><p id="clock-status" role="status"></p></fieldset><fieldset class="favorite-fieldset"><legend>Season Opening Countdown</legend><p class="muted">Optional shared countdown. Enter an opening date with its timezone offset, such as 2027-03-25T13:00:00-04:00. Disabled until configured.</p><p><label><input id="countdown-enabled" type="checkbox"> Enable countdown</label></p><p><label>Sport <select id="countdown-sport"><option value="mlb">MLB</option><option value="nba">NBA</option><option value="nfl">NFL</option><option value="nhl">NHL</option><option value="mls">MLS</option><option value="efl">EFL</option></select></label> <label>Season <input id="countdown-season" type="text" placeholder="2027"></label></p><p><label>Date source <select id="countdown-source"><option value="manual">Manual date</option><option value="automatic">Automatic MLB schedule</option></select></label></p><p><label>Opening date/time (ISO with timezone) <input id="countdown-opening" type="text" placeholder="2027-03-25T13:00:00-04:00"></label></p><p><label>Target <select id="countdown-target"><option value="league">League opening</option><option value="favorite">Favorite team opening</option></select></label> <label>Team code <input id="countdown-team" type="text" placeholder="ATL"></label></p><p><label>Display <select id="countdown-window"><option value="offseason">Offseason only</option><option value="within_days">Within N days</option><option value="always">Always when no live game</option></select></label> <label>Days <input id="countdown-days" type="number" min="1" max="366" value="30"></label></p><button type="button" onclick="saveCountdown()">Save Countdown</button><p id="countdown-status" role="status" aria-live="polite"></p><p id="countdown-feed-status" class="muted" role="status" aria-live="polite">Schedule status not checked.</p><button type="button" onclick="refreshCountdownStatus()">Check Schedule Status</button></fieldset></section><section data-page="wifi" hidden><h2>Wi-Fi & Hotspot</h2><p id="wifi-recovery-readiness" class="muted" role="status">Checking recovery protection…</p><p id="wifi-info">Loading…</p><h4>Saved Wi-Fi connections</h4><div id="wifi-profiles" class="grid"><p class="muted">Loading saved profiles…</p></div><button type="button" onclick="refreshWifi()">Refresh Wi-Fi</button> <button type="button" onclick="scanWifi()">Scan Networks</button><p id="wifi-scan-status" class="muted" role="status" aria-live="polite">Click Scan Networks to list nearby access points.</p><div id="wifi-networks" class="grid"></div><div id="wifi-selection" hidden><h4>Selected network: <span id="wifi-selected-name"></span></h4><p id="wifi-selected-security"></p><label>Network password <input id="wifi-password" type="password" autocomplete="off" minlength="8" maxlength="63"></label><p id="wifi-connect-note" class="muted">Network switching requires the privileged helper and recovery worker. Keep Ethernet connected during initial testing.</p><button type="button" onclick="connectWifi()">Connect Wi-Fi</button><p id="wifi-connect-result" role="status"></p></div><h4>Hotspot Settings</h4><p class="muted">Change the password for Universal-LED-Setup. Changes take effect the next time the hotspot starts.</p><label>New hotspot password <input id="hotspot-password" type="password" minlength="8" maxlength="63" autocomplete="new-password"></label> <label>Confirm password <input id="hotspot-confirm" type="password" minlength="8" maxlength="63" autocomplete="new-password"></label> <button type="button" onclick="saveHotspotPassword()">Save Hotspot Password</button><p id="hotspot-result" role="status"></p></section><section data-page="matrix-settings" hidden><h2>Physical Matrix Settings</h2><p class="muted">Hardware changes require restarting only uls-matrix.service. Saving does not restart the hardware automatically.</p><div class="grid"><label class="item"><input type="checkbox" id="matrix-enabled"> Enable physical matrix output</label><label class="item">Brightness (1–100%) <input type="number" id="matrix-brightness" min="1" max="100" value="40"></label><label class="item">GPIO slowdown (0–10) <input type="number" id="matrix-slowdown" min="0" max="10" value="4"></label><label class="item">Hardware mapping <select id="matrix-mapping"><option value="adafruit-hat">Adafruit HAT</option><option value="adafruit-hat-pwm">Adafruit HAT PWM</option><option value="regular">Regular</option><option value="compute-module">Compute Module</option></select></label><label class="item">Frame poll interval (seconds) <input type="number" id="matrix-interval" min="0.05" max="10" step="0.05" value="0.2"></label></div><p><button type="button" onclick="saveMatrixSettings()">Save Matrix Settings</button> <button type="button" onclick="applyMatrixSettings()">Apply Saved Settings</button></p><p id="matrix-service-state" class="muted" role="status">Checking matrix service…</p><p id="matrix-settings-status" role="status" aria-live="polite"></p></section><section data-page="plugins" hidden><div class="page-heading"><div><p class="page-kicker">Extensions</p><h2>Plugin Manager</h2><p class="muted">Install, configure and manage optional 64×32 scoreboard screens.</p></div><button type="button" onclick="loadPluginInventory()">Refresh plugins</button></div>
<div class="dashboard-grid">
<div class="dashboard-tile"><h3>Installed plugins</h3><p class="muted">Manage active plugins. Disable a plugin before uninstalling it.</p><div id="plugin-inventory" role="status" aria-live="polite">Loading installed plugins…</div><div id="plugin-settings-editor" role="region" aria-label="Plugin settings"></div></div>
<div class="dashboard-tile"><h3>Install from GitHub</h3><p class="muted">For custom plugins not listed below. Review never installs or runs code.</p><label for="plugin-github-url">GitHub plugin URL</label><input id="plugin-github-url" type="url" placeholder="https://github.com/owner/repo"><button type="button" onclick="reviewGithubPlugin()">Review plugin</button><pre id="plugin-github-review" role="status" style="white-space:pre-wrap;overflow-wrap:anywhere"></pre><button id="plugin-github-install" type="button" onclick="installReviewedGithubPlugin()" hidden>Install reviewed plugin (disabled)</button><button id="plugin-github-update" type="button" onclick="updateReviewedGithubPlugin()" hidden>Update reviewed plugin</button></div>
<div class="dashboard-tile"><h3>Available plugins</h3><p class="muted">Official ULS plugins, maintained separately from Core. Review a source before installation.</p><div id="plugin-available" role="status" aria-live="polite">Loading available plugins…</div></div>
<div class="dashboard-tile"><h3>Bundled examples</h3><p class="muted">Examples included with ULS Core, independent of the official plugin catalog.</p><div id="plugin-bundled"><p>Hello World v0.1.0 · 64×32 reference screen</p><p id="plugin-bundled-state" class="muted">Checking installation…</p><button id="plugin-bundled-install" type="button" onclick="installBundledHelloWorld()" hidden>Install Hello World</button><p id="plugin-bundled-install-status" role="status"></p></div><button type="button" onclick="previewHelloWorld()">Preview Hello World</button><canvas id="plugin-hello-preview" width="64" height="32" style="width:256px;max-width:100%;aspect-ratio:2/1;image-rendering:pixelated;background:#000" aria-label="Hello World 64 by 32 plugin preview" hidden></canvas><p id="plugin-hello-status" role="status"></p></div>
</div></section><section data-page="system" hidden><h2>System</h2><h3>Software Updates</h3><p id="update-status" class="muted" role="status">Update status not checked.</p><label for="update-branch">Release branch</label> <select id="update-branch" onchange="updateBranchChanged()"><option value="">Check for branches…</option></select><label><input type="checkbox" id="update-show-all" onchange="renderUpdateBranches()"> Show all branches (including older releases)</label> <button type="button" onclick="checkSoftwareUpdate()">Check for Updates</button> <button type="button" id="install-update" onclick="installSoftwareUpdate()" disabled>Install Update</button><button type="button" id="copy-update-log" onclick="copyUpdateLog()">Copy Log</button><pre id="update-log" style="white-space:pre-wrap;overflow-wrap:anywhere;max-height:220px;overflow:auto"></pre><p id="system-info">Checking server information…</p><div id="pi-info" class="grid"><p class="muted">Loading Raspberry Pi diagnostics…</p></div><p class="muted">Service status is read-only. Hardware output and remote service controls are not enabled.</p></section><div data-page="colors" hidden><section><h2>64 × 32 Live Preview</h2><canvas id="matrix" width="64" height="32"></canvas>
<p class="muted">Changes preview immediately. Saving is optional.</p><label for="preview-team">Preview favorite team: </label><select id="preview-team"></select><span id="dirty" role="status">All changes saved</span></section>
<section><h2>Scoreboard Colors</h2><p class="muted">General display text, accents, separators and status colors.</p><div id="scoreboard" class="grid"></div></section>
<section><h2>NHL Team Colors</h2><p class="muted">NHL colors are stored separately from MLB. Use the same RGB editor for both sports.</p><label for="nhl-edit-team">NHL team to edit</label> <select id="nhl-edit-team"></select><div id="nhl-color-editor" class="grid"></div><button type="button" id="nhl-save-color">Save NHL Color</button> <button type="button" id="nhl-reset-color">Reset NHL Color</button> <span id="nhl-color-status" role="status"></span></section>
<section><h2>MLB Team Colors</h2><p class="muted">Edit one team at a time, using the same compact controls as NHL. All other team colors remain unchanged.</p><label for="edit-team">MLB team to edit</label> <select id="edit-team"></select><div id="teams" class="grid"></div><button id="mlb-save-color" type="button">Save MLB Color</button> <button id="mlb-reset-color" type="button">Reset MLB Color</button> <span id="mlb-color-status" role="status"></span></section>
<section><button id="save">Save Color Settings</button> <button id="cancel" type="button">Cancel Changes</button> <button id="reset" type="button">Reset Selected Color</button> <span id="status" role="status"></span>
<p class="muted">Available on your trusted LAN. Backups are created before overwriting existing files.</p></section></div><div data-page="news" hidden><section><h2>Content &amp; News Sources</h2><p class="muted">Configure RSS or Atom feeds for future ticker use. Automatic and custom feeds display during available news rotation slots.</p><fieldset class="favorite-fieldset"><legend>Automatic Sports News</legend><p class="muted">Enable headlines separately for each sport. News appears during non-live rotation slots when that sport is enabled.</p><label><input type="checkbox" id="mlb-news-enabled"> MLB official headlines</label> <label><input type="checkbox" id="nhl-news-enabled"> NHL headlines</label> <label><input type="checkbox" id="nba-news-enabled"> NBA headlines</label> <label><input type="checkbox" id="wnba-news-enabled"> WNBA headlines</label> <label><input type="checkbox" id="nfl-news-enabled"> NFL headlines</label> <label><input type="checkbox" id="mls-news-enabled"> MLS headlines</label> <label><input type="checkbox" id="nwsl-news-enabled"> NWSL headlines</label> <label><input type="checkbox" id="english-news-enabled"> Premier League headlines</label> <label><input type="checkbox" id="efl-news-enabled"> EFL Championship, League One &amp; League Two headlines</label> <button type="button" onclick="saveAutomaticNews()">Save Automatic News</button><p id="auto-news-status" role="status"></p></fieldset><fieldset class="favorite-fieldset"><legend>News Display Timing</legend><label>Show news every N non-live slots <input id="news-interval" type="number" min="1" max="20"></label> <label>Headline duration (seconds) <input id="news-duration" type="number" min="3" max="120"></label> <label>Scroll speed (characters/second) <input id="news-speed" type="number" min="1" max="15"></label> <button type="button" onclick="saveNewsTiming()">Save News Timing</button><p id="news-timing-status" role="status"></p></fieldset><fieldset class="favorite-fieldset"><legend>Scoring Alerts</legend><p>Briefly interrupt the board for confirmed scoring events from supported sports. Availability depends on each sport's event feed; favorite-team selections control priority and filtering.</p><label><input type="checkbox" id="scoring-alerts-enabled"> Enable scoring alerts</label><label>Announce scoring events for <select id="scoring-alerts-scope"><option value="favorites">Favorite teams only</option><option value="all">All enabled games</option></select></label><label>Alert duration (seconds) <input id="scoring-alerts-seconds" type="number" min="1" max="60" step="1"></label><button type="button" onclick="saveScoringAlerts()">Save Scoring Alerts</button><p id="scoring-alerts-status" role="status"></p></fieldset><fieldset class="favorite-fieldset"><legend>Game Delays &amp; Schedule Changes</legend><p>Choose when interrupted games appear. Live games remain the default priority.</p><label>Delayed games <select id="interruption-delayed"><option value="when_no_live">Show when no games are live</option><option value="hide">Hide</option><option value="always">Always show</option></select></label><label>Postponed games <select id="interruption-postponed"><option value="when_no_live">Show when no games are live</option><option value="hide">Hide</option><option value="always">Always show</option></select></label><label>Rescheduled games <select id="interruption-rescheduled"><option value="when_no_live">Show when no games are live</option><option value="hide">Hide</option><option value="always">Always show</option></select></label><label>Suspended games <select id="interruption-suspended"><option value="when_no_live">Show when no games are live</option><option value="hide">Hide</option><option value="always">Always show</option></select></label><button type="button" onclick="saveGameInterruptions()">Save Game Status Preferences</button><p id="game-interruptions-status" role="status"></p></fieldset><fieldset class="favorite-fieldset"><legend>Standings Pages</legend><p class="muted">Show cached standings only when no eligible games are available. Currently English football standings are supported; additional sport and division controls are being developed. Scoring alerts and live games always take priority.</p><p><label><input type="checkbox" id="standings-enabled"> Enable standings pages</label></p><div class="grid"><label>Page duration (seconds) <input type="number" id="standings-page-seconds" min="3" max="3600" step="1" value="12"></label><label>Refresh interval (seconds) <input type="number" id="standings-refresh-seconds" min="60" max="86400" step="1" value="900"></label></div><p><button type="button" onclick="saveStandingsSettings()">Save Standings Preferences</button></p><p id="standings-status" role="status"></p></fieldset><h3>Additional Custom Feeds</h3><div id="news-sources"></div><button type="button" id="news-add" onclick="addNewsSource()">Add Source</button> <button type="button" onclick="saveNewsSources()">Save News Sources</button> <p id="news-status" role="status"></p></section></div></main></div>
<script>
const token=__TOKEN__;
async function logout(){await fetch('/logout',{method:'POST',headers:{'X-Configurator-Token':token}});location.href='/login'}
let state=null,saved=null,dirty=false,selectedTeam='ATL',selected=null,settings=null;
const newsSettingsGroups={automatic:['mlb-news-enabled','nhl-news-enabled','nba-news-enabled','wnba-news-enabled','nfl-news-enabled','mls-news-enabled','nwsl-news-enabled','english-news-enabled','efl-news-enabled'],scoring:['scoring-alerts-enabled','scoring-alerts-scope','scoring-alerts-seconds'],timing:['news-interval','news-duration','news-speed'],interruptions:['interruption-delayed','interruption-postponed','interruption-rescheduled','interruption-suspended'],standings:['standings-enabled','standings-page-seconds','standings-refresh-seconds']};
const newsSettingsSaved={};
function newsGroupSnapshot(group){return JSON.stringify(newsSettingsGroups[group].map(id=>{const el=document.getElementById(id);return el?(el.type==='checkbox'?el.checked:el.value):null}))}
function newsGroupDirty(group){return Object.prototype.hasOwnProperty.call(newsSettingsSaved,group)&&newsSettingsSaved[group]!==newsGroupSnapshot(group)}
function newsSettingsDirty(){return Object.keys(newsSettingsGroups).some(newsGroupDirty)}
function newsGroupLoaded(group){newsSettingsSaved[group]=newsGroupSnapshot(group)}
function newsGroupCanLoad(group){return !newsGroupDirty(group)}
function newsGroupSaved(group){newsSettingsSaved[group]=newsGroupSnapshot(group)}
function discardNewsEdits(){
 newsSources=clone(newsSourcesSaved);newsSourcesDirty=false;
 for(const group of Object.keys(newsSettingsGroups))delete newsSettingsSaved[group];
}
async function previewHelloWorld(){
 const status=document.getElementById('plugin-hello-status');
 const canvas=document.getElementById('plugin-hello-preview');
 status.textContent='Rendering Hello World…';
 try{
  const response=await fetch('/api/plugins/hello-world/frame',{credentials:'same-origin',cache:'no-store'});
  if(!response.ok)throw new Error('Preview request failed (HTTP '+response.status+')');
  const frame=await response.json();
  if(frame.width!==64||frame.height!==32||!Array.isArray(frame.pixels)||frame.pixels.length!==2048)throw new Error('Invalid 64x32 frame');
  const ctx=canvas.getContext('2d'),pixels=ctx.createImageData(64,32);
  frame.pixels.forEach((rgb,i)=>{pixels.data[i*4]=rgb[0];pixels.data[i*4+1]=rgb[1];pixels.data[i*4+2]=rgb[2];pixels.data[i*4+3]=255});
  ctx.putImageData(pixels,0,0);canvas.hidden=false;status.textContent='Hello World example rendered. Live scoreboard unchanged.';
 }catch(error){status.textContent='Preview unavailable: '+error.message}
}
let reviewedGithubPlugin=null;
let reviewedGithubUpdate=null;
async function reviewInstalledPlugin(plugin){
 const target=document.getElementById('plugin-github-review');
 reviewedGithubUpdate=null;
 document.getElementById('plugin-github-update').hidden=true;
 target.textContent='Checking '+plugin.name+' for updates…';
 try{
  const response=await fetch('/api/plugins/github/review',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify({source:plugin.source})});
  const result=await response.json();
  if(!response.ok)throw new Error(result.error||'HTTP '+response.status);
  if(result.id!==plugin.id||result.source!==plugin.source)throw new Error('Plugin identity or reviewed source changed');
  if(result.commit.toLowerCase()===plugin.commit.toLowerCase()){
   target.textContent=plugin.name+' is already at the latest reviewed commit.';
   return;
  }
  reviewedGithubUpdate={...result,previousSource:plugin.installedSource||plugin.source};
  target.textContent=['Update available: '+plugin.name,'Installed version: '+plugin.version,'Reviewed version: '+result.version,'Installed commit: '+plugin.commit,'Proposed commit: '+result.commit,'Current source: '+(plugin.installedSource||plugin.source),'Reviewed source: '+result.source,(plugin.installedSource&&plugin.installedSource!==result.source?'Official source migration will be performed.':'Source unchanged.'),'Enabled state and saved settings will be preserved.'].join('\\n');
  document.getElementById('plugin-github-update').hidden=false;
  target.scrollIntoView({block:'nearest'});
 }catch(error){target.textContent='Update review failed for '+plugin.source+': '+error.message}
}
async function updateReviewedGithubPlugin(){
 const reviewed=reviewedGithubUpdate;
 if(!reviewed||!confirm('Update '+reviewed.name+' to pinned commit '+reviewed.commit+'? Existing enabled state and settings will be preserved.'))return;
 const target=document.getElementById('plugin-github-review');
 target.textContent='Updating reviewed plugin…';
 try{
  const response=await fetch('/api/plugins/github/update',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify({source:reviewed.source,commit:reviewed.commit,id:reviewed.id,previous_source:reviewed.previousSource,confirm:true})});
  const result=await response.json();
  if(!response.ok)throw new Error(result.error||'HTTP '+response.status);
  reviewedGithubUpdate=null;
  document.getElementById('plugin-github-update').hidden=true;
  target.textContent='Updated '+result.id+' to '+result.version+'. Saved settings and enabled state preserved.';
  await loadPluginInventory();
 }catch(error){target.textContent='Plugin update failed: '+error.message}
}
async function installReviewedGithubPlugin(){
 const reviewed=reviewedGithubPlugin;
 if(!reviewed||!confirm('Install '+reviewed.name+' v'+reviewed.version+' from pinned GitHub commit '+reviewed.commit+' as disabled?'))return;
 const target=document.getElementById('plugin-github-review');
 target.textContent='Installing reviewed commit…';
 try{
  const response=await fetch('/api/plugins/github/install',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify({source:reviewed.source,commit:reviewed.commit,id:reviewed.id,confirm:true})});
  const result=await response.json();
  if(!response.ok)throw new Error(result.error||'HTTP '+response.status);
  reviewedGithubPlugin=null;
  document.getElementById('plugin-github-install').hidden=true;
  target.textContent='Installed '+result.id+' v'+result.version+' (disabled).';
  await loadPluginInventory();
 }catch(error){target.textContent='Installation failed: '+error.message}
}
async function installBundledHelloWorld(){
 const target=document.getElementById('plugin-bundled-install-status');
 if(!confirm('Install bundled Hello World plugin as disabled?'))return;
 target.textContent='Installing Hello World…';
 try{
  const response=await fetch('/api/plugins/bundled/install',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify({id:'hello-world',confirm:true})});
  const result=await response.json();
  if(!response.ok)throw new Error(result.error||'HTTP '+response.status);
  target.textContent='Installed '+result.id+' v'+result.version+' (disabled).';
  await loadPluginInventory();
 }catch(error){target.textContent='Installation failed: '+error.message}
}
async function reviewGithubPlugin(){
 const target=document.getElementById('plugin-github-review');
 const source=document.getElementById('plugin-github-url').value.trim();
 reviewedGithubPlugin=null;
 document.getElementById('plugin-github-install').hidden=true;
 target.textContent='Reviewing repository…';
 try{
  const response=await fetch('/api/plugins/github/review',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify({source})});
  const result=await response.json();
  if(!response.ok)throw new Error(result.error||'HTTP '+response.status);
  reviewedGithubPlugin=result;
  document.getElementById('plugin-github-install').hidden=false;
  target.textContent=[result.name+' v'+result.version,result.description||'', 'ID: '+result.id,'Capabilities: '+result.capabilities.join(', '),'Source: '+result.source,'Pinned commit: '+result.commit,'Not installed. Review only.'].join('\\n');
 }catch(error){target.textContent='Review failed: '+error.message}
}
async function removePlugin(id){
 const target=document.getElementById('plugin-inventory');
 if(!confirm('Uninstall '+id+'? The installed package will be removed. Saved external data will be preserved. This cannot be undone without reinstalling.'))return;
 try{
  const response=await fetch('/api/plugins/uninstall',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-Configurator-Token':__TOKEN__},body:JSON.stringify({id,confirm:true})});
  const result=await response.json();
  if(!response.ok)throw new Error(result.error||'HTTP '+response.status);
  document.getElementById('plugin-settings-editor').replaceChildren();
  await loadPluginInventory();
 }catch(error){target.textContent='Uninstall failed: '+error.message}
}
async function setPluginEnabled(id,enabled){
 const target=document.getElementById('plugin-inventory');
 if(!confirm((enabled?'Enable ':'Disable ')+id+'?'))return;
 try{
  const response=await fetch('/api/plugins/enabled',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-Configurator-Token':__TOKEN__},body:JSON.stringify({id,enabled})});
  if(!response.ok){const error=await response.json();throw new Error(error.error||'HTTP '+response.status)}
  await loadPluginInventory();
 }catch(error){target.textContent='Plugin setting failed: '+error.message}
}
async function editPluginSettings(pluginId){
 const target=document.getElementById('plugin-settings-editor');
 if(!target)return;
 target.replaceChildren();
 target.textContent='Loading settings for '+pluginId+'…';
 try{
  const response=await fetch('/api/plugins/settings?id='+encodeURIComponent(pluginId),{credentials:'same-origin',cache:'no-store'});
  const data=await response.json();
  if(!response.ok)throw new Error(data.error||'HTTP '+response.status);
  target.replaceChildren();
  const title=document.createElement('h3');title.textContent='Settings: '+pluginId;target.appendChild(title);
  const form=document.createElement('form');
  const inputs={};
  for(const [key,spec] of Object.entries(data.fields)){
   const label=document.createElement('label');
   label.textContent=(spec.label||key)+' ';
   let control;
   if(Array.isArray(spec.choices)){
    control=document.createElement('select');
    for(const choice of spec.choices){
     const option=document.createElement('option');
     option.value=String(choice);option.textContent=String(choice);
     control.appendChild(option);
    }
    control.value=String(data.values[key]);
   }else{
    control=document.createElement('input');
    control.type=spec.type==='boolean'?'checkbox':spec.type==='string'?'text':'number';
    if(spec.type==='boolean')control.checked=data.values[key];
    else control.value=String(data.values[key]);
    if(spec.type==='integer')control.step='1';
    else if(spec.type==='number')control.step='any';
    if(spec.min!==undefined)control.min=String(spec.min);
    if(spec.max!==undefined)control.max=String(spec.max);
   }
   control.name=key;
   inputs[key]=control;
   label.appendChild(control);
   if(spec.description){const hint=document.createElement('small');hint.textContent=spec.description;label.appendChild(hint)}
   form.appendChild(label);
  }
  const save=document.createElement('button');save.type='submit';save.textContent='Save plugin settings';form.appendChild(save);
  const status=document.createElement('p');status.setAttribute('role','status');form.appendChild(status);
  form.addEventListener('submit',async event=>{
   event.preventDefault();
   const values={};
   for(const [key,spec] of Object.entries(data.fields)){
    const control=inputs[key];
    values[key]=spec.type==='boolean'?control.checked:spec.type==='integer'?Number.parseInt(control.value,10):spec.type==='number'?Number(control.value):control.value;
   }
   save.disabled=true;status.textContent='Saving…';
   try{
    const response=await fetch('/api/plugins/settings',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify({id:pluginId,values})});
    const contentType=response.headers.get('Content-Type')||'';
    if(!contentType.includes('application/json'))throw new Error('Server returned HTTP '+response.status+' ('+contentType+'), not JSON');
    const result=await response.json();
    if(!response.ok)throw new Error(result.error||'HTTP '+response.status);
    status.textContent='Settings saved.';
   }catch(error){status.textContent='Could not save settings: '+error.message}
   finally{save.disabled=false}
  });
  target.appendChild(form);
 }catch(error){target.textContent='Plugin settings unavailable: '+error.message}
}
async function loadPluginInventory(){
 const installed=document.getElementById('plugin-inventory');
 const available=document.getElementById('plugin-available');
 const bundledState=document.getElementById('plugin-bundled-state');
 const bundledInstall=document.getElementById('plugin-bundled-install');
 if(!installed||!available)return;
 installed.textContent='Loading installed plugins…';
 available.textContent='Loading official catalog…';
 try{
  const response=await fetch('/api/plugins/inventory',{credentials:'same-origin',cache:'no-store'});
  if(!response.ok)throw new Error('Inventory request failed (HTTP '+response.status+')');
  const data=await response.json();
  installed.replaceChildren();
  available.replaceChildren();
  const plugins=data.plugins||[];
  const helloInstalled=plugins.some(plugin=>plugin.id==='hello-world');
  bundledState.textContent=helloInstalled?'Installed in ULS · manage under Installed plugins':'Not installed';
  bundledInstall.hidden=helloInstalled;
  const addButton=(parent,label,action)=>{
   const button=document.createElement('button');
   button.type='button';button.textContent=label;button.addEventListener('click',action);
   parent.appendChild(button);
  };
  if(!plugins.length)installed.textContent='No plugins installed.';
  else{
   const summary=document.createElement('p');
   summary.textContent=plugins.length+' installed · '+plugins.filter(p=>p.enabled&&!p.error).length+' enabled';
   installed.appendChild(summary);
  }
  for(const plugin of plugins){
   const item=document.createElement('div');item.className='plugin-entry';
   const title=document.createElement('h4');
   title.textContent=plugin.name+' · v'+plugin.version;
   item.appendChild(title);
   const status=document.createElement('p');status.className='muted';
   status.textContent=(plugin.enabled?'Enabled':'Disabled')+(plugin.error?' · '+plugin.error:'');
   item.appendChild(status);
   if(plugin.source){
    const source=document.createElement('p');source.className='muted';
    source.textContent='Source: '+plugin.source+' · '+(plugin.commit||'').slice(0,12);
    item.appendChild(source);
   }
   if(!plugin.error){
    const official=(data.official||[]).find(p=>p.id===plugin.id);
    if(plugin.source.startsWith('https://github.com/')&&/^[0-9a-f]{40}$/i.test(plugin.commit)){
     addButton(item,'Check for update',()=>{
      let source=plugin.source;
      if(official){
       const installedRepo=plugin.source.split('/tree/')[0].replace(/\\/$/,'');
       const officialRepo=official.source.split('/tree/')[0].replace(/\\/$/,'');
       if(installedRepo===officialRepo)source=official.source;
      }
      reviewInstalledPlugin({...plugin,installedSource:plugin.source,source});
     });
    }
    if(plugin.id!=='hello-world')addButton(item,'Settings',()=>editPluginSettings(plugin.id));
    addButton(item,plugin.enabled?'Disable':'Enable',()=>setPluginEnabled(plugin.id,!plugin.enabled));
    if(!plugin.enabled)addButton(item,'Uninstall',()=>removePlugin(plugin.id));
   }
   installed.appendChild(item);
  }
  for(const [name,error] of Object.entries(data.errors||{})){
   const note=document.createElement('p');note.textContent='Invalid package '+name+': '+error;installed.appendChild(note);
  }
  if((data.unregistered||[]).length){
   const note=document.createElement('p');note.textContent='Unregistered packages: '+data.unregistered.join(', ');installed.appendChild(note);
  }
  const catalog=data.official||[];
  if(!catalog.length)available.textContent='No official plugins listed.';
  for(const plugin of catalog){
   const item=document.createElement('div');item.className='plugin-entry';
   const title=document.createElement('h4');title.textContent=plugin.name+' · v'+plugin.version;item.appendChild(title);
   const description=document.createElement('p');description.className='muted';
   description.textContent=plugin.description;item.appendChild(description);
   const state=document.createElement('p');state.className='muted';
   state.textContent=plugin.installed?'Installed':'Available to install';item.appendChild(state);
   if(!plugin.installed)addButton(item,'Review & install',async()=>{
    document.getElementById('plugin-github-url').value=plugin.source;
    await reviewGithubPlugin();
    document.getElementById('plugin-github-review')?.scrollIntoView({block:'nearest'});
   });
   available.appendChild(item);
  }
 }catch(error){
  installed.textContent='Plugin inventory unavailable: '+error.message;
  available.textContent='Catalog unavailable.';
  bundledState.textContent='Installation state unavailable.';
  bundledInstall.hidden=true;
 }
}
function showPage(name){if(!document.querySelector('[data-page="'+name+'"]'))return;if(name!=='sports'&&sportsSettingsDirty&&!confirm('You have unsaved sport settings changes. Leave this page without saving?'))return;if(name!=='news'&&(newsSourcesDirty||newsSettingsDirty())){if(!confirm('You have unsaved Content & News changes. Leave this page without saving?'))return;discardNewsEdits();}document.querySelectorAll('.nav-item').forEach(button=>{const active=button.getAttribute('onclick')==="showPage('"+name+"')";button.classList.toggle('active',active);if(active)button.setAttribute('aria-current','page');else button.removeAttribute('aria-current');});document.querySelectorAll('[data-page]').forEach(el=>el.hidden=el.dataset.page!==name);if(name==='news'){if(!newsSourcesDirty)loadNewsSources();loadAutomaticNews();loadNewsTiming();loadScoringAlerts();loadGameInterruptions();loadStandingsSettings()}if(name==='display'){loadClockSettings();loadCountdown();}if(name==='dashboard'||name==='system')refreshStatus();if(name==='system'){refreshSystem();checkSoftwareUpdate();}if(name==='matrix-settings'){loadMatrixSettings();refreshMatrixStatus();}if(name==='wifi'){refreshWifi();refreshWifiProfiles();refreshRecoveryReadiness();scanWifi()}if(name==='plugins')loadPluginInventory()}
async function refreshMatrixStatus(){
 const el=document.getElementById('matrix-service-state');
 try{const response=await fetch('/api/matrix-status',{cache:'no-store'});const result=await response.json();
 if(!response.ok)throw Error(result.error||'Status unavailable');
 el.textContent='Physical matrix: '+result.label;
 }catch(error){el.textContent=error.message}
}
async function applyMatrixSettings(){
 const status=document.getElementById('matrix-settings-status');
 if(!confirm('Apply saved matrix settings? The physical matrix may briefly go dark.'))return;
 status.textContent='Applying saved matrix settings…';
 try{const response=await fetch('/api/matrix/apply',{method:'POST',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify({confirm:true})});
 const result=await response.json();if(!response.ok)throw Error(result.error||'Apply failed');
 status.textContent='Matrix settings applied. The startup splash may appear before the live display.';
 }catch(error){status.textContent=error.message}
 await refreshMatrixStatus();
}
async function loadMatrixSettings(){
 const status=document.getElementById('matrix-settings-status');status.textContent='Loading…';
 try{const response=await fetch('/api/matrix-settings',{cache:'no-store'});const data=await response.json();if(!response.ok)throw Error(data.error||'Load failed');
 document.getElementById('matrix-enabled').checked=data.enabled;
 document.getElementById('matrix-brightness').value=data.brightness;
 document.getElementById('matrix-slowdown').value=data.gpio_slowdown;
 document.getElementById('matrix-mapping').value=data.mapping;
 document.getElementById('matrix-interval').value=data.interval;
 status.textContent='Settings loaded. Saving requires a matrix-service restart to apply.';
 }catch(error){status.textContent=error.message}
}
async function saveMatrixSettings(){
 const status=document.getElementById('matrix-settings-status');status.textContent='Saving…';
 const data={enabled:document.getElementById('matrix-enabled').checked,
 brightness:Number(document.getElementById('matrix-brightness').value),
 gpio_slowdown:Number(document.getElementById('matrix-slowdown').value),
 mapping:document.getElementById('matrix-mapping').value,
 interval:Number(document.getElementById('matrix-interval').value)};
 try{const response=await fetch('/api/matrix-settings',{method:'POST',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify(data)});
 const result=await response.json();if(!response.ok)throw Error(result.error||'Save failed');
 status.textContent='Saved. Choose Apply Saved Settings to update the physical matrix.';
 }catch(error){status.textContent=error.message}
}
async function loadAutomaticNews(){
 if(!newsGroupCanLoad('automatic'))return;
 const status=document.getElementById('auto-news-status');
 try{const response=await fetch('/api/settings',{cache:'no-store'});if(!response.ok)throw Error('Unable to load sports settings');const data=await response.json();document.getElementById('mlb-news-enabled').checked=data.sports.mlb.news_enabled;document.getElementById('nhl-news-enabled').checked=data.sports.nhl.news_enabled;document.getElementById('nba-news-enabled').checked=data.sports.nba.news_enabled;document.getElementById('wnba-news-enabled').checked=data.sports.wnba.news_enabled;document.getElementById('nfl-news-enabled').checked=data.sports.nfl.news_enabled;document.getElementById('mls-news-enabled').checked=data.sports.mls.news_enabled;document.getElementById('nwsl-news-enabled').checked=data.sports.nwsl.news_enabled;document.getElementById('english-news-enabled').checked=data.sports.english.news_enabled;document.getElementById('efl-news-enabled').checked=data.sports.efl.news_enabled;status.textContent='';newsGroupLoaded('automatic');
 }catch(err){status.textContent=err.message}

}
async function saveAutomaticNews(){
 const status=document.getElementById('auto-news-status');status.textContent='Saving…';
 try{const response=await fetch('/api/settings',{cache:'no-store'});if(!response.ok)throw Error('Unable to load sports settings');const data=await response.json();data.sports.mlb.news_enabled=document.getElementById('mlb-news-enabled').checked;data.sports.nhl.news_enabled=document.getElementById('nhl-news-enabled').checked;data.sports.nba.news_enabled=document.getElementById('nba-news-enabled').checked;data.sports.wnba.news_enabled=document.getElementById('wnba-news-enabled').checked;data.sports.nfl.news_enabled=document.getElementById('nfl-news-enabled').checked;data.sports.mls.news_enabled=document.getElementById('mls-news-enabled').checked;data.sports.nwsl.news_enabled=document.getElementById('nwsl-news-enabled').checked;data.sports.english.news_enabled=document.getElementById('english-news-enabled').checked;data.sports.efl.news_enabled=document.getElementById('efl-news-enabled').checked;
 const saved=await fetch('/api/settings',{method:'POST',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify(data)});
 const result=await saved.json();if(!saved.ok)throw Error(result.error||'Save failed');settings=result.settings;status.textContent='Automatic sports news preferences saved.';newsGroupSaved('automatic')}
 catch(err){status.textContent=err.message}
}
async function loadStandingsSettings(){
 if(!newsGroupCanLoad('standings'))return;
 const status=document.getElementById('standings-status');
 try{
  const response=await fetch('/api/settings',{cache:'no-store'});
  if(!response.ok)throw Error('Unable to load standings settings');
  const data=await response.json(), options=data.standings||{};
  document.getElementById('standings-enabled').checked=options.enabled===true;
  document.getElementById('standings-page-seconds').value=options.page_seconds??12;
  document.getElementById('standings-refresh-seconds').value=options.refresh_seconds??900;
  status.textContent='';
  newsGroupLoaded('standings');
 }catch(error){status.textContent=error.message}

}
async function saveStandingsSettings(){
 const status=document.getElementById('standings-status');
 status.textContent='Saving…';
 try{
  const response=await fetch('/api/settings',{cache:'no-store'});
  if(!response.ok)throw Error('Unable to load settings');
  const data=await response.json();
  data.standings={
   enabled:document.getElementById('standings-enabled').checked,
   page_seconds:Number(document.getElementById('standings-page-seconds').value),
   refresh_seconds:Number(document.getElementById('standings-refresh-seconds').value),
   ...(data.standings?.leagues!==undefined?{leagues:data.standings.leagues}:{}),
   ...(data.standings?.mlb_divisions!==undefined?{mlb_divisions:data.standings.mlb_divisions}:{}),
   ...(data.standings?.nhl_divisions!==undefined?{nhl_divisions:data.standings.nhl_divisions}:{}),
   ...(data.standings?.nhl_wild_cards!==undefined?{nhl_wild_cards:data.standings.nhl_wild_cards}:{}),
   ...(data.standings?.nba_conferences!==undefined?{nba_conferences:data.standings.nba_conferences}:{}),
   ...(data.standings?.nfl_divisions!==undefined?{nfl_divisions:data.standings.nfl_divisions}:{}),
    ...(data.standings?.mls_conferences!==undefined?{mls_conferences:data.standings.mls_conferences}:{}),
    nwsl:data.standings?.nwsl===true,
    wnba:data.standings?.wnba===true
  };
  const saved=await fetch('/api/settings',{method:'POST',
   headers:{'Content-Type':'application/json','X-Configurator-Token':token},
   body:JSON.stringify(data)});
  const result=await saved.json();
  if(!saved.ok)throw Error(result.error||'Save failed');
  settings=result.settings;
  status.textContent='Standings preferences saved and applied.';newsGroupSaved('standings');
 }catch(error){status.textContent=error.message}
}
async function loadGameInterruptions(){
 if(!newsGroupCanLoad('interruptions'))return;
 const status=document.getElementById('game-interruptions-status');
 try{
  const response=await fetch('/api/settings',{cache:'no-store'});
  if(!response.ok)throw Error('Unable to load game status preferences');
  const data=await response.json();
  const options=data.game_interruptions||{};
  for(const kind of ['delayed','postponed','rescheduled','suspended'])
   document.getElementById('interruption-'+kind).value=options[kind]||'when_no_live';
  status.textContent='';
  newsGroupLoaded('interruptions');
 }catch(err){status.textContent=err.message}

}
async function saveGameInterruptions(){
 const status=document.getElementById('game-interruptions-status');
 status.textContent='Saving…';
 try{
  const response=await fetch('/api/settings',{cache:'no-store'});
  if(!response.ok)throw Error('Unable to load settings');
  const data=await response.json();
  data.game_interruptions={};
  for(const kind of ['delayed','postponed','rescheduled','suspended'])
   data.game_interruptions[kind]=document.getElementById('interruption-'+kind).value;
  const saved=await fetch('/api/settings',{method:'POST',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify(data)});
  const result=await saved.json();
  if(!saved.ok)throw Error(result.error||'Save failed');
  settings=result.settings;
  status.textContent='Game status preferences saved.';newsGroupSaved('interruptions');
 }catch(err){status.textContent=err.message}
}
async function loadScoringAlerts(){
 if(!newsGroupCanLoad('scoring'))return;
 const status=document.getElementById('scoring-alerts-status');
 try{
  const response=await fetch('/api/settings',{cache:'no-store'});
  if(!response.ok)throw Error('Unable to load scoring alerts');
  const data=await response.json();
  const options=data.scoring_alerts||{enabled:false,scope:'favorites',seconds:8};
  document.getElementById('scoring-alerts-enabled').checked=options.enabled;
  document.getElementById('scoring-alerts-scope').value=options.scope;
  document.getElementById('scoring-alerts-seconds').value=options.seconds;
  status.textContent='';
  newsGroupLoaded('scoring');
 }catch(err){status.textContent=err.message}

}
async function saveScoringAlerts(){
 const status=document.getElementById('scoring-alerts-status');
 const seconds=Number(document.getElementById('scoring-alerts-seconds').value);
 if(!Number.isInteger(seconds)||seconds<1||seconds>60){status.textContent='Duration must be 1 to 60 seconds.';return}
 status.textContent='Saving…';
 try{
  const response=await fetch('/api/settings',{cache:'no-store'});
  if(!response.ok)throw Error('Unable to load settings');
  const data=await response.json();
  data.scoring_alerts={
   enabled:document.getElementById('scoring-alerts-enabled').checked,
   scope:document.getElementById('scoring-alerts-scope').value,
   seconds:seconds
  };
  const saved=await fetch('/api/settings',{method:'POST',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify(data)});
  const result=await saved.json();
  if(!saved.ok)throw Error(result.error||'Save failed');
  settings=result.settings;
  status.textContent='Scoring alerts saved. Apply saved settings if prompted.';newsGroupSaved('scoring');
 }catch(err){status.textContent=err.message}
}
async function loadNewsTiming(){
 if(!newsGroupCanLoad('timing'))return;
 const status=document.getElementById('news-timing-status');
 try{const response=await fetch('/api/settings',{cache:'no-store'});if(!response.ok)throw Error('Unable to load news timing');const data=await response.json();document.getElementById('news-interval').value=data.news.rotation_interval;document.getElementById('news-duration').value=data.news.headline_seconds;document.getElementById('news-speed').value=data.news.scroll_chars_per_second;status.textContent='';newsGroupLoaded('timing');
 }catch(err){status.textContent=err.message}

}
async function saveNewsTiming(){
 const status=document.getElementById('news-timing-status');
 const fields=[['news-interval',1,20,'News interval'],['news-duration',3,120,'Headline duration'],['news-speed',1,15,'Scroll speed']];
 for(const [id,min,max,label] of fields){const input=document.getElementById(id),value=Number(input.value);if(input.value.trim()===''||!Number.isInteger(value)||value<min||value>max){status.textContent=label+' must be a whole number from '+min+' to '+max+'.';input.focus();return;}}
 status.textContent='Saving…';
 try{const response=await fetch('/api/settings',{cache:'no-store'});if(!response.ok)throw Error('Unable to load settings');const data=await response.json();data.news={rotation_interval:Number(document.getElementById('news-interval').value),headline_seconds:Number(document.getElementById('news-duration').value),scroll_chars_per_second:Number(document.getElementById('news-speed').value)};
 const saved=await fetch('/api/settings',{method:'POST',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify(data)});
 const result=await saved.json();if(!saved.ok)throw Error(result.error||'Save failed');settings=result.settings;status.textContent='News timing saved.';newsGroupSaved('timing')}
 catch(err){status.textContent=err.message}
}
let newsSources=[],newsSourcesSaved=[],newsSourcesDirty=false;
function markNewsSourcesDirty(){newsSourcesDirty=JSON.stringify(newsSources)!==JSON.stringify(newsSourcesSaved);document.getElementById('news-status').textContent=newsSourcesDirty?'Unsaved news source changes. Save before leaving.':'';}
async function loadNewsSources(){
 const status=document.getElementById('news-status');
 try{const response=await fetch('/api/news-sources',{cache:'no-store'});if(!response.ok)throw Error('Unable to load news sources');newsSources=(await response.json()).sources;newsSourcesSaved=clone(newsSources);newsSourcesDirty=false;renderNewsSources();status.textContent='';}
 catch(err){status.textContent=err.message}
}
function renderNewsSources(){
 const target=document.getElementById('news-sources');target.replaceChildren();
 newsSources.forEach((source,index)=>{
  const row=document.createElement('div');row.className='item';
  [['name','Name','text'],['url','RSS/Atom URL','url'],['category','Category','text'],['refresh_seconds','Refresh seconds','number']].forEach(([key,label,type])=>{
   const wrapper=document.createElement('label');wrapper.textContent=label+' ';
   const input=document.createElement('input');input.type=type;input.value=source[key];input.setAttribute('aria-label',label+' for source '+(index+1));
   if(type==='number'){input.min='60';input.max='86400';input.step='1'}
   input.oninput=()=>{source[key]=type==='number'?Number(input.value):input.value;markNewsSourcesDirty()};
   wrapper.append(input);row.append(wrapper);
  });
  const enabled=document.createElement('label');enabled.textContent='Enabled ';
  const checkbox=document.createElement('input');checkbox.type='checkbox';checkbox.checked=source.enabled;checkbox.onchange=()=>{source.enabled=checkbox.checked;markNewsSourcesDirty()};enabled.append(checkbox);row.append(enabled);
  const remove=document.createElement('button');remove.type='button';remove.textContent='Remove';remove.onclick=()=>{newsSources.splice(index,1);renderNewsSources();markNewsSourcesDirty()};row.append(remove);target.append(row);
 });
}
function addNewsSource(){if(newsSources.length>=20){document.getElementById('news-status').textContent='Maximum 20 sources';return}newsSources.push({name:'',url:'',category:'news',enabled:true,refresh_seconds:900});renderNewsSources();markNewsSourcesDirty()}
async function saveNewsSources(){
 const status=document.getElementById('news-status');
 for(const [index,source] of newsSources.entries()){
  const label='News source '+(index+1);
  if(typeof source.name!=='string'||!source.name.trim()){status.textContent=label+' needs a name.';return;}
  if(typeof source.url!=='string'||!/^https?:[/][/][^\\s/?#]+(?:[/?#][^\\s]*)?$/i.test(source.url.trim())){status.textContent=label+' needs a valid HTTP or HTTPS URL.';return;}
  if(typeof source.category!=='string'||!source.category.trim()){status.textContent=label+' needs a category.';return;}
  if(!Number.isInteger(source.refresh_seconds)||source.refresh_seconds<60||source.refresh_seconds>86400){status.textContent=label+' refresh interval must be a whole number from 60 to 86400 seconds.';return;}
 }
 status.textContent='Saving…';
 try{const response=await fetch('/api/news-sources',{method:'POST',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify({sources:newsSources})});const result=await response.json();if(!response.ok)throw Error(result.error||'Save failed');newsSources=result.settings.sources;newsSourcesSaved=clone(newsSources);newsSourcesDirty=false;renderNewsSources();status.textContent='News sources saved.'}
 catch(err){status.textContent=err.message}
}
const clone=value=>JSON.parse(JSON.stringify(value));
function markDirty(){dirty=JSON.stringify(state)!==JSON.stringify(saved)||(nhlColors!==null&&nhlSavedColors!==null&&JSON.stringify(nhlColors)!==JSON.stringify(nhlSavedColors));document.getElementById('dirty').textContent=dirty?'Unsaved changes':'All changes saved';}
const hex=rgb=>'#'+rgb.map(x=>x.toString(16).padStart(2,'0')).join('');
const rgb=hex=>[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16));
function section(name){
 const target=document.getElementById(name);target.replaceChildren();
 Object.entries(state[name]).sort().filter(([key])=>name!=='teams'||key===document.getElementById('edit-team').value).forEach(([key,value])=>{
  const wrapper=document.createElement('div');wrapper.className='item color-editor';
  const heading=document.createElement('label');heading.className='color-name';heading.textContent=key;
  const picker=document.createElement('input');picker.type='color';picker.value=hex(value);
  picker.setAttribute('aria-label',key+' color picker');
  const hexValue=document.createElement('output');hexValue.className='color-hex';hexValue.textContent=hex(value).toUpperCase();
  const channels=document.createElement('div');channels.className='color-channels';
  const sliders=[];
  const update=next=>{
   state[name][key]=next;
   picker.value=hex(next);hexValue.textContent=hex(next).toUpperCase();
   sliders.forEach((entry,i)=>{entry.input.value=next[i];entry.output.textContent=next[i]});
   selected={name,key};markDirty();draw();
  };
  ['Red','Green','Blue'].forEach((channel,i)=>{
   const row=document.createElement('label');row.className='color-channel';
   const title=document.createElement('span');title.textContent=channel;
   const slider=document.createElement('input');slider.type='range';slider.min='0';slider.max='255';slider.step='1';slider.value=value[i];
   slider.setAttribute('aria-label',key+' '+channel+' channel');
   const output=document.createElement('output');output.textContent=value[i];
   slider.oninput=()=>{const next=[...state[name][key]];next[i]=Number(slider.value);update(next)};
   slider.onfocus=()=>{selected={name,key}};
   row.append(title,slider,output);channels.append(row);sliders.push({input:slider,output});
  });
  picker.oninput=()=>update(rgb(picker.value));
  picker.onfocus=()=>{selected={name,key}};
  wrapper.append(heading,picker,hexValue,channels);target.append(wrapper);
 });
}
async function load(){
 const response=await fetch('/api/config',{cache:'no-store'});
 if(!response.ok)throw Error('Cannot load configuration');
 state=await response.json();saved=clone(state);
 const picker=document.getElementById('preview-team');picker.replaceChildren();
 const editor=document.getElementById('edit-team');editor.replaceChildren();
 Object.keys(state.teams).sort().forEach(team=>{const option=document.createElement('option');option.value=team;option.textContent=team;picker.append(option);editor.append(option.cloneNode(true))});
 picker.value=selectedTeam in state.teams?selectedTeam:Object.keys(state.teams).sort()[0];selectedTeam=picker.value;editor.value=selectedTeam;
 section('scoreboard');section('teams');markDirty();draw();await loadNHLColors();
}
async function draw(){
 if(!state)return;
 try{
  const response=await fetch('/api/frame',{method:'POST',
   headers:{'Content-Type':'application/json','X-Configurator-Token':token},
   body:JSON.stringify({...state,preview_team:selectedTeam})});
  if(!response.ok)throw Error('Preview unavailable');
  const f=await response.json(),canvas=document.getElementById('matrix');
  const ctx=canvas.getContext('2d'),image=ctx.createImageData(64,32);
  f.pixels.forEach((p,i)=>{image.data.set([...p,255],i*4)});
  ctx.putImageData(image,0,0);
 }catch(err){document.getElementById('status').textContent=err.message}
}
document.getElementById('preview-team').onchange=event=>{selectedTeam=event.target.value;document.getElementById('edit-team').value=selectedTeam;section('teams');draw()};
document.getElementById('edit-team').onchange=event=>{selectedTeam=event.target.value;document.getElementById('preview-team').value=selectedTeam;selected=null;section('teams');draw()};
document.getElementById('mlb-save-color').onclick=async()=>{
 const code=document.getElementById('edit-team').value,status=document.getElementById('mlb-color-status');
 const color=clone(state.teams[code]);
 const invalid=invalidColorEntry({teams:{[code]:color}});
 if(invalid){status.textContent='Invalid MLB RGB color for '+code+'. Each channel must be a whole number from 0 to 255.';return;}
 status.textContent='Saving…';
 try{
  const response=await fetch('/api/mlb-colors',{method:'POST',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify({[code]:color})});
  const result=await response.json();if(!response.ok)throw Error(result.error||'Save failed');
  saved.teams[code]=color;markDirty();status.textContent='Saved MLB '+code+' color.';
 }catch(err){status.textContent=err.message}
};
document.getElementById('mlb-reset-color').onclick=async()=>{
 const code=document.getElementById('edit-team').value,status=document.getElementById('mlb-color-status');
 try{
  const response=await fetch('/api/defaults');if(!response.ok)throw Error('Defaults unavailable');
  state.teams[code]=clone((await response.json()).teams[code]);selected={name:'teams',key:code};
  section('teams');markDirty();draw();status.textContent='Default restored in editor. Save to apply.';
 }catch(err){status.textContent=err.message}
};
document.getElementById('cancel').onclick=()=>{state=clone(saved);if(nhlSavedColors!==null){nhlColors=clone(nhlSavedColors);showNHLColorEditor();document.getElementById('nhl-color-status').textContent='Unsaved NHL color changes discarded.';}selected=null;section('scoreboard');section('teams');markDirty();draw();document.getElementById('status').textContent='Unsaved changes discarded.'};
document.getElementById('reset').onclick=async()=>{
 const status=document.getElementById('status');
 if(!selected){status.textContent='Select a color first.';return;}
 const target={...selected};
 try{
  const response=await fetch('/api/defaults');
  if(!response.ok)throw Error('Unable to load default colors (HTTP '+response.status+').');
  const defaults=await response.json();
  const color=defaults[target.name]?.[target.key];
  if(!Array.isArray(color)||color.length!==3)throw Error('No default color found for '+target.key+'.');
  state[target.name][target.key]=clone(color);
  section(target.name);markDirty();draw();
  status.textContent='Default restored for '+target.key+' in editor. Save to apply.';
 }catch(err){status.textContent='Could not reset color: '+err.message;}
};
function invalidColorEntry(palette){
 for(const group of ['scoreboard','teams']){
  for(const [name,channels] of Object.entries(palette[group]||{})){
   if(!Array.isArray(channels)||channels.length!==3||channels.some(value=>!Number.isInteger(value)||value<0||value>255))return group+' / '+name;
  }
 }
 return null;
}
document.getElementById('save').onclick=async()=>{
 const status=document.getElementById('status');
 const invalid=invalidColorEntry(state);
 if(invalid){status.textContent='Invalid RGB color in '+invalid+'. Each channel must be a whole number from 0 to 255.';return;}
 status.textContent='Saving…';
 try{
  const response=await fetch('/api/config',{method:'POST',
   headers:{'Content-Type':'application/json','X-Configurator-Token':token},
   body:JSON.stringify(state)});
  const result=await response.json();
  if(!response.ok)throw Error(result.error||'Save failed');
  saved=clone(state);markDirty();status.textContent='Saved. Other running preview processes may require restart to reload colors.';
 }catch(err){status.textContent=err.message}
};
let nhlColors=null,nhlSavedColors=null,nhlColorDefaults=null;
function showNHLColorEditor(){
 const code=document.getElementById('nhl-edit-team').value;
 const target=document.getElementById('nhl-color-editor');target.replaceChildren();
 if(!nhlColors||!nhlColors[code])return;
 const value=nhlColors[code];
 const wrapper=document.createElement('div');wrapper.className='item color-editor';
 const heading=document.createElement('label');heading.className='color-name';heading.textContent=code+' primary';
 const picker=document.createElement('input');picker.type='color';picker.id='nhl-color-picker';picker.value=hex(value);
 picker.setAttribute('aria-label',code+' primary color picker');
 const hexValue=document.createElement('output');hexValue.className='color-hex';hexValue.textContent=hex(value).toUpperCase();
 const channels=document.createElement('div');channels.className='color-channels';
 const sliders=[];
 const update=next=>{
  nhlColors[code]=next;picker.value=hex(next);hexValue.textContent=hex(next).toUpperCase();
  sliders.forEach((entry,i)=>{entry.input.value=next[i];entry.output.textContent=next[i]});
  markDirty();document.getElementById('nhl-color-status').textContent='Unsaved NHL color changes.';
 };
 ['Red','Green','Blue'].forEach((channel,i)=>{
  const row=document.createElement('label');row.className='color-channel';
  const title=document.createElement('span');title.textContent=channel;
  const input=document.createElement('input');input.type='range';input.min='0';input.max='255';input.step='1';input.value=value[i];
  input.setAttribute('aria-label',code+' '+channel+' channel');
  const output=document.createElement('output');output.textContent=value[i];
  input.oninput=()=>{const next=[...nhlColors[code]];next[i]=Number(input.value);update(next)};
  row.append(title,input,output);channels.append(row);sliders.push({input,output});
 });
 picker.oninput=()=>update(rgb(picker.value));
 wrapper.append(heading,picker,hexValue,channels);target.append(wrapper);
}
async function loadNHLColors(){
 const response=await fetch('/api/nhl-colors',{cache:'no-store'});if(!response.ok)throw Error('Cannot load NHL colors');
 nhlColors=await response.json();nhlSavedColors=clone(nhlColors);markDirty();
 const defaults=await fetch('/api/defaults');if(!defaults.ok)throw Error('Cannot load default colors');
 nhlColorDefaults=(await defaults.json()).nhl_teams;
 const select=document.getElementById('nhl-edit-team'),previous=select.value;select.replaceChildren();
 NHL_TEAMS.forEach(([code,name])=>{const option=document.createElement('option');option.value=code;option.textContent=name+' ('+code+')';select.append(option)});
 if(previous&&nhlColors[previous])select.value=previous;
 showNHLColorEditor();
}
document.getElementById('nhl-edit-team').onchange=showNHLColorEditor;
document.getElementById('nhl-reset-color').onclick=()=>{
 const code=document.getElementById('nhl-edit-team').value;
 nhlColors[code]=[...nhlColorDefaults[code]];showNHLColorEditor();markDirty();
 document.getElementById('nhl-color-status').textContent='Default restored in editor. Save to apply.';
};
document.getElementById('nhl-save-color').onclick=async()=>{
 const code=document.getElementById('nhl-edit-team').value,status=document.getElementById('nhl-color-status');
 const color=[...(nhlColors[code]||[])];
 const invalid=invalidColorEntry({teams:{[code]:color}});
 if(invalid){status.textContent='Invalid NHL RGB color for '+code+'. Each channel must be a whole number from 0 to 255.';return;}
 status.textContent='Saving…';
 try{
  const response=await fetch('/api/nhl-colors',{method:'POST',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify({[code]:color})});
  const result=await response.json();if(!response.ok)throw Error(result.error||'Save failed');
  nhlSavedColors[code]=clone(color);markDirty();status.textContent='Saved NHL '+code+' color.';
 }catch(err){status.textContent=err.message}
};
const NHL_TEAMS=[["ANA","Anaheim Ducks"],["BOS","Boston Bruins"],["BUF","Buffalo Sabres"],["CGY","Calgary Flames"],["CAR","Carolina Hurricanes"],["CHI","Chicago Blackhawks"],["COL","Colorado Avalanche"],["CBJ","Columbus Blue Jackets"],["DAL","Dallas Stars"],["DET","Detroit Red Wings"],["EDM","Edmonton Oilers"],["FLA","Florida Panthers"],["LAK","Los Angeles Kings"],["MIN","Minnesota Wild"],["MTL","Montréal Canadiens"],["NSH","Nashville Predators"],["NJD","New Jersey Devils"],["NYI","New York Islanders"],["NYR","New York Rangers"],["OTT","Ottawa Senators"],["PHI","Philadelphia Flyers"],["PIT","Pittsburgh Penguins"],["SJS","San Jose Sharks"],["SEA","Seattle Kraken"],["STL","St. Louis Blues"],["TBL","Tampa Bay Lightning"],["TOR","Toronto Maple Leafs"],["UTA","Utah Mammoth"],["VAN","Vancouver Canucks"],["VGK","Vegas Golden Knights"],["WSH","Washington Capitals"],["WPG","Winnipeg Jets"]];
const NFL_TEAMS=[['ARI','Arizona Cardinals'],['ATL','Atlanta Falcons'],['BAL','Baltimore Ravens'],['BUF','Buffalo Bills'],['CAR','Carolina Panthers'],['CHI','Chicago Bears'],['CIN','Cincinnati Bengals'],['CLE','Cleveland Browns'],['DAL','Dallas Cowboys'],['DEN','Denver Broncos'],['DET','Detroit Lions'],['GB','Green Bay Packers'],['HOU','Houston Texans'],['IND','Indianapolis Colts'],['JAC','Jacksonville Jaguars'],['KC','Kansas City Chiefs'],['LAC','Los Angeles Chargers'],['LAR','Los Angeles Rams'],['LV','Las Vegas Raiders'],['MIA','Miami Dolphins'],['MIN','Minnesota Vikings'],['NE','New England Patriots'],['NO','New Orleans Saints'],['NYG','New York Giants'],['NYJ','New York Jets'],['PHI','Philadelphia Eagles'],['PIT','Pittsburgh Steelers'],['SEA','Seattle Seahawks'],['SF','San Francisco 49ers'],['TB','Tampa Bay Buccaneers'],['TEN','Tennessee Titans'],['WAS','Washington Commanders']];
document.getElementById('nfl-teams').replaceChildren(...NFL_TEAMS.map(([code,name])=>{
 const label=document.createElement('label'),input=document.createElement('input');
 input.type='checkbox';input.value=code;label.append(input,document.createTextNode(' '+name));return label;
}));
const SOCCER_TEAMS={
 mls:[['ATL','Atlanta United FC'],['ATX','Austin FC'],['CLT','Charlotte FC'],['CHI','Chicago Fire FC'],['CIN','FC Cincinnati'],['COL','Colorado Rapids'],['CLB','Columbus Crew'],['DAL','FC Dallas'],['DC','D.C. United'],['HOU','Houston Dynamo FC'],['MIA','Inter Miami CF'],['LA','LA Galaxy'],['LAFC','Los Angeles FC'],['MIN','Minnesota United FC'],['MTL','CF Montréal'],['NSH','Nashville SC'],['NE','New England Revolution'],['NYC','New York City FC'],['RBNY','New York Red Bulls'],['ORL','Orlando City SC'],['PHI','Philadelphia Union'],['POR','Portland Timbers'],['RSL','Real Salt Lake'],['SD','San Diego FC'],['SJ','San Jose Earthquakes'],['SEA','Seattle Sounders FC'],['SKC','Sporting Kansas City'],['STL','St. Louis CITY SC'],['TOR','Toronto FC'],['VAN','Vancouver Whitecaps FC']],
 nwsl:[['BAY','Bay FC'],['BOS','Boston Legacy FC'],['CHI','Chicago Stars FC'],['DEN','Denver Summit FC'],['GFC','Gotham FC'],['HOU','Houston Dash'],['KC','Kansas City Current'],['LA','Angel City FC'],['LOU','Racing Louisville FC'],['NC','North Carolina Courage'],['ORL','Orlando Pride'],['POR','Portland Thorns FC'],['SD','San Diego Wave FC'],['SEA','Seattle Reign FC'],['UTA','Utah Royals FC'],['WAS','Washington Spirit']]
};
for(const league of ['mls','nwsl']){
 const target=document.getElementById(league+'-teams');
 target.replaceChildren(...SOCCER_TEAMS[league].map(([code,name])=>{
  const label=document.createElement('label'),input=document.createElement('input');
  input.type='checkbox';input.value=code;label.append(input,document.createTextNode(' '+name));return label;
 }));
}
function getNHLFavorites(){return [...document.querySelectorAll('#nhl-teams input:checked')].map(input=>input.value)}
function setNHLFavorites(teams){document.querySelectorAll('#nhl-teams input').forEach(input=>input.checked=teams.includes(input.value));updateNHLFavoriteSummary()}
function updateNHLFavoriteSummary(){const selected=getNHLFavorites();document.getElementById('nhl-favorite-summary').textContent=selected.length?selected.length+' selected: '+selected.join(', '):'No favorite NHL teams selected.'}
document.getElementById('nhl-teams').addEventListener('change',updateNHLFavoriteSummary);
function getFavoriteTeams(){return [...document.querySelectorAll('#favorite-teams input:checked')].map(input=>input.value)}
function setFavoriteTeams(teams){
 document.querySelectorAll('#favorite-teams input').forEach(input=>input.checked=teams.includes(input.value));
 updateFavoriteSummary();
}
function updateFavoriteSummary(){
 const names=[...document.querySelectorAll('#favorite-teams input:checked')].map(input=>input.parentElement.textContent.trim());
 document.getElementById('favorite-summary').textContent=names.length?names.length+' selected: '+names.join(', '):'Select at least one favorite team.';
}
document.getElementById('favorite-teams').addEventListener('change',updateFavoriteSummary);
async function refreshCountdownStatus(){
 const output=document.getElementById('countdown-feed-status');
 try{
  const response=await fetch('/api/season-countdown/status',{cache:'no-store'});
  const data=await response.json();
  if(!response.ok)throw Error(data.error||'Status unavailable');
  if(!data.enabled){output.textContent='Countdown disabled.';return}
  if(data.source==='manual'){output.textContent='Manual opening date: '+(data.opening_at||'not configured');return}
  const parts=[data.refreshing?'Retrieving MLB schedule…':data.resolved_at?'Opening: '+new Date(data.resolved_at).toLocaleString():'Opening date unavailable'];
  if(data.target==='favorite')parts.push('Team: '+data.team);
  if(data.last_success)parts.push('Last fetched: '+new Date(data.last_success).toLocaleString());
  if(data.error)parts.push('Schedule warning: '+data.error);
  output.textContent=parts.join(' · ');
 }catch(err){output.textContent='Schedule status: '+err.message}
}
async function loadCountdown(){
 const status=document.getElementById('countdown-status');
 try{
  const response=await fetch('/api/season-countdown',{cache:'no-store'});
  const data=await response.json();if(!response.ok)throw Error(data.error||'Unable to load countdown');
  for(const [id,value] of Object.entries({'sport':data.sport,'season':data.season,'opening':data.opening_at||'','target':data.target,'team':data.team||'','window':data.window,'days':data.within_days,'source':data.source||'manual'})){
   document.getElementById('countdown-'+id).value=value;
  }
  document.getElementById('countdown-enabled').checked=data.enabled;status.textContent='';await refreshCountdownStatus();
 }catch(err){status.textContent=err.message}
}
async function saveCountdown(){
 const status=document.getElementById('countdown-status');status.textContent='Saving…';
 const value=id=>document.getElementById('countdown-'+id).value.trim();
 const data={enabled:document.getElementById('countdown-enabled').checked,sport:value('sport'),
  season:value('season'),opening_at:value('opening')||null,source:value('source'),target:value('target'),
  team:value('team')||null,window:value('window'),within_days:Number(value('days'))};
 const reject=(id,message)=>{status.textContent=message;document.getElementById('countdown-'+id).focus();};
 if(value('days')===''||!Number.isInteger(data.within_days)||data.within_days<1||data.within_days>366){reject('days','Countdown days must be a whole number from 1 to 366.');return;}
 if(data.enabled){
  if(data.source==='automatic'){
   if(data.sport!=='mlb'){reject('sport','Automatic countdown dates currently support MLB only.');return;}
   if(!/^\\d{4}$/.test(data.season)){reject('season','Automatic MLB countdown requires a four-digit season.');return;}
   if(data.target==='favorite'&&!/^[A-Za-z]{3}$/.test(data.team||'')){reject('team','Favorite-team automatic countdown requires a three-letter team code.');return;}
  }else if(!data.opening_at){reject('opening','Enabled manual countdown requires an opening date and timezone.');return;}
 }
 if(data.opening_at){
  const hasZone=/(Z|[+-]\\d{2}:\\d{2})$/i.test(data.opening_at);
  if(!hasZone||!Number.isFinite(Date.parse(data.opening_at))){reject('opening','Opening date must be a valid ISO timestamp with a timezone offset.');return;}
  if(!data.season){reject('season','A season is required when an opening date is set.');return;}
  if(data.target==='favorite'&&!data.team){reject('team','A favorite-team opening date requires a team code.');return;}
 }
 try{
  const response=await fetch('/api/season-countdown',{method:'POST',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify(data)});
  const result=await response.json();if(!response.ok)throw Error(result.error||'Save failed');
  status.textContent='Countdown saved. Automatic dates are retrieved from MLB when available; missing schedules do not show a countdown.';await refreshCountdownStatus();
 }catch(err){status.textContent=err.message}
}
async function loadClockSettings(){
 const status=document.getElementById('clock-status');
 try{
  const response=await fetch('/api/time-weather',{cache:'no-store'});
  if(!response.ok)throw Error('Unable to load time settings');
  const data=await response.json();
  document.getElementById('clock-enabled').checked=data.clock_enabled;
  const zoneSelect=document.getElementById('clock-timezone');
  if(!Array.from(zoneSelect.options).some(option=>option.value===data.timezone)){
   const customOption=document.createElement('option');
   customOption.value=data.timezone;
   customOption.textContent=data.timezone+' (saved setting)';
   zoneSelect.appendChild(customOption);
  }
  zoneSelect.value=data.timezone;
  document.getElementById('clock-format').value=data.time_format;
  document.getElementById('clock-interval').value=data.rotation_interval;
  document.getElementById('weather-location').value=data.location;
  document.getElementById('weather-enabled').checked=data.weather_enabled;
  document.getElementById('weather-provider').value=data.weather_provider;
  document.getElementById('weather-unit').value=data.temperature_unit;
  status.textContent='';
 }catch(err){status.textContent=err.message}
}
async function saveClockSettings(){
 const status=document.getElementById('clock-status');
 const intervalInput=document.getElementById('clock-interval');
 const interval=Number(intervalInput.value);
 if(intervalInput.value.trim()===''||!Number.isInteger(interval)||interval<1||interval>20){
  status.textContent='Clock rotation interval must be a whole number from 1 to 20.';
  intervalInput.focus();
  return;
 }
 const locationInput=document.getElementById('weather-location');
 if(locationInput.value.trim().length>120){
  status.textContent='Weather location must be 120 characters or fewer.';
  locationInput.focus();
  return;
 }
 status.textContent='Saving…';
 try{
  const response=await fetch('/api/time-weather',{cache:'no-store'});
  if(!response.ok)throw Error('Unable to load time settings');
  const data=await response.json();
  data.clock_enabled=document.getElementById('clock-enabled').checked;
  data.timezone=document.getElementById('clock-timezone').value.trim();
  data.time_format=document.getElementById('clock-format').value;
  data.rotation_interval=interval;
  data.weather_enabled=document.getElementById('weather-enabled').checked;
  data.weather_provider=document.getElementById('weather-provider').value;
  data.location=document.getElementById('weather-location').value.trim();
  data.temperature_unit=document.getElementById('weather-unit').value;
  const key=document.getElementById('weather-key').value.trim();
  if(key){const secret=await fetch('/api/weather-key',{method:'POST',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify({api_key:key})});const result=await secret.json();if(!secret.ok)throw Error(result.error||'API key save failed');document.getElementById('weather-key').value='';}
  const saved=await fetch('/api/time-weather',{method:'POST',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify(data)});
  const result=await saved.json();
  if(!saved.ok)throw Error(result.error||'Save failed');
  status.textContent='Time & weather settings saved. Rotation updates automatically.';
 }catch(err){status.textContent=err.message}
}

function showSportsView(view){
 if(!['overview','configure','rotation'].includes(view))return;
 document.querySelectorAll('.sports-subnav button').forEach(button=>{const active=button.dataset.sportsView===view;button.classList.toggle('active',active);button.setAttribute('aria-pressed',String(active))});
 ['overview','configure','rotation'].forEach(name=>document.getElementById('sports-'+name).hidden=name!==view);
 if(view==='rotation')refreshSportsRotationSummary();
}
function selectSport(name){
 const picker=document.getElementById('sport-picker');
 if(!Array.from(picker.options).some(option=>option.value===name))return;
 const current=document.querySelector('[data-sport-panel]:not([hidden])');
 if(current&&current.dataset.sportPanel!==name&&sportsSettingsDirty&&!confirm('You have unsaved sport settings changes. Switch sports? Your unsaved changes will remain in the form until you save or reload.')){picker.value=current.dataset.sportPanel;return;}
 picker.value=name;
 document.querySelectorAll('[data-sport-panel]').forEach(panel=>panel.hidden=panel.dataset.sportPanel!==name);
 showSportsView('configure');
}
function refreshSportsRotationSummary(){
 const target=document.getElementById('sports-rotation-summary');target.replaceChildren();
 if(!settings)return;
 ['mlb','nhl','nba','wnba','nfl','mls','nwsl','english'].forEach(name=>{
  const node=document.createElement('button');node.type='button';node.className='item sport-choice';
  const sport=settings[name],enabled=settings.sports[name].enabled;
  node.textContent=name.toUpperCase()+' · '+(enabled?'Enabled':'Disabled')+' · '+sport.rotation_seconds+'s per game · '+sport.refresh_seconds+'s feed refresh · Configure →';
  node.setAttribute('aria-label','Configure '+name.toUpperCase()+' rotation settings');
  node.addEventListener('click',()=>selectSport(name));
  target.append(node);
 });
}
function refreshEnglishCoverageSummary(){
 const gameCount=document.querySelectorAll('#english-leagues input:checked').length;
 const standingsCount=document.querySelectorAll('#english-standings-leagues input:checked').length;
 document.getElementById('english-game-coverage-summary').textContent=gameCount+' division(s) selected for game coverage'+(gameCount===0?' · No English Football matches will be included.':'');
 document.getElementById('english-standings-coverage-summary').textContent=standingsCount+' division(s) selected for standings pages'+(standingsCount===0?' · No English division standings selected.':'')+' · Standings pages also require Standings Pages to be enabled under Content/News.';
}
document.querySelector('[data-page="sports"]').addEventListener('change',event=>{
 if(event.target.closest('#english-leagues,#english-standings-leagues'))refreshEnglishCoverageSummary();
});
function refreshGameSelectionHelp(){
 const explanations={favorite:'Only games involving selected favorite teams will be displayed.',fallback:'Show favorite-team games when available; otherwise show all games in the selected coverage.',all:'Show all games in the selected coverage, regardless of favorites.'};
 for(const id of ['mode','nhl-mode','nba-mode','wnba-mode','nfl-mode','mls-mode','nwsl-mode','english-mode']){
  const select=document.getElementById(id);
  const help=document.getElementById(id+'-help');
  if(!select||!help)continue;
  const sport=id==='mode'?'mlb':id.slice(0,-5);
  const favoritesSelector=sport==='mlb'?'#favorite-teams input:checked':'#'+sport+'-teams input:checked';
  const favorites=document.querySelectorAll(favoritesSelector).length;
  const warning=favorites===0&&select.value==='favorite'?' No favorites selected, so this mode will have no matching games.':'';
  help.textContent=(explanations[select.value]||'')+warning;
 }
}
document.querySelector('[data-page="sports"]').addEventListener('change',event=>{
 if(event.target.matches('#mode,#nhl-mode,#nba-mode,#wnba-mode,#nfl-mode,#mls-mode,#nwsl-mode,#english-mode')||event.target.closest('#favorite-teams,#nhl-teams,#nba-teams,#wnba-teams,#nfl-teams,#mls-teams,#nwsl-teams,#english-teams'))refreshGameSelectionHelp();
});
function refreshSportsOverview(){
 if(!settings)return;
 ['mlb','nhl','nba','wnba','nfl','mls','nwsl','english'].forEach(name=>{
  const enabled=settings.sports[name].enabled;
  const sport=settings[name];
  const favorites=(sport.favorite_teams||[]).length;
  const details=[enabled?'Enabled':'Disabled',favorites+' favorite'+(favorites===1?'':'s')];
  if(name==='english')details.push((sport.enabled_leagues||[]).length+' game division(s)');
  document.getElementById('sport-state-'+name).textContent=details.join(' · ')+' · Configure →';
 });
}
showSportsView('overview');selectSport('mlb');showSportsView('overview');

function filterEnglishClubs(){
 const query=document.getElementById('english-team-search').value.trim().toLowerCase();
 let visible=0,selected=0;
 document.querySelectorAll('#english-teams label').forEach(label=>{
  label.hidden=!label.textContent.toLowerCase().includes(query);
  if(!label.hidden)visible++;
  if(label.querySelector('input')?.checked)selected++;
 });
 const summary=document.getElementById('english-team-filter-summary');
 summary.textContent=selected+' favorite clubs selected'+(query?' · '+visible+' matching clubs'+(visible===0?' (try another search)':''):'');
}
async function loadEnglishClubs(favorites){
 const grid=document.getElementById('english-teams');
 const status=document.getElementById('english-team-status');
 try{
  const response=await fetch('/api/english/clubs',{cache:'no-store'});
  const data=await response.json();
  if(!response.ok)throw Error(data.error||'Club directory unavailable');
  const seen=new Set();
  const clubs=data.clubs.slice();
  for(const key of favorites){
   if(!clubs.some(club=>club.key===key))clubs.push({key,name:key+' (saved favorite)',division:'Previously selected'});
  }
  grid.replaceChildren(...clubs.filter(club=>{
   if(seen.has(club.key))return false;seen.add(club.key);return true;
  }).map(club=>{
   const label=document.createElement('label'),input=document.createElement('input');
   input.type='checkbox';input.value=club.key;input.checked=favorites.includes(club.key);
   label.append(input,document.createTextNode(' '+club.name+' · '+club.division));
   return label;
  }));
  status.textContent=clubs.length+' clubs available. Favorites persist across divisions.';
  filterEnglishClubs();
 }catch(error){
  status.textContent=error.message+'. Existing favorites will be preserved.';
  grid.replaceChildren(...favorites.map(key=>{
   const label=document.createElement('label'),input=document.createElement('input');
   input.type='checkbox';input.value=key;input.checked=true;
   label.append(input,document.createTextNode(' '+key+' (saved favorite)'));return label;
  }));
  filterEnglishClubs();
 }
}
async function loadSettings(){
 const response=await fetch('/api/settings',{cache:'no-store'});
 if(!response.ok)throw Error('Could not load sport settings');
 settings=await response.json();
 const mlb=settings.mlb;
 const nhl=settings.nhl;
 const nba=settings.nba;
 const wnba=settings.wnba;
 const nfl=settings.nfl;
 const english=settings.english;
 document.querySelectorAll('#mlb-standings-divisions input').forEach(el=>el.checked=(settings.standings.mlb_divisions||[]).includes(el.value));
 document.querySelectorAll('#nfl-standings-divisions input').forEach(el=>el.checked=(settings.standings.nfl_divisions||[]).includes(el.value));
  document.querySelectorAll('#mls-standings-conferences input').forEach(el=>el.checked=(settings.standings.mls_conferences||[]).includes(el.value));
  for(const league of ['nwsl','wnba'])document.getElementById(league+'-standings-enabled').checked=settings.standings[league]===true;
 document.querySelectorAll('#nba-standings-conferences input').forEach(el=>el.checked=(settings.standings.nba_conferences||[]).includes(el.value));
 document.querySelectorAll('#nhl-standings-divisions input').forEach(el=>el.checked=(settings.standings.nhl_divisions||[]).includes(el.value));
 const nhlWildCards=settings.standings.nhl_wild_cards??[
  ...((settings.standings.nhl_divisions||[]).some(d=>['Atlantic','Metropolitan'].includes(d))?['Eastern_Wild_Card']:[]),
  ...((settings.standings.nhl_divisions||[]).some(d=>['Central','Pacific'].includes(d))?['Western_Wild_Card']:[])
 ];
 document.querySelectorAll('#nhl-standings-wild-cards input').forEach(el=>el.checked=nhlWildCards.includes(el.value));
 document.getElementById('english-enabled').checked=settings.sports.english.enabled;
 document.querySelectorAll('#english-leagues input').forEach(el=>el.checked=english.enabled_leagues.includes(el.value));
 document.querySelectorAll('#english-standings-leagues input').forEach(el=>el.checked=(settings.standings.leagues??english.enabled_leagues).includes(el.value));
 document.getElementById('english-mode').value=english.mode;
 document.getElementById('english-rotation').value=english.rotation_seconds;
 document.getElementById('english-refresh').value=english.refresh_seconds;
 await loadEnglishClubs(english.favorite_teams);
 for(const league of ['mls','nwsl']){
  const options=settings[league];
  document.getElementById(league+'-enabled').checked=settings.sports[league].enabled;
  document.querySelectorAll('#'+league+'-teams input').forEach(el=>el.checked=options.favorite_teams.includes(el.value));
  for(const key of ['mode','provider','rotation','refresh'])document.getElementById(league+'-'+key).value=options[key==='rotation'?'rotation_seconds':key==='refresh'?'refresh_seconds':key];
 }
 document.getElementById('mlb-enabled').checked=settings.sports.mlb.enabled;
 document.getElementById('nhl-enabled').checked=settings.sports.nhl.enabled;
 document.getElementById('nba-enabled').checked=settings.sports.nba.enabled;
 document.getElementById('wnba-enabled').checked=settings.sports.wnba.enabled;
 document.getElementById('nfl-enabled').checked=settings.sports.nfl.enabled;
 document.querySelectorAll('#nfl-teams input').forEach(el=>el.checked=nfl.favorite_teams.includes(el.value));
 document.getElementById('nfl-mode').value=nfl.mode;
 document.getElementById('nfl-rotation').value=nfl.rotation_seconds;
 document.getElementById('nfl-refresh').value=nfl.refresh_seconds;
 document.querySelectorAll('#wnba-teams input').forEach(el=>el.checked=wnba.favorite_teams.includes(el.value));
 document.getElementById('wnba-mode').value=wnba.mode;
 document.getElementById('wnba-rotation').value=wnba.rotation_seconds;
 document.getElementById('wnba-refresh').value=wnba.refresh_seconds;
 document.querySelectorAll('#nba-teams input').forEach(el=>el.checked=nba.favorite_teams.includes(el.value));
 document.getElementById('nba-mode').value=nba.mode;
 document.getElementById('nba-rotation').value=nba.rotation_seconds;
 document.getElementById('nba-refresh').value=nba.refresh_seconds;
 setNHLFavorites(nhl.favorite_teams);
 document.getElementById('nhl-mode').value=nhl.mode;
 document.getElementById('nhl-rotation').value=nhl.rotation_seconds;
 document.getElementById('nhl-refresh').value=nhl.refresh_seconds;
 setFavoriteTeams(mlb.favorite_teams);
 document.getElementById('mode').value=mlb.mode;
 document.getElementById('rotation').value=mlb.rotation_seconds;
 document.getElementById('refresh').value=mlb.refresh_seconds;
 document.getElementById('live-classic').value=mlb.live_classic_percent;
 document.getElementById('live-matchup').value=mlb.live_matchup_percent;
 updateLiveShare();
 refreshGameSelectionHelp();refreshEnglishCoverageSummary();
 refreshSportsOverview();refreshSportsRotationSummary();
 const enabled=['mlb','nhl','nba','wnba','nfl','mls','nwsl','english'].filter(s=>settings.sports[s]?.enabled);
 const favoriteCounts=enabled.map(s=>{const favorites=settings[s]?.favorite_teams||[];return s.toUpperCase()+': '+favorites.length+' favorites';});
 document.getElementById('summary').textContent=enabled.length+' enabled sports: '+enabled.map(s=>s.toUpperCase()).join(', ')+' | '+favoriteCounts.join(' · ');
}
function updateLiveShare(){
 const classic=Number(document.getElementById('live-classic').value);
 const matchup=Number(document.getElementById('live-matchup').value);
 const valid=Number.isInteger(classic)&&Number.isInteger(matchup)&&classic>=1&&matchup>=0&&classic+matchup<=100;
 const node=document.getElementById('live-play-share');
 node.textContent=valid?'Last Play: '+(100-classic-matchup)+'%':'Invalid allocation: Classic + Matchup must not exceed 100%.';
 return valid;
}
document.getElementById('live-classic').addEventListener('input',updateLiveShare);
document.getElementById('live-matchup').addEventListener('input',updateLiveShare);
let sportsSettingsDirty=false;
function markSportsSettingsDirty(event){
 if(!event.target.closest('#sports-configure')||event.target.id==='english-team-search')return;
 sportsSettingsDirty=true;
 document.getElementById('settings-status').textContent='Unsaved sport settings changes';
}
document.querySelector('[data-page="sports"]').addEventListener('input',markSportsSettingsDirty);
document.querySelector('[data-page="sports"]').addEventListener('change',markSportsSettingsDirty);
document.getElementById('english-teams').addEventListener('change',filterEnglishClubs);
function validateSportTiming(){
 for(const sport of ['mlb','nhl','nba','wnba','nfl','mls','nwsl','english']){
  for(const field of ['rotation','refresh']){
   const id=sport==='mlb'?field:sport+'-'+field;
   const input=document.getElementById(id);
   const value=Number(input.value);
   const minimum=sport==='mlb'?1:5;
   if(input.value.trim()===''||!Number.isFinite(value)||value<minimum||value>3600){
    input.focus();
    return sport.toUpperCase()+' '+field+' seconds must be between '+minimum+' and 3600.';
   }
  }
 }
 return null;
}
async function saveSportSettings(source){
 const status=document.getElementById('settings-status');
 const saveButton=document.getElementById('save-settings');
 if(saveButton.disabled)return;
 const timingError=validateSportTiming();
 if(timingError){status.textContent=timingError;return;}
 status.textContent='Saving…';
 const next=clone(settings);
 if(source==='sports'){
  next.mlb.favorite_teams=getFavoriteTeams();
  next.sports.mlb.enabled=document.getElementById('mlb-enabled').checked;
  next.sports.nhl.enabled=document.getElementById('nhl-enabled').checked;
  next.sports.nba.enabled=document.getElementById('nba-enabled').checked;
  next.sports.wnba.enabled=document.getElementById('wnba-enabled').checked;
  next.sports.nfl.enabled=document.getElementById('nfl-enabled').checked;
  next.sports.english.enabled=document.getElementById('english-enabled').checked;
  next.english.enabled_leagues=Array.from(document.querySelectorAll('#english-leagues input:checked'),el=>el.value);
  next.standings.leagues=Array.from(document.querySelectorAll('#english-standings-leagues input:checked'),el=>el.value);
  next.standings.mlb_divisions=Array.from(document.querySelectorAll('#mlb-standings-divisions input:checked'),el=>el.value);
  next.standings.nfl_divisions=Array.from(document.querySelectorAll('#nfl-standings-divisions input:checked'),el=>el.value);
   next.standings.mls_conferences=Array.from(document.querySelectorAll('#mls-standings-conferences input:checked'),el=>el.value);
   for(const league of ['nwsl','wnba'])next.standings[league]=document.getElementById(league+'-standings-enabled').checked;
  next.standings.nba_conferences=Array.from(document.querySelectorAll('#nba-standings-conferences input:checked'),el=>el.value);
  next.standings.nhl_divisions=Array.from(document.querySelectorAll('#nhl-standings-divisions input:checked'),el=>el.value);
  next.standings.nhl_wild_cards=Array.from(document.querySelectorAll('#nhl-standings-wild-cards input:checked'),el=>el.value);
  next.english.favorite_teams=Array.from(document.querySelectorAll('#english-teams input:checked'),el=>el.value);
  next.english.mode=document.getElementById('english-mode').value;
  next.english.rotation_seconds=Number(document.getElementById('english-rotation').value);
  next.english.refresh_seconds=Number(document.getElementById('english-refresh').value);
  for(const league of ['mls','nwsl']){
   next.sports[league].enabled=document.getElementById(league+'-enabled').checked;
   next[league].favorite_teams=Array.from(document.querySelectorAll('#'+league+'-teams input:checked'),el=>el.value);
   for(const key of ['mode','provider'])next[league][key]=document.getElementById(league+'-'+key).value;
   for(const key of ['rotation','refresh'])next[league][key+'_seconds']=Number(document.getElementById(league+'-'+key).value);
  }
  next.nfl.favorite_teams=Array.from(document.querySelectorAll('#nfl-teams input:checked'),el=>el.value);
  next.nfl.mode=document.getElementById('nfl-mode').value;
  next.nfl.rotation_seconds=Number(document.getElementById('nfl-rotation').value);
  next.nfl.refresh_seconds=Number(document.getElementById('nfl-refresh').value);
  next.wnba.favorite_teams=Array.from(document.querySelectorAll('#wnba-teams input:checked'),el=>el.value);
  next.wnba.mode=document.getElementById('wnba-mode').value;
  next.wnba.rotation_seconds=Number(document.getElementById('wnba-rotation').value);
  next.wnba.refresh_seconds=Number(document.getElementById('wnba-refresh').value);
  next.nba.favorite_teams=Array.from(document.querySelectorAll('#nba-teams input:checked'),el=>el.value);
  next.nba.mode=document.getElementById('nba-mode').value;
  next.nba.rotation_seconds=Number(document.getElementById('nba-rotation').value);
  next.nba.refresh_seconds=Number(document.getElementById('nba-refresh').value);
  if(!['mlb','nhl','nba','wnba','nfl','mls','nwsl','english'].some(league=>next.sports[league].enabled)){status.textContent='Enable at least one sport.';return;}
  if(!next.sports[next.active_sport].enabled)next.active_sport=['mlb','nhl','nba','wnba','nfl','mls','nwsl','english'].find(league=>next.sports[league].enabled);
  next.nhl.favorite_teams=getNHLFavorites();
  next.nhl.mode=document.getElementById('nhl-mode').value;
  next.nhl.rotation_seconds=Number(document.getElementById('nhl-rotation').value);
  next.nhl.refresh_seconds=Number(document.getElementById('nhl-refresh').value);
  if(!next.mlb.favorite_teams.length){status.textContent='MLB requires at least one favorite team, even when MLB is disabled.';document.querySelector('#favorite-teams input')?.focus();return;}
  next.mlb.mode=document.getElementById('mode').value;
 next.mlb.rotation_seconds=Number(document.getElementById('rotation').value);
 next.mlb.refresh_seconds=Number(document.getElementById('refresh').value);
 if(!updateLiveShare()){status.textContent='Fix the MLB live screen percentages before saving.';return;}
 next.mlb.live_classic_percent=Number(document.getElementById('live-classic').value);
 next.mlb.live_matchup_percent=Number(document.getElementById('live-matchup').value)}
 saveButton.disabled=true;
 try{
  const response=await fetch('/api/settings',{method:'POST',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify(next)});
  let result;
  try{result=await response.json()}catch(_){throw Error('Server returned an unreadable response (HTTP '+response.status+'). Check configurator logs.');}
  if(!response.ok)throw Error('Server rejected sport settings (HTTP '+response.status+'): '+(result.error||'Save failed'));
  settings=result.settings;
  sportsSettingsDirty=false;
  status.textContent='Sport settings saved.';
  try{await loadSettings();draw();await refreshStatus();status.textContent='Saved and applied to configurator preview.';}
  catch(refreshError){status.textContent='Settings saved, but the dashboard could not refresh: '+refreshError.message;}
 }catch(err){status.textContent='Settings not confirmed saved: '+(err instanceof TypeError?'Network error. Check connection and retry.':err.message);}
 finally{saveButton.disabled=false;}
}
document.getElementById('save-settings').onclick=()=>saveSportSettings('sports');
let updateAvailable=false;
let updateBranchData=null;
let updateBranchUserSelected=false;
function renderUpdateBranches(){
 if(!updateBranchData)return;
 const data=updateBranchData,picker=document.getElementById('update-branch');
 // The installed Git branch is authoritative on every page load. Preserve an
 // explicit in-page selection only when the user changes the dropdown.
 const selected=updateBranchUserSelected?picker.value:data.branch;
 const showAll=document.getElementById('update-show-all').checked;
 const branches=data.branches||[data.branch];
 const releaseMatch=new RegExp('^(feature|release)/([0-9]+[.][0-9]+)').exec(data.branch);
 const relevant=branches.filter(name=>name===data.branch||name==='main'||name==='master'||(releaseMatch&&name.startsWith(releaseMatch[1]+'/'+releaseMatch[2]+'.')));
 const visible=showAll?branches:relevant;
 picker.replaceChildren();
 for(const name of visible){const option=document.createElement('option');option.value=name;option.textContent=name;picker.appendChild(option)}
 picker.value=visible.includes(selected)?selected:(visible.includes(data.branch)?data.branch:visible[0]||'');
 updateAvailable=!!data.update_available||picker.value!==data.branch;
 document.getElementById('install-update').disabled=!updateAvailable;
}
async function checkSoftwareUpdate(){
 const out=document.getElementById('update-status'),button=document.getElementById('install-update');
 out.textContent='Checking Git remote…';button.disabled=true;updateAvailable=false;
 try{
  const response=await fetch('/api/update/check',{cache:'no-store'});
  const raw=await response.text();let data;try{data=JSON.parse(raw)}catch(_){throw Error('Update service returned a non-JSON response (HTTP '+response.status+'). Check web service logs.')}if(!response.ok)throw Error(data.error||'Check failed');
  updateBranchData=data;renderUpdateBranches();
  out.textContent='Branch: '+data.branch+' · Installed: '+data.installed.slice(0,8)+' · Remote: '+data.remote.slice(0,8)+(updateAvailable?' · Update available':' · Up to date');
  button.disabled=!updateAvailable;
 }catch(error){out.textContent='Update check failed: '+error.message}
 await refreshUpdateProgress();
}
function updateBranchChanged(){
 updateBranchUserSelected=true;
 updateAvailable=!!updateBranchData&&(document.getElementById('update-branch').value!==updateBranchData.branch||updateBranchData.update_available);
 document.getElementById('install-update').disabled=!updateAvailable;
 document.getElementById('update-status').textContent='Selected branch: '+document.getElementById('update-branch').value+'. Review before installing.';
}
async function copyUpdateLog(){
 const button=document.getElementById('copy-update-log');
 const value=document.getElementById('update-log').textContent;
 if(!value)return;
 try{
  if(navigator.clipboard&&window.isSecureContext){
   await navigator.clipboard.writeText(value);
  }else{
   const field=document.createElement('textarea');
   field.value=value;
   field.style.position='fixed';
   field.style.left='-9999px';
   document.body.appendChild(field);
   field.select();
   const copied=document.execCommand('copy');
   field.remove();
   if(!copied)throw new Error('Clipboard unavailable');
  }
  button.textContent='Copied!';
 }catch(error){
  button.textContent='Copy failed';
 }
}
async function refreshUpdateProgress(){
 try{
  const response=await fetch('/api/update/progress',{cache:'no-store'});
  if(!response.ok)return;
  const data=await response.json();
  const logElement=document.getElementById('update-log');
  const nextText=(data.status||'not started')+'\\n'+(data.log||'');
  if(logElement.textContent!==nextText){
   const pinned=logElement.scrollTop+logElement.clientHeight>=logElement.scrollHeight-24;
   const oldScroll=logElement.scrollTop;
   logElement.textContent=nextText;
   logElement.scrollTop=pinned?logElement.scrollHeight:oldScroll;
  }
  if(data.status==='running')document.getElementById('install-update').disabled=true;
  if(data.status==='completed'||data.status==='failed')document.getElementById('update-status').textContent='Last update: '+data.status+'. Review log below.';
 }catch(error){}
}
async function installSoftwareUpdate(){
 if(!updateAvailable||!confirm('Install the selected branch/update? Candidate tests will run before services restart.'))return;
 const out=document.getElementById('update-status');
 document.getElementById('install-update').disabled=true;
 try{
  const response=await fetch('/api/update/install',{method:'POST',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify({confirm:true,branch:document.getElementById('update-branch').value})});
  const raw=await response.text();let data;try{data=JSON.parse(raw)}catch(_){throw Error('Update endpoint returned a non-JSON response (HTTP '+response.status+'). Check web service logs before retrying.')}if(!response.ok)throw Error(data.error||'Update could not start');
  out.textContent='Update scheduled. The dashboard may briefly disconnect during restart.';
  await refreshUpdateProgress();
 }catch(error){out.textContent='Update error: '+error.message}
}
setInterval(()=>{const panel=document.querySelector('[data-page="system"]');if(panel&&!panel.hidden)refreshUpdateProgress()},2000);
async function restartScoreboard(){
 const button=document.getElementById('restart-scoreboard'),status=document.getElementById('restart-status');
 if(!confirm('Restart the web and matrix services now? The startup splash will appear.'))return;
 button.disabled=true;status.textContent='Requesting scoreboard restart…';
 try{
  const response=await fetch('/api/service/restart',{method:'POST',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify({confirm:true})});
  const result=await response.json();
  if(!response.ok)throw Error(result.error||'Restart failed');
  status.textContent='Restart scheduled. Waiting for the dashboard to return…';
  let restored=false;
  for(let attempt=0;attempt<15;attempt++){
   await new Promise(resolve=>setTimeout(resolve,1000));
   try{const health=await fetch('/health',{cache:'no-store'});if(health.ok&&attempt>=2){restored=true;break}}catch(error){}
  }
  status.textContent=restored?'Scoreboard service is responding again.':'Restart was requested, but the service has not responded yet. Check System status.';
 }catch(error){status.textContent='Restart failed: '+error.message}
 finally{button.disabled=false}
}
async function downloadBackup(){
 const button=document.getElementById('download-backup'),status=document.getElementById('backup-status');
 button.disabled=true;status.textContent='Preparing portable backup…';
 try{
  const response=await fetch('/api/backup/export',{cache:'no-store'});
  if(!response.ok){let error;try{error=(await response.json()).error}catch(_){}throw Error(error||'Backup download failed')}
  const blob=await response.blob(),url=URL.createObjectURL(blob);
  const link=document.createElement('a');link.href=url;const filename=response.headers.get('Content-Disposition')||'';const match=filename.match(/filename="?([^";]+)"?/i);link.download=match?match[1]:'uls-portable-backup-'+new Date().toISOString().slice(0,10)+'.zip';
  document.body.appendChild(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
  status.textContent='Portable backup downloaded. Matrix and device settings were excluded.';
 }catch(error){status.textContent='Backup failed: '+error.message}
 finally{button.disabled=false}
}
let pendingBackup=null;
async function backupRequest(mode,body){
 const response=await fetch('/api/backup/'+mode,{method:'POST',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify(body)});
 const result=await response.json();if(!response.ok)throw Error(result.error||'Backup operation failed');return result;
}
async function previewBackup(){
 const file=document.getElementById('import-backup-file').files[0],area=document.getElementById('import-backup-preview');
 document.getElementById('apply-backup').hidden=true;pendingBackup=null;area.textContent='';
 if(!file)return;
 if(file.size>8*1024*1024){area.textContent='Archive exceeds 8 MiB limit.';return}
 try{
  const bytes=new Uint8Array(await file.arrayBuffer());let binary='';for(let i=0;i<bytes.length;i+=8192)binary+=String.fromCharCode(...bytes.subarray(i,i+8192));
  const archive=btoa(binary);const result=await backupRequest('preview',{archive});
  pendingBackup=archive;
  const title=document.createElement('p');title.textContent='Validated portable backup. Select sections to restore:';area.appendChild(title);
  for(const [name,detail] of Object.entries(result.sections)){
   const label=document.createElement('label');label.style.display='block';
   const check=document.createElement('input');check.type='checkbox';check.value=name;check.className='backup-section';check.checked=detail.action!=='unchanged';
   label.append(check,document.createTextNode(' '+name+' ('+detail.action+')'));area.appendChild(label);
  }
  const warning=document.createElement('p');warning.textContent='Hardware, Wi-Fi, passwords and device identity will NOT be imported. A recovery snapshot is created before applying.';area.appendChild(warning);
  document.getElementById('apply-backup').hidden=false;
 }catch(error){area.textContent='Import preview failed: '+error.message}
}
async function applyBackup(){
 if(!pendingBackup)return;
 const sections=Array.from(document.querySelectorAll('.backup-section:checked')).map(input=>input.value);
 const area=document.getElementById('import-backup-preview'),button=document.getElementById('apply-backup');
 if(!sections.length){area.append(' Select at least one section.');return}
 if(!confirm('Restore '+sections.join(', ')+'? Current application settings will be backed up. Hardware and credentials remain unchanged.'))return;
 button.disabled=true;
 try{
  const result=await backupRequest('restore',{archive:pendingBackup,sections,confirm:true});
  area.textContent='Restored: '+result.sections.join(', ')+'. Recovery snapshot: '+result.recovery_directory+'. Restart scoreboard services to load restored settings.';
  button.hidden=true;pendingBackup=null;
 }catch(error){area.textContent='Restore failed: '+error.message}
 finally{button.disabled=false}
}
async function refreshStatus(){
 try{
  const response=await fetch('/api/status',{cache:'no-store'});
  if(!response.ok)throw Error('Status unavailable');
  const data=await response.json();
  document.getElementById('feed-status').textContent='MLB feed: '+data.feed.state+' | Cached games: '+data.feed.games+(data.feed.error?' | Error: '+data.feed.error:'');
  document.getElementById('feed-indicator').dataset.state=data.feed.error?'error':(data.feed.state==='ok'||data.feed.state==='healthy'?'healthy':'unknown');
  const when=timestamp=>timestamp?new Date(timestamp*1000).toLocaleString():'Not yet';
  document.getElementById('last-refresh').textContent='Last attempt: '+when(data.feed.last_attempt)+' | Last successful refresh: '+when(data.feed.last_success);
  const rotation=data.rotation||{};
  const selected=rotation.selected_sport?String(rotation.selected_sport).toUpperCase():'None';
  const priority=rotation.priority==='live'?'Live games first':rotation.priority==='normal'?'Normal rotation':'Unavailable';
  document.getElementById('current-game').textContent=(data.current_game?('Selected game: '+data.current_game.away+' @ '+data.current_game.home+' | '+data.current_game.status):'No game selected')+' | Selected sport: '+selected+' | '+priority;
  const sportGrid=document.getElementById('dashboard-sports');
  if(sportGrid){
   let healthy=0,staleCount=0,errorCount=0,starting=0,enabled=0;
   sportGrid.replaceChildren();
   for(const sport of (data.sports||[])){
    const card=document.createElement('div');card.className='dashboard-tile';
    const heading=document.createElement('h3');heading.textContent=sport.label;
    const active=rotation.selected_sport===sport.id;
    const live=Array.isArray(rotation.live_sports)&&rotation.live_sports.includes(sport.id);
    const detail=document.createElement('p');
    const activity=!sport.enabled?'Disabled':active?'Currently selected':live?'Live game available':'Enabled';
    const refreshed=sport.feed_last_success==null?'Never':when(sport.feed_last_success);
    const age=sport.feed_last_success==null?null:Math.max(0,Date.now()/1000-sport.feed_last_success);
    const stale=sport.enabled&&sport.feed_state==='running'&&age!==null&&age>Math.max(300,3*sport.refresh_seconds);
    const health=!sport.enabled?'Not monitored':sport.feed_state==='error'?'Error':stale?'Stale':sport.feed_state==='starting'?'Starting':sport.feed_state==='running'?'Healthy':'Unavailable';
    if(sport.enabled){enabled++;if(health==='Healthy')healthy++;else if(health==='Stale')staleCount++;else if(health==='Error')errorCount++;else starting++;}
    detail.textContent=activity+' | Rotation: '+sport.rotation_seconds+'s | Feed: '+health+(sport.feed_games==null?'':' | Games: '+sport.feed_games)+' | Last success: '+refreshed+(sport.feed_error?' | Error: '+sport.feed_error:'');
    if(active){card.style.borderColor='#d7b46d';card.setAttribute('aria-label',sport.label+' currently selected');}
    card.append(heading,detail);sportGrid.append(card);
   }
   const overview=document.getElementById('dashboard-sports-summary');
   if(overview)overview.textContent=enabled+' enabled | '+healthy+' healthy | '+staleCount+' stale | '+errorCount+' errors | '+starting+' starting or unavailable';
  }
  document.getElementById('system-info').textContent='Application: '+data.application+' | Board: '+data.board.width+' × '+data.board.height+' | Uptime: '+data.uptime_seconds+' seconds | Configurator: online';
 }catch(err){document.getElementById('feed-indicator').dataset.state='error';document.getElementById('feed-status').textContent=err.message;document.getElementById('system-info').textContent=err.message;const overview=document.getElementById('dashboard-sports-summary');if(overview)overview.textContent='Dashboard status unavailable: '+err.message;}
}
async function refreshWifiProfiles(){
 const target=document.getElementById('wifi-profiles');
 if(!target)return;
 try{
  const response=await fetch('/api/wifi/profiles',{cache:'no-store'});
  const data=await response.json();
  target.replaceChildren();
  if(!response.ok||!data.available)throw Error(data.error||'Profiles unavailable');
  if(!data.profiles.length){target.textContent='No saved Wi-Fi connections.';return;}
  for(const profile of data.profiles){
   const item=document.createElement('p');
   item.textContent=profile.ssid+(profile.active?' (connected on '+profile.interface+')':' (saved)')+(profile.name!==profile.ssid?' · '+profile.name:'');
   target.appendChild(item);
  }
 }catch(error){target.textContent='Saved profiles unavailable: '+error.message;}
}
async function refreshWifi(){
 const target=document.getElementById('wifi-info');
 try{
  const response=await fetch('/api/wifi',{cache:'no-store'});
  if(!response.ok)throw Error('Unable to read Wi-Fi status');
  const data=await response.json();
  target.replaceChildren();
  if(!data.available){target.textContent='NetworkManager unavailable';return;}
  const connected=(data.devices||[]).filter(d=>d.state==='connected');
  const headline=document.createElement('strong');
  headline.textContent=connected.length?'Connected: '+connected.map(d=>d.connection||d.device).join(', '):'Not connected';
  const details=document.createElement('p');details.className='muted';
  details.textContent='Wi-Fi radio: '+data.state+' · Interface: '+(data.devices||[]).map(d=>d.device).join(', ');
  const setup=document.createElement('p');setup.className='muted';
  setup.textContent='Fallback hotspot: not configured yet';
  target.append(headline,details,setup);
 }catch(err){target.textContent=err.message;}
}
async function refreshRecoveryReadiness(){
 const target=document.getElementById('wifi-recovery-readiness');
 try{
  const response=await fetch('/api/wifi/recovery-readiness',{cache:'no-store'});
  if(!response.ok)throw Error('Recovery readiness unavailable');
  const data=await response.json();
  const missing=Object.entries(data.checks||{}).filter(([key,ok])=>!ok).map(([key])=>key.replaceAll('_',' '));
  target.textContent=data.ready?'Recovery worker ready. Connection switching requires the separate Wi-Fi control helper.':'Recovery deployment preflight: incomplete ('+(missing.join(', ')||data.worker_reason||'unknown')+'). Install recovery and control helpers before switching.';
 }catch(err){target.textContent=err.message+'; verify helpers before switching.';}
}
let selectedWifi=null;
function selectWifiNetwork(network){
 selectedWifi=network;
 document.getElementById('wifi-selection').hidden=false;
 document.getElementById('wifi-selected-name').textContent=network.ssid;
 document.getElementById('wifi-selected-security').textContent='Security: '+network.security;
 const field=document.getElementById('wifi-password');field.value='';const saved=(window.savedWifiSsids||[]).includes(network.ssid);field.disabled=saved||network.security==='Open';field.placeholder=saved?'Saved credentials will be reused':(field.disabled?'No password required':'Enter Wi-Fi password');
}
async function saveHotspotPassword(){
 const output=document.getElementById('hotspot-result');
 const password=document.getElementById('hotspot-password').value;
 const confirm=document.getElementById('hotspot-confirm').value;
 if(password.length<8||password.length>63){output.textContent='Use 8 to 63 characters.';return;}
 if(password!==confirm){output.textContent='Passwords do not match.';return;}
 output.textContent='Saving hotspot password…';
 try{
  const response=await fetch('/api/wifi/control',{method:'POST',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify({action:'hotspot_password',password})});
  const result=await response.json();
  output.textContent=result.ok?'Hotspot password saved. Reconnect with the new password after the next hotspot activation.':(result.error||result.message||'Password update failed');
  if(result.ok){document.getElementById('hotspot-password').value='';document.getElementById('hotspot-confirm').value='';}
 }catch(error){output.textContent='Unable to save hotspot password.';}
}
async function connectWifi(){
 const output=document.getElementById('wifi-connect-result');
 if(!selectedWifi){output.textContent='Select a network first';return;}
 const password=document.getElementById('wifi-password').value;
 output.textContent='Requesting connection; rollback will remain armed until confirmed…';
 try{
  const wifi=await (await fetch('/api/wifi')).json();
  const current=(wifi.devices||[]).find(d=>d.state==='connected');
  if(!current||!current.connection)throw Error('No existing Wi-Fi connection to restore. Use Ethernet for initial setup.');
  const profiles=await (await fetch('/api/wifi/profiles')).json();
  const saved=(profiles.profiles||[]).find(p=>p.ssid===selectedWifi.ssid);
  const payload=saved?{action:'connect_saved',interface:current.device,previous_connection:current.connection,target_ssid:selectedWifi.ssid,profile_uuid:saved.uuid}:{action:'connect_new',interface:current.device,previous_connection:current.connection,target_ssid:selectedWifi.ssid,password};
  const response=await fetch('/api/wifi/control',{method:'POST',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify(payload)});
  const result=await response.json();
  if(!result.token)throw Error(result.error||'Unable to arm rollback');
  output.textContent=result.message+'. Confirming connectivity…';
  if(!result.ok)return;
  const observed=await (await fetch('/api/wifi',{cache:'no-store'})).json();
  if(!(observed.devices||[]).some(d=>d.state==='connected'&&d.device===current.device&&d.connection!==current.connection)){
   output.textContent='New connection not verified; rollback remains armed.';
   return;
  }
  const confirmation=await fetch('/api/wifi/control',{method:'POST',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify({action:'confirm',token:result.token})});
  const verified=await confirmation.json();
  output.textContent=verified.confirmed?'Connection confirmed.':'Rollback remains armed: '+(verified.error||verified.reason||'not confirmed');
  await Promise.all([refreshWifi(),refreshWifiProfiles(),scanWifi()]);
 }catch(err){output.textContent='Connection request failed: '+err.message+'; rollback will restore the previous connection if armed.';}
}
let lastWifiScan=[];
function renderWifiNetworks(networks){
 lastWifiScan=networks;
 // Reuses the MLB Scoreboard Configurator's network row + security/signal metadata layout.
 const target=document.getElementById('wifi-networks');target.replaceChildren();
 if(!networks.length){const empty=document.createElement('p');empty.className='muted';empty.textContent='No networks found.';target.append(empty);return;}
 networks.forEach(network=>{
  const item=document.createElement('div');item.className='item';
  item.style.display='flex';item.style.alignItems='center';item.style.justifyContent='space-between';item.style.gap='1rem';
  const details=document.createElement('div');details.style.minWidth='0';
  const name=document.createElement('strong');name.textContent=network.ssid;
  const meta=document.createElement('div');meta.className='muted';
  const connected=!!network.connected;
  const saved=(window.savedWifiSsids||[]).includes(network.ssid);
  meta.textContent=(network.security||'Open')+' · signal '+network.signal+'%'+(connected?' · Connected':'');
  details.append(name,meta);
  const select=document.createElement('button');select.type='button';
  select.textContent=connected?'Connected':(saved?'Connect saved':'Select');
  select.disabled=connected;
  select.onclick=()=>selectWifiNetwork(network);
  item.append(details,select);target.append(item);
 });
}
async function scanWifi(){
 const status=document.getElementById('wifi-scan-status');status.textContent='Scanning…';
 try{const response=await fetch('/api/wifi/scan',{cache:'no-store'});const data=await response.json();if(!response.ok||!data.available)throw Error(data.error||'Scan failed');
 const wifi=await (await fetch('/api/wifi',{cache:'no-store'})).json();
 const active=(wifi.devices||[]).filter(d=>d.state==='connected').map(d=>d.connection||'');
 const profiles=await (await fetch('/api/wifi/profiles',{cache:'no-store'})).json();
 window.savedWifiSsids=(profiles.profiles||[]).map(p=>p.ssid);
 const activeProfiles=(profiles.profiles||[]).filter(p=>p.active).map(p=>p.ssid||'');
 const networks=data.networks.map(n=>({...n,connected:activeProfiles.includes(n.ssid)||(!activeProfiles.length&&active.some(c=>c===n.ssid))}));
 status.textContent=networks.length+' network(s) found. Select a network to connect using the recovery-protected helper.';
 document.getElementById('wifi-selection').hidden=true;document.getElementById('wifi-password').value='';renderWifiNetworks(networks);
 }catch(err){status.textContent=err.message}
}
async function refreshDashboardRotation(){
 const target=document.getElementById('dashboard-rotation');
 if(!target)return;
 try{
  const response=await fetch('/api/rotation-status',{cache:'no-store'});
  if(!response.ok)throw Error('Rotation status unavailable');
  const data=await response.json();
  const names={mlb:'MLB',nhl:'NHL',nba:'NBA',wnba:'WNBA',nfl:'NFL',mls:'MLS',nwsl:'NWSL',english:'English Football'};
  const selected=data.selected_sport?(names[data.selected_sport]||data.selected_sport):'No eligible sport';
  const live=(data.live_sports||[]).map(s=>names[s]||s);
  target.textContent='Selected: '+selected+' | Priority: '+(data.priority==='live'?'Live games':'Normal rotation')+(live.length?' | Live: '+live.join(', '):'');
 }catch(error){target.textContent='Rotation status unavailable: '+error.message;}
}
async function refreshDashboardSystem(){
 const host=document.getElementById('dashboard-host');
 const hardware=document.getElementById('dashboard-hardware');
 if(!host||!hardware)return;
 try{
  const response=await fetch('/api/system',{cache:'no-store'});
  if(!response.ok)throw Error('System diagnostics unavailable');
  const data=await response.json();
  const service=data.service||{};
  host.textContent='Hostname: '+(data.hostname||'Unavailable')+' | Service: '+(service.state||'unknown')+' | Host uptime: '+(data.host_uptime_seconds==null?'Unavailable':data.host_uptime_seconds+'s');
  hardware.textContent='Device: '+(data.model||'Unknown')+' | Backend: '+(data.backend||'Unknown')+' | CPU: '+(data.temperature_c==null?'Unavailable':data.temperature_c+' °C')+' | Free disk: '+(data.disk_free_gb==null?'Unavailable':data.disk_free_gb+' GiB');
 }catch(error){host.textContent='System status unavailable: '+error.message;hardware.textContent='Hardware status unavailable';}
}
async function refreshSystem(){
 const target=document.getElementById('pi-info');
 try{
  const response=await fetch('/api/system',{cache:'no-store'});
  if(!response.ok)throw Error('System diagnostics unavailable');
  const data=await response.json();target.replaceChildren();
  const fields={'Device':data.model,'Hostname':data.hostname,'Operating system':data.os,'Python':data.python,'CPU temperature':data.temperature_c===null?'Unavailable':data.temperature_c+' °C','Free disk':data.disk_free_gb+' GiB','Host uptime':data.host_uptime_seconds===null?'Unavailable':data.host_uptime_seconds+' seconds','User service':data.service.state,'Service enabled':data.service.enabled||'Unknown','Output backend':data.backend,'LED hardware':data.led_hardware};
  Object.entries(fields).forEach(([label,value])=>{const box=document.createElement('div');box.className='item';const heading=document.createElement('strong');heading.textContent=label+': ';const body=document.createElement('span');body.textContent=String(value);box.append(heading,body);target.append(box)});
 }catch(err){target.textContent=err.message}
}
refreshStatus();setInterval(refreshStatus,10000);
refreshDashboardSystem();setInterval(refreshDashboardSystem,30000);
refreshDashboardRotation();setInterval(refreshDashboardRotation,10000);
load().catch(err=>document.getElementById('status').textContent=err.message);
loadSettings().catch(err=>document.getElementById('settings-status').textContent=err.message);
</script></body></html>'''

def dashboard_feed_status(status, *, unix_time=False, wall_now=None, monotonic_now=None):
    """Return a display-safe feed snapshot without altering worker timestamps."""
    result=dict(status)
    stamp=result.get('last_success')
    if stamp is not None and not unix_time:
        wall_now=time.time() if wall_now is None else wall_now
        monotonic_now=time.monotonic() if monotonic_now is None else monotonic_now
        result['last_success']=wall_now-(monotonic_now-stamp)
    return result

def make_handler(config_dir,token,frame_provider=None,settings_callback=None,feed_status=None,board_provider=None,countdown_status=None,standings_status=None,rotation_status=None,sports_feed_status=None,plugin_root=None,plugin_registry=None):
    started=time.monotonic()
    sessions=Sessions(config_dir)
    class Handler(BaseHTTPRequestHandler):
        def session_token(self):
            from http.cookies import SimpleCookie
            cookie=SimpleCookie()
            try:cookie.load(self.headers.get('Cookie',''))
            except Exception:return ''
            item=cookie.get('uls_session')
            return item.value if item else ''
        def authenticated(self):
            return sessions.valid(self.session_token())
        def send_login(self, error=False):
            body=LOGIN_HTML.replace("__LOGIN_ERROR__", '<p role="alert" class="login-error">Incorrect password. Please try again.</p>' if error else "").encode()
            self.send_response(200)
            self.send_header('Content-Type','text/html; charset=utf-8')
            self.send_header('Cache-Control','no-store')
            self.send_header('Content-Length',str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        def send_json(self,code,obj):
            body=json.dumps(obj).encode()
            self.send_response(code)
            self.send_header('Content-Type','application/json')
            self.send_header('Cache-Control','no-store')
            self.send_header('Content-Length',str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        def do_GET(self):
            path=urlsplit(self.path).path
            if path=='/login':
                self.send_login();return
            if path=='/health':
                self.send_json(200,{'status':'ok'});return
            # Public, read-only scoreboard surfaces. All configuration APIs stay private.
            if path in ('/board', '/frame.json'):
                if path == '/board':
                    body = BOARD_HTML.encode()
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.send_header('Cache-Control', 'no-store')
                    self.send_header('Content-Length', str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                elif board_provider is None:
                    self.send_json(503, {'error': 'Board emulator not configured'})
                else:
                    frame = board_provider()
                    from .web_preview import frame_payload
                    self.send_json(200, frame_payload(frame))
                return
            if not self.authenticated():
                if path=='/':
                    self.send_response(303);self.send_header('Location','/login');self.end_headers()
                elif path.startswith('/api/'):
                    self.send_json(401,{'error':'Authentication required'})
                else:
                    self.send_response(303);self.send_header('Location','/login');self.end_headers()
                return
            if path=='/':
                body=HTML.replace('__TOKEN__',json.dumps(token)).replace('__PREVIEW_VERSION__',display_version()).encode()
                self.send_response(200)
                self.send_header('Content-Type','text/html; charset=utf-8')
                self.send_header('Cache-Control','no-store')
                self.send_header('Content-Length',str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif path=='/api/backup/export':
                from .config_archive import export_portable
                import socket
                import re
                try:
                    body=export_portable(config_dir)
                    hostname=re.sub(r'[^A-Za-z0-9_-]+','-',socket.gethostname()).strip('-')[:63] or 'scoreboard'
                    filename='uls-'+hostname+'-portable-backup-'+time.strftime('%Y-%m-%d')+'.zip'
                    self.send_response(200)
                    self.send_header('Content-Type','application/zip')
                    self.send_header('Content-Disposition','attachment; filename="'+filename+'"')
                    self.send_header('Cache-Control','no-store')
                    self.send_header('X-Content-Type-Options','nosniff')
                    self.send_header('Content-Length',str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                except (OSError,ValueError) as exc:
                    self.send_json(500,{'error':str(exc)})
            elif path=='/api/plugins/hello-world/frame':
                try:
                    from .example_plugin_runner import render_hello_world
                    from .web_preview import frame_payload
                    self.send_json(200, frame_payload(render_hello_world()))
                except (OSError, ValueError, ImportError, AttributeError) as exc:
                    self.send_json(500, {'error': str(exc)})
            elif path=='/api/plugins/settings':
                from .plugin_registry import read_registry
                from .plugin_settings_schema import load_settings_schema
                from .plugin_settings_store import read_plugin_settings
                from .plugin_manifest import ManifestError
                from urllib.parse import parse_qs
                plugin_id = parse_qs(urlsplit(self.path).query).get('id', [''])[0]
                root = Path(plugin_root) if plugin_root is not None else Path('/var/lib/uls/plugins')
                registry = Path(plugin_registry) if plugin_registry is not None else Path('/var/lib/uls/plugins.json')
                try:
                    if plugin_id not in read_registry(registry):
                        raise ManifestError('Plugin is not installed')
                    package = root / plugin_id
                    fields = load_settings_schema(package)
                    values = read_plugin_settings(package, root.parent / 'plugin-settings', plugin_id)
                    self.send_json(200, {'id': plugin_id, 'fields': fields, 'values': values})
                except (ManifestError, OSError, ValueError) as exc:
                    self.send_json(400, {'error': str(exc)})
            elif path=='/api/plugins/inventory':
                from .plugin_inventory import installed_plugin_inventory
                try:
                    root = Path(plugin_root) if plugin_root is not None else Path('/var/lib/uls/plugins')
                    registry = Path(plugin_registry) if plugin_registry is not None else Path('/var/lib/uls/plugins.json')
                    inventory = installed_plugin_inventory(root, registry)
                    from .official_plugin_catalog import read_official_catalog
                    installed_ids = {item['id'] for item in inventory['plugins']}
                    inventory['official'] = [dict(item, installed=item['id'] in installed_ids)
                                             for item in read_official_catalog()]
                    self.send_json(200, inventory)
                except (OSError, ValueError) as exc:
                    self.send_json(500, {'error': str(exc)})
            elif path=='/api/config':
                try:self.send_json(200,read_config(config_dir))
                except (OSError,ValueError) as exc:self.send_json(500,{'error':str(exc)})
            elif path=='/api/matrix-status':
                try:
                    result=subprocess.run(['systemctl','is-active','uls-matrix.service'],capture_output=True,text=True,timeout=4)
                    state=result.stdout.strip() or 'unknown'
                    saved=load_matrix_settings(Path(config_dir)/'matrix.json')
                    desired=saved['enabled']
                    label=matrix_service_label(state,desired)
                    self.send_json(200,{'state':state,'running':state=='active',
                                        'configured_enabled':desired,'label':label})
                except (OSError,subprocess.TimeoutExpired):
                    self.send_json(503,{'error':'Matrix service status unavailable'})
            elif path=='/api/matrix-settings':
                try:self.send_json(200,load_matrix_settings(Path(config_dir)/'matrix.json'))
                except (OSError,ValueError) as exc:self.send_json(500,{'error':str(exc)})
            elif path=='/api/nhl-colors':
                from .config_store import read_nhl_colors
                try:self.send_json(200,read_nhl_colors(config_dir))
                except (OSError,ValueError) as exc:self.send_json(500,{'error':str(exc)})
            elif path=='/api/news-sources':
                from .news_settings import load_news_settings
                try:self.send_json(200,load_news_settings(config_dir))
                except (OSError,ValueError) as exc:self.send_json(500,{'error':str(exc)})
            elif path=='/api/season-countdown':
                from .season_countdown_settings import load
                try:self.send_json(200,load(config_dir))
                except (OSError,ValueError) as exc:self.send_json(500,{'error':str(exc)})
            elif path=='/api/season-countdown/status':
                if countdown_status is None:
                    self.send_json(503,{'error':'Countdown diagnostics unavailable'})
                else:
                    try:self.send_json(200,countdown_status())
                    except (OSError,ValueError,TypeError) as exc:self.send_json(500,{'error':str(exc)})
            elif path=='/api/time-weather':
                from .time_weather_settings import load_time_weather
                try:self.send_json(200,load_time_weather(config_dir))
                except (OSError,ValueError) as exc:self.send_json(500,{'error':str(exc)})
            elif path=='/api/english/clubs':
                from .english_clubs import cached_clubs
                try:self.send_json(200,{'clubs':cached_clubs()})
                except RuntimeError as exc:self.send_json(503,{'error':str(exc)})
            elif path=='/api/settings':
                from .sport_settings import load_settings
                try:self.send_json(200,load_settings(config_dir))
                except (OSError,ValueError) as exc:self.send_json(500,{'error':str(exc)})
            elif path=='/api/wifi/recovery-readiness':
                from .wifi_deployment_preflight import deployment_preflight
                self.send_json(200,deployment_preflight())
            elif path=='/api/wifi/scan':
                from .wifi_scan import scan_networks
                self.send_json(200,scan_networks())
            elif path=='/api/wifi/profiles':
                from .wifi_saved_profiles import saved_wifi_profiles
                self.send_json(200,saved_wifi_profiles())
            elif path=='/api/wifi':
                from .wifi_diagnostics import wifi_status
                self.send_json(200,wifi_status())
            elif path=='/api/update/check':
                try:
                    result=subprocess.run(['sudo','-n','/usr/local/libexec/uls-update-status'],capture_output=True,text=True,timeout=20,check=True)
                    self.send_json(200,json.loads(result.stdout))
                except (OSError,ValueError,subprocess.CalledProcessError,subprocess.TimeoutExpired):
                    self.send_json(503,{'error':'Update check unavailable; verify the privileged helper'})
            elif path=='/api/update/progress':
                root=Path('/var/lib/uls/update')
                try:
                    state=(root/'status').read_text(encoding='utf-8').strip()
                    # Keep complete updater output available in the dashboard. Cap at
                    # 2 MiB to avoid unbounded response sizes on broken installs.
                    log_path=root/'latest.log'
                    with log_path.open('rb') as stream:
                        log=stream.read(2 * 1024 * 1024 + 1)
                    if len(log)>2 * 1024 * 1024:
                        log=log[:2 * 1024 * 1024]+b'\\n[Log exceeds 2 MiB; view complete file over SSH.]'
                    log=log.decode('utf-8', errors='replace')
                except OSError:
                    state,log='not started',''
                self.send_json(200,{'status':state,'log':log})
            elif path=='/api/standings/diagnostics':
                if standings_status is None:
                    self.send_json(503,{'error':'Standings diagnostics not connected to running service'})
                else:
                    self.send_json(200,{'leagues':standings_status()})
            elif path=='/api/system':
                from .system_diagnostics import system_status
                self.send_json(200,system_status())
            elif path=='/api/rotation-status':
                self.send_json(200,rotation_status() if rotation_status else {'selected_sport':None,'priority':'unavailable','live_sports':[]})
            elif path=='/api/status':
                feed=feed_status() if feed_status else {'state':'unavailable','games':0,'error':None}
                game=frame_provider() if frame_provider else None
                current={'away':game.away,'home':game.home,'status':game.status} if game else None
                from .sport_settings import load_settings
                settings=load_settings(config_dir)
                labels={'mlb':'MLB','nhl':'NHL','nba':'NBA','wnba':'WNBA','nfl':'NFL','mls':'MLS','nwsl':'NWSL','english':'English Football'}
                feed_states=sports_feed_status() if sports_feed_status else {}
                sports=[{'id':name,'label':label,'enabled':settings['sports'][name]['enabled'],
                         'rotation_seconds':settings[name]['rotation_seconds'],
                         'refresh_seconds':settings[name]['refresh_seconds'],
                         'feed_state':feed_states.get(name,{}).get('state','unavailable'),
                         'feed_games':feed_states.get(name,{}).get('games'),
                         'feed_error':feed_states.get(name,{}).get('error'),
                         'feed_last_success':feed_states.get(name,{}).get('last_success')}
                        for name,label in labels.items()]
                self.send_json(200,{'application':'Universal LED Scoreboard','uptime_seconds':int(time.monotonic()-started),'board':{'width':64,'height':32,'backend':'emulator'},'feed':feed,'current_game':current,'sports':sports,'rotation':rotation_status() if rotation_status else {'selected_sport':None,'priority':'unavailable','live_sports':[]}})
            elif path=='/api/feed':
                self.send_json(200,feed_status() if feed_status else {'state':'unavailable'})
            elif path=='/api/defaults':
                from .colors import TEAM_COLORS,DEFAULT_SCOREBOARD
                from .nhl_colors import NHL_TEAM_COLORS
                self.send_json(200,{'teams':TEAM_COLORS,'scoreboard':DEFAULT_SCOREBOARD,'nhl_teams':NHL_TEAM_COLORS})
            elif path=='/health':
                self.send_json(200,{'status':'ok'})
            else:self.send_error(404)
        def do_POST(self):
            path=urlsplit(self.path).path
            if path=='/login':
                from urllib.parse import parse_qs
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=4096:
                    self.send_json(400,{'error':'Invalid login request'});return
                if self.headers.get('Content-Type','').split(';')[0].strip()!='application/x-www-form-urlencoded':
                    self.send_json(415,{'error':'Form required'});return
                password=parse_qs(self.rfile.read(size).decode('utf-8',errors='replace')).get('password',[''])[0]
                if not verify_password(config_dir,password):
                    time.sleep(0.5)
                    self.send_login(error=True);return
                session=sessions.create()
                self.send_response(303)
                self.send_header('Set-Cookie','uls_session='+session+'; HttpOnly; SameSite=Strict; Path=/; Max-Age=28800')
                self.send_header('Location','/')
                self.send_header('Cache-Control','no-store')
                self.end_headers();return
            if not self.authenticated():
                self.send_json(401,{'error':'Authentication required'});return
            if path=='/logout':
                if not secrets.compare_digest(self.headers.get('X-Configurator-Token',''),token):
                    self.send_json(403,{'error':'Invalid session token'});return
                sessions.revoke(self.session_token())
                self.send_response(204)
                self.send_header('Set-Cookie','uls_session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0')
                self.end_headers();return
            if path not in ('/api/mlb-colors','/api/nhl-colors','/api/config','/api/frame','/api/settings','/api/wifi/control','/api/service/restart','/api/news-sources','/api/time-weather','/api/weather-key','/api/season-countdown','/api/update/install','/api/matrix-settings','/api/matrix/apply','/api/backup/preview','/api/backup/restore','/api/plugins/enabled','/api/plugins/uninstall','/api/plugins/settings','/api/plugins/github/review','/api/plugins/bundled/install','/api/plugins/github/install','/api/plugins/github/update'):
                self.send_error(404);return
            if not secrets.compare_digest(self.headers.get('X-Configurator-Token',''),token):
                self.send_json(403,{'error':'Invalid session token'});return
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=(12*1024*1024 if path.startswith('/api/backup/') else 65536):
                    self.send_json(413,{'error':'Invalid request size'});return
                if self.headers.get('Content-Type','').split(';')[0].strip()!='application/json':
                    self.send_json(415,{'error':'JSON required'});return
                data=json.loads(self.rfile.read(size))
                if path=='/api/plugins/github/update':
                    from .plugin_github_update import update_reviewed_github_plugin
                    from .plugin_manifest import ManifestError
                    if (not isinstance(data,dict) or set(data)!={'source','commit','id','previous_source','confirm'}
                            or data['confirm'] is not True):
                        raise ValueError('Explicit pinned plugin update confirmation required')
                    root = Path(plugin_root) if plugin_root is not None else Path('/var/lib/uls/plugins')
                    registry = Path(plugin_registry) if plugin_registry is not None else Path('/var/lib/uls/plugins.json')
                    try:
                        self.send_json(200,update_reviewed_github_plugin(data['source'],data['commit'],data['id'],root,registry,previous_source=data['previous_source']))
                    except (ManifestError,ValueError,OSError,KeyError) as exc:
                        self.send_json(400,{'error':str(exc)})
                    return
                if path=='/api/plugins/github/install':
                    from .plugin_github_install import install_reviewed_github_plugin
                    from .plugin_manifest import ManifestError
                    if (not isinstance(data,dict) or set(data)!={'source','commit','id','confirm'}
                            or data['confirm'] is not True):
                        raise ValueError('Explicit pinned plugin installation confirmation required')
                    root = Path(plugin_root) if plugin_root is not None else Path('/var/lib/uls/plugins')
                    registry = Path(plugin_registry) if plugin_registry is not None else Path('/var/lib/uls/plugins.json')
                    try:
                        self.send_json(200,install_reviewed_github_plugin(data['source'],data['commit'],data['id'],root,registry))
                    except (ManifestError,ValueError,OSError,KeyError) as exc:
                        self.send_json(400,{'error':str(exc)})
                    return
                if path=='/api/plugins/bundled/install':
                    if data != {'id':'hello-world','confirm':True}:
                        raise ValueError('Explicit confirmation for bundled Hello World required')
                    from .example_plugin_install import install_example
                    from .plugin_manifest import ManifestError
                    root = Path(plugin_root) if plugin_root is not None else Path('/var/lib/uls/plugins')
                    registry = Path(plugin_registry) if plugin_registry is not None else Path('/var/lib/uls/plugins.json')
                    try:
                        self.send_json(200,install_example(root,registry))
                    except (ManifestError,OSError) as exc:
                        self.send_json(400,{'error':str(exc)})
                    return
                if path=='/api/plugins/github/review':
                    from .plugin_review import inspect_github_plugin
                    if not isinstance(data,dict) or set(data)!={'source'} or not isinstance(data['source'],str):
                        raise ValueError('Expected GitHub repository source URL')
                    try:
                        self.send_json(200,inspect_github_plugin(data['source']))
                    except (ValueError, KeyError, OSError) as exc:
                        from .plugin_source import parse_plugin_source
                        try:
                            parse_plugin_source(data['source'])
                        except ValueError:
                            import logging
                            logging.warning('Plugin review rejected source: length=%d repr=%r',
                                            len(data['source']),data['source'][:500])
                            self.send_json(400,{'error':'Invalid GitHub plugin URL; check server log for submitted source'})
                        else:
                            self.send_json(400,{'error':str(exc)})
                    return
                if path=='/api/plugins/settings':
                    from .plugin_registry import read_registry
                    from .plugin_settings_store import save_plugin_settings
                    from .plugin_manifest import ManifestError
                    if not isinstance(data, dict) or set(data) != {'id', 'values'} or not isinstance(data['id'], str):
                        raise ValueError('Expected plugin id and values')
                    root = Path(plugin_root) if plugin_root is not None else Path('/var/lib/uls/plugins')
                    registry = Path(plugin_registry) if plugin_registry is not None else Path('/var/lib/uls/plugins.json')
                    try:
                        if data['id'] not in read_registry(registry):
                            raise ManifestError('Plugin is not installed')
                        values = save_plugin_settings(root / data['id'], root.parent / 'plugin-settings',
                                                      data['id'], data['values'])
                        self.send_json(200, {'id': data['id'], 'values': values})
                    except (ManifestError, OSError, ValueError) as exc:
                        self.send_json(400, {'error': str(exc)})
                    return
                if path=='/api/plugins/uninstall':
                    from .plugin_registry import uninstall_plugin
                    from .plugin_manifest import ManifestError
                    if (not isinstance(data,dict) or set(data)!={'id','confirm'}
                            or not isinstance(data['id'],str) or data['confirm'] is not True):
                        raise ValueError('Explicit plugin uninstall confirmation required')
                    root = Path(plugin_root) if plugin_root is not None else Path('/var/lib/uls/plugins')
                    registry = Path(plugin_registry) if plugin_registry is not None else Path('/var/lib/uls/plugins.json')
                    try:
                        removed = uninstall_plugin(root,registry,data['id'])
                        self.send_json(200,{'id':removed['id'],'removed':True,'data_preserved':True})
                    except (ManifestError,OSError,ValueError) as exc:
                        self.send_json(400,{'error':str(exc)})
                    return
                if path=='/api/plugins/enabled':
                    from .plugin_inventory import installed_plugin_inventory
                    from .plugin_registry import set_plugin_enabled
                    from .plugin_manifest import ManifestError
                    if not isinstance(data,dict) or set(data)!={'id','enabled'} or type(data['enabled']) is not bool:
                        raise ValueError('Expected plugin id and boolean enabled')
                    root = Path(plugin_root) if plugin_root is not None else Path('/var/lib/uls/plugins')
                    registry = Path(plugin_registry) if plugin_registry is not None else Path('/var/lib/uls/plugins.json')
                    inventory = installed_plugin_inventory(root,registry)
                    matching = [item for item in inventory['plugins'] if item['id']==data['id']]
                    if not matching:
                        raise ValueError('Plugin is not installed')
                    if matching[0]['error']:
                        raise ValueError('Plugin package is invalid: '+matching[0]['error'])
                    self.send_json(200,set_plugin_enabled(registry,data['id'],data['enabled']))
                    return
                if path in ('/api/backup/preview','/api/backup/restore'):
                    import base64
                    from .config_archive import inspect_portable, validate_portable_sections, restore_portable
                    encoded=data.get('archive','') if isinstance(data,dict) else ''
                    if not isinstance(encoded,str) or len(encoded)>12*1024*1024:
                        raise ValueError('Invalid backup payload')
                    try:
                        archive_bytes=base64.b64decode(encoded,validate=True)
                    except (ValueError,base64.binascii.Error) as exc:
                        raise ValueError('Invalid backup encoding') from exc
                    if path=='/api/backup/preview':
                        self.send_json(200,validate_portable_sections(archive_bytes,config_dir))
                    else:
                        if data.get('confirm') is not True:
                            raise ValueError('Explicit restore confirmation required')
                        self.send_json(200,restore_portable(archive_bytes,config_dir,data.get('sections')))
                    return
                if path=='/api/matrix/apply':
                    if data != {'confirm':True}:
                        raise ValueError('Explicit matrix apply confirmation required')
                    try:
                        result=subprocess.run(['sudo','-n','/usr/local/libexec/uls-matrix-control','apply'],
                                              capture_output=True,text=True,timeout=20)
                    except (OSError,subprocess.TimeoutExpired):
                        self.send_json(503,{'error':'Matrix helper unavailable or timed out'});return
                    if result.returncode:
                        self.send_json(503,{'error':'Matrix service apply failed. Check matrix service logs.'});return
                    self.send_json(200,{'applied':True});return
                if path=='/api/matrix-settings':
                    import tempfile
                    settings=validate_matrix_settings(data)
                    target=Path(config_dir)/'matrix.json'
                    temporary=None
                    try:
                        with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=target.parent,
                                                         prefix='.matrix-',suffix='.tmp',delete=False) as out:
                            temporary=Path(out.name)
                            os.chmod(out.name,0o600)
                            json.dump(settings,out)
                            out.flush()
                            os.fsync(out.fileno())
                        os.replace(temporary,target)
                    finally:
                        if temporary is not None:
                            temporary.unlink(missing_ok=True)
                    self.send_json(200,{'saved':True,'restart_required':True,'settings':settings});return
                if path=='/api/mlb-colors':
                    from .colors import normalize_team_colors, TEAM_COLORS
                    updates=normalize_team_colors(data)
                    if set(updates)-set(TEAM_COLORS):raise ValueError('Unknown MLB team')
                    merged=read_config(config_dir)['teams']
                    merged.update(updates)
                    save_config(config_dir,'teams',merged)
                    self.send_json(200,{'saved':True});return
                if path=='/api/nhl-colors':
                    from .config_store import read_nhl_colors
                    from .colors import normalize_team_colors
                    from .nhl_colors import NHL_TEAM_COLORS
                    updates=normalize_team_colors(data)
                    if set(updates)-set(NHL_TEAM_COLORS):raise ValueError('Unknown NHL team')
                    merged=read_nhl_colors(config_dir)
                    merged.update(updates)
                    save_config(config_dir,'nhl_teams',merged)
                    self.send_json(200,{'saved':True});return
                if path=='/api/update/install':
                    import re
                    branch=data.get('branch') if isinstance(data,dict) else None
                    if data.get('confirm') is not True or not isinstance(branch,str) or not re.fullmatch(r'[A-Za-z0-9._/-]{1,160}',branch) or '..' in branch or branch.startswith('/') or branch.endswith('/'):
                        raise ValueError('Explicit confirmation and valid branch required')
                    try:
                        subprocess.run(['sudo','-n','/usr/local/libexec/uls-update-select'],
                                       input=branch,text=True,capture_output=True,timeout=5,check=True)
                    except (OSError,subprocess.TimeoutExpired,subprocess.CalledProcessError):
                        self.send_json(503,{'error':'Unable to select update branch'});return
                    try:
                        subprocess.run(['sudo','-n','/usr/local/libexec/uls-update-launch'],capture_output=True,text=True,timeout=10,check=True)
                    except (OSError,subprocess.TimeoutExpired,subprocess.CalledProcessError):
                        self.send_json(503,{'error':'Update could not be scheduled; check service logs or concurrent update'})
                        return
                    self.send_json(202,{'ok':True,'message':'Update scheduled'})
                    return
                if path=='/api/service/restart':
                    if data != {'confirm':True}:
                        raise ValueError('Explicit restart confirmation required')
                    # The configurator may be hosted by the service being restarted.
                    # Reply before invoking systemctl so the HTTP request is not killed.
                    def restart_after_response():
                        time.sleep(0.75)
                        try:
                            subprocess.run(['sudo','-n','/usr/local/libexec/uls-restart-services'],
                                           capture_output=True,text=True,timeout=10,check=True)
                        except (OSError,subprocess.TimeoutExpired,subprocess.CalledProcessError) as exc:
                            print(f'Dashboard restart scheduling failed: {exc}', flush=True)
                    self.send_json(202,{'ok':True,'message':'Both scoreboard services restart scheduled'})
                    threading.Thread(target=restart_after_response,daemon=True,name='scoreboard-restart').start()
                    return
                if path=='/api/wifi/control':
                    from .wifi_web_bridge import request_wifi_change
                    if not isinstance(data,dict) or data.get('action') not in ('connect_saved','connect_new','confirm','hotspot','hotspot_password'):
                        raise ValueError('Unsupported Wi-Fi operation')
                    result=request_wifi_change(data)
                    self.send_json(200 if result.get('ok') or result.get('confirmed') else 409,result)
                    return
                if path=='/api/news-sources':
                    from .news_settings import save_news_settings
                    self.send_json(200,{'saved':True,'settings':save_news_settings(config_dir,data)})
                    return
                if path=='/api/weather-key':
                    from .weather_credentials import save_openweathermap_key
                    if not isinstance(data,dict) or set(data)!={'api_key'}:
                        raise ValueError('Expected API key')
                    save_openweathermap_key(config_dir,data['api_key'])
                    self.send_json(200,{'saved':True})
                    return
                if path=='/api/season-countdown':
                    self.send_json(200,{'saved':True,'settings':save_config(config_dir,'season_countdown',data)})
                    return
                if path=='/api/time-weather':
                    from .time_weather_settings import save_time_weather
                    self.send_json(200,{'saved':True,'settings':save_time_weather(config_dir,data)})
                    return
                if path=='/api/settings':
                    from .sport_settings import save_settings
                    saved_settings=save_settings(config_dir,data)
                    if settings_callback:settings_callback(saved_settings)
                    self.send_json(200,{'saved':True,'settings':saved_settings})
                    return
                if not isinstance(data,dict) or not isinstance(data.get('teams'),dict) or not isinstance(data.get('scoreboard'),dict):
                    raise ValueError('Expected teams and scoreboard objects')
                from .colors import normalize_team_colors,normalize_scoreboard_colors
                teams=normalize_team_colors(data['teams'])
                colors=normalize_scoreboard_colors(data['scoreboard'])
                if path=='/api/frame':
                    game=(frame_provider() if frame_provider else None) or BaseballGame()
                    requested=data.get('preview_team')
                    if requested in teams and requested not in (game.away,game.home):
                        game=BaseballGame(away='NYM' if requested!='NYM' else 'ATL',home=requested)
                    frame=MLBPaletteScreen(game,teams,colors).render()
                    self.send_json(200,{'width':64,'height':32,'pixels':[p for row in frame.pixels for p in row]})
                else:
                    # Validate both sections before writing either.
                    save_config(config_dir,'teams',teams)
                    save_config(config_dir,'scoreboard',colors)
                    self.send_json(200,{'saved':True})
            except (ValueError,TypeError,json.JSONDecodeError) as exc:
                self.send_json(400,{'error':str(exc)})
            except OSError as exc:
                self.send_json(500,{'error':str(exc)})
    return Handler

def persistent_form_token(directory):
    """Keep the form CSRF token stable across web service restarts.

    Authentication still requires the separate, revocable session cookie.
    """
    path = Path(directory) / 'form_token'
    try:
        value = path.read_text(encoding='ascii').strip()
        if len(value) < 32:
            raise ValueError('Invalid form token')
        return value
    except FileNotFoundError:
        pass
    value = secrets.token_urlsafe(32)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open('x', encoding='ascii') as stream:
            os.chmod(path, 0o600)
            stream.write(value + '\n')
    except FileExistsError:
        return persistent_form_token(directory)
    return value

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--host',default='0.0.0.0')
    p.add_argument('--port',type=int,default=8080)
    p.add_argument('--config-dir',default=str(Path.home()/'.config/universal-led-scoreboard'))
    p.add_argument('--team',default='ATL')
    p.add_argument('--date')
    p.add_argument('--set-admin-password',action='store_true',help='Set or reset administrator password and exit')
    args=p.parse_args()
    if args.set_admin_password:
        configure_cli(args.config_dir)
        print('Administrator password saved. Existing sessions will be invalidated.')
        return
    if not (Path(args.config_dir)/'admin.json').exists():
        p.error('Administrator password missing. Run python3 -m universal_led.configurator --set-admin-password first.')
    token=persistent_form_token(args.config_dir)
    from .runtime_settings import ConfiguredMLBRenderer
    from .sport_settings import load_settings
    initial=load_settings(args.config_dir)
    feed=BackgroundMLBFeed(MLBFeed(team=None,date=args.date,refresh_seconds=initial['mlb']['refresh_seconds']))
    feed.start()
    from .news_background import BackgroundNews
    news=BackgroundNews(args.config_dir)
    from .weather_worker import WeatherWorker
    weather=WeatherWorker(args.config_dir)
    renderer=ConfiguredMLBRenderer(args.config_dir,feed,news=news,weather=weather)
    weather.start()
    news.start(renderer.settings)
    # NHL remains opt-in. Both browser and matrix consume the same routed frame.
    from .nhl_feed import NHLFeed
    from .nhl_runtime import BackgroundNHLFeed
    from .nhl_engine import ConfiguredNHLRenderer
    from .multisport_runtime import MultiSportRenderer
    nhl_feed = BackgroundNHLFeed(NHLFeed())
    from .scoring_alerts import ScoringAlerts
    scoring_alerts = ScoringAlerts()
    nhl_renderer = ConfiguredNHLRenderer(nhl_feed, config_dir=args.config_dir, scoring_alerts=scoring_alerts)
    from .nba_feed import NBAFeed
    from .nba_runtime import BackgroundNBAFeed
    from .nba_engine import ConfiguredNBARenderer
    nba_feed = BackgroundNBAFeed(NBAFeed())
    nba_renderer = ConfiguredNBARenderer(nba_feed, scoring_alerts=scoring_alerts, league='NBA')
    from .wnba_feed import WNBAFeed
    from .wnba_engine import ConfiguredWNBARenderer
    wnba_feed = BackgroundNBAFeed(WNBAFeed())
    wnba_renderer = ConfiguredWNBARenderer(wnba_feed, scoring_alerts=scoring_alerts, league='WNBA')
    from .nfl_feed import NFLFeed
    from .nfl_runtime import BackgroundNFLFeed
    from .nfl_engine import ConfiguredNFLRenderer
    nfl_feed = BackgroundNFLFeed(NFLFeed())
    nfl_renderer = ConfiguredNFLRenderer(nfl_feed, scoring_alerts=scoring_alerts)
    # Track game completion on background refresh, independent of which
    # sport is currently displayed. The handoff remains opt-in until the
    # live-rotation policy and exact-game renderers are fully integrated.
    from .final_score_handoff import FinalScoreHandoff
    final_handoff = FinalScoreHandoff()
    def observe_finals(sport, games):
        final_handoff.observe(sport, games, id_getter=lambda game: game.game_id)
    # Observe score changes as feeds refresh, even when another sport owns the display.
    nhl_feed.on_games = lambda games: (nhl_renderer.score_observer.observe(games, favorite_teams=nhl_renderer.favorite_teams), observe_finals('nhl', games))
    nfl_feed.on_games = lambda games: nfl_renderer.score_observer.observe(games, favorite_teams=nfl_renderer.favorite_teams)
    from .mlb_score_alerts import MLBRunObserver
    mlb_run_observer = MLBRunObserver(scoring_alerts, lambda: renderer.settings()['mlb']['favorite_teams'])
    feed.on_games = mlb_run_observer.observe
    from .score_change_observer import BasketballMomentObserver
    nba_score_observer = BasketballMomentObserver(scoring_alerts, 'nba', 'NBA')
    wnba_score_observer = BasketballMomentObserver(scoring_alerts, 'wnba', 'WNBA')
    nba_feed.on_games = lambda games: (nba_score_observer.observe(games, favorite_teams=nba_renderer.favorite_teams),
                                       observe_finals('nba', games))
    wnba_feed.on_games = lambda games: (wnba_score_observer.observe(games, favorite_teams=wnba_renderer.favorite_teams),
                                        observe_finals('wnba', games))
    from .soccer_data import SoccerFeed, fetch_scores
    from .soccer_runtime import BackgroundSoccerFeed
    from .soccer_engine import ConfiguredSoccerRenderer
    from .soccer_feed import parse_scoreboard
    from .soccer_providers import SoccerProviderRouter
    from .soccer_native_http import NativeLeagueProvider
    # Native URLs are opt-in until the league-specific API contract is verified.
    # ESPN remains a safe fallback without requiring credentials.
    # One shared queue for every soccer league. Opt-in settings are introduced
    # separately; disabled by default so existing installations are unchanged.
    soccer_workers = {}
    soccer_renderers = {}
    for league in ('MLS', 'NWSL'):
        key = league.lower()
        native_url = os.environ.get('ULS_' + league + '_API_URL', '').strip()
        primary = (NativeLeagueProvider(league, url_template=native_url)
                   if native_url else None)
        fallback = lambda day, name=league: parse_scoreboard(fetch_scores(name, day), name)
        router = SoccerProviderRouter(league, primary=primary, fallback=fallback)
        soccer_feed = SoccerFeed(league, provider=router)
        soccer_renderer = ConfiguredSoccerRenderer(soccer_feed, league=league, scoring_alerts=scoring_alerts)
        soccer_worker = BackgroundSoccerFeed(soccer_feed, on_match=soccer_renderer.update)
        soccer_workers[key] = soccer_worker
        soccer_renderers[key] = soccer_renderer
    from .english_football import COMPETITIONS
    from .english_rotation import EnglishFootballRenderer
    from .english_goals import EnglishGoalEnricher
    english_goal_enricher = EnglishGoalEnricher()
    english_feeds = {league: SoccerFeed(league, enrich=english_goal_enricher) for league in COMPETITIONS}
    english_renderer = EnglishFootballRenderer(english_feeds, scoring_alerts=scoring_alerts)
    english_workers = {
        league: BackgroundSoccerFeed(english_feeds[league], on_match=english_renderer.update)
        for league in COMPETITIONS
    }
    from .football_standings_runtime import FootballStandingsCache, BackgroundFootballStandings
    from .standings_rotation import StandingsRotation
    standings_caches = {
        league: FootballStandingsCache(league, refresh_seconds=initial['standings']['refresh_seconds'],
                                     cache_dir=Path(args.config_dir) / 'standings-cache')
        for league in COMPETITIONS
    }
    standings_workers = {
        league: BackgroundFootballStandings(cache)
        for league, cache in standings_caches.items()
    }
    from .mlb_standings_feed import DIVISION_KEYS, WILD_CARD_KEYS, fetch_mlb_group, fetch_mlb_wild_card_group
    mlb_standings_caches = {
        division: FootballStandingsCache(
            'MLB', fetcher=lambda _league, group=division: fetch_mlb_group(group),
            refresh_seconds=initial['standings']['refresh_seconds'],
            cache_dir=Path(args.config_dir) / 'standings-cache',
            cache_key='mlb-' + division.lower())
        for division in DIVISION_KEYS.values()
    }
    mlb_standings_caches.update({
        group: FootballStandingsCache(
            'MLB', fetcher=lambda _league, key=group: fetch_mlb_wild_card_group(key),
            refresh_seconds=initial['standings']['refresh_seconds'],
            cache_dir=Path(args.config_dir) / 'standings-cache',
            cache_key='mlb-' + group.lower())
        for group in WILD_CARD_KEYS
    })
    mlb_standings_workers = {
        division: BackgroundFootballStandings(cache)
        for division, cache in mlb_standings_caches.items()
    }
    from .nhl_standings_feed import NHL_DIVISIONS, NHL_WILD_CARD_GROUPS, fetch_nhl_division, fetch_nhl_wild_card
    nhl_standings_caches = {
        division: FootballStandingsCache(
            'NHL', fetcher=lambda _league, group=division: fetch_nhl_division(group),
            refresh_seconds=initial['standings']['refresh_seconds'],
            cache_dir=Path(args.config_dir) / 'standings-cache',
            cache_key='nhl-' + division.lower())
        for division in NHL_DIVISIONS
    }
    nhl_standings_caches.update({
        group: FootballStandingsCache(
            'NHL', fetcher=lambda _league, key=group: fetch_nhl_wild_card(key),
            refresh_seconds=initial['standings']['refresh_seconds'],
            cache_dir=Path(args.config_dir) / 'standings-cache',
            cache_key='nhl-' + group.lower())
        for group in NHL_WILD_CARD_GROUPS
    })
    nhl_standings_workers = {
        division: BackgroundFootballStandings(cache)
        for division, cache in nhl_standings_caches.items()
    }
    standings_caches.update(mlb_standings_caches)
    standings_caches.update(nhl_standings_caches)
    from .nba_standings_feed import NBA_CONFERENCES, fetch_nba_conference
    nba_standings_caches = {
        conference: FootballStandingsCache(
            'NBA', fetcher=lambda _league, group=conference: fetch_nba_conference(group),
            refresh_seconds=initial['standings']['refresh_seconds'],
            cache_dir=Path(args.config_dir) / 'standings-cache',
            cache_key='nba-' + conference.lower(), expected_group=conference)
        for conference in NBA_CONFERENCES
    }
    nba_standings_workers = {
        conference: BackgroundFootballStandings(cache)
        for conference, cache in nba_standings_caches.items()
    }
    standings_caches.update(nba_standings_caches)
    from .nfl_standings_feed import NFL_DIVISIONS, fetch_nfl_division
    nfl_standings_caches = {
        division: FootballStandingsCache(
            'NFL', fetcher=lambda _league, group=division: fetch_nfl_division(group),
            refresh_seconds=initial['standings']['refresh_seconds'],
            cache_dir=Path(args.config_dir) / 'standings-cache',
            cache_key='nfl-' + division.lower().replace(' ', '-'),
            expected_group=division)
        for division in NFL_DIVISIONS
    }
    nfl_standings_workers = {
        division: BackgroundFootballStandings(cache)
        for division, cache in nfl_standings_caches.items()
    }
    standings_caches.update(nfl_standings_caches)
    from .mls_standings_feed import MLS_CONFERENCES, fetch_mls_conference
    mls_standings_caches = {
        conference: FootballStandingsCache(
            'MLS', fetcher=lambda _league, group=conference: fetch_mls_conference(group),
            refresh_seconds=initial['standings']['refresh_seconds'],
            cache_dir=Path(args.config_dir) / 'standings-cache',
            cache_key='mls-' + conference.lower().replace(' ', '-'),
            expected_group=conference)
        for conference in MLS_CONFERENCES
    }
    mls_standings_workers = {
        conference: BackgroundFootballStandings(cache)
        for conference, cache in mls_standings_caches.items()
    }
    standings_caches.update(mls_standings_caches)
    from .nwsl_standings_feed import fetch_nwsl_standings
    from .wnba_standings_feed import fetch_wnba_standings
    single_table_caches = {
        league: FootballStandingsCache(
            league, fetcher=fetcher,
            refresh_seconds=initial['standings']['refresh_seconds'],
            cache_dir=Path(args.config_dir) / 'standings-cache',
            cache_key=league.lower() + '-standings',
            expected_group=league)
        for league, fetcher in (('NWSL', fetch_nwsl_standings),
                                ('WNBA', fetch_wnba_standings))
    }
    single_table_workers = {
        league: BackgroundFootballStandings(cache)
        for league, cache in single_table_caches.items()
    }
    standings_caches.update(single_table_caches)
    from .standings_season_status import StandingsSeasonStatus
    from .standings_season_worker import SeasonCalendarWorker
    from .mlb_season_calendar import fetch_mlb_season_windows
    from .nhl_season_calendar import fetch_nhl_season_windows
    season_status = StandingsSeasonStatus()
    mlb_season_worker = SeasonCalendarWorker(
        'MLB', fetch_mlb_season_windows, season_status)
    nhl_season_worker = SeasonCalendarWorker(
        'NHL', fetch_nhl_season_windows, season_status)
    # Opt-in only: without a verified provider URL, preserve existing NBA pages.
    from .nba_season_provider import fetch_nba_season_windows
    nba_calendar_url = os.environ.get('ULS_NBA_SEASON_CALENDAR_URL', '').strip()
    nba_season_worker = (
        SeasonCalendarWorker('NBA',
            lambda competition: fetch_nba_season_windows(competition, url=nba_calendar_url),
            season_status)
        if nba_calendar_url.startswith('https://') else None)
    def standings_season_eligible(competition):
        if competition in mlb_standings_caches:
            return season_status.eligible('MLB')
        if competition in nhl_standings_caches:
            return (season_status.eligible('NHL') and
                    any(row.played > 0 for row in nhl_standings_caches[competition].rows()))
        if competition in single_table_caches:
            return any(row.played > 0 for row in single_table_caches[competition].rows())
        if competition in mls_standings_caches:
            return any(row.played > 0 for row in mls_standings_caches[competition].rows())
        if competition in nfl_standings_caches:
            return any(row.played > 0 for row in nfl_standings_caches[competition].rows())
        if competition in nba_standings_caches and nba_season_worker is not None:
            return season_status.eligible('NBA')
        return True
    standings_rotation = StandingsRotation(
        standings_caches, season_policy=standings_season_eligible)
    renderer.news = None  # Universal news is owned by the shared board scheduler.
    board = MultiSportRenderer(renderer, nhl_renderer, news=news, settings_getter=renderer.settings, nba_renderer=nba_renderer, wnba_renderer=wnba_renderer, nfl_renderer=nfl_renderer, mls_renderer=soccer_renderers['mls'], nwsl_renderer=soccer_renderers['nwsl'], english_renderer=english_renderer, scoring_alerts=scoring_alerts, standings_rotation=standings_rotation)
    # Apply persisted sport choice on service startup, not just after web saves.
    def game():
        return board.game()
    def apply_settings(settings):
        from .game_interruptions import InterruptionPolicy
        interruption_policy = InterruptionPolicy(**settings['game_interruptions'])
        for sport_renderer in (*soccer_renderers.values(), english_renderer,
                               nhl_renderer, nba_renderer, wnba_renderer, nfl_renderer):
            sport_renderer.interruption_policy = interruption_policy
        scoring_alerts.configure(**settings['scoring_alerts'])
        renderer.apply(settings)
        feed.feed.refresh_seconds=settings['mlb']['refresh_seconds']
        from .time_weather_settings import load_time_weather
        time_preferences = load_time_weather(args.config_dir)
        nhl_feed.set_timezone(time_preferences['timezone'])
        nba_feed.set_timezone(time_preferences['timezone'])
        wnba_feed.set_timezone(time_preferences['timezone'])
        nfl_feed.set_timezone(time_preferences['timezone'])
        nfl_renderer.timezone_name = time_preferences['timezone']
        nfl_renderer.time_format = time_preferences['time_format']
        wnba_renderer.timezone_name=time_preferences['timezone']
        wnba_renderer.time_format=time_preferences['time_format']
        nba_renderer.timezone_name = time_preferences['timezone']
        nba_renderer.time_format = time_preferences['time_format']
        nhl_renderer.timezone_name = time_preferences['timezone']
        nhl_renderer.time_format = time_preferences['time_format']
        nhl = settings['nhl']
        nhl_renderer.configure(favorite_teams=nhl['favorite_teams'],
                               mode=nhl['mode'],
                               rotation_seconds=nhl['rotation_seconds'])
        nhl_feed.feed.refresh_seconds = nhl['refresh_seconds']
        if settings['sports']['nhl']['enabled']:
            nhl_feed.start()
        nba = settings['nba']
        nba_renderer.configure(favorite_teams=nba['favorite_teams'], mode=nba['mode'], rotation_seconds=nba['rotation_seconds'])
        nba_feed.feed.refresh_seconds = nba['refresh_seconds']
        if settings['sports']['nba']['enabled']:
            nba_feed.start()
        wnba = settings['wnba']
        wnba_renderer.configure(favorite_teams=wnba['favorite_teams'], mode=wnba['mode'], rotation_seconds=wnba['rotation_seconds'])
        wnba_feed.feed.refresh_seconds = wnba['refresh_seconds']
        if settings['sports']['wnba']['enabled']:
            wnba_feed.start()
        nfl = settings['nfl']
        nfl_renderer.configure(favorite_teams=nfl['favorite_teams'], mode=nfl['mode'],
                               rotation_seconds=nfl['rotation_seconds'])
        nfl_feed.feed.refresh_seconds = nfl['refresh_seconds']
        if settings['sports']['nfl']['enabled']:
            nfl_feed.start()
        for league in ('mls', 'nwsl'):
            options = settings[league]
            soccer_renderers[league].configure(
                favorite_teams=options['favorite_teams'], mode=options['mode'],
                rotation_seconds=options['rotation_seconds'])
            soccer_workers[league].feed.refresh_seconds = options['refresh_seconds']
            soccer_workers[league].feed.provider.mode = options['provider']
            soccer_workers[league].set_timezone(time_preferences['timezone'])
            if settings['sports'][league]['enabled']:
                soccer_workers[league].start()
        english = settings['english']
        english_renderer.configure(
            enabled=english['enabled_leagues'],
            favorite_teams=english['favorite_teams'],
            mode=english['mode'],
            rotation_seconds=english['rotation_seconds'])
        from .english_workers import sync_english_workers
        sync_english_workers(
            english_workers,
            sport_enabled=settings['sports']['english']['enabled'],
            enabled_leagues=english['enabled_leagues'],
            refresh_seconds=english['refresh_seconds'],
            timezone_name=time_preferences['timezone'])
        standings_options = settings['standings']
        # A disabled sport/league must not appear in standings rotation.
        english_enabled = settings['sports']['english']['enabled']
        selected_standings_leagues = [
            league for league in standings_options.get('leagues', english['enabled_leagues'])
            if english_enabled and league in english['enabled_leagues']]

        selected_mlb_divisions = (standings_options.get('mlb_divisions', [])
                                  if settings['sports']['mlb']['enabled'] else [])
        selected_mlb_groups = [*selected_mlb_divisions]
        if any(group.startswith('AL_') for group in selected_mlb_divisions):
            selected_mlb_groups.append('AL_WILD_CARD')
        if any(group.startswith('NL_') for group in selected_mlb_divisions):
            selected_mlb_groups.append('NL_WILD_CARD')
        if standings_options['enabled'] and selected_mlb_groups:
            mlb_season_worker.start()
        else:
            mlb_season_worker.stop()
        selected_nhl_divisions = (standings_options.get('nhl_divisions', [])
                                  if settings['sports']['nhl']['enabled'] else [])
        # Explicit wild card preferences override legacy automatic inclusion.
        # Existing installations retain their previous selection behavior.
        selected_nhl_groups = [*selected_nhl_divisions]
        if 'nhl_wild_cards' in standings_options:
            if settings['sports']['nhl']['enabled']:
                selected_nhl_groups.extend(standings_options['nhl_wild_cards'])
        else:
            if any(group in ('Atlantic', 'Metropolitan') for group in selected_nhl_divisions):
                selected_nhl_groups.append('Eastern_Wild_Card')
            if any(group in ('Central', 'Pacific') for group in selected_nhl_divisions):
                selected_nhl_groups.append('Western_Wild_Card')
        if standings_options['enabled'] and selected_nhl_groups:
            nhl_season_worker.start()
        else:
            nhl_season_worker.stop()
        selected_nba_conferences = (standings_options.get('nba_conferences', [])
                                    if settings['sports']['nba']['enabled'] else [])
        if nba_season_worker is not None:
            if standings_options['enabled'] and selected_nba_conferences:
                nba_season_worker.start()
            else:
                nba_season_worker.stop()
        selected_nfl_divisions = (standings_options.get('nfl_divisions', [])
                                  if settings['sports']['nfl']['enabled'] else [])
        selected_mls_conferences = (standings_options.get('mls_conferences', [])
                                    if settings['sports']['mls']['enabled'] else [])
        selected_single_tables = [
            league for league in ('NWSL', 'WNBA')
            if standings_options.get(league.lower(), False)
            and settings['sports'][league.lower()]['enabled']
        ]
        standings_rotation.configure(
            enabled=standings_options['enabled'],
            page_seconds=standings_options['page_seconds'],
            selected_leagues=[*selected_standings_leagues, *selected_mlb_groups,
                              *selected_nhl_groups, *selected_nba_conferences,
                              *selected_nfl_divisions, *selected_mls_conferences, *selected_single_tables])
        for league, cache in standings_caches.items():
            cache.refresh_seconds = standings_options['refresh_seconds']
            if league in single_table_workers:
                if standings_options['enabled'] and league in selected_single_tables:
                    single_table_workers[league].start()
                else:
                    single_table_workers[league].stop()
                continue
            if league in mls_standings_workers:
                if standings_options['enabled'] and league in selected_mls_conferences:
                    mls_standings_workers[league].start()
                else:
                    mls_standings_workers[league].stop()
                continue
            if league in nfl_standings_workers:
                if standings_options['enabled'] and league in selected_nfl_divisions:
                    nfl_standings_workers[league].start()
                else:
                    nfl_standings_workers[league].stop()
                continue
            if league in nba_standings_workers:
                if standings_options['enabled'] and league in selected_nba_conferences:
                    nba_standings_workers[league].start()
                else:
                    nba_standings_workers[league].stop()
                continue
            if league in nhl_standings_workers:
                if standings_options['enabled'] and league in selected_nhl_groups:
                    nhl_standings_workers[league].start()
                else:
                    nhl_standings_workers[league].stop()
                continue
            if league in mlb_standings_workers:
                if standings_options['enabled'] and league in selected_mlb_groups:
                    mlb_standings_workers[league].start()
                else:
                    mlb_standings_workers[league].stop()
                continue
            # Pregame and standings data are both limited to enabled leagues.
            needs_pregame_records = (settings['sports']['english']['enabled'] and
                                     league in english['enabled_leagues'])
            needs_standings_page = (standings_options['enabled'] and english_enabled and
                                    league in selected_standings_leagues)
            if needs_pregame_records or needs_standings_page:
                standings_workers[league].start()
            else:
                standings_workers[league].stop()
        enabled = [sport for sport in ('mlb', 'nhl', 'nba', 'wnba', 'nfl', 'mls', 'nwsl', 'english') if settings['sports'][sport]['enabled']]
        renderer.set_supplemental_stride(len(enabled))
        board.configure_rotation(enabled, interval=settings['mlb']['rotation_seconds'],
                                 preferred=settings['active_sport'])
    apply_settings(initial)
    # Restore only fresh, pending notifications after saved settings are active.
    # Keep the snapshot in the same persistent config directory as other ULS data.
    from .scoring_alert_persistence import ScoringAlertPersistence
    scoring_persistence = ScoringAlertPersistence(
        scoring_alerts, Path(args.config_dir) / 'scoring-alerts-pending.json')
    scoring_persistence.restore()
    scoring_persistence.start()
    import atexit
    atexit.register(scoring_persistence.stop)
    def standings_status():
        return board.soccer_pregame_diagnostics()
    def feed_status():
        return feed.status()
    def sports_feed_status():
        # Non-MLB workers expose monotonic timestamps for scheduling.
        # Translate them to wall-clock seconds only for dashboard reporting.
        def dashboard_status(worker, *, unix_time=False):
            return dashboard_feed_status(worker.status(),unix_time=unix_time)
        feeds={'mlb':feed,'nhl':nhl_feed,'nba':nba_feed,'wnba':wnba_feed,
               'nfl':nfl_feed,'mls':soccer_workers['mls'],'nwsl':soccer_workers['nwsl']}
        result={name:dashboard_status(worker,unix_time=name=='mlb') for name,worker in feeds.items()}
        league_states=[dashboard_status(worker) for worker in english_workers.values()]
        errors=[entry.get('error') for entry in league_states if entry.get('error')]
        result['english']={'state':'error' if errors else 'running' if any(entry.get('state')=='running' for entry in league_states) else 'starting',
                           'games':sum(entry.get('games',0) for entry in league_states),
                           'last_success':min((entry['last_success'] for entry in league_states if entry.get('last_success') is not None),default=None) if all(entry.get('last_success') is not None for entry in league_states) else None,
                           'error':'; '.join(str(error) for error in errors) if errors else None}
        return result
    def countdown_status():
        from .season_countdown_settings import load
        settings = load(args.config_dir)
        info = {'enabled':settings['enabled'], 'source':settings['source'],
                'target':settings['target'], 'team':settings['team'],
                'opening_at':settings['opening_at']}
        if not settings['enabled'] or settings['source'] != 'automatic':
            return info
        event = renderer.opening_feed.opening(settings['season'],
                        target=settings['target'], team=settings['team'])
        snapshot = renderer.opening_feed.status(settings['season'])
        info.update(snapshot)
        info['resolved_at'] = event.starts_at.isoformat() if event else None
        return info
    # Publish the exact framebuffer used by /frame.json, without exposing an
    # unauthenticated HTTP endpoint to the privileged matrix worker.
    from .frame_bridge import write_frame
    frame_path = Path(os.environ.get('ULS_FRAME_FILE', '/run/universal-led-scoreboard/live-frame.ppm'))
    frame_stop = threading.Event()
    from .native_plugin_runtime import enabled_screen_slots
    plugin_root = Path('/var/lib/uls/plugins')
    plugin_registry = Path('/var/lib/uls/plugins.json')
    active_plugin_ids = None
    def publish_frames():
        nonlocal active_plugin_ids
        last_plugin_scan = 0.0
        while not frame_stop.is_set():
            try:
                now = time.monotonic()
                if now - last_plugin_scan >= 5.0 or active_plugin_ids is None:
                    last_plugin_scan = now
                    try:
                        slots = enabled_screen_slots(plugin_root, plugin_registry)
                        signature = tuple((slot.plugin_id, slot.display_seconds) for slot in slots)
                        if signature != active_plugin_ids:
                            board.set_bullpen_slots(slots)
                            active_plugin_ids = signature
                    except (OSError, ValueError) as exc:
                        print(f'Plugin discovery failed: {exc}', flush=True)
                write_frame(frame_path, board.frame())
            except Exception as exc:
                print(f'Frame publishing failed: {exc}', flush=True)
            frame_stop.wait(1.0)
    frame_thread = threading.Thread(target=publish_frames, daemon=True, name='frame-publisher')
    frame_thread.start()
    try:
        with ThreadingHTTPServer((args.host,args.port),make_handler(args.config_dir,token,game,apply_settings,feed_status,board.frame,countdown_status,standings_status,lambda: {'selected_sport':board._selected(), 'live_sports':list(board._live_sports()), 'priority':'live' if board._live_sports() else 'normal'},sports_feed_status)) as server:
            print(f'Configurator listening on {args.host}:{args.port}',flush=True)
            server.serve_forever()
    finally:
        frame_stop.set()
        frame_thread.join(timeout=3)
        weather.stop()
        news.stop()
        feed.stop()
        nhl_feed.stop()
        nba_feed.stop()
        wnba_feed.stop()
        nfl_feed.stop()
        for worker in soccer_workers.values():
            worker.stop()
        for worker in english_workers.values():
            worker.stop()
        for worker in standings_workers.values():
            worker.stop()
        for worker in mlb_standings_workers.values():
            worker.stop()
        for worker in nhl_standings_workers.values():
            worker.stop()
        for worker in nba_standings_workers.values():
            worker.stop()
        for worker in nfl_standings_workers.values():
            worker.stop()
        for worker in mls_standings_workers.values():
            worker.stop()
        for worker in single_table_workers.values():
            worker.stop()
        mlb_season_worker.stop()
        nhl_season_worker.stop()
        if nba_season_worker is not None:
            nba_season_worker.stop()
if __name__=='__main__':
    main()
