# FFmpeg 命令参考

所有命令在视频工作目录下执行。假设视频片段命名为 clip1.mp4 ~ clipN.mp4，旁白为 voiceover.wav，背景音乐为 bgm.wav。

## 1. 拼接视频片段

### 创建 concat 列表文件
```bash
echo "file 'clip1.mp4'" > concat.txt
echo "file 'clip2.mp4'" >> concat.txt
echo "file 'clip3.mp4'" >> concat.txt
# ... 依次添加所有片段
```

### 执行拼接（无损，直接copy）
```bash
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy video_concat.mp4
```

注意：所有 clip 必须编码格式、分辨率、帧率完全一致（同一工具生成的没问题）。

## 2. 混合旁白 + 背景音乐

```bash
ffmpeg -y -i video_concat.mp4 -i voiceover.wav -i bgm.wav \
  -filter_complex "[1:a]volume=1.0[voice];[2:a]volume=0.18[music];[voice][music]amix=inputs=2:duration=first:dropout_transition=2[aout]" \
  -map 0:v -map "[aout]" \
  -c:v copy -c:a aac -b:a 192k \
  -t 60 \
  output.mp4
```

参数说明：
- `volume=1.0`：旁白音量 100%
- `volume=0.18`：背景音乐音量 18%（不抢人声）
- `duration=first`：以第一个输入（旁白）的时长为准
- `-t 60`：最终裁剪到 60 秒，与总时长一致
- `-b:a 192k`：音频码率 192kbps

## 3. 去除水印

### 同时去除左上角和右下角（推荐）
```bash
ffmpeg -y -i input.mp4 \
  -vf "delogo=x=10:y=10:w=220:h=80,delogo=x=1030:y=635:w=235:h=75" \
  -c:v libx264 -preset medium -crf 20 \
  -c:a copy \
  output_nowm.mp4
```

参数说明：
- `delogo=x:y:w:h`：水印区域的左上角坐标和宽高
- 第一组 `x=10:y=10:w=220:h=80`：左上角水印
- 第二组 `x=1030:y=635:w=235:h=75`：右下角水印（1280×720分辨率下）
- `-crf 20`：视频质量，数值越小质量越高文件越大，20 是高质量
- 去水印必须重新编码视频（不能 -c:v copy），音频可以 copy

### 不同分辨率下的右下角坐标
- 1280×720：`x=1030:y=635:w=235:h=75`
- 854×480：`x=685:y=420:w=160:h=55`
- 1920×1080：`x=1545:y=955:w=350:h=110`

## 4. 验证水印去除效果

抽多个时间点的帧检查（至少 4 个时间点）：
```bash
for t in 5 20 40 55; do
  ffmpeg -y -ss $t -i output_nowm.mp4 -vframes 1 -update 1 "check_t${t}.png"
done
```
然后逐张查看 check_t*.png，确认左上角和右下角都无水印残留。

## 5. 常用检查命令

### 查看视频信息
```bash
ffprobe -v quiet -show_entries format=duration,size -show_entries stream=codec_name,width,height,r_frame_rate -of default=noprint_wrappers=1 input.mp4
```

### 提取单帧
```bash
ffmpeg -y -ss 30 -i input.mp4 -vframes 1 -update 1 frame.png
```

### 查看所有片段时长
```bash
for f in clip*.mp4; do echo -n "$f: "; ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$f"; done
```

## 6. 完整一键流程（拼接+合成+去水印）

如果要一步完成拼接、音频合成、去水印：
```bash
# 第一步：拼接
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy video_concat.mp4

# 第二步：合成音频
ffmpeg -y -i video_concat.mp4 -i voiceover.wav -i bgm.wav \
  -filter_complex "[1:a]volume=1.0[voice];[2:a]volume=0.18[music];[voice][music]amix=inputs=2:duration=first[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 192k -t 60 video_with_audio.mp4

# 第三步：去水印
ffmpeg -y -i video_with_audio.mp4 \
  -vf "delogo=x=10:y=10:w=220:h=80,delogo=x=1030:y=635:w=235:h=75" \
  -c:v libx264 -preset medium -crf 20 -c:a copy final.mp4
```

注意：去水印必须在最后一步（因为需要重新编码），音频合成可以在去水印之前或之后。
