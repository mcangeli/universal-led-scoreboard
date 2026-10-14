"""Hardware-independent 64x32 RGB framebuffer and startup splash."""
from dataclasses import dataclass, field
RGB = tuple[int, int, int]
FONT = {
'A':('01110','10001','10001','11111','10001','10001','10001'),
'B':('11110','10001','10001','11110','10001','10001','11110'),
'C':('01111','10000','10000','10000','10000','10000','01111'),
'D':('11110','10001','10001','10001','10001','10001','11110'),
'E':('11111','10000','10000','11110','10000','10000','11111'),
'I':('11111','00100','00100','00100','00100','00100','11111'),
'L':('10000','10000','10000','10000','10000','10000','11111'),
'N':('10001','11001','10101','10101','10011','10001','10001'),
'O':('01110','10001','10001','10001','10001','10001','01110'),
'R':('11110','10001','10001','11110','10100','10010','10001'),
'S':('01111','10000','10000','01110','00001','00001','11110'),
'U':('10001','10001','10001','10001','10001','10001','01110'),
'V':('10001','10001','10001','10001','10001','01010','00100'),
' ':('00000',)*7,
'M':('10001','11011','10101','10101','10001','10001','10001'),
'Y':('10001','10001','01010','00100','00100','00100','00100'),
'T':('11111','00100','00100','00100','00100','00100','00100'),
'0':('01110','10001','10011','10101','11001','10001','01110'),
'1':('00100','01100','00100','00100','00100','00100','01110'),
'2':('01110','10001','00001','00010','00100','01000','11111'),
'3':('11110','00001','00001','01110','00001','00001','11110'),
'4':('00010','00110','01010','10010','11111','00010','00010'),
'5':('11111','10000','10000','11110','00001','00001','11110'),
'6':('01111','10000','10000','11110','10001','10001','01110'),
'7':('11111','00001','00010','00100','01000','01000','01000'),
'8':('01110','10001','10001','01110','10001','10001','01110'),
'9':('01110','10001','10001','01111','00001','00001','11110'),
}
@dataclass
class Framebuffer:
    width: int = 64
    height: int = 32
    pixels: list[list[RGB]] = field(init=False)
    def __post_init__(self):
        if self.width < 1 or self.height < 1:
            raise ValueError('Invalid framebuffer dimensions')
        self.pixels = [[(0,0,0) for _ in range(self.width)] for _ in range(self.height)]
    def pixel(self, x: int, y: int, color: RGB):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = color
    def text(self, value: str, x: int, y: int, color: RGB, scale: int = 1):
        if scale < 1:
            raise ValueError('Scale must be positive')
        for index, char in enumerate(value.upper()):
            glyph = FONT.get(char)
            if glyph is None:
                raise ValueError(f'Unsupported character: {char!r}')
            for row, bits in enumerate(glyph):
                for col, bit in enumerate(bits):
                    if bit == '1':
                        for dy in range(scale):
                            for dx in range(scale):
                                self.pixel(x+(index*6+col)*scale+dx, y+row*scale+dy, color)
    def ppm(self) -> bytes:
        header = f'P6\n{self.width} {self.height}\n255\n'.encode('ascii')
        return header + bytes(channel for row in self.pixels for rgb in row for channel in rgb)

def splash(width: int = 64, height: int = 32) -> Framebuffer:
    if width < 64 or height < 32:
        raise ValueError('Classic splash requires at least 64x32')
    fb = Framebuffer(width, height)
    x0, y0 = (width-64)//2, (height-32)//2
    # Three centered rows fit the native 64x32 panel without clipping.
    for label, y, color in (
        ('UNIVERSAL', 2, (245, 245, 240)),
        ('LED', 11, (239, 195, 95)),
        ('SCOREBOARD', 20, (239, 195, 95)),
    ):
        text_width = len(label) * 6 - 1
        fb.text(label, x0 + (64 - text_width) // 2, y0 + y, color)
    # Keep indicators on their own bottom row, separated from the 7px text.
    for index, color in enumerate(((222,82,82),(90,157,217),(102,193,129),(229,187,79),(166,136,219))):
        for x in range(x0+19+index*6, x0+23+index*6):
            fb.pixel(x, y0+30, color)
    return fb
