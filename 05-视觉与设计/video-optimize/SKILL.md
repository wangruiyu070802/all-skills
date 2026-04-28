---
name: video-optimize
description: >
  爆款视频拆解与优化专家。用户丢视频链接（B站/YouTube/小红书/抖音）或本地文件，
  自动完成：下载→ffmpeg压缩→豆包大模型原生视频理解→8维度爆款拆解+5大进阶模块→
  逐场景15-25秒粒度细拆→生成自包含HTML可视化报告。
  触发场景：用户说「拆解视频」「分析视频」「视频拆解」「video-optimize」「爆款拆解」
  「分析这个视频」，或直接丢视频链接/文件要求分析时使用。
---

# 爆款视频拆解引擎

## 一键命令

```bash
python3 ~/.claude/skills/video-optimize/scripts/video_analyzer.py run \
  "<URL或本地路径>" --title "视频标题" --archive-dir ./outputs/reports
```

子命令：`download` | `compress` | `analyze` | `report`

## 执行协议

1. 收到视频链接/路径后直接开始，不反复确认
2. 始终使用 `--archive-dir ./outputs/reports` 和 `--title` 参数
3. 如果用户没给标题，从URL或文件名推断
4. 报告生成后，用 `<file type="static">` 附件方式输出 report.html
5. 最后输出完整 Markdown 拆解摘要（8维度评分表 + 时间线 + 可复制模板 + TOP3建议）

## 异常处理

| 异常 | 处理 |
|------|------|
| yt-dlp 下载失败 (412/403) | 读取 [FALLBACK.md](FALLBACK.md)，走浏览器方案 |
| 小红书/抖音链接（exit code 2） | 自动读取 [FALLBACK.md](FALLBACK.md) 走浏览器方案 |
| 豆包 API 调用失败 | 脚本自动重试3次。仍失败则检查 API Key 和网络 |
| 视频过大（base64 > 50MB） | 脚本自动二次压缩。仍超限则手动用 compress 命令进一步压缩 |
| ffmpeg/yt-dlp 未安装 | 提示用户：`brew install ffmpeg yt-dlp` |

## 输出结构

```
outputs/reports/
├── index.html                  # 汇总页（深色主题卡片）
└── YYYYMMDD_slug/
    ├── report.html             # 自包含完整报告（含base64视频）
    ├── report-lite.html        # 轻量版（引用video.mp4）
    ├── video.mp4               # 视频文件
    └── meta.json               # 元数据
```

## Markdown 摘要模板

分析完成后在聊天中输出：

```
## 🎬 {标题} 爆款拆解

**综合评分：{分数}/10** | 时长：{时长}

### 8维度评分
| 维度 | 分数 | 要点 |
|------|------|------|
| 开头吸引力 | X/10 | ... |
| 叙事结构 | X/10 | ... |
| ... | ... | ... |

### ✅ TOP 3 亮点
1. ...

### 💡 TOP 3 改进建议
1. ...

### 📋 可复制模板
**结构公式**：...
**文案模板**：...

📊 完整可视化报告已生成 → report.html
```

## 依赖

- Python 3（纯标准库）
- ffmpeg（`brew install ffmpeg`）
- yt-dlp（`brew install yt-dlp`，小红书/抖音不需要）
- 豆包大模型 API（已硬编码在脚本中）
