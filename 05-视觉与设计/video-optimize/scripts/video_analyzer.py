#!/usr/bin/env python3
"""
爆款视频拆解引擎 - 下载、压缩、豆包API分析、场景细拆
用法:
  python3 video_analyzer.py run "<URL或本地路径>" --title "标题" --archive-dir ./outputs/reports
  python3 video_analyzer.py download "<URL>" --output video.mp4
  python3 video_analyzer.py compress "<路径>" --output compressed.mp4
  python3 video_analyzer.py analyze "<路径>" --title "标题"
  python3 video_analyzer.py report "<analysis.json>" --video "<视频路径>" --archive-dir ./outputs/reports
"""

import argparse
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.request
import urllib.error

# ── API 配置 ─────────────────────────────────────────────
API_ENDPOINT = "https://ark.cn-beijing.volces.com/api/v3/responses"
API_MODEL = "doubao-seed-2-0-pro-260215"
API_KEY = "f587c2fc-10a7-4cce-871b-4be47dc2671f"

MAX_BASE64_BYTES = 50 * 1024 * 1024  # 50MB API limit
TARGET_FILE_SIZE = 35 * 1024 * 1024   # 35MB -> base64 ~47MB < 50MB
MAX_RETRIES = 3

# ── 工具函数 ─────────────────────────────────────────────

def log(msg, level="INFO"):
    colors = {"INFO": "\033[36m", "OK": "\033[32m", "WARN": "\033[33m", "ERR": "\033[31m"}
    reset = "\033[0m"
    c = colors.get(level, "")
    print(f"{c}[{level}]{reset} {msg}", file=sys.stderr)

def run_cmd(cmd, check=True, capture=True):
    """Run shell command, return stdout."""
    r = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=capture, text=True)
    if check and r.returncode != 0:
        stderr = r.stderr if capture else ""
        raise RuntimeError(f"Command failed ({r.returncode}): {cmd}\n{stderr}")
    return r

def detect_platform(url):
    """Detect video platform from URL."""
    url_lower = url.lower()
    if "bilibili.com" in url_lower or "b23.tv" in url_lower:
        return "bilibili"
    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        return "youtube"
    if "xiaohongshu.com" in url_lower or "xhslink.com" in url_lower:
        return "xiaohongshu"
    if "douyin.com" in url_lower or "tiktok.com" in url_lower:
        return "douyin"
    return "unknown"

def get_video_duration(path):
    """Get video duration in seconds using ffprobe."""
    r = run_cmd(f'ffprobe -v quiet -print_format json -show_format "{path}"')
    info = json.loads(r.stdout)
    return float(info.get("format", {}).get("duration", 0))

def get_file_size(path):
    return os.path.getsize(path)

def to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")

def base64_size(path):
    """Estimate base64 size without loading entire file."""
    return int(get_file_size(path) * 4 / 3) + 100

def extract_json(text):
    """Extract JSON from text, handling ```json blocks and nested structures."""
    # Try ```json ... ``` block first
    m = re.search(r'```json\s*\n?(.*?)\n?\s*```', text, re.DOTALL)
    if m:
        text = m.group(1)

    # Find outermost { ... }
    depth = 0
    start = None
    for i, c in enumerate(text):
        if c == '{':
            if depth == 0:
                start = i
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0 and start is not None:
                try:
                    return json.loads(text[start:i+1])
                except json.JSONDecodeError:
                    start = None

    # Try outermost [ ... ]
    depth = 0
    start = None
    for i, c in enumerate(text):
        if c == '[':
            if depth == 0:
                start = i
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0 and start is not None:
                try:
                    return json.loads(text[start:i+1])
                except json.JSONDecodeError:
                    start = None

    raise ValueError(f"No valid JSON found in response (length={len(text)})")


# ── Step 1: 下载 ─────────────────────────────────────────

def download_video(url, output_path=None):
    """Download video from URL. Returns path to downloaded file.
    Exit code 2 for platforms needing browser fallback."""
    platform = detect_platform(url)
    log(f"Detected platform: {platform}")

    if platform in ("xiaohongshu", "douyin"):
        log(f"{platform} requires browser fallback (FALLBACK.md)", "WARN")
        print(json.dumps({"error": "browser_fallback_required", "platform": platform}))
        sys.exit(2)

    if platform not in ("bilibili", "youtube"):
        log(f"Unknown platform, trying yt-dlp anyway", "WARN")

    if not output_path:
        output_path = tempfile.mktemp(suffix=".mp4", dir=".")

    cmd = [
        "yt-dlp",
        "-f", "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
        "--merge-output-format", "mp4",
        "-o", output_path,
        "--no-playlist",
        url
    ]
    log(f"Downloading with yt-dlp: {url}")
    r = subprocess.run(cmd, capture_output=True, text=True)

    if r.returncode != 0:
        # Check for 412/403 errors
        if any(code in r.stderr for code in ["HTTP Error 412", "HTTP Error 403", "ERROR"]):
            log(f"yt-dlp blocked ({r.stderr[:200]}), need browser fallback", "WARN")
            print(json.dumps({"error": "ytdlp_blocked", "platform": platform, "stderr": r.stderr[:500]}))
            sys.exit(2)
        raise RuntimeError(f"yt-dlp failed: {r.stderr}")

    # Find the actual output file (yt-dlp may add extension)
    if os.path.exists(output_path):
        log(f"Downloaded: {output_path} ({get_file_size(output_path) / 1024 / 1024:.1f}MB)", "OK")
        return output_path

    # Check for file with different extension
    base = os.path.splitext(output_path)[0]
    for ext in [".mp4", ".mkv", ".webm"]:
        candidate = base + ext
        if os.path.exists(candidate):
            log(f"Downloaded: {candidate} ({get_file_size(candidate) / 1024 / 1024:.1f}MB)", "OK")
            return candidate

    raise FileNotFoundError(f"Download completed but file not found: {output_path}")


# ── Step 2: 压缩 ─────────────────────────────────────────

def compress_video(input_path, output_path=None, target_bytes=TARGET_FILE_SIZE):
    """Compress video to target size. Always ensures faststart."""
    if not output_path:
        output_path = tempfile.mktemp(suffix=".mp4", dir=os.path.dirname(input_path) or ".")

    file_size = get_file_size(input_path)
    b64_est = base64_size(input_path)

    # If small enough, just do faststart
    if file_size < target_bytes and b64_est < MAX_BASE64_BYTES:
        log(f"Video {file_size/1024/1024:.1f}MB < {target_bytes/1024/1024:.0f}MB, applying faststart only")
        cmd = f'ffmpeg -y -i "{input_path}" -c copy -movflags +faststart "{output_path}"'
        run_cmd(cmd)
        log(f"Faststart applied: {output_path}", "OK")
        return output_path

    duration = get_video_duration(input_path)
    if duration <= 0:
        duration = 60  # fallback

    def do_compress(target_mb):
        target_b = target_mb * 1024 * 1024
        # Reserve 10% for audio
        video_bitrate = int((target_b * 0.9 * 8) / duration)
        audio_bitrate = "128k"
        vbr_k = f"{video_bitrate // 1000}k"

        scale_filter = "-vf scale=-2:720" if True else ""  # always limit to 720p
        cmd = (
            f'ffmpeg -y -i "{input_path}" '
            f'-c:v libx264 -b:v {vbr_k} -maxrate {int(video_bitrate * 1.5) // 1000}k '
            f'-bufsize {int(video_bitrate * 2) // 1000}k '
            f'-preset medium -crf 23 '
            f'{scale_filter} '
            f'-c:a aac -b:a {audio_bitrate} '
            f'-movflags +faststart '
            f'"{output_path}"'
        )
        run_cmd(cmd)

    # First pass
    target_mb = target_bytes / (1024 * 1024)
    log(f"Compressing {file_size/1024/1024:.1f}MB → target {target_mb:.0f}MB (duration={duration:.0f}s)")
    do_compress(target_mb)

    # Check result
    result_size = get_file_size(output_path)
    result_b64 = base64_size(output_path)
    log(f"Compressed: {result_size/1024/1024:.1f}MB (base64 est: {result_b64/1024/1024:.1f}MB)")

    if result_b64 > MAX_BASE64_BYTES:
        log("Still too large, doing aggressive 2nd pass", "WARN")
        # More aggressive: target 25MB
        second_target = 25
        do_compress(second_target)
        result_size = get_file_size(output_path)
        log(f"2nd pass: {result_size/1024/1024:.1f}MB", "OK")

    return output_path


# ── Step 3: 8维度分析 ────────────────────────────────────

ANALYSIS_PROMPT = """你是一位爆款短视频拆解专家。请仔细观看这个视频，从以下 8 个基础维度和 5 个进阶模块进行深度分析。

你必须基于视频的实际质量独立评分，不要受到示例格式中任何数字的影响。评分应有明显区分度：
- 1-3分：差，明显不足，业余水平
- 4-5分：一般，有基本功但缺乏亮点
- 6-7分：良好，有一定专业度和创意
- 8-9分：优秀，接近头部水平
- 10分：顶级，教科书级别（极少给出）

overall_score 应该是8个维度评分的加权平均（hook和narrative权重更高），不要简单给一个笼统的高分。
差的视频就应该给低分（3-5分），一般的给中间分（5-7分），只有真正优秀的才给8分以上。

请严格按以下 JSON 格式输出（不要输出其他内容）：

```json
{
  "overall_score": <float>,
  "summary": "<一句话总结>",
  "hook": {
    "score": <int 1-10>,
    "description": "<描述>",
    "formula": "<开头公式>",
    "template": "<可复制的开头模板>"
  },
  "narrative": {
    "score": <int 1-10>,
    "type": "<叙事类型>",
    "description": "<描述>",
    "timeline": [{"time": "<时间段>", "chapter": "<章节名>", "description": "<描述>"}],
    "template": "<叙事结构模板>"
  },
  "pacing": {
    "score": <int 1-10>,
    "description": "<描述>",
    "cut_points": ["<时间点>"],
    "pattern": "<节奏模式>"
  },
  "visual": {
    "score": <int 1-10>,
    "description": "<描述>",
    "shots": [{"time": "<时间>", "type": "<镜头类型>", "description": "<描述>"}],
    "color_style": "<色彩风格>",
    "effects": ["<效果>"]
  },
  "text_overlay": {
    "score": <int 1-10>,
    "description": "<描述>",
    "has_text": <bool>,
    "style": "<字幕风格>",
    "highlights": ["<高亮手法>"]
  },
  "audio": {
    "score": <int 1-10>,
    "description": "<描述>",
    "estimated_bpm": <int or null>,
    "sync_evidence": "<音画同步证据>",
    "voice_style": "<声音风格>"
  },
  "cta": {
    "score": <int 1-10>,
    "description": "<描述>",
    "has_cta": <bool>,
    "cta_time": "<CTA时间点>",
    "cta_type": "<CTA类型>"
  },
  "ending": {
    "score": <int 1-10>,
    "description": "<描述>",
    "is_loopable": <bool>,
    "has_series_hook": <bool>,
    "ending_type": "<结尾类型>"
  },
  "emotional_arc": {
    "arc_type": "<弧线类型>",
    "arc_description": "<描述>",
    "curve_points": [{"time": "<时间>", "valence": <float -5 to 5>, "arousal": <float 0 to 10>, "label": "<标签>"}],
    "turning_points": [{"time": "<时间>", "type": "<类型>", "description": "<描述>"}]
  },
  "retention_prediction": {
    "hook_rate_3s": "<3秒留存率预估>",
    "retention_30s": "<30秒留存率预估>",
    "midpoint_retention": "<中段留存率预估>",
    "completion_rate": "<完播率预估>",
    "risk_segments": [{"time": "<时间段>", "risk": "<low/medium/high>", "label": "<标签>", "reason": "<原因>", "fix": "<修复建议>"}]
  },
  "viral_formulas": {
    "script_formula": {
      "steps": ["<步骤>"],
      "fill_template": "<可填空模板>"
    },
    "emotion_formula": {
      "nodes": ["<情绪节点>"],
      "key_principles": ["<核心原则>"]
    },
    "algorithm_formula": {
      "drivers": ["<算法驱动因子>"],
      "weight_tips": ["<权重技巧>"]
    }
  },
  "algorithm_fitness": {
    "metrics": {
      "completion_rate": "<预估完播率>",
      "interaction_rate": "<预估互动率>",
      "share_rate": "<预估分享率>",
      "save_rate": "<预估收藏率>"
    },
    "platform_fit": [{"platform": "<平台>", "score": <int 1-10>, "reason": "<原因>", "recommended": <bool>}]
  },
  "learning_path": [
    {"rank": <int>, "technique": "<技巧名>", "difficulty": "<难度>", "why": "<为什么学>", "exercises": ["<练习>"], "reference": "<参考案例>"}
  ],
  "replicable_template": {
    "structure": "<结构公式>",
    "shot_list": [{"order": <int>, "duration": "<时长>", "shot_type": "<镜头>", "content": "<内容>"}],
    "script_template": "<文案模板>"
  },
  "top3_strengths": ["<亮点>"],
  "top3_improvements": ["<改进建议>"]
}
```"""

SCENE_DETAIL_PROMPT_TEMPLATE = """你是爆款短视频场景拆解专家。我已经对这个视频进行了章节分段分析，现在需要你对每个章节进行更细粒度的场景拆解。

以下是第一轮分析得到的章节分段：
{chapters_json}

请对每个章节按 15-25 秒粒度拆分为多个 scene（每个章节 2-5 个 scene）。

每个 scene 必须包含以下字段：
- visual: 画面描述
- audio: 音频描述（BGM、音效、语气）
- emotion: 情绪标签
- emotion_valence: 情绪效价（-5 到 +5，负=消极，0=中性，正=积极）
- emotion_arousal: 唤醒度（0 到 10，0=平静，10=极度兴奋）
- retention_risk: 留存风险等级（low/medium/high）
- risk_reason: 风险原因（如无风险写 null）
- risk_fix: 修复建议（如无风险写 null）
- quote: 该场景的核心台词/旁白
- techniques: 使用的爆款手法列表，每项包含 name（手法名）、category（Hook/留存/节奏/情绪/信任/互动/视觉）、why（为什么有效）

留存风险判断标准：
- 画面单一超过15秒 = medium
- 纯文字无画面变化超过20秒 = high
- 抽象概念无类比/案例 = medium
- 无以上情况 = low

请严格按以下 JSON 格式输出（不要输出其他内容）：

```json
{{
  "chapters": [
    {{
      "chapter": "<章节名>",
      "time": "<时间段>",
      "scenes": [
        {{
          "scene_id": "<chapter_idx>_<scene_idx>",
          "time_range": "<开始-结束>",
          "visual": "<画面>",
          "audio": "<音频>",
          "emotion": "<情绪>",
          "emotion_valence": <float>,
          "emotion_arousal": <float>,
          "retention_risk": "<low/medium/high>",
          "risk_reason": "<原因或null>",
          "risk_fix": "<建议或null>",
          "quote": "<台词>",
          "techniques": [
            {{"name": "<手法>", "category": "<类别>", "why": "<原因>"}}
          ]
        }}
      ]
    }}
  ]
}}
```"""


def call_doubao_api(video_path, prompt, retry=MAX_RETRIES):
    """Call Doubao video understanding API with base64 video."""
    log("Encoding video to base64...")
    b64 = to_base64(video_path)
    b64_len = len(b64)
    log(f"Base64 size: {b64_len / 1024 / 1024:.1f}MB")

    if b64_len > MAX_BASE64_BYTES:
        raise ValueError(f"Base64 too large: {b64_len / 1024 / 1024:.1f}MB > {MAX_BASE64_BYTES / 1024 / 1024:.0f}MB")

    data_url = f"data:video/mp4;base64,{b64}"

    payload = {
        "model": API_MODEL,
        "input": [{
            "role": "user",
            "content": [
                {"type": "input_video", "video_url": data_url},
                {"type": "input_text", "text": prompt}
            ]
        }]
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    log(f"Sending request to Doubao API ({len(body) / 1024 / 1024:.1f}MB payload)...")

    for attempt in range(1, retry + 1):
        try:
            req = urllib.request.Request(API_ENDPOINT, data=body, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=300) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            break
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            log(f"API attempt {attempt}/{retry} failed: {e}", "WARN")
            if attempt == retry:
                raise
            time.sleep(2 ** attempt)

    # Parse response - handle multiple formats
    text = _extract_text_from_response(result)
    log(f"API response text length: {len(text)}", "OK")
    return text


def _extract_text_from_response(result):
    """Extract text from various Doubao API response formats."""
    # Format 1: responses API - output is list
    if "output" in result:
        output = result["output"]
        if isinstance(output, list):
            for item in output:
                if item.get("type") == "message":
                    for content in item.get("content", []):
                        if content.get("type") == "output_text":
                            return content["text"]
            # Fallback: just get first text content
            for item in output:
                if isinstance(item, dict):
                    for content in item.get("content", []):
                        if "text" in content:
                            return content["text"]
        elif isinstance(output, dict):
            # output is a dict with content
            if "content" in output:
                for c in output["content"]:
                    if "text" in c:
                        return c["text"]
            if "text" in output:
                return output["text"]
        elif isinstance(output, str):
            return output

    # Format 2: chat completions format
    if "choices" in result:
        choices = result["choices"]
        if choices and "message" in choices[0]:
            return choices[0]["message"].get("content", "")

    # Format 3: simple text field
    if "text" in result:
        return result["text"]

    raise ValueError(f"Cannot extract text from API response: {json.dumps(result, ensure_ascii=False)[:500]}")


def analyze_video(video_path, title=""):
    """Run 8-dimension analysis + scene breakdown. Returns merged JSON."""

    # Step 3: 8-dimension analysis
    log("=== Step 3: 8-dimension analysis ===")
    prompt = ANALYSIS_PROMPT
    if title:
        prompt = f"视频标题: {title}\n\n" + prompt

    raw_text = call_doubao_api(video_path, prompt)
    analysis = extract_json(raw_text)
    log(f"8-dimension analysis complete. Overall score: {analysis.get('overall_score', 'N/A')}", "OK")

    # Step 4: Scene breakdown
    log("=== Step 4: Scene breakdown ===")
    chapters = analysis.get("narrative", {}).get("timeline", [])
    if not chapters:
        log("No chapters found in narrative timeline, skipping scene breakdown", "WARN")
        analysis["scene_breakdown"] = {"chapters": []}
        return analysis

    chapters_json = json.dumps(chapters, ensure_ascii=False, indent=2)
    scene_prompt = SCENE_DETAIL_PROMPT_TEMPLATE.format(chapters_json=chapters_json)
    if title:
        scene_prompt = f"视频标题: {title}\n\n" + scene_prompt

    scene_text = call_doubao_api(video_path, scene_prompt)
    scene_data = extract_json(scene_text)
    analysis["scene_breakdown"] = scene_data
    log("Scene breakdown complete", "OK")

    return analysis


# ── Step 5: 截图 ─────────────────────────────────────────

def extract_screenshots(video_path, interval=20, max_frames=15):
    """Extract screenshots at regular intervals. Returns list of {time, base64}."""
    duration = get_video_duration(video_path)
    if duration <= 0:
        return []

    # Calculate actual interval
    num_frames = min(max_frames, max(1, int(duration / interval)))
    actual_interval = duration / (num_frames + 1)

    screenshots = []
    tmp_dir = tempfile.mkdtemp()

    for i in range(num_frames):
        t = actual_interval * (i + 1)
        out_path = os.path.join(tmp_dir, f"frame_{i:03d}.jpg")
        cmd = f'ffmpeg -y -ss {t:.1f} -i "{video_path}" -vframes 1 -q:v 5 -vf scale=480:-2 "{out_path}" 2>/dev/null'
        r = run_cmd(cmd, check=False)
        if r.returncode == 0 and os.path.exists(out_path):
            with open(out_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("ascii")
            screenshots.append({"time": round(t, 1), "base64": b64})
            os.remove(out_path)

    os.rmdir(tmp_dir)
    log(f"Extracted {len(screenshots)} screenshots", "OK")
    return screenshots


# ── 主流水线 ─────────────────────────────────────────────

def pipeline_run(source, title="", archive_dir="./outputs/reports"):
    """Full pipeline: download → compress → analyze → report."""
    is_url = source.startswith("http://") or source.startswith("https://")
    work_dir = tempfile.mkdtemp(prefix="video_analyze_")

    # Step 1: Download or use local file
    log("=== Step 1: Download ===")
    if is_url:
        video_path = download_video(source, os.path.join(work_dir, "source.mp4"))
    else:
        if not os.path.exists(source):
            log(f"File not found: {source}", "ERR")
            sys.exit(1)
        video_path = os.path.abspath(source)

    duration = get_video_duration(video_path)
    log(f"Video: {video_path} | Duration: {duration:.0f}s | Size: {get_file_size(video_path)/1024/1024:.1f}MB")

    # Step 2: Compress
    log("=== Step 2: Compress ===")
    compressed_path = os.path.join(work_dir, "compressed.mp4")
    compressed_path = compress_video(video_path, compressed_path)

    # Step 3 & 4: Analyze
    log("=== Step 3-4: Analyze ===")
    analysis = analyze_video(compressed_path, title)

    # Extract screenshots
    log("=== Extracting screenshots ===")
    screenshots = extract_screenshots(compressed_path)

    # Step 5: Generate report
    log("=== Step 5: Generate report ===")
    report_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "report_generator.py")

    # Save analysis + screenshots + video base64 as a bundle
    bundle = {
        "title": title or "Untitled",
        "duration": duration,
        "source_url": source if is_url else "",
        "analysis": analysis,
        "screenshots": screenshots,
    }

    bundle_path = os.path.join(work_dir, "analysis_bundle.json")
    with open(bundle_path, "w", encoding="utf-8") as f:
        json.dump(bundle, f, ensure_ascii=False, indent=2)

    # Call report generator
    cmd = (
        f'python3 "{report_script}" '
        f'"{bundle_path}" '
        f'--video "{compressed_path}" '
        f'--archive-dir "{archive_dir}"'
    )
    r = run_cmd(cmd)
    log(r.stdout.strip() if r.stdout else "Report generated", "OK")

    # Output final paths
    log("=== DONE ===", "OK")
    print(json.dumps({
        "status": "success",
        "analysis_bundle": bundle_path,
        "archive_dir": archive_dir,
        "analysis_summary": {
            "overall_score": analysis.get("overall_score"),
            "summary": analysis.get("summary"),
            "top3_strengths": analysis.get("top3_strengths", []),
            "top3_improvements": analysis.get("top3_improvements", []),
        }
    }, ensure_ascii=False, indent=2))


# ── CLI ──────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="爆款视频拆解引擎")
    sub = parser.add_subparsers(dest="command", help="子命令")

    # run
    p_run = sub.add_parser("run", help="完整流水线")
    p_run.add_argument("source", help="视频URL或本地路径")
    p_run.add_argument("--title", default="", help="视频标题")
    p_run.add_argument("--archive-dir", default="./outputs/reports", help="报告归档目录")

    # download
    p_dl = sub.add_parser("download", help="仅下载")
    p_dl.add_argument("url", help="视频URL")
    p_dl.add_argument("--output", "-o", default=None, help="输出路径")

    # compress
    p_cp = sub.add_parser("compress", help="仅压缩")
    p_cp.add_argument("path", help="视频路径")
    p_cp.add_argument("--output", "-o", default=None, help="输出路径")

    # analyze
    p_an = sub.add_parser("analyze", help="仅分析（跳过下载压缩）")
    p_an.add_argument("path", help="视频路径")
    p_an.add_argument("--title", default="", help="视频标题")

    # report
    p_rp = sub.add_parser("report", help="从已有JSON生成报告")
    p_rp.add_argument("bundle_json", help="分析JSON路径")
    p_rp.add_argument("--video", required=True, help="视频路径")
    p_rp.add_argument("--archive-dir", default="./outputs/reports", help="报告归档目录")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "run":
        pipeline_run(args.source, args.title, args.archive_dir)

    elif args.command == "download":
        path = download_video(args.url, args.output)
        print(json.dumps({"status": "success", "path": path}))

    elif args.command == "compress":
        out = compress_video(args.path, args.output)
        print(json.dumps({"status": "success", "path": out, "size_mb": round(get_file_size(out) / 1024 / 1024, 1)}))

    elif args.command == "analyze":
        result = analyze_video(args.path, args.title)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "report":
        report_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "report_generator.py")
        cmd = f'python3 "{report_script}" "{args.bundle_json}" --video "{args.video}" --archive-dir "{args.archive_dir}"'
        r = run_cmd(cmd)
        print(r.stdout)


if __name__ == "__main__":
    main()
