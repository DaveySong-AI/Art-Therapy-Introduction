#!/usr/bin/env python3
"""Scene 01 V3: static Gold Master world + selective whiteboard storytelling.

The boy and room are always the approved artwork. Only story pressure points are
removed from that base, then restored from the same approved pixels via a moving
marker and progressive reveal mattes.
"""
from __future__ import annotations
import math, shutil, subprocess
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps

FPS, DURATION, SIZE = 30, 5.8, (1920,1080)
ROOT=Path(__file__).resolve().parents[1]
MASTER=ROOT/"assets/approved/episode-00/scene-01-gold-master.png"
STATIC_BASE=ROOT/"assets/derived/episode-00/scene-01-static-base-v3.png"
# time, source crop in Gold Master coordinates, marker travel (in source coordinates)
BEATS=[
 (0.60,1.40,(340,390,630,580),(373,440),(574,510)),  # game + label
 (1.40,2.30,(440,150,660,410),(484,205),(626,362)),  # phone + messages
 (2.30,3.10,(990,145,1260,390),(1038,195),(1181,350)),# clock + label
 (3.10,3.80,(1040,380,1325,580),(1080,445),(1243,531)),# battery + label
 (3.80,4.80,(1280,175,1605,560),(1330,215),(1517,438)),# task list
 (4.80,5.70,(670,75,1010,275),(702,138),(960,260)),  # mental clutter
]

def smooth(x): x=max(0,min(1,x)); return x*x*(3-2*x)
def p_at(t,start,end): return smooth((t-start)/(end-start))
def scale_box(box):
 sx,sy=SIZE[0]/1672,SIZE[1]/941
 return tuple(int(v*(sx if i%2==0 else sy)) for i,v in enumerate(box))

def strokes(size, box, p, width=54):
 """Soft serpentine brush reveal—an actual animated matte, never a fade."""
 x0,y0,x1,y1=scale_box(box); out=Image.new("L",size,0); d=ImageDraw.Draw(out)
 rows=max(2,int((y1-y0)/max(width*.8,38))); pts=[]
 for row in range(rows):
  y=int(y0+(row+.5)*(y1-y0)/rows)
  pts += [(x0,y),(x1,y)] if row%2==0 else [(x1,y),(x0,y)]
 n=max(1,int(len(pts)*p))
 if n==1: d.ellipse((pts[0][0]-width,pts[0][1]-width,pts[0][0]+width,pts[0][1]+width),fill=255)
 else:
  d.line(pts[:n],fill=255,width=width,joint="curve"); x,y=pts[n-1]; d.ellipse((x-width//2,y-width//2,x+width//2,y+width//2),fill=255)
 return out.filter(ImageFilter.GaussianBlur(3))

def local_strokes(size, p, width=42):
 """The same brush matte in crop-local coordinates."""
 w,h=size; out=Image.new("L",size,0); d=ImageDraw.Draw(out)
 rows=max(2,int(h/max(width*.8,38))); pts=[]
 for row in range(rows):
  y=int((row+.5)*h/rows)
  pts += [(0,y),(w,y)] if row%2==0 else [(w,y),(0,y)]
 n=max(1,int(len(pts)*p))
 if n==1: d.ellipse((pts[0][0]-width,pts[0][1]-width,pts[0][0]+width,pts[0][1]+width),fill=255)
 else:
  d.line(pts[:n],fill=255,width=width,joint="curve"); x,y=pts[n-1]; d.ellipse((x-width//2,y-width//2,x+width//2,y+width//2),fill=255)
 return out.filter(ImageFilter.GaussianBlur(3))

def edge_underdrawing(layer):
 gray=ImageOps.grayscale(layer).filter(ImageFilter.FIND_EDGES)
 alpha=ImageOps.invert(gray).point(lambda v: 255 if v>230 else 0).filter(ImageFilter.GaussianBlur(1))
 ink=Image.new("RGBA",layer.size,(47,67,103,0)); ink.putalpha(alpha.point(lambda v:int(v*.42))); return ink

def cut_hand(original):
 crop=original.crop((1425,75,1672,345)).convert("RGBA"); matte=Image.new("L",crop.size,0)
 ImageDraw.Draw(matte).polygon([(20,8),(70,0),(152,18),(225,53),(246,91),(246,260),(187,260),(154,222),(113,202),(79,166),(58,128),(29,94),(6,52)],fill=255)
 px=crop.load()
 for y in range(crop.height):
  for x in range(crop.width):
   r,g,b,a=px[x,y]; chroma=max(r,g,b)-min(r,g,b)
   if (min(r,g,b)>222 and chroma<23) or (min(r,g,b)>239 and chroma<34): px[x,y]=(r,g,b,0)
 crop.putalpha(ImageChops.multiply(crop.getchannel("A"),matte).filter(ImageFilter.GaussianBlur(1)))
 return crop.resize((148,162),Image.Resampling.LANCZOS)

def static_base():
 """Approved-art derivative with only V3's dynamic pressure points removed."""
 return Image.open(STATIC_BASE).convert("RGBA").resize(SIZE,Image.Resampling.LANCZOS)

def layer_from(master, box):
 crop=master.crop(scale_box(box))
 # The crop is placed over the matching original location. Its white surroundings
 # blend into the same board and its edges are revealed by the animated matte.
 return crop

def foreground_alpha(crop):
 """Remove the original whiteboard from a source crop, retaining only the
 colored/dark approved line art, fills and lettering for seamless compositing."""
 alpha=Image.new("L",crop.size,0); src=crop.convert("RGB").load(); out=alpha.load()
 for y in range(crop.height):
  for x in range(crop.width):
   r,g,b=src[x,y]
   chroma=max(r,g,b)-min(r,g,b)
   # Warm white board and its soft neutral lighting are transparent; actual
   # ink, pastel fills, yellow sticky note and red battery remain opaque.
   out[x,y]=0 if (min(r,g,b)>218 and chroma<34) else 255
 return alpha.filter(ImageFilter.GaussianBlur(.6))

def compose(t, master, base, hand, layers):
 frame=base.copy()
 active=None
 for start,end,box,pt0,pt1 in BEATS:
  if t < start: continue
  p=p_at(t,start,end); destination=scale_box(box)[:2]
  crop, clean_alpha=layers[box]
  # outline first, then source pixels sweep in behind the marker.
  if p<.36:
   outline=edge_underdrawing(crop); outline.putalpha(local_strokes(crop.size,min(1,p/.36),34))
   frame.alpha_composite(outline,destination)
  else:
   reveal=local_strokes(crop.size,min(1,(p-.18)/.82),42)
   shown=crop.copy(); shown.putalpha(ImageChops.multiply(clean_alpha,reveal)); frame.alpha_composite(shown,destination)
  if start<=t<=end: active=(pt0,pt1,p)
 # Gentle controller bounce and phone vibration are small positional motions on
 # their already-revealed artwork, making escalation legible without a PPT pop.
 if 1.16<t<1.40:
  pass # the reveal already carries the controller's slight drawn-in motion
 if active:
  a,b,p=active; x=(a[0]+(b[0]-a[0])*p)*SIZE[0]/1672; y=(a[1]+(b[1]-a[1])*p)*SIZE[1]/941
  frame.alpha_composite(hand,(int(x-hand.width*.42),int(y-hand.height*.35)))
 return frame.convert("RGB")

def render():
 original=Image.open(MASTER).convert("RGBA").resize(SIZE,Image.Resampling.LANCZOS)
 base=static_base(); hand=cut_hand(Image.open(MASTER).convert("RGBA"))
 layers={box:(layer_from(original,box),None) for _,_,box,_,_ in BEATS}
 layers={box:(crop,foreground_alpha(crop)) for box,(crop,_) in layers.items()}
 work=ROOT/"output"/"scene-01-selective-v3-frames"; work.mkdir(parents=True,exist_ok=True)
 for f in work.glob("*"): f.unlink()
 for n in range(round(FPS*DURATION)):
  compose(n/FPS,original,base,hand,layers).save(work/f"frame-{n:04d}.jpg",quality=96,subsampling=0)
 target=ROOT/"output"/"scene-01-selective-whiteboard-v3.mp4"
 subprocess.run(["ffmpeg","-y","-framerate",str(FPS),"-i",str(work/"frame-%04d.jpg"),"-f","lavfi","-i","anullsrc=r=48000:cl=stereo","-t",str(DURATION),"-c:v","libx264","-pix_fmt","yuv420p","-crf","17","-c:a","aac","-b:a","128k","-movflags","+faststart",str(target)],check=True)
 print(target)
if __name__=="__main__": render()
