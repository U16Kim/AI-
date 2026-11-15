import sys, colorsys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SS = 3                      # supersampling factor over the 1280x670 design grid
W1, H1 = 1280, 670
W, H = W1 * SS, H1 * SS
SEMI = '/usr/share/fonts/opentype/noto/NotoSerifCJK-SemiBold.ttc'
MED = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Medium.ttc'
PALT = ['palt']

def font(path, size1x):
    return ImageFont.truetype(path, int(round(size1x * SS)), index=0, layout_engine=ImageFont.Layout.RAQM)

def lum(c):
    c = [v / 255.0 for v in c]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]

def contrast(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)

def hsv255(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h / 360.0, s, v)
    return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))

class Layer:
    def __init__(self):
        self.mask = Image.new('L', (W, H), 0)        # union of all glyphs (for the shadow)
        self.rgba = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        self.dm = ImageDraw.Draw(self.mask)
        self.dr = ImageDraw.Draw(self.rgba)

    def run(self, x1, y1, text, f, fill, track_em=0.0, size1x=0):
        """draw text char by char with proportional (palt) advances + tracking; x1,y1 on the 1x grid (baseline)."""
        x = x1 * SS; y = y1 * SS
        for ch in text:
            self.dr.text((x, y), ch, font=f, fill=fill + (255,), anchor='ls', features=PALT)
            self.dm.text((x, y), ch, font=f, fill=255, anchor='ls', features=PALT)
            x += f.getlength(ch, features=PALT) + track_em * size1x * SS
        return x / SS

    def width(self, text, f, track_em=0.0, size1x=0):
        return (sum(f.getlength(ch, features=PALT) for ch in text) + track_em * size1x * SS * len(text)) / SS

    def _ink(self, ch, f):
        """measure real ink extent by rendering the glyph: returns (left, right) offsets from the origin, in SS px"""
        n = int(f.size * 3)
        im = Image.new('L', (n, n), 0)
        ImageDraw.Draw(im).text((f.size, f.size * 2), ch, font=f, fill=255, anchor='ls', features=PALT)
        cols = np.where(np.asarray(im).max(axis=0) > 60)[0]
        return cols.min() - f.size, cols.max() + 1 - f.size

    def ink_left(self, ch, f):
        return self._ink(ch, f)[0] / SS

    def ink_right_of_last(self, ch, f):
        return (self._ink(ch, f)[1] - f.getlength(ch, features=PALT)) / SS

    def rule(self, x1, y1, w1, t1, fill):
        self.dr.rectangle([x1 * SS, y1 * SS, (x1 + w1) * SS, (y1 + t1) * SS], fill=fill + (255,))
        self.dm.rectangle([x1 * SS, y1 * SS, (x1 + w1) * SS, (y1 + t1) * SS], fill=255)

def build(bgpath, top, out, pal, geo, scrim=0.30):
    bg = Image.open(bgpath).convert('RGB')
    band = int(round(bg.size[0] * H1 / W1))
    bg = bg.crop((0, top, bg.size[0], top + band)).resize((W, H), Image.LANCZOS)
    a = np.asarray(bg, dtype=np.float32) / 255.0
    xx = np.linspace(0, 1, W, dtype=np.float32)[None, :, None]
    s = 1 - scrim * np.clip(1 - xx / 0.64, 0, 1) ** 1.25      # baked legibility scrim, left only
    a = a * s
    bgimg = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    L = Layer()
    M = geo['M']
    f_label = font(MED, geo['label'])
    f_head = font(SEMI, geo['head'])
    f_sub = font(MED, geo['sub'])
    ivory, ivory2 = pal['ivory'], pal['ivory2']
    # series label (ink-aligned to the margin)
    L.run(M - L.ink_left('都', f_label), geo['y_label'], '都市とAI', f_label, ivory2, 0.20, geo['label'])
    xw = M + L.width('都市とAI', f_label, 0.20, geo['label']) + 12
    L.rule(xw, geo['y_label'] - geo['label'] * 0.78, 1.6, geo['label'] * 0.95, pal['gold'])
    L.run(xw + 14, geo['y_label'], '第31話', f_label, ivory2, 0.20, geo['label'])
    # headline: the bracket hangs; A and ど share the same optical (ink) left edge = M
    tr = 0.012
    adv_br = L.width('「', f_head, tr, geo['head'])
    x_l1 = M - adv_br - L.ink_left('A', f_head)
    L.run(x_l1, geo['y_h1'], '「AIの工場」は', f_head, ivory, tr, geo['head'])
    x_l2 = M - L.ink_left('ど', f_head)
    end2 = L.run(x_l2, geo['y_h2'], 'どの街に建つのか', f_head, ivory, tr, geo['head'])
    ink_end2 = end2 + L.ink_right_of_last('か', f_head) - tr * geo['head']
    # rule: from the margin to the ink end of the longest headline line
    L.rule(M, geo['y_rule'], ink_end2 - M, 1.8, pal['gold'])
    # subtitle: three words take the colour of the three lines in the artwork
    x = M - L.ink_left('電', f_sub)
    for t, c in pal['sub']:
        x = L.run(x, geo['y_sub'], t, f_sub, c, 0.10, geo['sub'])
    w2 = ink_end2
    # soft shadow only for legibility (no outline)
    sh = L.mask.filter(ImageFilter.GaussianBlur(10 * SS / 2))
    sh = Image.eval(sh, lambda v: int(v * 0.42))
    base = bgimg.convert('RGBA')
    black = Image.new('RGBA', (W, H), (0, 0, 0, 255)); black.putalpha(sh)
    base = Image.alpha_composite(base, Image.new('RGBA', (W, H), (0, 0, 0, 0)))
    base.alpha_composite(black, (0, int(3 * SS)))
    base.alpha_composite(L.rgba)
    final = base.convert('RGB')
    final.resize((W1, H1), Image.LANCZOS).save(out + '_1280x670.png', optimize=True)
    final.resize((W1 * 2, H1 * 2), Image.LANCZOS).save(out + '_2560x1340.png', optimize=True)
    return w2

PAL_S = {}
sky = (15, 34, 59)
PAL_S['ivory'] = hsv255(40, 0.10, 0.97)      # warm white: hue taken from the window light, de-saturated
PAL_S['ivory2'] = hsv255(40, 0.07, 0.86)
PAL_S['gold'] = hsv255(41, 0.50, 0.93)       # hue of the gold line
cy = hsv255(191, 0.46, 0.95)                 # hue of the cyan line
co = hsv255(9, 0.52, 0.97)                   # hue of the coral line
PAL_S['sub'] = [('電力', PAL_S['gold']), ('・', PAL_S['ivory2']), ('水', cy), ('・', PAL_S['ivory2']), ('熱', co),
                ('を、都市計画はどう受け止めるか', PAL_S['ivory2'])]

GEO = dict(M=88, label=18, head=94, sub=29, y_label=68, y_h1=196, y_h2=318, y_rule=352, y_sub=404)

if __name__ == '__main__':
    d = '/home/user/AI-/note_31/'
    for n, c in (('ivory', PAL_S['ivory']), ('gold', PAL_S['gold']), ('cyan', cy), ('coral', co), ('ivory2', PAL_S['ivory2'])):
        print(n, c, 'contrast vs sky: %.1f' % contrast(c, sky))
    w2 = build(d + 'codex_bg2/bgS_文字除去版.png', 40, d + '20261115_都市とAI第31話_タイトル画像_組版S', PAL_S, GEO)
    print('headline line2 width(1x px):', round(w2 - GEO['M']))

def build_Q():
    d = '/home/user/AI-/note_31/'
    pal = {}
    pal['ivory'] = hsv255(38, 0.09, 0.98)
    pal['ivory2'] = hsv255(38, 0.06, 0.90)
    pal['gold'] = hsv255(34, 0.52, 0.95)          # hue of the sunset band
    pal['sub'] = [('電力・水・熱', pal['gold']), ('を、都市計画はどう受け止めるか', pal['ivory2'])]
    geo = dict(M=88, label=18, head=90, sub=28, y_label=62, y_h1=184, y_h2=300, y_rule=332, y_sub=382)
    w2 = build(d + 'codex_bg2/bgQ_文字除去版.png', 60, d + '20261115_都市とAI第31話_タイトル画像_組版Q', pal, geo, scrim=0.38)
    print('Q headline width', round(w2 - geo['M']))

if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'Q':
    build_Q()
