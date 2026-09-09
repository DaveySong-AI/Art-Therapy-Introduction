# Scene 01 Gold Standard — Codex Execution Brief

## 目标

请只制作 Episode 00 的 Scene 01，时长约 4 秒。

不要制作整集，不要重做视觉设计。

本次任务只有一个目的：

> 验证现有 Gold Master 画面能否被高质量地转化为 Color Cartoon Whiteboard Animation。

---

## 唯一视觉母版

使用：

`assets/approved/episode-00/scene-01-gold-master.png`

该文件是：

**Approved Visual Master / Gold Standard**

它不是“灵感参考”，而是视觉约束。

禁止：

- 重新设计人物
- 重新画一个简化版人物
- 用 Pillow/Canvas 程序化几何图形替代人物
- 改变角色发型
- 改变蓝色 hoodie
- 改变画面配色
- 改成扁平 icon 风
- 改成纯白板黑白风
- 改成 PPT 动画风
- 改成极简 infographic

必须最大程度保留：

- 男孩角色外观
- 房间氛围
- 书桌和学习元素
- 彩色绘本质感
- 柔和光线
- 压力符号
- 手机、时钟、电量、游戏等图形
- 整体构图和视觉丰富度

核心原则：

> Animate the approved art. Do not replace the approved art.

---

## 动画目标

不是直接显示整张图片。

目标是模拟：

**一只手正在把这个画面逐步画出来。**

推荐做法：

### 1. Background Reveal

背景先以非常轻的浅色轮廓/底稿出现。

然后使用：

- animated mask
- stroke reveal
- wipe reveal

逐渐显现。

### 2. Character Reveal

男孩不能重新程序化绘制。

请从 Gold Master 中：

- crop / isolate / segment character
- 或建立 mask

然后通过 reveal 动画逐渐显现。

推荐顺序：

头发 → 脸 → 蓝色 hoodie → 手臂 → 表情。

### 3. Object Sequence

根据旁白节奏依次出现：

0.0–0.8s  
男孩和桌面主体开始出现。

0.8–1.4s  
左侧书本 / 作业相关元素。

1.4–2.0s  
手机 + “消息不断”。

2.0–2.5s  
游戏手柄。

2.5–3.0s  
时钟 + “时间不够”。

3.0–3.4s  
电池 + “电量不足”。

3.4–4.0s  
头顶压力乱线和整体情绪完成。

不要让所有元素一起淡入。

---

## Hand Animation

一只真实或拟真的手持蓝色马克笔进入画面。

手的位置应该尽量跟随当前正在 reveal 的区域。

例如：

绘制手机时，手在手机附近。

绘制时钟时，手移动到右上。

绘制压力乱线时，手移动到男孩头顶。

不要让手固定在右上角。

不要只是把一张手的 PNG 放在屏幕边缘。

---

## Whiteboard Illusion

本系列的核心并不是“真的用代码一笔画出复杂插画”。

正确方式是：

> High-quality artwork + animated mask + moving marker hand

让观众感觉：

“这幅漂亮的插画正在被画出来。”

允许适度使用：

- opacity
- mask path
- progressive reveal
- texture reveal

但必须避免普通 fade in。

---

## 文字

本 Scene 的核心屏幕文字：

“你有没有过这样的时刻？”

可以保留 Gold Master 中现有设计。

不要重复额外加一套大字幕覆盖画面。

---

## 输出

输出两个文件：

`output/scene-01-gold-prototype-landscape.mp4`

1920×1080  
16:9  
30fps  
约 4 秒

以及：

`output/scene-01-gold-prototype-portrait.mp4`

1080×1920  
9:16  
30fps

竖屏版本需要重新构图，不要简单拉伸或裁掉人物。

---

## 本次禁止事项

不要：

- 重新生成角色
- 使用简笔画角色替代
- 使用 procedural cartoon character
- 使用代码画脸
- 使用圆形和矩形重新拼人物
- 改变画风
- 为追求代码复用而牺牲画面质量
- 一次性制作完整 60 秒

---

## 验收标准

只有以下条件全部满足，才算通过：

1. 第一眼看起来仍然是 Gold Master 的画风。
2. 人物与 Gold Master 明显是同一个角色。
3. 画面不是 PPT 式淡入。
4. 能明显感受到“手在画”。
5. 元素按照节奏逐步出现。
6. 画面品质没有因为动画化明显下降。
7. 横屏版本达到可用于正式成片的视觉质量。

本次重点不是代码优雅，而是：

> Visual fidelity first.