# Art-Therapy-Introduction

《艺术疗愈 · 10 节课》的视频制作工作区。当前从 Episode 00《艺术疗愈是什么？为什么我们需要它？》开始，目标是先验证 Color Cartoon Whiteboard Animation 的视觉和制作流程。

## 仓库内容

- [`skills/art-healing-video/SKILL.md`](skills/art-healing-video/SKILL.md)：制作规范、Episode 00 分镜脚本、视觉规则和后续 MVP 计划。
- [`assets/reference/episode-00-color-storyboard.png`](assets/reference/episode-00-color-storyboard.png)：主要彩色视觉参考。
- [`assets/reference/episode-00-whiteboard-storyboard.png`](assets/reference/episode-00-whiteboard-storyboard.png)：白板手绘镜头结构参考。
- [`docs/SKILL_ASSESSMENT.md`](docs/SKILL_ASSESSMENT.md)：对当前 Skill 完整性的判断和下一步闭环建议。

## 当前阶段

V1 已提供可重复运行的 Episode 00 四场景原型管线。它使用 Python + Pillow 绘制逐笔出现的原创矢量风格画面，再由 FFmpeg 封装为 H.264/AAC MP4；不裁切或移动现有的分镜图作为成片。

## V1 原型

对应的源规格保存在 `episodes/episode-00/`，可编辑渲染代码在 `src/render_prototype.py`。当前只制作 Scene 01、06、10、12，合计 18 秒，不是完整 60 秒成片。

### 前置条件

- Python 3.9+ 和 Pillow（本机可通过 `python3 -m pip install -r requirements.txt` 安装）
- FFmpeg / FFprobe
- macOS 的 Hiragino Sans GB（脚本使用其中文字符支持）

### 渲染

```bash
python3 src/render_prototype.py --format landscape
python3 src/render_prototype.py --format portrait
python3 src/verify_output.py
```

输出文件：

- `output/episode-00-prototype-landscape.mp4` — 1920×1080，30 fps
- `output/episode-00-prototype-portrait.mp4` — 1080×1920，30 fps

渲染中间帧位于 `output/frames/`，每次渲染会自动重建。成片包含静音 AAC 轨道，为后续接入温暖普通话旁白、授权 BGM 与少量笔触音效预留接口。文案明确表达的是情绪觉察、表达和短暂舒缓，不作诊断或治疗承诺。

### 验收范围

自动检查确认两个成片的时长、帧率、尺寸与 H.264/AAC 编码。人工审核仍需确认：角色与参考分镜的一致性、逐笔出现的自然程度、中文可读性、竖屏安全区，以及未来加入旁白和音乐后的情绪节奏。

建议先对这四幕进行人工视觉审核，再扩展到完整 60 秒 Episode 00。

## Scene 01 Gold Master prototype

`assets/approved/episode-00/scene-01-gold-master.png` 是 Scene 01 的唯一视觉母版。`src/render_scene01_gold.py` 只从该文件派生浅色边缘底稿、逐笔遮罩与移动蓝色马克笔手；它不会重绘、替代或简化角色和物件。

```bash
python3 src/render_scene01_gold.py --format all
python3 src/verify_scene01_gold.py
```

渲染会输出 `output/scene-01-gold-prototype-landscape.mp4`（1920×1080）和 `output/scene-01-gold-prototype-portrait.mp4`（1080×1920）。两者均为 4 秒、30fps H.264/AAC。竖版保留完整人物和批准画面，并以母版派生的柔焦背景重新构图，绝不拉伸人物或用新插画填充画面。

— Davey's Codex agent
