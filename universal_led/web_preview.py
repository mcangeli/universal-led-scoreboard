"""Read-only browser preview server, using only Python's standard library."""
from __future__ import annotations
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from html import escape
from .display import Framebuffer, splash

HTML = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Universal LED Scoreboard Preview</title>
<style>body{font-family:system-ui;background:#0b1422;color:#f5f5f5;text-align:center;padding:2rem}
canvas{width:min(96vw,896px);image-rendering:pixelated;border:8px solid #29384b;background:black}
small{color:#b7c4d2}</style></head><body>
<h1>Universal LED Scoreboard</h1><p>64 × 32 software emulator</p>
<canvas id="led" width="64" height="32" aria-label="LED matrix preview"></canvas>
<p><small>Live preview refreshes once per second. No GPIO hardware required.</small></p>
<script>
const canvas=document.getElementById('led'),ctx=canvas.getContext('2d');
async function refresh(){
 try {
  const response=await fetch('/frame.json',{cache:'no-store'});
  if(!response.ok)throw new Error('Preview unavailable');
  const frame=await response.json();
  if(canvas.width!==frame.width||canvas.height!==frame.height){
   canvas.width=frame.width;canvas.height=frame.height;
  }
  const image=ctx.createImageData(frame.width,frame.height);
  frame.pixels.forEach((rgb,i)=>{image.data[i*4]=rgb[0];image.data[i*4+1]=rgb[1];
   image.data[i*4+2]=rgb[2];image.data[i*4+3]=255;});
  ctx.putImageData(image,0,0);
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
