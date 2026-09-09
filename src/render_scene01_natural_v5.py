#!/usr/bin/env python3
"""Scene 01 V5 — Natural Cartoon Explainer Animation (landscape only)."""
from __future__ import annotations
import math, random, struct, subprocess, wave
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw
from render_scene01_selective_v3 import ROOT, MASTER, SIZE, FPS, scale_box, layer_from, foreground_alpha

DURATION=5.8
BASE=ROOT/"assets/derived/episode-00/scene-01-static-base-v5.png"
OUT=ROOT/"output"/"scene-01-natural-animation-v5.mp4"

def ease(x):
 x=max(0,min(1,x)); return x*x*(3-2*x)
def crop(master, box):
 image=layer_from(master,box); return image,foreground_alpha(image)
def put(frame, image, alpha, box, progress, scale=1, dx=0, dy=0, angle=0):
 p=ease(progress)
 if p<=0:return
 item=image.copy(); item.putalpha(alpha.point(lambda v:int(v*p)))
 s=scale
 if s!=1: item=item.resize((int(item.width*s),int(item.height*s)),Image.Resampling.LANCZOS)
 if angle:item=item.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
 x,y=scale_box(box)[:2]; x+=int((image.width-item.width)/2)+dx; y+=int((image.height-item.height)/2)+dy
 frame.alpha_composite(item,(x,y))

def scribble(draw, p):
 """The one hand-drawn emotion layer: small → medium → chaotic, without a hand."""
 if p<=0:return
 cx,cy=1030,220; points=[]
 for i in range(124):
  # Intersecting irregular loops read as thought clutter, rather than a tidy spiral.
  growth=.18+.82*i/123
  points.append((int(cx+growth*(145*math.sin(i*.31)+54*math.sin(i*.87))),
                 int(cy+growth*(76*math.sin(i*.47)+34*math.cos(i*.73)))))
 n=max(2,int(len(points)*p)); draw.line(points[:n],fill="#142f71",width=6,joint="curve")
 if p>.78:
  draw.arc((880,185,910,205),180,360,fill="#142f71",width=4)
  draw.arc((905,185,935,205),180,360,fill="#142f71",width=4)
  draw.line((1150,198,1138,220,1154,220,1142,242),fill="#142f71",width=4)
  draw.text((1140,278),'?',fill="#142f71",stroke_width=1)

def build_audio(path):
 rate=44100; total=round(rate*DURATION); data=[0.0]*total
 def tone(start,dur,freq,amp):
  a=max(0,int(start*rate)); b=min(total,int((start+dur)*rate))
  for i in range(a,b):
   u=(i-a)/(b-a); env=math.sin(math.pi*u)**1.6
   data[i]+=amp*env*math.sin(2*math.pi*freq*(i-a)/rate)
 # subtle semantic cues: game pop, phone buzz, clock ticks, battery warning, task taps.
 tone(.67,.07,620,.05)
 for t in (1.55,1.70): tone(t,.09,145,.035)
 for t in (2.40,2.53,2.66,2.79): tone(t,.035,900,.025)
 tone(3.40,.10,430,.04)
 for t in (3.93,4.08,4.23,4.38,4.53): tone(t,.025,1250,.02)
 random.seed(7)
 for i in range(int(4.9*rate),int(5.55*rate)):
  u=(i-int(4.9*rate))/(.65*rate); data[i]+=random.uniform(-1,1)*.006*math.sin(math.pi*u)
 with wave.open(str(path),'w') as w:
  w.setparams((1,2,rate,total,'NONE','not compressed'))
  w.writeframes(b''.join(struct.pack('<h',max(-32767,min(32767,int(x*32767)))) for x in data))

def frame_at(t, master, base, layers):
 f=base.copy()
 # Game: pop then a brief, inviting 2° tilt.
 if t>=.60:
  q=(t-.60)/.55; pop= .90+.15*ease(min(1,q/.55)) if q<.55 else 1
  tilt=2*math.sin(max(0,min(1,(t-1.0)/.28))*math.pi) if 1.0<t<1.28 else 0
  put(f,*layers['game'],(340,390,630,580),q,scale=pop,angle=tilt)
 # Phone: two gentle vibration offsets; separate badge has a quick pop.
 if t>=1.35:
  q=(t-1.35)/.45; vib=0
  if 1.67<t<1.92: vib=int(5*math.sin((t-1.67)*55)*math.exp(-(t-1.67)*4))
  put(f,*layers['phone'],(440,160,650,340),q,dx=vib)
  put(f,*layers['badge'],(560,145,665,245),(t-1.55)/.20,scale=.80+.35*ease((t-1.55)/.12) if t<1.67 else 1,dx=vib)
  put(f,*layers['msglabel'],(420,325,635,410),(t-1.72)/.25)
 # Clock enters, hands race around once, then the label settles.
 if t>=2.15:
  q=(t-2.15)/.35; put(f,*layers['clock'],(990,150,1200,360),q,scale=.86+.14*ease(q))
  if 2.48<t<2.83:
   d=ImageDraw.Draw(f); cx,cy=1258,299; a=(t-2.48)/.35*math.pi*2
   d.line((cx,cy,cx+int(math.cos(a)*42),cy+int(math.sin(a)*42)),fill="#183466",width=6)
   d.line((cx,cy,cx+int(math.cos(a*.5)*28),cy+int(math.sin(a*.5)*28)),fill="#183466",width=5)
  put(f,*layers['timelabel'],(1105,315,1290,400),(t-2.65)/.20)
 # Battery drains through three quick visual states, then a restrained blink.
 if t>=3.0:
  put(f,*layers['battery'],(1050,390,1250,520),(t-3.0)/.25,scale=.88+.12*ease((t-3.0)/.25))
  d=ImageDraw.Draw(f); x,y,w,h=1257,475,72,42; q=(t-3.25)/.38
  level=.60 if q<.33 else (.30 if q<.66 else .10)
  d.rectangle((x,y,x+w,y+h),fill="#fffdf8")
  d.rectangle((x+4,y+5,x+4+int((w-8)*level),y+h-5),fill="#e95c58" if level<=.30 else "#f2ad57")
  put(f,*layers['batterylabel'],(1090,495,1305,575),(t-3.43)/.20)
 # Task note reveals its approved rows in a quick pile-up, not a whole-card fade.
 if t>=3.75:
  image,alpha=layers['tasks']; shown=image.copy(); rowp=max(0,min(1,(t-3.75)/.72)); mask=Image.new('L',image.size,0); md=ImageDraw.Draw(mask)
  for row in range(5):
   if rowp>(row+1)/6: md.rectangle((0,row*image.height//5,image.width,(row+1)*image.height//5),fill=255)
  shown.putalpha(ImageChops.multiply(alpha,mask)); x,y=scale_box((1280,175,1445,560))[:2]; f.alpha_composite(shown,(x,y))
 # Scribble is the emotional hand-drawn exception; no hand appears. Its growing
 # path resolves into the approved master linework for the final held moment.
 if t>=4.65:
  sp=(t-4.65)/.78
  if sp<=.68: scribble(ImageDraw.Draw(f),sp)
  else: put(f,*layers['scribble'],(650,70,1050,285),(sp-.68)/.32)
 # One very brief blink and a final slightly worried brow proxy.
 if 3.55<t<3.64:
  d=ImageDraw.Draw(f); d.line((905,529,958,529),fill="#4a2d2a",width=7); d.line((1030,496,1075,496),fill="#4a2d2a",width=7)
 if t>5.25:
  d=ImageDraw.Draw(f); d.arc((895,445,970,475),190,340,fill="#4a2d2a",width=4); d.arc((1015,420,1090,450),200,350,fill="#4a2d2a",width=4)
 # Slow push-in: camera proximity rises with accumulating pressure.
 z=1+.03*ease(t/DURATION); resized=f.resize((int(SIZE[0]*z),int(SIZE[1]*z)),Image.Resampling.LANCZOS)
 ox=(resized.width-SIZE[0])//2; oy=(resized.height-SIZE[1])//2
 return resized.crop((ox,oy,ox+SIZE[0],oy+SIZE[1])).convert('RGB')

def render():
 master=Image.open(MASTER).convert('RGBA').resize(SIZE,Image.Resampling.LANCZOS)
 base=Image.open(BASE).convert('RGBA').resize(SIZE,Image.Resampling.LANCZOS)
 boxes={'game':(340,390,630,580),'phone':(440,160,650,340),'badge':(560,145,665,245),'msglabel':(420,325,635,410),'clock':(990,150,1200,360),'timelabel':(1105,315,1290,400),'battery':(1050,390,1250,520),'batterylabel':(1090,495,1305,575),'tasks':(1280,175,1445,560),'scribble':(650,70,1050,285)}
 layers={name:crop(master,box) for name,box in boxes.items()}
 work=ROOT/'output'/'scene-01-natural-v5-frames'; work.mkdir(parents=True,exist_ok=True)
 for p in work.glob('*'):p.unlink()
 for n in range(round(FPS*DURATION)): frame_at(n/FPS,master,base,layers).save(work/f'frame-{n:04d}.jpg',quality=96,subsampling=0)
 audio=ROOT/'output'/'scene-01-natural-v5-temp-sfx.wav'; build_audio(audio)
 subprocess.run(['ffmpeg','-y','-framerate',str(FPS),'-i',str(work/'frame-%04d.jpg'),'-i',str(audio),'-t',str(DURATION),'-c:v','libx264','-pix_fmt','yuv420p','-crf','17','-c:a','aac','-b:a','128k','-movflags','+faststart',str(OUT)],check=True)
 print(OUT)
if __name__=='__main__':render()
