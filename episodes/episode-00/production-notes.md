# Episode 00 制作记录

**制作日期：** 2026-09-09
**制作工具：** 豆包 AI（image_gen / image_to_video / text_to_audio_plus）+ FFmpeg
**最终成品：** [final/episode-00-whiteboard-animation.mp4](final/episode-00-whiteboard-animation.mp4)

---

## 制作流程

### 1. 风格探索（5 张参考图）
生成了 5 种白板手绘风格供选择：经典黑白、彩色卡通、极简扁平、粉笔黑板、水彩手绘。
**最终选择：** 黑白线条为主 + 关键情绪点彩色点缀，面向儿童青少年。

### 2. 分镜图生成（7 张 + 1 修正 + 1 修改）
- 批量生成 7 张分镜关键帧（2048×1152）
- 镜头 3 文字"画出来"生成错误，用 image_edit 修正
- 镜头 1 电池状态错误（满电→应为亏电），用 image_edit 修改为只剩 1 格

### 3. 视频片段生成（8 段）
- 用 image_to_video 以分镜图为参考，生成 7 段视频（每段 5–12 秒）
- 镜头 1 因电池修改重新生成 1 次
- 模型：seedance_2.0_fast（最经济）

### 4. 音频生成（2 条）
- 旁白：温柔女声，60 秒，text_to_audio_plus
- 背景音乐：轻柔钢琴 + 弦乐，60 秒，text_to_audio_plus

### 5. 后期合成（FFmpeg）
- concat 拼接 7 段视频
- amix 混合旁白（100%）+ 背景音乐（18%）
- 裁剪到 60 秒
- delogo 去除水印

---

## 踩坑经验（后续课程必读）

### 坑 1：分镜图文字易错
AI 生成图片中的中文文字经常写错或变形。
**解决：** prompt 中明确写出文字内容，生成后逐张检查，错了立即用 image_edit 修正，**不要带着错误分镜图去生成视频**。

### 坑 2：水印位置不固定
"豆包AI生成"水印可能在左上角，也可能在右下角，甚至动态切换。
**解决：** 去水印时用 delogo **同时处理左上角和右下角两个区域**，处理后抽至少 4 个时间点的帧验证。

```
delogo=x=10:y=10:w=220:h=80,delogo=x=1030:y=635:w=235:h=75
```

### 坑 3：细节错误导致视频重制
镜头 1 的电池状态（满电 vs 亏电）在分镜图阶段没注意，导致视频生成后才发现，不得不重新生成镜头 1 并重新拼接。
**解决：** 分镜图阶段逐项检查所有细节（图标状态、元素数量、文字内容），确认无误后再批量生成视频。视频生成是消耗最大的环节，重制成本最高。

### 坑 4：TTS 时长必须匹配
旁白音频 duration 必须与视频总时长一致，否则合成时会截断或留白。
**解决：** 生成旁白时 duration 设为视频总时长（如 60 秒），合成时用 `-t 60` 裁剪对齐。

---

## 积分消耗分析

| 环节 | 调用次数 | 相对消耗 |
|---|---|---|
| 视频生成（image_to_video） | 8 段 | ~65%（最大） |
| 图片生成（image_gen + image_edit） | 14 张 | ~25% |
| 音频生成（text_to_audio_plus） | 2 条 | ~5% |
| FFmpeg 后期 | 多次 | 0%（本地计算） |

**优化方向：**
1. 避免视频重制（最大节省）
2. 分辨率从 720p 降到 480p（白板风格画质损失不明显）
3. 减少风格参考图数量（确认风格后直接复用）
4. 紧凑简单镜头的时长（如结尾定格可缩到 3–5 秒）

---

## 可复用资产

- **分镜模板：** 见 `skills/whiteboard-video-maker/references/storyboard-template.md`
- **Prompt 库：** 见 `skills/whiteboard-video-maker/references/prompt-templates.md`
- **FFmpeg 命令：** 见 `skills/whiteboard-video-maker/references/ffmpeg-guide.md`
- **完整制作流程：** 见 `skills/whiteboard-video-maker/SKILL.md`
