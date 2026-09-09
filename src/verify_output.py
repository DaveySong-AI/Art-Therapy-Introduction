#!/usr/bin/env python3
"""Minimal automated acceptance checks for released prototype files."""
import json, subprocess, sys
from pathlib import Path
EXPECTED={"landscape":(1920,1080),"portrait":(1080,1920)}
for kind, size in EXPECTED.items():
    path=Path("output")/f"episode-00-prototype-{kind}.mp4"
    data=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries","stream=codec_type,codec_name,width,height,r_frame_rate,duration","-of","json",str(path)]))
    streams=data["streams"]; video=next(s for s in streams if s["codec_type"]=="video"); audio=next(s for s in streams if s["codec_type"]=="audio")
    assert video["codec_name"]=="h264" and audio["codec_name"]=="aac", (kind, streams)
    assert (video["width"],video["height"])==size, (kind, video)
    assert 17.8 <= float(video["duration"]) <= 18.1, (kind, video["duration"])
    assert video["r_frame_rate"]=="30/1", (kind, video["r_frame_rate"])
    print(f"PASS {path}: {size[0]}x{size[1]}, 30 fps, H.264/AAC, {video['duration']}s")
