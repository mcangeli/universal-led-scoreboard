"""Native LAN configurator and shared scoreboard emulator."""
from __future__ import annotations
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

LOGIN_HTML='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Scoreboard Login</title><style>body{font:16px system-ui;background:#0c1624;color:#e9eef5;max-width:400px;margin:12vh auto;padding:24px}form{background:#18283b;border:1px solid #34445b;border-radius:12px;padding:24px}input,button{box-sizing:border-box;width:100%;padding:12px;margin:8px 0;border-radius:6px}button{background:#d7b46d;border:0;font-weight:bold;cursor:pointer}</style></head><body><form method="post" action="/login"><h2>Universal LED Scoreboard</h2><p>Administrator login</p><label>Password<input name="password" type="password" autocomplete="current-password" required></label><button type="submit">Sign In</button><p>Use HTTPS before accessing outside a trusted LAN.</p></form></body></html>'''

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
.dashboard-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin:14px 0 22px}.dashboard-tile{background:#0e1623;border:1px solid #263650;border-radius:9px;padding:15px;min-width:0}.dashboard-tile h3{font-size:13px;text-transform:uppercase;letter-spacing:.05em;color:#aebed1;margin:0 0 9px}.dashboard-tile p{margin:0;overflow-wrap:anywhere;line-height:1.5}.status-dot{display:inline-block;width:9px;height:9px;border-radius:50%;background:#91a0b7;margin-left:5px}.status-dot[data-state="healthy"]{background:#4cc98a}.status-dot[data-state="error"]{background:#f07b72}.sidebar-footer .board-button{display:block;text-align:center;background:#1769d2;color:white;border-radius:7px;padding:11px 12px;text-decoration:none;font-weight:700}.sidebar-footer .board-button:hover{background:#287be0}.favorite-fieldset{border:1px solid #34445b;border-radius:9px;padding:14px;margin:12px 0}.favorite-team-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:9px;max-height:310px;overflow:auto;padding:8px}.favorite-team-grid label{display:flex;align-items:center;gap:9px;padding:7px;border-radius:5px;background:#101d2c;cursor:pointer}.favorite-team-grid input{accent-color:#d7b46d}.favorite-fieldset legend{font-weight:700}.color-editor{display:grid;grid-template-columns:1fr auto auto;gap:8px 12px;align-items:center}.color-editor .color-name{font-weight:700;min-width:0;overflow-wrap:anywhere}.color-editor .color-hex{font:12px ui-monospace,monospace;color:#d7b46d}.color-channels{grid-column:1/-1;display:grid;gap:6px;width:100%}.color-channel{display:grid;grid-template-columns:44px minmax(0,1fr) 32px;align-items:center;gap:7px;font-size:12px}.color-channel input[type=range]{width:100%;min-width:0;accent-color:#d7b46d}.color-channel output{text-align:right;font-variant-numeric:tabular-nums}.color-editor input[type=color]{width:42px;height:32px}</style></head><body>
<header><div><div class="eyebrow">UNIVERSAL LED SCOREBOARD</div><h1>Scoreboard Configurator</h1><span class="muted">__PREVIEW_VERSION__</span></div><span class="header-note">64 × 32 Display Manager</span></header>
<div class="shell"><aside><div class="side-title">DISPLAY</div><nav aria-label="Configurator navigation"><button class="nav-item" type="button" onclick="showPage('dashboard')">◫ Dashboard</button> <button class="nav-item" type="button" onclick="showPage('sports')">⚾ Sports</button> <button class="nav-item" type="button" onclick="showPage('display')">▦ Display</button> <button class="nav-item" type="button" onclick="showPage('colors')">◉ Colors</button> <button class="nav-item" type="button" onclick="showPage('wifi')">◈ Wi-Fi</button> <button class="nav-item" type="button" onclick="showPage('system')">⚙ System</button></nav><div class="sidebar-footer"><a class="board-button" href="/board" target="_blank" rel="noopener">Open Board View ↗</a><button type="button" class="signout" onclick="logout()">Sign Out</button></div></aside><main><section data-page="dashboard"><h2>Dashboard</h2><div class="dashboard-grid"><div class="dashboard-tile"><h3>Active Configuration</h3><p id="summary">Loading settings…</p></div><div class="dashboard-tile"><h3>MLB Feed <span id="feed-indicator" class="status-dot" aria-hidden="true"></span></h3><p id="feed-status" class="muted" role="status">MLB feed loading…</p></div><div class="dashboard-tile"><h3>Current Game</h3><p id="current-game" class="muted">Waiting for game information…</p></div><div class="dashboard-tile"><h3>Feed Refresh</h3><p id="last-refresh" class="muted">Last feed update: pending</p></div></div><p class="muted">The board view refreshes independently every second.</p><button type="button" id="restart-scoreboard" onclick="restartScoreboard()">Restart Scoreboard</button><p id="restart-status" class="muted" role="status" aria-live="polite">Restart the scoreboard service after changing configuration. This does not reboot the Pi.</p></section><section data-page="sports" hidden><h2>Sports & Rotation</h2><p>MLB is available. Other sports will be enabled as their renderers are completed.</p><fieldset class="favorite-fieldset"><legend>Favorite MLB teams</legend><p class="muted">Select one or more teams. Games featuring any favorite will be included.</p><div id="favorite-teams" class="favorite-team-grid"><label><input type="checkbox" value="ARI"> Arizona Diamondbacks</label><label><input type="checkbox" value="ATL"> Atlanta Braves</label><label><input type="checkbox" value="BAL"> Baltimore Orioles</label><label><input type="checkbox" value="BOS"> Boston Red Sox</label><label><input type="checkbox" value="CHC"> Chicago Cubs</label><label><input type="checkbox" value="CWS"> Chicago White Sox</label><label><input type="checkbox" value="CIN"> Cincinnati Reds</label><label><input type="checkbox" value="CLE"> Cleveland Guardians</label><label><input type="checkbox" value="COL"> Colorado Rockies</label><label><input type="checkbox" value="DET"> Detroit Tigers</label><label><input type="checkbox" value="HOU"> Houston Astros</label><label><input type="checkbox" value="KCR"> Kansas City Royals</label><label><input type="checkbox" value="LAA"> Los Angeles Angels</label><label><input type="checkbox" value="LAD"> Los Angeles Dodgers</label><label><input type="checkbox" value="MIA"> Miami Marlins</label><label><input type="checkbox" value="MIL"> Milwaukee Brewers</label><label><input type="checkbox" value="MIN"> Minnesota Twins</label><label><input type="checkbox" value="NYM"> New York Mets</label><label><input type="checkbox" value="NYY"> New York Yankees</label><label><input type="checkbox" value="OAK"> Athletics</label><label><input type="checkbox" value="PHI"> Philadelphia Phillies</label><label><input type="checkbox" value="PIT"> Pittsburgh Pirates</label><label><input type="checkbox" value="SDP"> San Diego Padres</label><label><input type="checkbox" value="SFG"> San Francisco Giants</label><label><input type="checkbox" value="SEA"> Seattle Mariners</label><label><input type="checkbox" value="STL"> St. Louis Cardinals</label><label><input type="checkbox" value="TBR"> Tampa Bay Rays</label><label><input type="checkbox" value="TEX"> Texas Rangers</label><label><input type="checkbox" value="TOR"> Toronto Blue Jays</label><label><input type="checkbox" value="WSN"> Washington Nationals</label></div><p id="favorite-summary" class="muted" aria-live="polite"></p></fieldset><p class="muted">Choose the favorite team for MLB. Rotation and feed timing are under Display.</p><button id="save-settings">Save Sport Settings</button><span id="settings-status" role="status"></span></section><section data-page="display" hidden><h2>Display Settings</h2><label>Game selection <select id="mode"><option value="favorite">Favorite only</option><option value="fallback">Favorite, otherwise all</option><option value="all">All games</option></select></label><p><label>Rotation seconds <input id="rotation" type="number" min="1" max="3600" value="12"></label> <label>Feed refresh seconds <input id="refresh" type="number" min="1" max="3600" value="60"></label></p><h3>MLB live screen rotation</h3><p class="muted">Percent of each live game interval. Last Play uses the remaining time. Classic must be at least 1%.</p><p><label>Classic % <input id="live-classic" type="number" min="1" max="100" step="1" value="50"></label> <label>Matchup % <input id="live-matchup" type="number" min="0" max="99" step="1" value="25"></label></p><p id="live-play-share" class="muted" aria-live="polite">Last Play: 25%</p><button id="save-display">Save Display Settings</button><span id="display-status" role="status"></span></section><section data-page="wifi" hidden><h2>Wi-Fi & Hotspot</h2><p id="wifi-recovery-readiness" class="muted" role="status">Checking recovery protection…</p><p id="wifi-info">Loading…</p><h4>Saved Wi-Fi connections</h4><div id="wifi-profiles" class="grid"><p class="muted">Loading saved profiles…</p></div><button type="button" onclick="refreshWifi()">Refresh Wi-Fi</button> <button type="button" onclick="scanWifi()">Scan Networks</button><p id="wifi-scan-status" class="muted" role="status" aria-live="polite">Click Scan Networks to list nearby access points.</p><div id="wifi-networks" class="grid"></div><div id="wifi-selection" hidden><h4>Selected network: <span id="wifi-selected-name"></span></h4><p id="wifi-selected-security"></p><label>Network password <input id="wifi-password" type="password" autocomplete="off" minlength="8" maxlength="63"></label><p id="wifi-connect-note" class="muted">Network switching requires the privileged helper and recovery worker. Keep Ethernet connected during initial testing.</p><button type="button" onclick="connectWifi()">Connect Wi-Fi</button><p id="wifi-connect-result" role="status"></p></div><h4>Hotspot Settings</h4><p class="muted">Change the password for Universal-LED-Setup. Changes take effect the next time the hotspot starts.</p><label>New hotspot password <input id="hotspot-password" type="password" minlength="8" maxlength="63" autocomplete="new-password"></label> <label>Confirm password <input id="hotspot-confirm" type="password" minlength="8" maxlength="63" autocomplete="new-password"></label> <button type="button" onclick="saveHotspotPassword()">Save Hotspot Password</button><p id="hotspot-result" role="status"></p></section><section data-page="system" hidden><h2>System</h2><p id="system-info">Checking server information…</p><div id="pi-info" class="grid"><p class="muted">Loading Raspberry Pi diagnostics…</p></div><p class="muted">Service status is read-only. Hardware output and remote service controls are not enabled.</p></section><div data-page="colors" hidden><section><h2>64 × 32 Live Preview</h2><canvas id="matrix" width="64" height="32"></canvas>
<p class="muted">Changes preview immediately. Saving is optional.</p><label for="preview-team">Preview favorite team: </label><select id="preview-team"></select><span id="dirty" role="status">All changes saved</span></section>
<section><h2>Scoreboard Colors</h2><div id="scoreboard" class="grid"></div></section>
<section><h2>MLB Team Colors</h2><div id="teams" class="grid"></div></section>
<section><button id="save">Save Color Settings</button> <button id="cancel" type="button">Cancel Changes</button> <button id="reset" type="button">Reset Selected Color</button> <span id="status" role="status"></span>
<p class="muted">Available on your trusted LAN. Backups are created before overwriting existing files.</p></section></div></main></div>
<script>
const token=__TOKEN__;
async function logout(){await fetch('/logout',{method:'POST',headers:{'X-Configurator-Token':token}});location.href='/login'}
let state=null,saved=null,dirty=false,selectedTeam='ATL',selected=null,settings=null;
function showPage(name){document.querySelectorAll('.nav-item').forEach(button=>button.classList.toggle('active',button.getAttribute('onclick')==="showPage('"+name+"')"));document.querySelectorAll('[data-page]').forEach(el=>el.hidden=el.dataset.page!==name);if(name==='dashboard'||name==='system')refreshStatus();if(name==='system')refreshSystem();if(name==='wifi'){refreshWifi();refreshWifiProfiles();refreshRecoveryReadiness();scanWifi()}}
const clone=value=>JSON.parse(JSON.stringify(value));
function markDirty(){dirty=JSON.stringify(state)!==JSON.stringify(saved);document.getElementById('dirty').textContent=dirty?'Unsaved changes':'All changes saved';}
const hex=rgb=>'#'+rgb.map(x=>x.toString(16).padStart(2,'0')).join('');
const rgb=hex=>[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16));
function section(name){
 const target=document.getElementById(name);target.replaceChildren();
 Object.entries(state[name]).sort().forEach(([key,value])=>{
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
 Object.keys(state.teams).sort().forEach(team=>{const option=document.createElement('option');option.value=team;option.textContent=team;picker.append(option)});
 picker.value=selectedTeam in state.teams?selectedTeam:'ATL';selectedTeam=picker.value;
 section('scoreboard');section('teams');markDirty();draw();
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
document.getElementById('preview-team').onchange=event=>{selectedTeam=event.target.value;draw()};
document.getElementById('cancel').onclick=()=>{state=clone(saved);section('scoreboard');section('teams');markDirty();draw();document.getElementById('status').textContent='Unsaved changes discarded.'};
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
async function loadSettings(){
 const response=await fetch('/api/settings',{cache:'no-store'});
 if(!response.ok)throw Error('Could not load sport settings');
 settings=await response.json();
 const mlb=settings.mlb;
 setFavoriteTeams(mlb.favorite_teams);
 document.getElementById('mode').value=mlb.mode;
 document.getElementById('rotation').value=mlb.rotation_seconds;
 document.getElementById('refresh').value=mlb.refresh_seconds;
 document.getElementById('live-classic').value=mlb.live_classic_percent;
 document.getElementById('live-matchup').value=mlb.live_matchup_percent;
 updateLiveShare();
 document.getElementById('summary').textContent='Active sport: MLB | Favorites: '+mlb.favorite_teams.join(', ')+' | Rotation: '+mlb.mode;
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
 const status=document.getElementById(source==='display'?'display-status':'settings-status');status.textContent='Saving…';
 const next=clone(settings);
 if(source==='sports'){
  next.mlb.favorite_teams=getFavoriteTeams();
  if(!next.mlb.favorite_teams.length){status.textContent='Select at least one favorite team.';return;}
 }
 else {next.mlb.mode=document.getElementById('mode').value;
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
document.getElementById('save-display').onclick=()=>saveSportSettings('display');
async function restartScoreboard(){
 const button=document.getElementById('restart-scoreboard'),status=document.getElementById('restart-status');
 if(!confirm('Restart the scoreboard service now? The display may briefly go blank.'))return;
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

def make_handler(config_dir,token,frame_provider=None,settings_callback=None,feed_status=None,board_provider=None):
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
                self.send_json(200,{'teams':TEAM_COLORS,'scoreboard':DEFAULT_SCOREBOARD})
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
            if path not in ('/api/config','/api/frame','/api/settings','/api/wifi/control','/api/service/restart'):
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
                if path=='/api/service/restart':
                    if data != {'confirm':True}:
                        raise ValueError('Explicit restart confirmation required')
                    # The configurator may be hosted by the service being restarted.
                    # Reply before invoking systemctl so the HTTP request is not killed.
                    def restart_after_response():
                        time.sleep(0.75)
                        try:
                            subprocess.run(['systemctl','--user','restart','universal-led-scoreboard.service'],
                                           capture_output=True,text=True,timeout=20,check=False)
                        except (OSError,subprocess.TimeoutExpired):
                            pass
                    self.send_json(202,{'ok':True,'message':'Scoreboard restart scheduled'})
                    threading.Thread(target=restart_after_response,daemon=True,name='scoreboard-restart').start()
                    return
                if path=='/api/wifi/control':
                    from .wifi_web_bridge import request_wifi_change
                    if not isinstance(data,dict) or data.get('action') not in ('connect_saved','connect_new','confirm','hotspot','hotspot_password'):
                        raise ValueError('Unsupported Wi-Fi operation')
                    result=request_wifi_change(data)
                    self.send_json(200 if result.get('ok') or result.get('confirmed') else 409,result)
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
    token=secrets.token_urlsafe(32)
    from .runtime_settings import ConfiguredMLBRenderer
    from .sport_settings import load_settings
    initial=load_settings(args.config_dir)
    feed=BackgroundMLBFeed(MLBFeed(team=None,date=args.date,refresh_seconds=initial['mlb']['refresh_seconds']))
    feed.start()
    renderer=ConfiguredMLBRenderer(args.config_dir,feed)
    def game():
        return renderer.game()
    def apply_settings(settings):
        renderer.apply(settings)
        feed.feed.refresh_seconds=settings['mlb']['refresh_seconds']
    def feed_status():
        return feed.status()
    try:
        with ThreadingHTTPServer((args.host,args.port),make_handler(args.config_dir,token,game,apply_settings,feed_status,renderer.frame)) as server:
            print(f'Configurator listening on {args.host}:{args.port}',flush=True)
            server.serve_forever()
    finally:
        feed.stop()
if __name__=='__main__':
    main()
