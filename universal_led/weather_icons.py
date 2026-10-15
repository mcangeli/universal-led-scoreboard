"""Original 16x16 pixel-art weather symbols for the RGB matrix."""
SUN=(255,195,55)
SUN_EDGE=(255,145,42)
CLOUD=(202,218,232)
SHADE=(112,143,173)
RAIN=(68,160,255)
SNOW=(230,247,255)
STORM=(255,219,72)

def _disc(f,x,y,cx,cy,r,color):
    for dy in range(-r,r+1):
        for dx in range(-r,r+1):
            if dx*dx+dy*dy<=r*r:
                f.pixel(x+cx+dx,y+cy+dy,color)

def _sun(f,x,y,partly=False):
    cx,cy=(6,6) if partly else (8,8)
    _disc(f,x,y,cx,cy,4,SUN)
    for dx,dy in ((0,-7),(0,7),(-7,0),(7,0),(-5,-5),(5,-5),(-5,5),(5,5)):
        for step in (0,1):
            f.pixel(x+cx+dx+(1 if dx<0 else -1 if dx>0 else 0)*step,
                    y+cy+dy+(1 if dy<0 else -1 if dy>0 else 0)*step,SUN_EDGE)

def _cloud(f,x,y):
    _disc(f,x,y,6,9,4,CLOUD)
    _disc(f,x,y,11,7,4,CLOUD)
    _disc(f,x,y,14,10,3,CLOUD)
    for py in range(9,14):
        for px in range(3,16):
            f.pixel(x+px,y+py,CLOUD if py<12 else SHADE)

def draw_weather_icon(frame,x,y,weather_code):
    """Draw condition-specific artwork without network calls or image assets."""
    code=int(weather_code)
    if code==0:
        _sun(frame,x,y)
    elif code in (1,2):
        _sun(frame,x,y,True)
        _cloud(frame,x,y)
    elif code==3:
        _cloud(frame,x,y)
    elif code in (45,48):
        _cloud(frame,x,y)
        for py in (15,17):
            for px in range(3,16,3):
                frame.pixel(x+px,y+py,SHADE)
    elif code in (71,73,75,77,85,86):
        _cloud(frame,x,y)
        for px,py in ((5,15),(10,16),(15,15)):
            frame.pixel(x+px,y+py,SNOW)
            frame.pixel(x+px-1,y+py,SNOW)
            frame.pixel(x+px,y+py-1,SNOW)
    elif code in (95,96,99):
        _cloud(frame,x,y)
        for px,py in ((9,14),(8,15),(10,15),(7,17),(9,17)):
            frame.pixel(x+px,y+py,STORM)
    else:
        _cloud(frame,x,y)
        for px,py in ((5,15),(10,16),(15,15)):
            frame.pixel(x+px,y+py,RAIN)
            frame.pixel(x+px-1,y+py+1,RAIN)
