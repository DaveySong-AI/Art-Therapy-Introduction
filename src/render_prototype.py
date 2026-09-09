#!/usr/bin/env python3
"""Render Episode 00's four-scene animation prototype without external assets.

The artwork is deliberately procedural: each visible mark is drawn from source code,
so later episodes can reuse the palette, typography, safe area, and animation helpers.
"""
from __future__ import annotations

import argparse
import math
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FPS = 30
FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"
PALETTE = {"ink": "#36435c", "paper": "#fffdf8", "blue": "#7faee8",
           "yellow": "#f6c85f", "pink": "#efa8ae", "mint": "#93cdb8",
           "lavender": "#a79bd9", "stress": "#59647b", "orange": "#efa16e"}

def ease(x):
    x = max(0, min(1, x))
    return x * x * (3 - 2 * x)

def visible(t, start, span=.45): return ease((t - start) / span)

def font(size): return ImageFont.truetype(FONT, size)

def fit_text(d, xy, text, size, fill=PALETTE["ink"], anchor="mm"):
    d.text(xy, text, font=font(size), fill=fill, anchor=anchor, stroke_width=1)

def line(d, points, fill, width, amount=1):
    count = max(2, int((len(points) - 1) * amount) + 1)
    d.line(points[:count], fill=fill, width=width, joint="curve")

def hand(d, x, y, p, scale=1):
    """Simple marker-holding hand that travels with a drawn mark."""
    if p <= 0: return
    alpha = int(255 * min(1, p * 3))
    skin = (242, 195, 162, alpha)
    layer = Image.new("RGBA", d._image.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    ld.ellipse((x-38*scale, y-25*scale, x+35*scale, y+39*scale), fill=skin, outline=PALETTE["ink"], width=3)
    ld.rounded_rectangle((x-9*scale, y-70*scale, x+12*scale, y+4*scale), radius=8*scale, fill=PALETTE["orange"], outline=PALETTE["ink"], width=3)
    ld.polygon([(x-9*scale,y-73*scale),(x+12*scale,y-73*scale),(x+2*scale,y-92*scale)], fill=PALETTE["ink"])
    d._image.alpha_composite(layer)

def character(d, cx, cy, p, calm=False):
    # hand-drawn boy: hoodie, face, hair, then changing eyebrows/mouth.
    a = ease(p)
    if not a: return
    d.ellipse((cx-84, cy-142, cx+84, cy+26), fill="#f4c8a6", outline=PALETTE["ink"], width=6)
    d.pieslice((cx-94, cy-165, cx+94, cy-18), 180, 360, fill="#4b4b62", outline=PALETTE["ink"], width=5)
    d.rounded_rectangle((cx-122, cy+2, cx+122, cy+220), radius=45, fill=PALETTE["blue"], outline=PALETTE["ink"], width=6)
    d.line((cx-36, cy+23, cx, cy+62, cx+36, cy+23), fill="#d7e8ff", width=5)
    if calm:
        d.arc((cx-46,cy-72,cx-8,cy-42), 190, 350, fill=PALETTE["ink"], width=5)
        d.arc((cx+8,cy-72,cx+46,cy-42), 190, 350, fill=PALETTE["ink"], width=5)
        d.arc((cx-22,cy-18,cx+22,cy+16), 10, 170, fill=PALETTE["ink"], width=5)
    else:
        d.line((cx-48,cy-60,cx-12,cy-69), fill=PALETTE["ink"], width=6)
        d.line((cx+12,cy-69,cx+48,cy-60), fill=PALETTE["ink"], width=6)
        d.arc((cx-21,cy-12,cx+21,cy+10), 190, 350, fill=PALETTE["ink"], width=5)

def icon(d, x, y, label, color, p):
    if p <= 0: return
    r = int(54 * (0.85 + .15*p)); d.rounded_rectangle((x-r,y-r,x+r,y+r), radius=18, fill=color, outline=PALETTE["ink"], width=4)
    fit_text(d, (x,y), label, 32, anchor="mm")

def scribble(d, cx, cy, p, colorful=False):
    pts=[]
    for i in range(90):
        a=i*.48; r=10+i*1.05
        pts.append((cx+math.cos(a)*r,cy+math.sin(a)*r*.58))
    if colorful:
        colors=[PALETTE["lavender"],PALETTE["pink"],PALETTE["yellow"],PALETTE["mint"],PALETTE["blue"]]
        amount=int(len(pts)*p)
        for j in range(0, max(0, amount - 1), 12):
            segment = pts[j:min(j + 14, amount)]
            if len(segment) >= 2:
                line(d, segment, colors[(j//12) % len(colors)], 13)
    else: line(d, pts, PALETTE["stress"], 11, p)
    return pts

def scene01(im, t, W, H):
    d=ImageDraw.Draw(im); fit_text(d,(W//2,100),"你有没有过这样的时刻？",54)
    character(d, W//2, H//2+90, visible(t,0), calm=False)
    placements=[(260,300,"作业",PALETTE["yellow"]),(W-260,300,"消息",PALETTE["pink"]),(240,H-260,"时钟",PALETTE["lavender"]),(W-240,H-260,"电量",PALETTE["mint"])]
    for i,item in enumerate(placements): icon(d,*item,visible(t,.45+i*.62))
    if t>3.05: scribble(d,W//2,H//2-190,visible(t,3.05))

def scene06(im, t, W, H):
    d=ImageDraw.Draw(im); fit_text(d,(W//2,105),"把它画出来。",60,PALETTE["ink"])
    # paper receives the dark line, then it becomes a colorful visual expression.
    paper=(W//2-390,H//2-205,W//2+390,H//2+270); d.rounded_rectangle(paper, radius=24, fill="#fffefa", outline="#d9d0c5", width=5)
    pts=scribble(d,W//2,H//2+28,visible(t,.2), colorful=False)
    if t>2.0:
        scribble(d,W//2,H//2+28,visible(t,2.0), colorful=True)
        pulse=1+0.06*math.sin(t*5); r=74*pulse
        d.polygon([(W//2,H//2+15-r),(W//2-r,H//2-12),(W//2,H//2+95),(W//2+r,H//2-12)],fill=PALETTE["pink"],outline=PALETTE["ink"],width=5)
    hand(d,W//2+220,H//2+165,visible(t,.2))
    if t>3.25: fit_text(d,(W//2,H-120),"画出来！",76,PALETTE["orange"])

def scene10(im,t,W,H):
    d=ImageDraw.Draw(im); fit_text(d,(W//2,100),"一张纸，一支笔，给情绪一个出口。",46)
    character(d, W//2-310,H//2+80,visible(t,0),calm=t>2.9)
    paper=(W//2+25,H//2-160,W//2+560,H//2+245); d.rounded_rectangle(paper, radius=22, fill="#fffefa", outline="#d9d0c5", width=5)
    # Stress leaves the character and enters paper.
    progress=visible(t,.5,2.6); x=(W//2-300)*(1-progress)+(W//2+250)*progress
    scribble(d,x,H//2-150,1)
    if t>2.3: scribble(d,W//2+285,H//2+30,visible(t,2.3),colorful=True)
    hand(d,W//2+430,H//2+215,visible(t,2.2))
    if t>3.65:
        fit_text(d,(W//2,H-165),"呼——",54,PALETTE["mint"])
        for i,word in enumerate(["更轻松","更清晰","更有力量"]):
            fit_text(d,(W//2-280+i*280,H-88),word,30,[PALETTE["mint"],PALETTE["blue"],PALETTE["orange"]][i])

def scene12(im,t,W,H):
    d=ImageDraw.Draw(im)
    # One continuous marker line draws a heart, then the series lock-up is revealed.
    pts=[]
    for i in range(101):
        q=i/100*math.pi*2; x=16*math.sin(q)**3; y=-(13*math.cos(q)-5*math.cos(2*q)-2*math.cos(3*q)-math.cos(4*q))
        pts.append((W//2+x*13,H//2-185+y*13))
    line(d,pts,PALETTE["pink"],15,visible(t,.1,1.2)); hand(d,pts[min(len(pts)-1,int(visible(t,.1,1.2)*(len(pts)-1)))][0],pts[min(len(pts)-1,int(visible(t,.1,1.2)*(len(pts)-1)))][1]+40,visible(t,.1))
    if t>1.15:
        fit_text(d,(W//2,H//2+90),"艺术疗愈 · 10 节课",68,PALETTE["ink"])
        fit_text(d,(W//2,H//2+180),"从一支笔开始，看见自己",37,PALETTE["stress"])
    if t>2.0: fit_text(d,(W//2,H-125),"LESSON 01  →",39,PALETTE["orange"])

SCENES=[(4,scene01),(5,scene06),(6,scene10),(3,scene12)]
def draw_frame(frame, W, H):
    im=Image.new("RGBA",(W,H),PALETTE["paper"])
    # restrained pastel frame and safe-area guides are intentionally absent from output.
    d=ImageDraw.Draw(im); d.ellipse((-160,-180,440,300),fill="#fff1dc"); d.ellipse((W-400,H-280,W+120,H+170),fill="#e8f5ee")
    seconds=frame/FPS; offset=0
    for duration,fn in SCENES:
        if seconds < offset+duration or fn is SCENES[-1][1]: fn(im,seconds-offset,W,H); break
        offset+=duration
    return im.convert("RGB")

def run(args):
    root=Path(__file__).resolve().parents[1]; work=root/"output"/"frames"; output=root/"output"
    W,H=(1920,1080) if args.format=="landscape" else (1080,1920)
    if work.exists(): shutil.rmtree(work)
    work.mkdir(parents=True); output.mkdir(exist_ok=True)
    total=sum(d for d,_ in SCENES)*FPS
    for n in range(total): draw_frame(n,W,H).save(work/f"frame-{n:05d}.png",optimize=True)
    target=output/f"episode-00-prototype-{args.format}.mp4"
    subprocess.run(["ffmpeg","-y","-framerate",str(FPS),"-i",str(work/"frame-%05d.png"),"-f","lavfi","-i","anullsrc=r=48000:cl=stereo","-t",str(total/FPS),"-c:v","libx264","-pix_fmt","yuv420p","-crf","19","-c:a","aac","-b:a","128k","-movflags","+faststart",str(target)],check=True)
    print(target)
if __name__=="__main__":
    parser=argparse.ArgumentParser(); parser.add_argument("--format",choices=["landscape","portrait"],default="landscape"); run(parser.parse_args())
