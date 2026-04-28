---
name: magazine-cover
description: >
  Generate magazine cover style images using Doubao Seedream API. Creates 2 versions
  (data visualization + abstract lines) in black-and-white brutalist editorial style.
  Use when user mentions "杂志封面", "magazine cover", "/杂志封面",
  "Bloomberg Businessweek风格", "纽约时报杂志风格", or wants editorial-style cover images.
  Supports 4 aspect ratios: WeChat header, WeChat secondary, Twitter/X article, Xiaohongshu.
---

# 杂志封面生图

黑白极简、高对比度杂志封面设计。一次生成 2 张不同风格图片（数据可视化 + 抽象线条）。

## 工作流程

### Step 1：确认图片比例

用户必须选择比例，未指定时反问：

| 选项 | 用途 | size 参数 |
|------|------|-----------|
| 1 | 微信公众号首图（2.35:1） | `2944x1253` |
| 2 | 微信公众号次图（1:1） | `2048x2048` |
| 3 | 推特文章封面（5:2） | `3040x1216` |
| 4 | 小红书封面（3:4） | `1728x2304` |

自动识别："微信首图" → 选项1，"小红书封面" → 选项4。

反问话术：
```
请先选择图片比例：
1. 微信公众号首图（2.35:1，2944×1253）
2. 微信公众号次图（1:1，2048×2048）
3. 推特文章封面（5:2，3040×1216）
4. 小红书封面（3:4，1728×2304）

回复数字 1-4。
```

### Step 2：提取核心概念

不要直接渲染完整文字段落，提取：
1. **核心概念**：一句话主题（如「工具陷阱 vs 简单执行」）
2. **关键词**：3-5 个（如「工具、执行、手机、爆火」）
3. **数据对比**：如有数据，提取对比关系（如「1 vs 100+」）

| 用户输入示例 | 核心概念 | 关键词 |
|-------------|---------|--------|
| 非常有经验的创作者沉迷工具…第一条爆火短视频全用手机 | 工具陷阱 vs 简单执行 | 工具、执行、手机、爆火、1 vs 100+ |
| 两套写作系统：推文即兴，文稿系统化 | 即兴 vs 系统 | 推文、文稿、71 vs 1785 |

### Step 3：生成 Prompt 并调用 API

固定生成 2 个版本，可并行调用。

#### 版本 1：数据可视化风格

适合：有明确数据对比、教育性内容。

Prompt 模板：
```
Pure black background, bold editorial magazine cover design, pure black and white only, ultra-high contrast, brutalist graphic design, Swiss International Typographic Style. Create a data visualization poster: show two numbers in massive typography - [数字1] (representing simplicity) versus [数字2] (representing tool complexity). Use horizontal bar charts below each number. Left side: single short bar labeled [关键词1]. Right side: many overlapping bars labeled [关键词2/关键词3/关键词4]. Bottom text in Chinese: [核心概念]. Minimal, clean, high impact.
```

#### 版本 2：抽象线条风格

适合：概念化内容、艺术感场景。

Prompt 模板：
```
Pure black background, editorial magazine cover, pure black and white, ultra-high contrast. Create abstract visual metaphor: top half shows dense overlapping horizontal lines (representing [复杂概念]), bottom half shows single clean horizontal line (representing [简单概念]). Massive Chinese typography overlaid: [关键词1] (top) and [关键词2] (bottom). Inspired by minimalist data visualization, brutalist design, maximum visual impact.
```

### Step 4：调用 API

API Key 获取：`$DOUBAO_API_KEY` 环境变量。

两个版本并行调用：

```bash
curl -s -X POST "https://ark.cn-beijing.volces.com/api/v3/images/generations" \
  -H "Authorization: Bearer $DOUBAO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-seedream-4-5-251128",
    "prompt": "[完整prompt]",
    "sequential_image_generation": "disabled",
    "response_format": "url",
    "size": "[尺寸]",
    "stream": false,
    "watermark": true
  }'
```

### Step 5：下载保存

保存根目录：`~/trae/outputs/杂志封面/`

目录结构：按日期子文件夹。

```bash
mkdir -p ~/trae/outputs/杂志封面/YYYY-MM-DD/
```

命名规范：`YYYY-MM-DD_[核心概念]_v1数据可视化_[比例标识].jpeg`

比例标识：微信首图 / 微信次图 / 推特 / 小红书

```bash
curl -o "~/trae/outputs/杂志封面/YYYY-MM-DD/YYYY-MM-DD_核心概念_v1数据可视化_微信次图.jpeg" "[图片URL]"
curl -o "~/trae/outputs/杂志封面/YYYY-MM-DD/YYYY-MM-DD_核心概念_v2抽象线条_微信次图.jpeg" "[图片URL]"
```

### Step 6：展示结果

生成完成后只报告文件路径，不打开浏览器。

格式：
```
✅ 杂志封面生成成功！

核心概念：[概念]
关键词：[关键词列表]

版本 1（数据可视化）：outputs/杂志封面/YYYY-MM-DD/文件名.jpeg
版本 2（抽象线条）：outputs/杂志封面/YYYY-MM-DD/文件名.jpeg

需要重新生成或调整参数吗？
```
