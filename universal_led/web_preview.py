"""Read-only browser preview server, using only Python's standard library."""
from __future__ import annotations
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from html import escape
from .display import Framebuffer, splash

HTML = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Universal LED Scoreboard Preview</title>
<style>*{box-sizing:border-box}
body{margin:0;font-family:system-ui;background:#0b1422;color:#f5f5f5;text-align:center;padding:clamp(12px,4vw,32px)}
canvas{display:block;width:100%;max-width:896px;height:auto;aspect-ratio:2/1;margin:0 auto;image-rendering:pixelated;border:clamp(3px,1vw,8px) solid #29384b;background:black}
small{color:#b7c4d2}
.preview-controls{margin:12px auto}
.preview-controls button{background:#253850;color:#f5f5f5;border:1px solid #61718a;border-radius:6px;padding:7px 14px;cursor:pointer}
.preview-controls button:focus-visible{outline:2px solid #f0cb7e;outline-offset:3px}</style></head><body>
<h1>Universal LED Scoreboard</h1><p>64 × 32 software emulator</p>
<canvas id="led" width="64" height="32" aria-label="LED matrix preview"></canvas>
<div class="preview-controls"><button id="mode" type="button" aria-pressed="true">LED view · switch to sharp pixels</button></div>
<p><small>Live preview refreshes once per second. No GPIO hardware required.</small></p>
<script>
const canvas=document.getElementById('led'),ctx=canvas.getContext('2d');
const mode=document.getElementById('mode');
let ledMode=true,lastFrame=null;
mode.addEventListener('click',()=>{
 ledMode=!ledMode;
 mode.setAttribute('aria-pressed',String(ledMode));
 mode.textContent=ledMode?'LED view · switch to sharp pixels':'Sharp pixels · switch to LED view';
 if(lastFrame)draw(lastFrame);
});
function draw(frame){
 const scale=8,width=frame.width*scale,height=frame.height*scale;
 if(canvas.width!==width||canvas.height!==height){
  canvas.width=width;canvas.height=height;
 }
 ctx.clearRect(0,0,width,height);
 ctx.fillStyle='#000';ctx.fillRect(0,0,width,height);
 frame.pixels.forEach((rgb,i)=>{
  if(!rgb.some(channel=>channel>0))return;
  const x=(i%frame.width)*scale,y=Math.floor(i/frame.width)*scale;
  const color='rgb('+rgb.join(',')+')';
  ctx.fillStyle=color;
  if(!ledMode){ctx.fillRect(x,y,scale,scale);return;}
  // Browser-only LED diffusion. The underlying RGB framebuffer is unchanged.
  ctx.globalAlpha=0.18;
  ctx.beginPath();ctx.arc(x+4,y+4,3.9,0,Math.PI*2);ctx.fill();
  ctx.globalAlpha=1;
  ctx.beginPath();ctx.arc(x+4,y+4,2.9,0,Math.PI*2);ctx.fill();
 });
}
async function refresh(){
 try {
  const response=await fetch('/frame.json',{cache:'no-store'});
  if(!response.ok)throw new Error('Preview unavailable');
  lastFrame=await response.json();
  draw(lastFrame);
 }catch(err){console.error(err)}
}
refresh();setInterval(refresh,1000);
</script></body></html>"""

def frame_payload(frame):
    """Serialize the same rendered frame for every browser preview surface."""
    return {'width': frame.width, 'height': frame.height,
            'pixels': [pixel for row in frame.pixels for pixel in row]}


def make_handler(frame_provider):
    class PreviewHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                data = HTML.encode('utf-8')
                mime = 'text/html; charset=utf-8'
            elif self.path == '/frame.json':
                import json
                frame = frame_provider()
                data = json.dumps(frame_payload(frame)).encode()
                mime = 'application/json'
            elif self.path == '/health':
                data = b'OK'
                mime = 'text/plain'
            else:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(data)
    return PreviewHandler

def serve(host: str = '127.0.0.1', port: int = 8765, frame_provider=None):
    if frame_provider is None:
        frame_provider = splash
    with ThreadingHTTPServer((host, port), make_handler(frame_provider)) as server:
        print(f'Preview available at http://{host}:{port}', flush=True)
        server.serve_forever()
