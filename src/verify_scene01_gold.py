#!/usr/bin/env python3
"""Verify the required delivery properties for the Scene 01 Gold prototype."""
import json, subprocess
from pathlib import Path

for kind, dimensions in (("landscape",(1920,1080)),("portrait",(1080,1920))):
    path=Path("output")/f"scene-01-gold-prototype-{kind}.mp4"
    data=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries","stream=codec_type,codec_name,width,height,r_frame_rate,duration","-of","json",str(path)]))
    video=next(x for x in data["streams"] if x["codec_type"]=="video")
    audio=next(x for x in data["streams"] if x["codec_type"]=="audio")
    assert video["codec_name"]=="h264" and audio["codec_name"]=="aac"
    assert (video["width"],video["height"])==dimensions
    assert video["r_frame_rate"]=="30/1" and 3.95<=float(video["duration"])<=4.05
    print(f"PASS {path}: H.264/AAC, {dimensions[0]}×{dimensions[1]}, 30 fps, {video['duration']}s")
