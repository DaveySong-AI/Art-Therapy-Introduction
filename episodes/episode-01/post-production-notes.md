# 第 1 课后期制作记录

## 概述
本文档记录第 1 课从原始素材到最终发布版的完整后期制作流程，供后续课程参考。

## 最终成品
- **文件**：`final/艺术疗愈第1集_含数字人开场_名牌卡片版.mp4`
- **分辨率**：1280×720
- **时长**：108.64 秒
- **大小**：16MB

---

## 一、替换于颖音色

### 背景
原始旁白使用的是通用 TTS 女声，用户希望统一为"于颖"的声音，与数字人讲师形象一致。

### 输入素材
- 参考语音：`于颖_语音参考.wav`（用户提供）
- 原始旁白时间线：`voiceover.wav`（93 秒）

### 制作步骤
1. 使用 `audio_to_audio_plus` 工具，以于颖语音参考为基准
2. 按照原始旁白的时间线和文字内容，生成于颖声音版旁白
3. 输出：`voiceover_于颖版.wav`（93 秒，40000Hz）

### 关键参数
- 参考音频：1–3 条
- 输出格式：WAV
- 时长：与原始旁白一致（93 秒）

### 注意事项
- 旁白语速需与画面分镜同步
- 生成后需检查每段旁白的起止时间是否与视频画面匹配

---

## 二、数字人开场视频拼接

### 背景
用户提供了独立的于颖数字人开场视频，需要与白板手绘正片拼接。

### 输入素材
- 数字人开场：`于颖_数字人_开场视频_最终对齐版.mp4`（13.64 秒，1280×720，HEVC）
- 课程正片：`艺术疗愈第1集_全程于颖旁白_720p高清.mp4`（93 秒，1280×720，H.264）

### 转场方案演变（重要！避免踩坑）

| 方案 | 问题 | 结论 |
|---|---|---|
| xfade 交叉淡化 0.5s | 过渡太短 | 否决 |
| 黑场停顿 2s | 不自然 | 否决 |
| xfade slideleft 0.8s | 速度太快 | 否决 |
| xfade slideleft 2s + acrossfade | 第二段旁白跟着太近 | 否决 |
| xfade + adelay 延迟旁白 | 视频没往后延，旁白错位 | 否决 |
| **独立转场视频 + 三段拼接** | **完美解决** | **采用** |

### 最终方案：独立转场视频 + 三段拼接

**核心原则：两段视频完整无损，中间独立增加 2 秒转场。**

#### 步骤 1：提取首末帧
```bash
# 提取第一段最后一帧
ffmpeg -ss 13.5 -i 开场视频.mp4 -vframes 1 last_frame.jpg

# 提取第二段第一帧
ffmpeg -ss 0.1 -i 正片.mp4 -vframes 1 first_frame.jpg
```

#### 步骤 2：生成 2 秒独立翻页转场
```bash
ffmpeg -loop 1 -t 4 -i last_frame.jpg \
       -loop 1 -t 4 -i first_frame.jpg \
       -filter_complex "[0:v][1:v]xfade=transition=slideleft:duration=2:offset=0,format=yuv420p[vout]" \
       -map "[vout]" -t 2 -r 24 transition_2s.mp4
```

#### 步骤 3：三段拼接
```bash
ffmpeg -i 开场视频.mp4 \
       -i transition_2s.mp4 \
       -f lavfi -i "anullsrc=channel_layout=stereo:sample_rate=44100:d=2" \
       -i 正片.mp4 \
       -filter_complex "[3:a]volume=9.6dB[a3];[0:v][0:a][1:v][2:a][3:v][a3]concat=n=3:v=1:a=1[vout][aout]" \
       -map "[vout]" -map "[aout]" \
       输出.mp4
```

#### 时间线结构
| 段落 | 时间 | 内容 | 音频 |
|---|---|---|---|
| 第一段 | 0–13.64s | 数字人开场 | 于颖旁白 |
| 转场 | 13.64–15.64s | 2 秒翻页（slideleft） | 2 秒静音 |
| 第二段 | 15.64–108.64s | 白板手绘正片 | 于颖旁白 |

### 音量对齐
- 数字人开场 mean_volume：-19.7 dB
- 课程正片 mean_volume：-29.3 dB
- **正片需提高 9.6 dB** 与开场对齐

### 避坑指南
1. **不要用 xfade 直接拼接两段带旁白的视频**——会导致视频重叠、旁白错位
2. **转场期间要静音**——给观众呼吸空间，避免旁白仓促
3. **两段视频必须完整无损**——不能裁剪任何一段的开头或结尾
4. **HEVC 编码的视频提取帧可能失败**——先转码为 H.264 再提取

---

## 三、添加课程 Logo

### 背景
用户提供课程 logo，需要叠加到视频左上角。

### 输入素材
- `课程logo.png`（2048×768，RGB，无透明通道）

### 步骤 1：去除白色背景（生成透明版）
原始 logo 有白色底色，与白板的米白色不一致，需要去除。

```python
from PIL import Image

img = Image.open('课程logo.png').convert('RGBA')
pixels = img.load()
width, height = img.size

# 将接近白色的像素设为透明（RGB > 235）
for y in range(height):
    for x in range(width):
        r, g, b, a = pixels[x, y]
        if r > 235 and g > 235 and b > 235:
            pixels[x, y] = (r, g, b, 0)

img.save('课程logo_透明.png')
```

输出：`课程logo_透明.png`（78% 像素透明）

### 步骤 2：叠加到视频
- **显示时段**：仅第二段（15.64 秒后），第一段数字人开场不显示
- **位置**：左上角，x=15, y=15
- **尺寸**：宽 250px

```bash
ffmpeg -i 输入视频.mp4 -i 课程logo_透明.png \
       -filter_complex "[1:v]scale=250:-1[logo];[0:v][logo]overlay=15:15:enable='gte(t,15.64)'[vout]" \
       -map "[vout]" -map "0:a" \
       输出.mp4
```

### 避坑指南
1. **logo 必须去白底**——否则白色矩形底色在白板上很突兀
2. **用 enable 参数控制显示时段**——不要全程显示
3. **logo 尺寸建议 200–250px 宽**——太小看不清，太大遮挡内容

---

## 四、添加名牌卡片

### 背景
用户提供名牌卡片 PNG，需要在第一段数字人开场时显示讲师身份。

### 输入素材
- `name_card.png`（655×243，RGBA，已有透明通道）
- 卡片内容：于颖 | 愿心工作室发起人 · 创新艺术疗愈师

### 显示设置
- **显示时段**：仅第一段（0–13.64 秒）
- **位置**：左下角，x=40, y=490
- **尺寸**：宽 480px
- **动画**：0.5 秒淡入，0.5 秒淡出

### 关键技术：淡入淡出实现（重要！）

**错误方式**：对静态图片直接用 `fade=...:alpha=1`——不生效
**正确方式**：将图片作为循环视频输入，再用 fade

```bash
ffmpeg -i 输入视频.mp4 \
       -loop 1 -t 14 -i name_card.png \
       -filter_complex "[1:v]scale=480:-1,fade=t=in:st=0:d=0.5:alpha=1,fade=t=out:st=13:d=0.5:alpha=1[card];[0:v][card]overlay=40:490[vout]" \
       -map "[vout]" -map "0:a" \
       输出.mp4
```

### 避坑指南
1. **静态图片的 fade:alpha=1 不生效**——必须用 `-loop 1 -t 14` 转为视频输入
2. **不要用 `overlay` 的 `shortest=1`**——会导致输出视频被限制为卡片时长（14 秒）
3. **卡片已有半透明磨砂效果**——不需要额外处理透明度
4. **淡入淡出只调整 alpha 通道**——用 `alpha=1` 参数，否则会把卡片 fade 成黑色

---

## 五、最终画面元素汇总

| 元素 | 显示时段 | 位置 | 尺寸 |
|---|---|---|---|
| 名牌卡片 | 第一段（0–13.64s） | 左下角 | 480px 宽 |
| 课程 logo | 第二段（15.64s 后） | 左上角 | 250px 宽 |
| 数字人窗口 | 全程 | 右上角 | 圆形 |

---

## 六、文件清单

### 最终成品
- `final/艺术疗愈第1集_含数字人开场_名牌卡片版.mp4`

### 素材
- `assets/name_card.png` — 名牌卡片（透明背景）
- `assets/课程logo_透明.png` — 课程 logo（透明背景）
- `final/voiceover_于颖版.wav` — 于颖声音旁白
- `final/bgm.wav` — 背景音乐

### 参考文档
- `production-notes.md` — 本文档
- `LESSON_01_INPUT.md` — 创作主文档
- `storyboard-images/` — 9 张分镜关键帧
