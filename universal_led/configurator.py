"""Native LAN configurator and shared scoreboard emulator."""
from __future__ import annotations
import argparse
import json
import secrets
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
</style></head><body>
<header><h1>Universal LED Scoreboard</h1><span class="muted">Native Configurator | Preview 21</span></header>
<main><nav><button type="button" onclick="logout()">Sign Out</button> <a class="board-button" href="/board" target="_blank" rel="noopener" aria-label="Open Board View in a new tab">Open Board View ↗</a> <button type="button" onclick="showPage('dashboard')">Dashboard</button> <button type="button" onclick="showPage('sports')">Sports</button> <button type="button" onclick="showPage('display')">Display</button> <button type="button" onclick="showPage('colors')">Colors</button> <button type="button" onclick="showPage('system')">System</button></nav><section data-page="dashboard"><h2>Dashboard</h2><p id="summary">Loading settings…</p><p id="feed-status" class="muted">MLB feed loading…</p><p id="current-game" class="muted">Waiting for game information…</p><p id="last-refresh" class="muted">Last feed update: pending</p><p class="muted">The board view refreshes independently every second.</p></section><section data-page="sports" hidden><h2>Sports & Rotation</h2><p>MLB is available. Other sports will be enabled as their renderers are completed.</p><label>Favorite MLB team <input id="favorite" maxlength="3" value="ATL"></label><p class="muted">Choose the favorite team for MLB. Rotation and feed timing are under Display.</p><button id="save-settings">Save Sport Settings</button><span id="settings-status" role="status"></span></section><section data-page="display" hidden><h2>Display Settings</h2><label>Game selection <select id="mode"><option value="favorite">Favorite only</option><option value="fallback">Favorite, otherwise all</option><option value="all">All games</option></select></label><p><label>Rotation seconds <input id="rotation" type="number" min="1" max="3600" value="12"></label> <label>Feed refresh seconds <input id="refresh" type="number" min="1" max="3600" value="60"></label></p><button id="save-display">Save Display Settings</button><span id="display-status" role="status"></span></section><section data-page="system" hidden><h2>System</h2><p id="system-info">Checking server information…</p><h3>Wi-Fi</h3><p id="wifi-info">Loading…</p><button type="button" onclick="refreshWifi()">Refresh Wi-Fi</button> <button type="button" onclick="scanWifi()">Scan Networks</button><p id="wifi-scan-status" class="muted"></p><div id="wifi-networks" class="grid"></div><div id="pi-info" class="grid"><p class="muted">Loading Raspberry Pi diagnostics…</p></div><p class="muted">Service status is read-only. Hardware output and remote service controls are not enabled.</p></section><div data-page="colors" hidden><section><h2>64 × 32 Live Preview</h2><canvas id="matrix" width="64" height="32"></canvas>
<p class="muted">Changes preview immediately. Saving is optional.</p><label for="preview-team">Preview favorite team: </label><select id="preview-team"></select><span id="dirty" role="status">All changes saved</span></section>
<section><h2>Scoreboard Colors</h2><div id="scoreboard" class="grid"></div></section>
<section><h2>MLB Team Colors</h2><div id="teams" class="grid"></div></section>
<section><button id="save">Save Color Settings</button> <button id="cancel" type="button">Cancel Changes</button> <button id="reset" type="button">Reset Selected Color</button> <span id="status" role="status"></span>
<p class="muted">Available on your trusted LAN. Backups are created before overwriting existing files.</p></section></div></main>
<script>
const token=__TOKEN__;
async function logout(){await fetch('/logout',{method:'POST',headers:{'X-Configurator-Token':token}});location.href='/login'}
let state=null,saved=null,dirty=false,selectedTeam='ATL',selected=null,settings=null;
function showPage(name){document.querySelectorAll('[data-page]').forEach(el=>el.hidden=el.dataset.page!==name);if(name==='dashboard'||name==='system')refreshStatus();if(name==='system'){refreshSystem();refreshWifi()}}
const clone=value=>JSON.parse(JSON.stringify(value));
function markDirty(){dirty=JSON.stringify(state)!==JSON.stringify(saved);document.getElementById('dirty').textContent=dirty?'Unsaved changes':'All changes saved';}
const hex=rgb=>'#'+rgb.map(x=>x.toString(16).padStart(2,'0')).join('');
const rgb=hex=>[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16));
function section(name){
 const target=document.getElementById(name);target.replaceChildren();
 Object.entries(state[name]).sort().forEach(([key,value])=>{
  const wrapper=document.createElement('div');wrapper.className='item';
  const label=document.createElement('label');label.textContent=key;
  const input=document.createElement('input');input.type='color';input.value=hex(value);
  input.setAttribute('aria-label',key+' color');
  input.oninput=()=>{state[name][key]=rgb(input.value);selected={name,key};markDirty();draw()};
  input.onfocus=()=>{selected={name,key}};
  wrapper.append(label,input);target.append(wrapper);
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
async function loadSettings(){
 const response=await fetch('/api/settings',{cache:'no-store'});
 if(!response.ok)throw Error('Could not load sport settings');
 settings=await response.json();
 const mlb=settings.mlb;
 document.getElementById('favorite').value=mlb.favorite_team;
 document.getElementById('mode').value=mlb.mode;
 document.getElementById('rotation').value=mlb.rotation_seconds;
 document.getElementById('refresh').value=mlb.refresh_seconds;
 document.getElementById('summary').textContent='Active sport: MLB | Favorite: '+mlb.favorite_team+' | Rotation: '+mlb.mode;
}
async function saveSportSettings(source){
 const status=document.getElementById(source==='display'?'display-status':'settings-status');status.textContent='Saving…';
 const next=clone(settings);
 if(source==='sports')next.mlb.favorite_team=document.getElementById('favorite').value.trim().toUpperCase();
 else {next.mlb.mode=document.getElementById('mode').value;
 next.mlb.rotation_seconds=Number(document.getElementById('rotation').value);
 next.mlb.refresh_seconds=Number(document.getElementById('refresh').value)}
 try{
  const response=await fetch('/api/settings',{method:'POST',headers:{'Content-Type':'application/json','X-Configurator-Token':token},body:JSON.stringify(next)});
  const result=await response.json();if(!response.ok)throw Error(result.error||'Save failed');
  settings=result.settings;status.textContent='Saved and applied to configurator preview.';
  await loadSettings();draw();await refreshStatus();
 }catch(err){status.textContent=err.message}
}
document.getElementById('save-settings').onclick=()=>saveSportSettings('sports');
document.getElementById('save-display').onclick=()=>saveSportSettings('display');
async function refreshStatus(){
 try{
  const response=await fetch('/api/status',{cache:'no-store'});
  if(!response.ok)throw Error('Status unavailable');
  const data=await response.json();
  document.getElementById('feed-status').textContent='MLB feed: '+data.feed.state+' | Cached games: '+data.feed.games+(data.feed.error?' | Error: '+data.feed.error:'');
  const when=timestamp=>timestamp?new Date(timestamp*1000).toLocaleString():'Not yet';
  document.getElementById('last-refresh').textContent='Last attempt: '+when(data.feed.last_attempt)+' | Last successful refresh: '+when(data.feed.last_success);
  document.getElementById('current-game').textContent=data.current_game?('On board: '+data.current_game.away+' @ '+data.current_game.home+' | '+data.current_game.status):'No MLB game selected';
  document.getElementById('system-info').textContent='Application: '+data.application+' | Board: '+data.board.width+' × '+data.board.height+' | Uptime: '+data.uptime_seconds+' seconds | Configurator: online';
 }catch(err){document.getElementById('feed-status').textContent=err.message;document.getElementById('system-info').textContent=err.message}
}
async function refreshWifi(){const response=await fetch('/api/wifi');const data=await response.json();document.getElementById('wifi-info').textContent=data.available?('Radio: '+data.state+' | '+data.devices.map(d=>d.device+': '+d.state+' '+d.connection).join(', ')):'NetworkManager unavailable';}
async function scanWifi(){
 const status=document.getElementById('wifi-scan-status');const target=document.getElementById('wifi-networks');status.textContent='Scanning…';target.replaceChildren();
 try{const response=await fetch('/api/wifi/scan',{cache:'no-store'});const data=await response.json();if(!response.ok||!data.available)throw Error(data.error||'Scan failed');
 status.textContent=data.networks.length+' network(s) found. Connection setup will be enabled after safe recovery is implemented.';
 data.networks.forEach(network=>{const item=document.createElement('div');item.className='item';const text=document.createElement('span');text.textContent=network.ssid+' | '+network.signal+'% | '+network.security+(network.connected?' | Connected':'');item.append(text);target.append(item)});
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
    sessions=Sessions()
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
                body=HTML.replace('__TOKEN__',json.dumps(token)).encode()
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
            elif path=='/api/wifi/scan':
                from .wifi_scan import scan_networks
                self.send_json(200,scan_networks())
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
            if path not in ('/api/config','/api/frame','/api/settings'):
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
        print('Administrator password saved. Restart service to invalidate existing sessions.')
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
