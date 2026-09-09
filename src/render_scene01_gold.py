#!/usr/bin/env python3
"""Animate Scene 01 directly from the approved Gold Master artwork.

No character, object, or visible illustration is redrawn here.  The script derives
an edge underdrawing, reveal mattes, and the moving marker hand from the approved
PNG itself, then composites those original pixels into a four-second animation.
"""
from __future__ import annotations

import argparse
import math
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

FPS, DURATION = 30, 4
ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "assets/approved/episode-00/scene-01-gold-master.png"

# Coordinates are measured against the approved 1672 × 941 Gold Master.
REGIONS = [
    # start, end, x0, y0, x1, y1, marker path endpoints (all in master pixels)
    (0.00, 0.80, (510, 255, 1125, 820), (610, 330), (1030, 710)), # boy + desk
    (0.80, 1.40, (0, 490, 435, 941), (52, 565), (362, 783)),     # books
    (1.40, 2.00, (420, 145, 685, 410), (488, 204), (603, 347)),  # phone
    (2.00, 2.50, (345, 385, 635, 575), (389, 454), (568, 512)),  # controller
    (2.50, 3.00, (980, 150, 1240, 390), (1044, 224), (1170, 307)),# clock
    (3.00, 3.40, (1040, 365, 1320, 570), (1096, 438), (1225, 512)),# battery
    (3.40, 4.00, (650, 70, 1010, 315), (701, 153), (931, 229)),  # stress scribble
]

def smooth(x: float) -> float:
    x = max(0.0, min(1.0, x)); return x*x*(3-2*x)

def alpha_for(t: float, start: float, end: float) -> float:
    return smooth((t-start)/(end-start))

def fit_master(size: tuple[int, int]) -> Image.Image:
    """Exact full-frame scaling for 16:9; it keeps all Gold Master pixels."""
    return Image.open(MASTER).convert("RGBA").resize(size, Image.Resampling.LANCZOS)

def soft_stroke_mask(size, box, progress, width=76) -> Image.Image:
    """A hand-drawn serpentine matte, not an opacity fade."""
    sx, sy = size[0] / 1672, size[1] / 941
    x0,y0,x1,y1 = [int(v*(sx if i % 2 == 0 else sy)) for i,v in enumerate(box)]
    mask = Image.new("L", size, 0); d = ImageDraw.Draw(mask)
    rows = max(2, int((y1-y0) / max(34, width*.62)))
    points=[]
    for row in range(rows):
        y = int(y0 + (row+.5)*(y1-y0)/rows)
        points.extend([(x0,y),(x1,y)] if row % 2 == 0 else [(x1,y),(x0,y)])
    count=max(1, int(len(points)*progress))
    if count == 1:
        d.ellipse((points[0][0]-width,points[0][1]-width,points[0][0]+width,points[0][1]+width),fill=255)
    else:
        d.line(points[:count], fill=255, width=width, joint="curve")
        px,py=points[count-1]; d.ellipse((px-width//2,py-width//2,px+width//2,py+width//2),fill=255)
    return mask.filter(ImageFilter.GaussianBlur(4))

def outline_from(master: Image.Image) -> Image.Image:
    """A pale underdrawing extracted from, rather than invented beyond, the master."""
    edges=ImageOps.grayscale(master).filter(ImageFilter.FIND_EDGES)
    edges=ImageOps.invert(edges).point(lambda v: 255 if v > 238 else 0).filter(ImageFilter.GaussianBlur(1.4))
    ink=Image.new("RGBA", master.size, (72,91,126,0)); ink.putalpha(edges.point(lambda v: int(v*.25)))
    base=Image.new("RGBA",master.size,(255,253,248,255)); base.alpha_composite(ink)
    return base

def hand_asset(master: Image.Image, output_scale: float) -> Image.Image:
    """Extract the existing blue-marker hand from the Gold Master; no stock hand."""
    crop=master.crop((1425, 75, 1672, 345)).convert("RGBA")
    shape=Image.new("L",crop.size,0)
    # Tight matte around the existing marker and hand; the original whiteboard is
    # deliberately excluded so the moving hand never carries a rectangular patch.
    ImageDraw.Draw(shape).polygon([(20,8),(70,0),(152,18),(225,53),(246,91),
                                   (246,260),(187,260),(154,222),(113,202),
                                   (79,166),(58,128),(29,94),(6,52)],fill=255)
    px=crop.load()
    for y in range(crop.height):
        for x in range(crop.width):
            r,g,b,a=px[x,y]
            # White whiteboard has extremely low chroma and very high brightness.
            chroma=max(r,g,b)-min(r,g,b)
            if min(r,g,b)>222 and chroma<23: px[x,y]=(r,g,b,0)
            elif min(r,g,b)>239 and chroma<34: px[x,y]=(r,g,b,0)
    crop.putalpha(ImageChops.multiply(crop.getchannel("A"),shape).filter(ImageFilter.GaussianBlur(1)))
    return crop.resize((int(crop.width*output_scale),int(crop.height*output_scale)),Image.Resampling.LANCZOS)

def transform_point(point, size, portrait):
    if not portrait:
        return point[0]*size[0]/1672, point[1]*size[1]/941
    # The retained master is fitted whole into the central 1030×580 card.
    scale=1030/1672
    return 25+point[0]*scale, 650+point[1]*scale

def compose(t: float, size: tuple[int,int], portrait: bool, master: Image.Image,
            base: Image.Image, hand: Image.Image) -> Image.Image:
    if portrait:
        # Derived only from the master: a quiet, blurred continuation lets the full
        # approved composition remain visible without stretching or cropping the boy.
        canvas=base.copy()
        outline=outline_from(master)
        card=Image.new("RGBA",(1060,610),(255,255,252,240)); card=card.filter(ImageFilter.GaussianBlur(.3))
        canvas.alpha_composite(card,(10,635)); position=(25,650)
    else:
        canvas=base.copy(); outline=canvas; position=(0,0)
    # Keep the artwork's own faint linework visible at frame 0, then reveal original pixels.
    if portrait:
        canvas.alpha_composite(outline,position)
    else:
        canvas=outline.copy()
    union=Image.new("L",master.size,0)
    active_hand=None
    for start,end,box,p0,p1 in REGIONS:
        p=alpha_for(t,start,end)
        if p:
            mask=soft_stroke_mask(master.size,box,p, width=max(52,int(master.size[0]/24)))
            union=ImageChops.lighter(union,mask)
        if start <= t <= end: active_hand=(p0,p1,p)
    # Final moment finishes residual texture in a broad brush pass—not a fade.
    if t>3.72:
        full=soft_stroke_mask(master.size,(0,0,1672,941),alpha_for(t,3.72,3.94),width=max(520,int(master.size[0]/3)))
        union=ImageChops.lighter(union,full)
    # The final held frames must be the untouched approved master, after the
    # preceding broad brush pass has completed.
    if t >= 3.90:
        union=Image.new("L",master.size,255)
    revealed=master.copy(); revealed.putalpha(union)
    canvas.alpha_composite(revealed,position)
    if active_hand:
        p0,p1,p=active_hand; x=p0[0]+(p1[0]-p0[0])*p; y=p0[1]+(p1[1]-p0[1])*p
        hx,hy=transform_point((x,y),size,portrait)
        canvas.alpha_composite(hand,(int(hx-hand.width*.45),int(hy-hand.height*.36)))
    return canvas.convert("RGB")

def render(kind: str):
    portrait=kind=="portrait"; size=(1080,1920) if portrait else (1920,1080)
    original=Image.open(MASTER).convert("RGBA")
    master=fit_master(size) if not portrait else original.resize((1030,580),Image.Resampling.LANCZOS)
    hand=hand_asset(original, .60 if not portrait else .43)
    if portrait:
        base=original.resize(size,Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(28))
        base.alpha_composite(Image.new("RGBA",size,(255,250,241,174)))
    else:
        base=outline_from(master)
    frames=ROOT/"output"/f"scene-01-gold-{kind}-frames"; frames.mkdir(parents=True,exist_ok=True)
    for p in frames.glob("*"): p.unlink()
    # JPEG intermediates are intentionally disposable; fast encoding keeps the
    # production loop practical while the final H.264 is rendered at CRF 17.
    for n in range(FPS*DURATION):
        compose(n/FPS,size,portrait,master,base,hand).save(frames/f"frame-{n:04d}.jpg",quality=96,subsampling=0)
    target=ROOT/"output"/f"scene-01-gold-prototype-{kind}.mp4"
    subprocess.run(["ffmpeg","-y","-framerate",str(FPS),"-i",str(frames/"frame-%04d.jpg"),"-f","lavfi","-i","anullsrc=r=48000:cl=stereo","-t",str(DURATION),"-c:v","libx264","-pix_fmt","yuv420p","-crf","17","-c:a","aac","-b:a","128k","-movflags","+faststart",str(target)],check=True)
    print(target)

if __name__=="__main__":
    parser=argparse.ArgumentParser(); parser.add_argument("--format",choices=["landscape","portrait","all"],default="all")
    args=parser.parse_args()
    for item in (["landscape","portrait"] if args.format=="all" else [args.format]): render(item)
