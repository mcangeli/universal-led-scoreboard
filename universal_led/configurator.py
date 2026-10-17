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
from .matrix_settings import load_matrix_settings, validate_matrix_settings

LOGIN_HTML='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Scoreboard Login</title><style>body{font:16px system-ui;background:#0c1624;color:#e9eef5;max-width:400px;margin:12vh auto;padding:24px}form{background:#18283b;border:1px solid #34445b;border-radius:12px;padding:24px}input,button{box-sizing:border-box;width:100%;padding:12px;margin:8px 0;border-radius:6px}button{background:#d7b46d;border:0;font-weight:bold;cursor:pointer}
</style></head><body><form method="post" action="/login"><h2>Universal LED Scoreboard</h2><p>Administrator login</p><label>Password<input name="password" type="password" autocomplete="current-password" required></label><button type="submit">Sign In</button><p>Use HTTPS before accessing outside a trusted LAN.</p></form></body></html>'''

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
<div class="shell"><aside><div class="side-title">DISPLAY</div><nav aria-label="Configurator navigation"><button class="nav-item" type="button" onclick="showPage('dashboard')">◫ Dashboard</button> <button class="nav-item" type="button" onclick="showPage('sports')">⚾ Sports</button> <button class="nav-item" type="button" onclick="showPage('display')">▦ Display</button> <button class="nav-item" type="button" onclick="showPage('colors')">◉ Colors</button> <button class="nav-item" type="button" onclick="showPage('news')">▤ Content &amp; News</button> <button class="nav-item" type="button" onclick="showPage('wifi')">◈ Wi-Fi</button> <button class="nav-item" type="button" onclick="showPage('matrix-settings')">▦ Matrix Hardware</button> <button class="nav-item" type="button" onclick="showPage('system')">⚙ System</button></nav><div class="sidebar-footer"><a class="board-button" href="/board" target="_blank" rel="noopener">Open Board View ↗</a><button type="button" class="signout" onclick="logout()">Sign Out</button></div></aside><main><section data-page="dashboard" class="dashboard-page"><div class="page-heading"><div><p class="page-kicker">Board overview</p><h2>Dashboard</h2><p class="muted">Your current display configuration and feed health at a glance.</p></div></div><div class="dashboard-grid"><div class="dashboard-tile dashboard-tile-primary"><h3>Active Configuration</h3><p id="summary">Loading settings…</p></div><div class="dashboard-tile dashboard-tile-primary"><h3>Current Game</h3><p id="current-game" class="muted">Waiting for game information…</p></div><div class="dashboard-tile"><h3>MLB Feed <span id="feed-indicator" class="status-dot" aria-hidden="true"></span></h3><p id="feed-status" class="muted" role="status">MLB feed loading…</p></div><div class="dashboard-tile"><h3>Feed Refresh</h3><p id="last-refresh" class="muted">Last feed update: pending</p></div></div><div class="dashboard-actions"><div><h3>Scoreboard controls</h3><p class="muted">Board view updates independently every second. Restarting shows the startup splash without rebooting the Pi.</p></div><button type="button" id="restart-scoreboard" onclick="restartScoreboard()">Restart Scoreboard</button></div><p id="restart-status" class="muted" role="status" aria-live="polite"></p></section><section data-page="sports" hidden><h2>Sports &amp; Rotation</h2><p class="muted">Manage active leagues, configure favorites, and review per-sport timing without scrolling through every team.</p><div class="sports-subnav" role="group" aria-label="Sports configuration views"><button type="button" data-sports-view="overview" onclick="showSportsView('overview')">Overview</button><button type="button" data-sports-view="configure" onclick="showSportsView('configure')">Configure Sport</button><button type="button" data-sports-view="rotation" onclick="showSportsView('rotation')">Rotation</button></div><div id="sports-overview" class="sports-view"><h3>Available sports</h3><div class="sports-overview-grid"><button type="button" class="sport-choice" onclick="selectSport('mlb')"><strong>MLB</strong><span id="sport-state-mlb">Configure →</span></button><button type="button" class="sport-choice" onclick="selectSport('nhl')"><strong>NHL</strong><span id="sport-state-nhl">Configure →</span></button><button type="button" class="sport-choice" onclick="selectSport('nba')"><strong>NBA</strong><span id="sport-state-nba">Configure →</span></button><button type="button" class="sport-choice" onclick="selectSport('wnba')"><strong>WNBA</strong><span id="sport-state-wnba">Configure →</span></button><button type="button" class="sport-choice" onclick="selectSport('nfl')"><strong>NFL</strong><span id="sport-state-nfl">Configure →</span></button></div><p class="muted">Choose a sport to edit its settings. Enable and disable sports within Configure Sport.</p></div><div id="sports-configure" class="sports-view" hidden><label for="sport-picker">Sport to configure</label> <select id="sport-picker" onchange="selectSport(this.value)"><option value="mlb">MLB</option><option value="nhl">NHL</option><option value="nba">NBA</option><option value="wnba">WNBA</option><option value="nfl">NFL</option></select><div class="sport-config-panel" data-sport-panel="mlb" hidden><div class="sport-config-panel" data-sport-panel="nhl" hidden><div class="sport-config-panel" data-sport-panel="nba" hidden><div class="sport-config-panel" data-sport-panel="wnba" hidden><div class="sport-config-panel" data-sport-panel="nfl" hidden><fieldset class="favorite-fieldset"><legend>MLB configuration</legend><p><label><input type="checkbox" id="mlb-enabled"> Enable MLB</label></p><h3>Favorite MLB teams</h3><p class="muted">Select one or more teams. Games featuring any favorite will be included.</p><div id="favorite-teams" class="favorite-team-grid"><label><input type="checkbox" value="ARI"> Arizona Diamondbacks</label><label><input type="checkbox" value="ATL"> Atlanta Braves</label><label><input type="checkbox" value="BAL"> Baltimore Orioles</label><label><input type="checkbox" value="BOS"> Boston Red Sox</label><label><input type="checkbox" value="CHC"> Chicago Cubs</label><label><input type="checkbox" value="CWS"> Chicago White Sox</label><label><input type="checkbox" value="CIN"> Cincinnati Reds</label><label><input type="checkbox" value="CLE"> Cleveland Guardians</label><label><input type="checkbox" value="COL"> Colorado Rockies</label><label><input type="checkbox" value="DET"> Detroit Tigers</label><label><input type="checkbox" value="HOU"> Houston Astros</label><label><input type="checkbox" value="KCR"> Kansas City Royals</label><label><input type="checkbox" value="LAA"> Los Angeles Angels</label><label><input type="checkbox" value="LAD"> Los Angeles Dodgers</label><label><input type="checkbox" value="MIA"> Miami Marlins</label><label><input type="checkbox" value="MIL"> Milwaukee Brewers</label><label><input type="checkbox" value="MIN"> Minnesota Twins</label><label><input type="checkbox" value="NYM"> New York Mets</label><label><input type="checkbox" value="NYY"> New York Yankees</label><label><input type="checkbox" value="OAK"> Athletics</label><label><input type="checkbox" value="PHI"> Philadelphia Phillies</label><label><input type="checkbox" value="PIT"> Pittsburgh Pirates</label><label><input type="checkbox" value="SDP"> San Diego Padres</label><label><input type="checkbox" value="SFG"> San Francisco Giants</label><label><input type="checkbox" value="SEA"> Seattle Mariners</label><label><input type="checkbox" value="STL"> St. Louis Cardinals</label><label><input type="checkbox" value="TBR"> Tampa Bay Rays</label><label><input type="checkbox" value="TEX"> Texas Rangers</label><label><input type="checkbox" value="TOR"> Toronto Blue Jays</label><label><input type="checkbox" value="WSN"> Washington Nationals</label></div><p id="favorite-summary" class="muted" aria-live="polite"></p><p><label>MLB game selection <select id="mode"><option value="favorite">Favorites only</option><option value="fallback">Favorites, otherwise all</option><option value="all">All games</option></select></label></p><p><label>MLB rotation seconds <input id="rotation" type="number" min="1" max="3600" value="12"></label> <label>MLB feed refresh seconds <input id="refresh" type="number" min="1" max="3600" value="60"></label></p><h3>MLB live screen rotation</h3><p class="muted">Percent of each live game interval. Last Play uses the remaining time. Classic must be at least 1%.</p><p><label>Classic % <input id="live-classic" type="number" min="1" max="100" step="1" value="50"></label> <label>Matchup % <input id="live-matchup" type="number" min="0" max="99" step="1" value="25"></label></p><p id="live-play-share" class="muted" aria-live="polite">Last Play: 25%</p></fieldset></div></div></div></div></div><fieldset class="favorite-fieldset"><legend>NHL configuration</legend>
<p><label><input type="checkbox" id="nhl-enabled"> Enable NHL</label></p>
<h3>Favorite NHL teams</h3><p class="muted">Select one or more teams, just like MLB.</p><p><button type="button" onclick="setNHLFavorites(NHL_TEAMS.map(team=>team[0]))">Select all</button> <button type="button" onclick="setNHLFavorites([])">Clear all</button></p><div id="nhl-teams" class="favorite-team-grid"><label><input type="checkbox" value="ANA"> Anaheim Ducks</label><label><input type="checkbox" value="BOS"> Boston Bruins</label><label><input type="checkbox" value="BUF"> Buffalo Sabres</label><label><input type="checkbox" value="CGY"> Calgary Flames</label><label><input type="checkbox" value="CAR"> Carolina Hurricanes</label><label><input type="checkbox" value="CHI"> Chicago Blackhawks</label><label><input type="checkbox" value="COL"> Colorado Avalanche</label><label><input type="checkbox" value="CBJ"> Columbus Blue Jackets</label><label><input type="checkbox" value="DAL"> Dallas Stars</label><label><input type="checkbox" value="DET"> Detroit Red Wings</label><label><input type="checkbox" value="EDM"> Edmonton Oilers</label><label><input type="checkbox" value="FLA"> Florida Panthers</label><label><input type="checkbox" value="LAK"> Los Angeles Kings</label><label><input type="checkbox" value="MIN"> Minnesota Wild</label><label><input type="checkbox" value="MTL"> Montréal Canadiens</label><label><input type="checkbox" value="NSH"> Nashville Predators</label><label><input type="checkbox" value="NJD"> New Jersey Devils</label><label><input type="checkbox" value="NYI"> New York Islanders</label><label><input type="checkbox" value="NYR"> New York Rangers</label><label><input type="checkbox" value="OTT"> Ottawa Senators</label><label><input type="checkbox" value="PHI"> Philadelphia Flyers</label><label><input type="checkbox" value="PIT"> Pittsburgh Penguins</label><label><input type="checkbox" value="SJS"> San Jose Sharks</label><label><input type="checkbox" value="SEA"> Seattle Kraken</label><label><input type="checkbox" value="STL"> St. Louis Blues</label><label><input type="checkbox" value="TBL"> Tampa Bay Lightning</label><label><input type="checkbox" value="TOR"> Toronto Maple Leafs</label><label><input type="checkbox" value="UTA"> Utah Mammoth</label><label><input type="checkbox" value="VAN"> Vancouver Canucks</label><label><input type="checkbox" value="VGK"> Vegas Golden Knights</label><label><input type="checkbox" value="WSH"> Washington Capitals</label><label><input type="checkbox" value="WPG"> Winnipeg Jets</label></div><p id="nhl-favorite-summary" class="muted" aria-live="polite"></p>
<p><label>NHL game selection <select id="nhl-mode"><option value="favorite">Favorites only</option><option value="fallback">Favorites, otherwise all</option><option value="all">All games</option></select></label></p>
<p><label>NHL rotation seconds <input id="nhl-rotation" type="number" min="5" max="3600" value="12"></label>
<label>NHL feed refresh seconds <input id="nhl-refresh" type="number" min="5" max="3600" value="60"></label></p>
</fieldset><fieldset class="favorite-fieldset"><legend>NBA configuration</legend><p><label><input type="checkbox" id="nba-enabled"> Enable NBA</label></p><h3>Favorite NBA teams</h3><div id="nba-teams" class="favorite-team-grid"><label><input type="checkbox" value="ATL"> Atlanta Hawks</label><label><input type="checkbox" value="BOS"> Boston Celtics</label><label><input type="checkbox" value="BKN"> Brooklyn Nets</label><label><input type="checkbox" value="CHA"> Charlotte Hornets</label><label><input type="checkbox" value="CHI"> Chicago Bulls</label><label><input type="checkbox" value="CLE"> Cleveland Cavaliers</label><label><input type="checkbox" value="DAL"> Dallas Mavericks</label><label><input type="checkbox" value="DEN"> Denver Nuggets</label><label><input type="checkbox" value="DET"> Detroit Pistons</label><label><input type="checkbox" value="GSW"> Golden State Warriors</label><label><input type="checkbox" value="HOU"> Houston Rockets</label><label><input type="checkbox" value="IND"> Indiana Pacers</label><label><input type="checkbox" value="LAC"> LA Clippers</label><label><input type="checkbox" value="LAL"> Los Angeles Lakers</label><label><input type="checkbox" value="MEM"> Memphis Grizzlies</label><label><input type="checkbox" value="MIA"> Miami Heat</label><label><input type="checkbox" value="MIL"> Milwaukee Bucks</label><label><input type="checkbox" value="MIN"> Minnesota Timberwolves</label><label><input type="checkbox" value="NOP"> New Orleans Pelicans</label><label><input type="checkbox" value="NYK"> New York Knicks</label><label><input type="checkbox" value="OKC"> Oklahoma City Thunder</label><label><input type="checkbox" value="ORL"> Orlando Magic</label><label><input type="checkbox" value="PHI"> Philadelphia 76ers</label><label><input type="checkbox" value="PHX"> Phoenix Suns</label><label><input type="checkbox" value="POR"> Portland Trail Blazers</label><label><input type="checkbox" value="SAC"> Sacramento Kings</label><label><input type="checkbox" value="SAS"> San Antonio Spurs</label><label><input type="checkbox" value="TOR"> Toronto Raptors</label><label><input type="checkbox" value="UTA"> Utah Jazz</label><label><input type="checkbox" value="WSH"> Washington Wizards</label></div><p><label>NBA game selection <select id="nba-mode"><option value="favorite">Favorites only</option><option value="fallback">Favorites, otherwise all</option><option value="all">All games</option></select></label></p><p><label>NBA rotation seconds <input id="nba-rotation" type="number" min="5" max="3600" value="12"></label> <label>NBA feed refresh seconds <input id="nba-refresh" type="number" min="5" max="3600" value="60"></label></p></fieldset><fieldset class="favorite-fieldset"><legend>WNBA configuration</legend><p><label><input type="checkbox" id="wnba-enabled"> Enable WNBA</label></p><h3>Favorite WNBA teams</h3><div id="wnba-teams" class="favorite-team-grid"><label><input type="checkbox" value="ATL"> Atlanta Dream</label><label><input type="checkbox" value="CHI"> Chicago Sky</label><label><input type="checkbox" value="CON"> Connecticut Sun</label><label><input type="checkbox" value="DAL"> Dallas Wings</label><label><input type="checkbox" value="GSV"> Golden State Valkyries</label><label><input type="checkbox" value="IND"> Indiana Fever</label><label><input type="checkbox" value="LVA"> Las Vegas Aces</label><label><input type="checkbox" value="LAS"> Los Angeles Sparks</label><label><input type="checkbox" value="MIN"> Minnesota Lynx</label><label><input type="checkbox" value="NYL"> New York Liberty</label><label><input type="checkbox" value="PHX"> Phoenix Mercury</label><label><input type="checkbox" value="SEA"> Seattle Storm</label><label><input type="checkbox" value="WAS"> Washington Mystics</label><label><input type="checkbox" value="POR"> Portland Fire</label><label><input type="checkbox" value="TOR"> Toronto Tempo</label></div><p><label>WNBA game selection <select id="wnba-mode"><option value="favorite">Favorites only</option><option value="fallback">Favorites, otherwise all</option><option value="all">All games</option></select></label></p><p><label>WNBA rotation seconds <input id="wnba-rotation" type="number" min="5" max="3600" value="12"></label> <label>WNBA feed refresh seconds <input id="wnba-refresh" type="number" min="5" max="3600" value="60"></label></p></fieldset><fieldset class="favorite-fieldset"><legend>NFL configuration</legend>
<p><label><input type="checkbox" id="nfl-enabled"> Enable NFL</label></p>
<h3>Favorite NFL teams</h3>
<div id="nfl-teams" class="favorite-team-grid"></div>
<p><label>NFL game selection <select id="nfl-mode"><option value="favorite">Favorites only</option><option value="fallback">Favorites, otherwise all</option><option value="all">All games</option></select></label></p>
<p><label>NFL rotation seconds <input id="nfl-rotation" type="number" min="5" max="3600" value="12"></label>
<label>NFL feed refresh seconds <input id="nfl-refresh" type="number" min="5" max="3600" value="60"></label></p></fieldset></div><div id="sports-rotation" class="sports-view" hidden><h3>Rotation behavior</h3><p>Each sport currently has its own game rotation and feed refresh timing. Use Configure Sport to adjust those values for the selected league.</p><div class="rotation-summary" id="sports-rotation-summary"></div><p class="muted">Shared clock, weather, and countdown rotation settings remain under Display. A separate global rotation priority control is not supported by the current configuration schema.</p></div><div class="sports-savebar"><button id="save-settings">Save Sport Settings</button><span id="settings-status" role="status" aria-live="polite"></span></div></section><section data-page="display" hidden><h2>Shared Display Settings</h2><fieldset class="favorite-fieldset"><legend>Time &amp; Weather</legend><label><input id="clock-enabled" type="checkbox"> Enable clock rotation</label><label>Time zone <select id="clock-timezone"><option value="America/New_York">Eastern (ET)</option><option value="America/Chicago">Central (CT)</option><option value="America/Denver">Mountain (MT)</option><option value="America/Phoenix">Arizona (MST, no DST)</option><option value="America/Los_Angeles">Pacific (PT)</option><option value="America/Anchorage">Alaska (AKT)</option><option value="Pacific/Honolulu">Hawaii (HST)</option><option value="UTC">UTC</option><option value="Europe/London">London (UK)</option><option value="Europe/Paris">Central Europe</option><option value="Asia/Tokyo">Japan</option><option value="Australia/Sydney">Sydney</option></select></label><label>Time format <select id="clock-format"><option value="12h">12-hour</option><option value="24h">24-hour</option></select></label><label>Clock every N non-live slots <input id="clock-interval" type="number" min="1" max="20" value="5"></label><label><input id="weather-enabled" type="checkbox"> Enable weather display</label><label>Weather location <input id="weather-location" type="text" placeholder="City or ZIP"></label><label>Temperature unit <select id="weather-unit"><option value="fahrenheit">Fahrenheit</option><option value="celsius">Celsius</option></select></label><label>Weather provider <select id="weather-provider"><option value="open-meteo">Open-Meteo (no key)</option><option value="openweathermap">OpenWeatherMap (API key)</option></select></label><label>OpenWeatherMap API key <input id="weather-key" type="password" autocomplete="new-password" placeholder="Leave blank to keep saved key"></label><button type="button" onclick="saveClockSettings()">Save Time &amp; Weather</button><p id="clock-status" role="status"></p></fieldset><fieldset class="favorite-fieldset"><legend>Season Opening Countdown</legend><p class="muted">Optional shared countdown. Enter an opening date with its timezone offset, such as 2027-03-25T13:00:00-04:00. Disabled until configured.</p><p><label><input id="countdown-enabled" type="checkbox"> Enable countdown</label></p><p><label>Sport <select id="countdown-sport"><option value="mlb">MLB</option><option value="nba">NBA</option><option value="nfl">NFL</option><option value="nhl">NHL</option><option value="mls">MLS</option><option value="efl">EFL</option></select></label> <label>Season <input id="countdown-season" type="text" placeholder="2027"></label></p><p><label>Date source <select id="countdown-source"><option value="manual">Manual date</option><option value="automatic">Automatic MLB schedule</option></select></label></p><p><label>Opening date/time (ISO with timezone) <input id="countdown-opening" type="text" placeholder="2027-03-25T13:00:00-04:00"></label></p><p><label>Target <select id="countdown-target"><option value="league">League opening</option><option value="favorite">Favorite team opening</option></select></label> <label>Team code <input id="countdown-team" type="text" placeholder="ATL"></label></p><p><label>Display <select id="countdown-window"><option value="offseason">Offseason only</option><option value="within_days">Within N days</option><option value="always">Always when no live game</option></select></label> <label>Days <input id="countdown-days" type="number" min="1" max="366" value="30"></label></p><button type="button" onclick="saveCountdown()">Save Countdown</button><p id="countdown-status" role="status" aria-live="polite"></p><p id="countdown-feed-status" class="muted" role="status" aria-live="polite">Schedule status not checked.</p><button type="button" onclick="refreshCountdownStatus()">Check Schedule Status</button></fieldset></section><section data-page="wifi" hidden><h2>Wi-Fi & Hotspot</h2><p id="wifi-recovery-readiness" class="muted" role="status">Checking recovery protection…</p><p id="wifi-info">Loading…</p><h4>Saved Wi-Fi connections</h4><div id="wifi-profiles" class="grid"><p class="muted">Loading saved profiles…</p></div><button type="button" onclick="refreshWifi()">Refresh Wi-Fi</button> <button type="button" onclick="scanWifi()">Scan Networks</button><p id="wifi-scan-status" class="muted" role="status" aria-live="polite">Click Scan Networks to list nearby access points.</p><div id="wifi-networks" class="grid"></div><div id="wifi-selection" hidden><h4>Selected network: <span id="wifi-selected-name"></span></h4><p id="wifi-selected-security"></p><label>Network password <input id="wifi-password" type="password" autocomplete="off" minlength="8" maxlength="63"></label><p id="wifi-connect-note" class="muted">Network switching requires the privileged helper and recovery worker. Keep Ethernet connected during initial testing.</p><button type="button" onclick="connectWifi()">Connect Wi-Fi</button><p id="wifi-connect-result" role="status"></p></div><h4>Hotspot Settings</h4><p class="muted">Change the password for Universal-LED-Setup. Changes take effect the next time the hotspot starts.</p><label>New hotspot password <input id="hotspot-password" type="password" minlength="8" maxlength="63" autocomplete="new-password"></label> <label>Confirm password <input id="hotspot-confirm" type="password" minlength="8" maxlength="63" autocomplete="new-password"></label> <button type="button" onclick="saveHotspotPassword()">Save Hotspot Password</button><p id="hotspot-result" role="status"></p></section><section data-page="matrix-settings" hidden><h2>Physical Matrix Settings</h2><p class="muted">Hardware changes require restarting only uls-matrix.service. Saving does not restart the hardware automatically.</p><div class="grid"><label class="item"><input type="checkbox" id="matrix-enabled"> Enable physical matrix output</label><label class="item">Brightness (1–100%) <input type="number" id="matrix-brightness" min="1" max="100" value="40"></label><label class="item">GPIO slowdown (0–10) <input type="number" id="matrix-slowdown" min="0" max="10" value="4"></label><label class="item">Hardware mapping <select id="matrix-mapping"><option value="adafruit-hat">Adafruit HAT</option><option value="adafruit-hat-pwm">Adafruit HAT PWM</option><option value="regular">Regular</option><option value="compute-module">Compute Module</option></select></label><label class="item">Frame poll interval (seconds) <input type="number" id="matrix-interval" min="0.05" max="10" step="0.05" value="0.2"></label></div><p><button type="button" onclick="saveMatrixSettings()">Save Matrix Settings</button> <button type="button" onclick="applyMatrixSettings()">Apply Saved Settings</button></p><p id="matrix-service-state" class="muted" role="status">Checking matrix service…</p><p id="matrix-settings-status" role="status" aria-live="polite"></p></section><section data-page="system" hidden><h2>System</h2><h3>Software Updates</h3><p id="update-status" class="muted" role="status">Update status not checked.</p><button type="button" onclick="checkSoftwareUpdate()">Check for Updates</button> <button type="button" id="install-update" onclick="installSoftwareUpdate()" disabled>Install Update</button><pre id="update-log" style="white-space:pre-wrap;overflow-wrap:anywhere;max-height:220px;overflow:auto"></pre><p id="system-info">Checking server information…</p><div id="pi-info" class="grid"><p class="muted">Loading Raspberry Pi diagnostics…</p></div><p class="muted">Service status is read-only. Hardware output and remote service controls are not enabled.</p></section><div data-page="colors" hidden><section><h2>64 × 32 Live Preview</h2><canvas id="matrix" width="64" height="32"></canvas>
<p class="muted">Changes preview immediately. Saving is optional.</p><label for="preview-team">Preview favorite team: </label><select id="preview-team"></select><span id="dirty" role="status">All changes saved</span></section>
<section><h2>Scoreboard Colors</h2><p class="muted">General display text, accents, separators and status colors.</p><div id="scoreboard" class="grid"></div></section>
<section><h2>NHL Team Colors</h2><p class="muted">NHL colors are stored separately from MLB. Use the same RGB editor for both sports.</p><label for="nhl-edit-team">NHL team to edit</label> <select id="nhl-edit-team"></select><div id="nhl-color-editor" class="grid"></div><button type="button" id="nhl-save-color">Save NHL Color</button> <button type="button" id="nhl-reset-color">Reset NHL Color</button> <span id="nhl-color-status" role="status"></span></section>
<section><h2>MLB Team Colors</h2><p class="muted">Edit one team at a time, using the same compact controls as NHL. All other team colors remain unchanged.</p><label for="edit-team">MLB team to edit</label> <select id="edit-team"></select><div id="teams" class="grid"></div><button id="mlb-save-color" type="button">Save MLB Color</button> <button id="mlb-reset-color" type="button">Reset MLB Color</button> <span id="mlb-color-status" role="status"></span></section>
<section><button id="save">Save Color Settings</button> <button id="cancel" type="button">Cancel Changes</button> <button id="reset" type="button">Reset Selected Color</button> <span id="status" role="status"></span>
<p class="muted">Available on your trusted LAN. Backups are created before overwriting existing files.</p></section></div><div data-page="news" hidden><section><h2>Content &amp; News Sources</h2><p class="muted">Configure RSS or Atom feeds for future ticker use. Automatic and custom feeds display during available news rotation slots.</p><fieldset class="favorite-fieldset"><legend>Automatic Sports News</legend><p class="muted">Enable headlines separately for each sport. News appears during non-live rotation slots when that sport is enabled.</p><label><input type="checkbox" id="mlb-news-enabled"> MLB official headlines</label> <label><input type="checkbox" id="nhl-news-enabled"> NHL headlines</label> <label><input type="checkbox" id="nba-news-enabled"> NBA headlines</label> <label><input type="checkbox" id="wnba-news-enabled"> WNBA headlines</label> <label><input type="checkbox" id="nfl-news-enabled"> NFL headlines</label> <button type="button" onclick="saveAutomaticNews()">Save Automatic News</button><p id="auto-news-status" role="status"></p></fieldset><fieldset class="favorite-fieldset"><legend>News Display Timing</legend><label>Show news every N non-live slots <input id="news-interval" type="number" min="1" max="20"></label> <label>Headline duration (seconds) <input id="news-duration" type="number" min="3" max="120"></label> <label>Scroll speed (characters/second) <input id="news-speed" type="number" min="1" max="15"></label> <button type="button" onclick="saveNewsTiming()">Save News Timing</button><p id="news-timing-status" role="status"></p></fieldset><h3>Additional Custom Feeds</h3><div id="news-sources"></div><button type="button" id="news-add" onclick="addNewsSource()">Add Source</button> <button type="button" onclick="saveNewsSources()">Save News Sources</button> <p id="news-status" role="status"></p></section></div></main></div>
<script>
const token=__TOKEN__;
async function logout(){await fetch('/logout',{method:'POST',headers:{'X-Configurator-Token':token}});location.href='/login'}
let state=null,saved=null,dirty=false,selectedTeam='ATL',selected=null,settings=null;
function showPage(name){document.querySelectorAll('.nav-item').forEach(button=>button.classList.toggle('active',button.getAttribute('onclick')==="showPage('"+name+"')"));document.querySelectorAll('[data-page]').forEach(el=>el.hidden=el.dataset.page!==name);if(name==='news'){loadNewsSources();loadAutomaticNews();loadNewsTiming()}if(name==='display'){loadClockSettings();loadCountdown();}if(name==='dashboard'||name==='system')refreshStatus();if(name==='system'){refreshSystem();refreshUpdateProgress();}if(name==='matrix-settings'){loadMatrixSettings();refreshMatrixStatus();}if(name==='wifi'){refreshWifi();refreshWifiProfiles();refreshRecoveryReadiness();scanWifi()}}
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
 const status=document.getElementById('auto-news-status');
 try{const response=await fetch('/api/settings',{cache:'no-store'});if(!response.ok)throw Error('Unable to load sports settings');const data=await response.json();document.getElementById('mlb-news-enabled').checked=data.sports.mlb.news_enabled;document.getElementById('nhl-news-enabled').checked=data.sports.nhl.news_enabled;document.getElementById('nba-news-enabled').checked=data.sports.nba.news_enabled;document.getElementById('wnba-news-enabled').checked=data.sports.wnba.news_enabled;document.getElementById('nfl-news-enabled').checked=data.sports.nfl.news_enabled;status.textContent=''}
 catch(err){status.textContent=err.message}
}
async function saveAutomaticNews(){
 const status=document.getElementById('auto-news-status');status.textContent='Saving…';
 try{const response=await fetch('/api/settings',{cache:'no-store'});if(!response.ok)throw Error('Unable to load sports settings');const data=await response.json();data.sports.mlb.news_enabled=document.getElementById('mlb-news-enabled').checked;data.sports.nhl.news_enabled=document.getElementById('nhl-news-enabled').checked;data.sports.nba.news_enabled=document.getElementById('nba-news-enabled').checked;data.sports.wnba.news_enabled=document.getElementById('wnba-news-enabled').checked;data.sports.nfl.news_enabled=document.getElementById('nfl-news-enabled').checked;
 const saved=await fetch('/api/settings',{method:'POST',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify(data)});
 const result=await saved.json();if(!saved.ok)throw Error(result.error||'Save failed');settings=result.settings;status.textContent='Automatic sports news preferences saved.'}
 catch(err){status.textContent=err.message}
}
async function loadNewsTiming(){
 const status=document.getElementById('news-timing-status');
 try{const response=await fetch('/api/settings',{cache:'no-store'});if(!response.ok)throw Error('Unable to load news timing');const data=await response.json();document.getElementById('news-interval').value=data.news.rotation_interval;document.getElementById('news-duration').value=data.news.headline_seconds;document.getElementById('news-speed').value=data.news.scroll_chars_per_second;status.textContent=''}
 catch(err){status.textContent=err.message}
}
async function saveNewsTiming(){
 const status=document.getElementById('news-timing-status');status.textContent='Saving…';
 try{const response=await fetch('/api/settings',{cache:'no-store'});if(!response.ok)throw Error('Unable to load settings');const data=await response.json();data.news={rotation_interval:Number(document.getElementById('news-interval').value),headline_seconds:Number(document.getElementById('news-duration').value),scroll_chars_per_second:Number(document.getElementById('news-speed').value)};
 const saved=await fetch('/api/settings',{method:'POST',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify(data)});
 const result=await saved.json();if(!saved.ok)throw Error(result.error||'Save failed');settings=result.settings;status.textContent='News timing saved.'}
 catch(err){status.textContent=err.message}
}
let newsSources=[];
async function loadNewsSources(){
 const status=document.getElementById('news-status');
 try{const response=await fetch('/api/news-sources',{cache:'no-store'});if(!response.ok)throw Error('Unable to load news sources');newsSources=(await response.json()).sources;renderNewsSources();status.textContent='';}
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
   input.oninput=()=>{source[key]=type==='number'?Number(input.value):input.value};
   wrapper.append(input);row.append(wrapper);
  });
  const enabled=document.createElement('label');enabled.textContent='Enabled ';
  const checkbox=document.createElement('input');checkbox.type='checkbox';checkbox.checked=source.enabled;checkbox.onchange=()=>{source.enabled=checkbox.checked};enabled.append(checkbox);row.append(enabled);
  const remove=document.createElement('button');remove.type='button';remove.textContent='Remove';remove.onclick=()=>{newsSources.splice(index,1);renderNewsSources()};row.append(remove);target.append(row);
 });
}
function addNewsSource(){if(newsSources.length>=20){document.getElementById('news-status').textContent='Maximum 20 sources';return}newsSources.push({name:'',url:'',category:'news',enabled:true,refresh_seconds:900});renderNewsSources()}
async function saveNewsSources(){
 const status=document.getElementById('news-status');status.textContent='Saving…';
 try{const response=await fetch('/api/news-sources',{method:'POST',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify({sources:newsSources})});const result=await response.json();if(!response.ok)throw Error(result.error||'Save failed');newsSources=result.settings.sources;renderNewsSources();status.textContent='News sources saved.'}
 catch(err){status.textContent=err.message}
}
const clone=value=>JSON.parse(JSON.stringify(value));
function markDirty(){dirty=JSON.stringify(state)!==JSON.stringify(saved);document.getElementById('dirty').textContent=dirty?'Unsaved changes':'All changes saved';}
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
 status.textContent='Saving…';
 try{
  const response=await fetch('/api/mlb-colors',{method:'POST',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify({[code]:state.teams[code]})});
  const result=await response.json();if(!response.ok)throw Error(result.error||'Save failed');
  saved.teams[code]=clone(state.teams[code]);markDirty();status.textContent='Saved MLB '+code+' color.';
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
document.getElementById('cancel').onclick=()=>{state=clone(saved);selected=null;section('scoreboard');section('teams');markDirty();draw();document.getElementById('status').textContent='Unsaved changes discarded.'};
document.getElementById('reset').onclick=async()=>{
 if(!selected){document.getElementById('status').textContent='Select a color first.';return}
 const response=await fetch('/api/defaults');const defaults=await response.json();
 state[selected.name][selected.key]=clone(defaults[selected.name][selected.key]);
 section(selected.name);markDirty();draw();
};
document.getElementById('save').onclick=async()=>{
 const status=document.getElementById('status');status.textContent='Saving…';
 try{
  const response=await fetch('/api/config',{method:'POST',
   headers:{'Content-Type':'application/json','X-Configurator-Token':token},
   body:JSON.stringify(state)});
  const result=await response.json();
  if(!response.ok)throw Error(result.error||'Save failed');
  saved=clone(state);markDirty();status.textContent='Saved. Other running preview processes may require restart to reload colors.';
 }catch(err){status.textContent=err.message}
};
let nhlColors=null,nhlColorDefaults=null;
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
  document.getElementById('nhl-color-status').textContent='Unsaved NHL color changes.';
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
 nhlColors=await response.json();
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
 nhlColors[code]=[...nhlColorDefaults[code]];showNHLColorEditor();
 document.getElementById('nhl-color-status').textContent='Default restored in editor. Save to apply.';
};
document.getElementById('nhl-save-color').onclick=async()=>{
 const code=document.getElementById('nhl-edit-team').value,status=document.getElementById('nhl-color-status');status.textContent='Saving…';
 try{
  const response=await fetch('/api/nhl-colors',{method:'POST',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify({[code]:nhlColors[code]})});
  const result=await response.json();if(!response.ok)throw Error(result.error||'Save failed');
  status.textContent='Saved NHL '+code+' color. Restart the matrix after renderer support is installed.';
 }catch(err){status.textContent=err.message}
};
const NHL_TEAMS=[["ANA","Anaheim Ducks"],["BOS","Boston Bruins"],["BUF","Buffalo Sabres"],["CGY","Calgary Flames"],["CAR","Carolina Hurricanes"],["CHI","Chicago Blackhawks"],["COL","Colorado Avalanche"],["CBJ","Columbus Blue Jackets"],["DAL","Dallas Stars"],["DET","Detroit Red Wings"],["EDM","Edmonton Oilers"],["FLA","Florida Panthers"],["LAK","Los Angeles Kings"],["MIN","Minnesota Wild"],["MTL","Montréal Canadiens"],["NSH","Nashville Predators"],["NJD","New Jersey Devils"],["NYI","New York Islanders"],["NYR","New York Rangers"],["OTT","Ottawa Senators"],["PHI","Philadelphia Flyers"],["PIT","Pittsburgh Penguins"],["SJS","San Jose Sharks"],["SEA","Seattle Kraken"],["STL","St. Louis Blues"],["TBL","Tampa Bay Lightning"],["TOR","Toronto Maple Leafs"],["UTA","Utah Mammoth"],["VAN","Vancouver Canucks"],["VGK","Vegas Golden Knights"],["WSH","Washington Capitals"],["WPG","Winnipeg Jets"]];
const NFL_TEAMS=[['ARI','Arizona Cardinals'],['ATL','Atlanta Falcons'],['BAL','Baltimore Ravens'],['BUF','Buffalo Bills'],['CAR','Carolina Panthers'],['CHI','Chicago Bears'],['CIN','Cincinnati Bengals'],['CLE','Cleveland Browns'],['DAL','Dallas Cowboys'],['DEN','Denver Broncos'],['DET','Detroit Lions'],['GB','Green Bay Packers'],['HOU','Houston Texans'],['IND','Indianapolis Colts'],['JAC','Jacksonville Jaguars'],['KC','Kansas City Chiefs'],['LAC','Los Angeles Chargers'],['LAR','Los Angeles Rams'],['LV','Las Vegas Raiders'],['MIA','Miami Dolphins'],['MIN','Minnesota Vikings'],['NE','New England Patriots'],['NO','New Orleans Saints'],['NYG','New York Giants'],['NYJ','New York Jets'],['PHI','Philadelphia Eagles'],['PIT','Pittsburgh Steelers'],['SEA','Seattle Seahawks'],['SF','San Francisco 49ers'],['TB','Tampa Bay Buccaneers'],['TEN','Tennessee Titans'],['WAS','Washington Commanders']];
document.getElementById('nfl-teams').replaceChildren(...NFL_TEAMS.map(([code,name])=>{
 const label=document.createElement('label'),input=document.createElement('input');
 input.type='checkbox';input.value=code;label.append(input,document.createTextNode(' '+name));return label;
}));
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
 const status=document.getElementById('clock-status');status.textContent='Saving…';
 try{
  const response=await fetch('/api/time-weather',{cache:'no-store'});
  if(!response.ok)throw Error('Unable to load time settings');
  const data=await response.json();
  data.clock_enabled=document.getElementById('clock-enabled').checked;
  data.timezone=document.getElementById('clock-timezone').value.trim();
  data.time_format=document.getElementById('clock-format').value;
  data.rotation_interval=Number(document.getElementById('clock-interval').value);
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
 document.querySelectorAll('.sports-subnav button').forEach(button=>{const active=button.dataset.sportsView===view;button.classList.toggle('active',active);button.setAttribute('aria-pressed',String(active))});
 ['overview','configure','rotation'].forEach(name=>document.getElementById('sports-'+name).hidden=name!==view);
 if(view==='rotation')refreshSportsRotationSummary();
}
function selectSport(name){
 const picker=document.getElementById('sport-picker');picker.value=name;
 document.querySelectorAll('[data-sport-panel]').forEach(panel=>panel.hidden=panel.dataset.sportPanel!==name);
 showSportsView('configure');
}
function refreshSportsRotationSummary(){
 const target=document.getElementById('sports-rotation-summary');target.replaceChildren();
 if(!settings)return;
 ['mlb','nhl','nba','wnba','nfl'].forEach(name=>{
  const node=document.createElement('div');node.className='item';
  const sport=settings[name],enabled=settings.sports[name].enabled;
  node.textContent=name.toUpperCase()+' · '+(enabled?'Enabled':'Disabled')+' · '+sport.rotation_seconds+'s per game · '+sport.refresh_seconds+'s feed refresh';
  target.append(node);
 });
}
function refreshSportsOverview(){
 if(!settings)return;
 ['mlb','nhl','nba','wnba','nfl'].forEach(name=>{
  document.getElementById('sport-state-'+name).textContent=(settings.sports[name].enabled?'Enabled':'Disabled')+' · Configure →';
 });
}
showSportsView('overview');selectSport('mlb');showSportsView('overview');

async function loadSettings(){
 const response=await fetch('/api/settings',{cache:'no-store'});
 if(!response.ok)throw Error('Could not load sport settings');
 settings=await response.json();
 const mlb=settings.mlb;
 const nhl=settings.nhl;
 const nba=settings.nba;
 const wnba=settings.wnba;
 const nfl=settings.nfl;
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
 refreshSportsOverview();refreshSportsRotationSummary();
 document.getElementById('summary').textContent='Enabled sports: '+['mlb','nhl','nba','wnba','nfl'].filter(s=>settings.sports[s].enabled).join(', ').toUpperCase()+' | MLB favorites: '+mlb.favorite_teams.join(', ')+' | Rotation: '+mlb.mode;
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
async function saveSportSettings(source){
 const status=document.getElementById('settings-status');status.textContent='Saving…';
 const next=clone(settings);
 if(source==='sports'){
  next.mlb.favorite_teams=getFavoriteTeams();
  next.sports.mlb.enabled=document.getElementById('mlb-enabled').checked;
  next.sports.nhl.enabled=document.getElementById('nhl-enabled').checked;
  next.sports.nba.enabled=document.getElementById('nba-enabled').checked;
  next.sports.wnba.enabled=document.getElementById('wnba-enabled').checked;
  next.sports.nfl.enabled=document.getElementById('nfl-enabled').checked;
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
  if(!next.sports.mlb.enabled&&!next.sports.nhl.enabled&&!next.sports.nba.enabled&&!next.sports.wnba.enabled&&!next.sports.nfl.enabled){status.textContent='Enable at least one sport.';return;}
  if(!next.sports[next.active_sport].enabled)next.active_sport=next.sports.mlb.enabled?'mlb':next.sports.nhl.enabled?'nhl':next.sports.nba.enabled?'nba':next.sports.wnba.enabled?'wnba':'nfl';
  next.nhl.favorite_teams=getNHLFavorites();
  next.nhl.mode=document.getElementById('nhl-mode').value;
  next.nhl.rotation_seconds=Number(document.getElementById('nhl-rotation').value);
  next.nhl.refresh_seconds=Number(document.getElementById('nhl-refresh').value);
  if(!next.mlb.favorite_teams.length){status.textContent='Select at least one favorite team.';return;}
  next.mlb.mode=document.getElementById('mode').value;
 next.mlb.rotation_seconds=Number(document.getElementById('rotation').value);
 next.mlb.refresh_seconds=Number(document.getElementById('refresh').value);
 if(!updateLiveShare()){status.textContent='Fix the MLB live screen percentages before saving.';return;}
 next.mlb.live_classic_percent=Number(document.getElementById('live-classic').value);
 next.mlb.live_matchup_percent=Number(document.getElementById('live-matchup').value)}
 try{
  const response=await fetch('/api/settings',{method:'POST',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify(next)});
  const result=await response.json();if(!response.ok)throw Error(result.error||'Save failed');
  settings=result.settings;status.textContent='Saved and applied to configurator preview.';
  await loadSettings();draw();await refreshStatus();
 }catch(err){status.textContent=err.message}
}
document.getElementById('save-settings').onclick=()=>saveSportSettings('sports');
let updateAvailable=false;
async function checkSoftwareUpdate(){
 const out=document.getElementById('update-status'),button=document.getElementById('install-update');
 out.textContent='Checking Git remote…';button.disabled=true;updateAvailable=false;
 try{
  const response=await fetch('/api/update/check',{cache:'no-store'});
  const raw=await response.text();let data;try{data=JSON.parse(raw)}catch(_){throw Error('Update service returned a non-JSON response (HTTP '+response.status+'). Check web service logs.')}if(!response.ok)throw Error(data.error||'Check failed');
  updateAvailable=!!data.update_available;
  out.textContent='Branch: '+data.branch+' · Installed: '+data.installed.slice(0,8)+' · Remote: '+data.remote.slice(0,8)+(updateAvailable?' · Update available':' · Up to date');
  button.disabled=!updateAvailable;
 }catch(error){out.textContent='Update check failed: '+error.message}
 await refreshUpdateProgress();
}
async function refreshUpdateProgress(){
 try{
  const response=await fetch('/api/update/progress',{cache:'no-store'});
  if(!response.ok)return;
  const data=await response.json();
  document.getElementById('update-log').textContent=(data.status||'not started')+'\\n'+(data.log||'');
  if(data.status==='running')document.getElementById('install-update').disabled=true;
  if(data.status==='completed'||data.status==='failed')document.getElementById('update-status').textContent='Last update: '+data.status+'. Review log below.';
 }catch(error){}
}
async function installSoftwareUpdate(){
 if(!updateAvailable||!confirm('Install the available update? Tests will run, then both services will restart.'))return;
 const out=document.getElementById('update-status');
 document.getElementById('install-update').disabled=true;
 try{
  const response=await fetch('/api/update/install',{method:'POST',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify({confirm:true})});
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
async function refreshStatus(){
 try{
  const response=await fetch('/api/status',{cache:'no-store'});
  if(!response.ok)throw Error('Status unavailable');
  const data=await response.json();
  document.getElementById('feed-status').textContent='MLB feed: '+data.feed.state+' | Cached games: '+data.feed.games+(data.feed.error?' | Error: '+data.feed.error:'');
  document.getElementById('feed-indicator').dataset.state=data.feed.error?'error':(data.feed.state==='ok'||data.feed.state==='healthy'?'healthy':'unknown');
  const when=timestamp=>timestamp?new Date(timestamp*1000).toLocaleString():'Not yet';
  document.getElementById('last-refresh').textContent='Last attempt: '+when(data.feed.last_attempt)+' | Last successful refresh: '+when(data.feed.last_success);
  document.getElementById('current-game').textContent=data.current_game?('On board: '+data.current_game.away+' @ '+data.current_game.home+' | '+data.current_game.status):'No MLB game selected';
  document.getElementById('system-info').textContent='Application: '+data.application+' | Board: '+data.board.width+' × '+data.board.height+' | Uptime: '+data.uptime_seconds+' seconds | Configurator: online';
 }catch(err){document.getElementById('feed-indicator').dataset.state='error';document.getElementById('feed-status').textContent=err.message;document.getElementById('system-info').textContent=err.message}
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
load().catch(err=>document.getElementById('status').textContent=err.message);
loadSettings().catch(err=>document.getElementById('settings-status').textContent=err.message);
</script></body></html>'''

def make_handler(config_dir,token,frame_provider=None,settings_callback=None,feed_status=None,board_provider=None,countdown_status=None):
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
        def send_login(self):
            body=LOGIN_HTML.encode()
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
            if not self.authenticated():
                if path=='/':
                    self.send_response(303);self.send_header('Location','/login');self.end_headers()
                else:self.send_json(401,{'error':'Authentication required'})
                return
            if path=='/':
                body=HTML.replace('__TOKEN__',json.dumps(token)).replace('__PREVIEW_VERSION__',display_version()).encode()
                self.send_response(200)
                self.send_header('Content-Type','text/html; charset=utf-8')
                self.send_header('Cache-Control','no-store')
                self.send_header('Content-Length',str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif path=='/board':
                body=BOARD_HTML.encode()
                self.send_response(200)
                self.send_header('Content-Type','text/html; charset=utf-8')
                self.send_header('Cache-Control','no-store')
                self.send_header('Content-Length',str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif path=='/frame.json':
                if board_provider is None:
                    self.send_json(503,{'error':'Board emulator not configured'})
                else:
                    frame=board_provider()
                    self.send_json(200,{'width':frame.width,'height':frame.height,'pixels':[pixel for row in frame.pixels for pixel in row]})
            elif path=='/api/config':
                try:self.send_json(200,read_config(config_dir))
                except (OSError,ValueError) as exc:self.send_json(500,{'error':str(exc)})
            elif path=='/api/matrix-status':
                try:
                    result=subprocess.run(['systemctl','is-active','uls-matrix.service'],capture_output=True,text=True,timeout=4)
                    state=result.stdout.strip() or 'unknown'
                    saved=load_matrix_settings(Path(config_dir)/'matrix.json')
                    desired=saved['enabled']
                    if not desired and state=='inactive':
                        label='Disabled by configuration'
                    elif not desired and state=='active':
                        label='Running; saved disable not yet applied'
                    elif desired and state=='active':
                        label='Running'
                    elif desired and state in ('inactive','failed'):
                        label='Not running; check service or apply saved settings'
                    else:
                        label='Service state: '+state
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
                    log=(root/'latest.log').read_text(encoding='utf-8')[-12000:]
                except OSError:
                    state,log='not started',''
                self.send_json(200,{'status':state,'log':log})
            elif path=='/api/system':
                from .system_diagnostics import system_status
                self.send_json(200,system_status())
            elif path=='/api/status':
                feed=feed_status() if feed_status else {'state':'unavailable','games':0,'error':None}
                game=frame_provider() if frame_provider else None
                current={'away':game.away,'home':game.home,'status':game.status} if game else None
                self.send_json(200,{'application':'Universal LED Scoreboard','uptime_seconds':int(time.monotonic()-started),'board':{'width':64,'height':32,'backend':'emulator'},'feed':feed,'current_game':current})
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
                    self.send_json(401,{'error':'Invalid credentials'});return
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
            if path not in ('/api/mlb-colors','/api/nhl-colors','/api/config','/api/frame','/api/settings','/api/wifi/control','/api/service/restart','/api/news-sources','/api/time-weather','/api/weather-key','/api/season-countdown','/api/update/install','/api/matrix-settings','/api/matrix/apply'):
                self.send_error(404);return
            if not secrets.compare_digest(self.headers.get('X-Configurator-Token',''),token):
                self.send_json(403,{'error':'Invalid session token'});return
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=65536:
                    self.send_json(413,{'error':'Invalid request size'});return
                if self.headers.get('Content-Type','').split(';')[0].strip()!='application/json':
                    self.send_json(415,{'error':'JSON required'});return
                data=json.loads(self.rfile.read(size))
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
                    if data != {'confirm':True}:
                        raise ValueError('Explicit update confirmation required')
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
    nhl_renderer = ConfiguredNHLRenderer(nhl_feed, config_dir=args.config_dir)
    from .nba_feed import NBAFeed
    from .nba_runtime import BackgroundNBAFeed
    from .nba_engine import ConfiguredNBARenderer
    nba_feed = BackgroundNBAFeed(NBAFeed())
    nba_renderer = ConfiguredNBARenderer(nba_feed)
    from .wnba_feed import WNBAFeed
    from .wnba_engine import ConfiguredWNBARenderer
    wnba_feed = BackgroundNBAFeed(WNBAFeed())
    wnba_renderer = ConfiguredWNBARenderer(wnba_feed)
    from .nfl_feed import NFLFeed
    from .nfl_runtime import BackgroundNFLFeed
    from .nfl_engine import ConfiguredNFLRenderer
    nfl_feed = BackgroundNFLFeed(NFLFeed())
    nfl_renderer = ConfiguredNFLRenderer(nfl_feed)
    renderer.news = None  # Universal news is owned by the shared board scheduler.
    board = MultiSportRenderer(renderer, nhl_renderer, news=news, settings_getter=renderer.settings, nba_renderer=nba_renderer, wnba_renderer=wnba_renderer, nfl_renderer=nfl_renderer)
    # Apply persisted sport choice on service startup, not just after web saves.
    def game():
        return board.game()
    def apply_settings(settings):
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
        enabled = [sport for sport in ('mlb', 'nhl', 'nba', 'wnba', 'nfl') if settings['sports'][sport]['enabled']]
        renderer.set_supplemental_stride(len(enabled))
        board.configure_rotation(enabled, interval=settings['mlb']['rotation_seconds'],
                                 preferred=settings['active_sport'])
    apply_settings(initial)
    def feed_status():
        return feed.status()
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
    def publish_frames():
        while not frame_stop.is_set():
            try:
                write_frame(frame_path, board.frame())
            except Exception as exc:
                print(f'Frame publishing failed: {exc}', flush=True)
            frame_stop.wait(1.0)
    frame_thread = threading.Thread(target=publish_frames, daemon=True, name='frame-publisher')
    frame_thread.start()
    try:
        with ThreadingHTTPServer((args.host,args.port),make_handler(args.config_dir,token,game,apply_settings,feed_status,board.frame,countdown_status)) as server:
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
if __name__=='__main__':
    main()
