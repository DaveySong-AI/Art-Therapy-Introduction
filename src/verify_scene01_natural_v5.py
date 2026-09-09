#!/usr/bin/env python3
import json,subprocess
from pathlib import Path
p=Path('output/scene-01-natural-animation-v5.mp4'); d=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,duration','-of','json',str(p)]))
v=next(x for x in d['streams'] if x['codec_type']=='video'); a=next(x for x in d['streams'] if x['codec_type']=='audio')
assert (v['codec_name'],a['codec_name'])==('h264','aac')
assert (v['width'],v['height'],v['r_frame_rate'])==(1920,1080,'30/1') and 5.6<=float(v['duration'])<=5.9
print(f"PASS {p}: 1920×1080, 30fps, H.264/AAC, {v['duration']}s")
