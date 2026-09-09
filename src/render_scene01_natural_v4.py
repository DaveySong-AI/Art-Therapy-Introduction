#!/usr/bin/env python3
"""Scene 01 V4: calm static world, naturally animated pressure elements.

This deliberately replaces the whiteboard-hand treatment.  All character and
illustration pixels still originate in the approved Gold Master/derived base;
story points enter with restrained cinematic motion instead of being drawn.
"""
from __future__ import annotations
import math, subprocess
from pathlib import Path
from PIL import Image, ImageDraw

from render_scene01_selective_v3 import FPS, DURATION, SIZE, ROOT, MASTER, STATIC_BASE, BEATS, layer_from, foreground_alpha

def smooth(x):
 x=max(0,min(1,x)); return x*x*(3-2*x)

def composite_layer(frame, crop, alpha, position, progress, style):
 """A soft rise/pop settles to the approved artwork—no drawing simulation."""
 p=smooth(progress)
 if not p: return
 if style=="game":
  scale=.83+.17*p; angle=2.0*(1-p); dy=int(18*(1-p))
 elif style=="phone":
  scale=.92+.08*p; angle=0; dy=int(-24*(1-p))
 elif style=="clock":
  scale=.86+.14*p; angle=0; dy=int(12*(1-p))
 elif style=="battery":
  scale=.88+.12*p; angle=0; dy=int(10*(1-p))
 elif style=="tasks":
  scale=.96+.04*p; angle=0; dy=0
 else: # clutter breathes in, then holds
  scale=.72+.28*p; angle=0; dy=int(8*(1-p))
 shown=crop.copy(); shown.putalpha(alpha.point(lambda v:int(v*p)))
 if scale!=1 or angle:
  shown=shown.resize((int(shown.width*scale),int(shown.height*scale)),Image.Resampling.LANCZOS)
  if angle: shown=shown.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
 x,y=position
 x+=int((crop.width-shown.width)/2); y+=int((crop.height-shown.height)/2)+dy
 frame.alpha_composite(shown,(x,y))

def render():
 original=Image.open(MASTER).convert("RGBA").resize(SIZE,Image.Resampling.LANCZOS)
 base=Image.open(STATIC_BASE).convert("RGBA").resize(SIZE,Image.Resampling.LANCZOS)
 layers={box:layer_from(original,box) for _,_,box,_,_ in BEATS}
 alphas={box:foreground_alpha(crop) for box,crop in layers.items()}
 # The original approved image includes a marker hand beside the task sticky.
 # V4 intentionally has no hand, so exclude that source area from this crop.
 task_box=BEATS[4][2]; cutoff=int((1450-task_box[0])*SIZE[0]/1672)
 if cutoff>0:
  ImageDraw.Draw(alphas[task_box]).rectangle((cutoff,0,alphas[task_box].width,alphas[task_box].height),fill=0)
 styles=["game","phone","clock","battery","tasks","clutter"]
 work=ROOT/"output"/"scene-01-natural-v4-frames"; work.mkdir(parents=True,exist_ok=True)
 for f in work.glob("*"): f.unlink()
 for n in range(round(FPS*DURATION)):
  t=n/FPS; frame=base.copy()
  for (start,end,box,_,_),style in zip(BEATS,styles):
   if t>=start:
    # Entry consumes 60% of the allocation; the rest is a quiet readable hold.
    p=(t-start)/((end-start)*.60)
    composite_layer(frame,layers[box],alphas[box],tuple(int(v) for v in (box[0]*SIZE[0]/1672,box[1]*SIZE[1]/941)),p,style)
  frame.convert("RGB").save(work/f"frame-{n:04d}.jpg",quality=96,subsampling=0)
 target=ROOT/"output"/"scene-01-natural-animation-v4.mp4"
 subprocess.run(["ffmpeg","-y","-framerate",str(FPS),"-i",str(work/"frame-%04d.jpg"),"-f","lavfi","-i","anullsrc=r=48000:cl=stereo","-t",str(DURATION),"-c:v","libx264","-pix_fmt","yuv420p","-crf","17","-c:a","aac","-b:a","128k","-movflags","+faststart",str(target)],check=True)
 print(target)
if __name__=="__main__": render()
