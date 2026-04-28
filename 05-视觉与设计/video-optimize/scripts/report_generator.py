#!/usr/bin/env python3
"""
HTML可视化报告生成器 - 从分析JSON生成自包含HTML报告
用法: python3 report_generator.py <bundle.json> --video <video.mp4> --archive-dir ./outputs/reports
"""

import argparse
import base64
import hashlib
import json
import os
import re
import sys
from datetime import datetime

def log(msg):
    print(f"[REPORT] {msg}", file=sys.stderr)

def to_base64_data_url(path, mime="video/mp4"):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{b64}"

def ascii_slug(title, maxlen=40):
    """Generate ASCII-safe slug from title."""
    # Try to use title as-is if ASCII
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', title).strip('-').lower()
    if slug and len(slug) > 3:
        return slug[:maxlen]
    # Fallback: md5 hash
    return hashlib.md5(title.encode('utf-8')).hexdigest()[:12]

def format_time(seconds):
    """Convert seconds to MM:SS format."""
    if isinstance(seconds, str):
        return seconds
    m, s = divmod(int(seconds), 60)
    return f"{m}:{s:02d}"

def build_webvtt(scene_breakdown):
    """Build WebVTT metadata track from scene breakdown."""
    cues = []
    chapters = scene_breakdown.get("chapters", [])
    for ch in chapters:
        for scene in ch.get("scenes", []):
            tr = scene.get("time_range", "")
            # Parse time range like "0:00-0:15" or "00:00-00:15"
            parts = tr.split("-")
            if len(parts) == 2:
                sid = scene.get("scene_id", "")
                cues.append(f"{_vtt_time(parts[0])} --> {_vtt_time(parts[1])}\n{sid}")
    if not cues:
        return ""
    return "WEBVTT\n\n" + "\n\n".join(cues)

def _vtt_time(t):
    """Convert time string to VTT format HH:MM:SS.000"""
    t = t.strip()
    parts = t.split(":")
    if len(parts) == 2:
        m, s = parts
        return f"00:{int(m):02d}:{float(s):06.3f}"
    elif len(parts) == 3:
        h, m, s = parts
        return f"{int(h):02d}:{int(m):02d}:{float(s):06.3f}"
    return "00:00:00.000"

def score_color(score):
    """Return CSS color for a score 1-10."""
    if score >= 8: return "#4ade80"
    if score >= 6: return "#facc15"
    if score >= 4: return "#fb923c"
    return "#f87171"

def score_bar_gradient(score):
    """Return CSS gradient for score bar."""
    pct = score * 10
    return f"linear-gradient(90deg, {score_color(score)} {pct}%, #333 {pct}%)"

def risk_color(risk):
    if risk == "high": return "#f87171"
    if risk == "medium": return "#facc15"
    return "#4ade80"

def generate_html(bundle, video_data_url):
    """Generate complete HTML report."""
    analysis = bundle["analysis"]
    title = bundle.get("title", "Video Analysis")
    duration = bundle.get("duration", 0)
    screenshots = bundle.get("screenshots", [])
    scenes = analysis.get("scene_breakdown", {})
    webvtt = build_webvtt(scenes)

    # Score dimensions
    dims = ["hook", "narrative", "pacing", "visual", "text_overlay", "audio", "cta", "ending"]
    dim_labels = {
        "hook": "开头吸引力", "narrative": "叙事结构", "pacing": "节奏感",
        "visual": "视觉构图", "text_overlay": "字幕设计", "audio": "音乐音效",
        "cta": "互动引导", "ending": "结尾设计"
    }
    scores = [analysis.get(d, {}).get("score", 5) for d in dims]
    overall = analysis.get("overall_score", sum(scores)/len(scores))

    # Emotion arc data
    emo_arc = analysis.get("emotional_arc", {})
    curve_pts = emo_arc.get("curve_points", [])

    # Retention risk segments
    retention = analysis.get("retention_prediction", {})
    risk_segs = retention.get("risk_segments", [])

    # Viral formulas
    viral = analysis.get("viral_formulas", {})

    # Algorithm fitness
    algo = analysis.get("algorithm_fitness", {})

    # Learning path
    learn_path = analysis.get("learning_path", [])

    # Replicable template
    template = analysis.get("replicable_template", {})

    # Strengths and improvements
    strengths = analysis.get("top3_strengths", [])
    improvements = analysis.get("top3_improvements", [])

    def _cat_color(cat):
        colors = {"Hook":"#f87171","留存":"#facc15","节奏":"#a78bfa","情绪":"#f472b6",
                  "信任":"#4ade80","互动":"#38bdf8","视觉":"#fb923c"}
        return colors.get(cat, "#888")

    # Scene cards HTML
    scene_cards_html = ""
    all_scenes_for_vtt = []
    for ch in scenes.get("chapters", []):
        ch_name = ch.get("chapter", "")
        for sc in ch.get("scenes", []):
            sid = sc.get("scene_id", "")
            all_scenes_for_vtt.append(sc)
            techs_html = "".join(
                f'<span class="tech-tag" style="border-color:{_cat_color(t.get("category",""))}">'
                f'{t.get("name","")} <small>({t.get("category","")})</small></span>'
                for t in sc.get("techniques", [])
            )
            risk = sc.get("retention_risk", "low")
            scene_cards_html += f'''
            <div class="scene-card" data-scene-id="{sid}" data-time-range="{sc.get("time_range","")}">
              <div class="scene-header">
                <span class="scene-id">{sid}</span>
                <span class="scene-time">{sc.get("time_range","")}</span>
                <span class="risk-badge" style="background:{risk_color(risk)}">{risk}</span>
              </div>
              <div class="scene-row"><strong>画面：</strong>{sc.get("visual","")}</div>
              <div class="scene-row"><strong>音频：</strong>{sc.get("audio","")}</div>
              <div class="scene-row"><strong>台词：</strong><em>{sc.get("quote","")}</em></div>
              <div class="scene-row"><strong>情绪：</strong>{sc.get("emotion","")}
                <span class="emo-val">效价:{sc.get("emotion_valence",0)}</span>
                <span class="emo-val">唤醒:{sc.get("emotion_arousal",0)}</span>
              </div>
              {f'<div class="scene-row risk-row"><strong>⚠️ 风险：</strong>{sc.get("risk_reason","")}<br><strong>修复：</strong>{sc.get("risk_fix","")}</div>' if risk != "low" else ""}
              <div class="scene-techniques">{techs_html}</div>
            </div>'''

    # Screenshots HTML
    screenshots_html = ""
    for ss in screenshots:
        t = ss["time"]
        screenshots_html += f'''
        <div class="ss-thumb" onclick="seekVideo({t})" title="{format_time(t)}">
          <img src="data:image/jpeg;base64,{ss["base64"]}" alt="Frame at {format_time(t)}">
          <span class="ss-time">{format_time(t)}</span>
        </div>'''

    # Dimension detail cards
    dim_cards_html = ""
    for d in dims:
        data = analysis.get(d, {})
        s = data.get("score", 5)
        desc = data.get("description", "")

        extra = ""
        if d == "narrative" and data.get("timeline"):
            rows = "".join(f"<tr><td>{r.get('time','')}</td><td>{r.get('chapter','')}</td><td>{r.get('description','')}</td></tr>" for r in data["timeline"])
            extra = f'<table class="mini-table"><tr><th>时间</th><th>章节</th><th>描述</th></tr>{rows}</table>'
        if d == "visual" and data.get("effects"):
            extra = "<div class='tag-list'>" + "".join(f"<span class='tag'>{e}</span>" for e in data["effects"]) + "</div>"
        if d == "text_overlay" and data.get("highlights"):
            extra = "<div class='tag-list'>" + "".join(f"<span class='tag'>{h}</span>" for h in data["highlights"]) + "</div>"

        dim_cards_html += f'''
        <div class="dim-card">
          <div class="dim-header">
            <span class="dim-name">{dim_labels.get(d,d)}</span>
            <span class="dim-score" style="color:{score_color(s)}">{s}/10</span>
          </div>
          <div class="score-bar"><div class="score-fill" style="width:{s*10}%;background:{score_color(s)}"></div></div>
          <p class="dim-desc">{desc}</p>
          {extra}
        </div>'''

    # Platform fit cards
    platform_html = ""
    for pf in algo.get("platform_fit", []):
        ps = pf.get("score", 5)
        platform_html += f'''
        <div class="platform-card">
          <div class="platform-name">{pf.get("platform","")}</div>
          <div class="platform-score" style="color:{score_color(ps)}">{ps}/10</div>
          <p>{pf.get("reason","")}</p>
          {"<span class='rec-badge'>✓ 推荐</span>" if pf.get("recommended") else ""}
        </div>'''

    # Emotion chart data
    emo_labels = json.dumps([p.get("time","") for p in curve_pts])
    emo_valence = json.dumps([p.get("valence",0) for p in curve_pts])
    emo_arousal = json.dumps([p.get("arousal",0) for p in curve_pts])

    # Radar chart data
    radar_labels = json.dumps([dim_labels.get(d,d) for d in dims])
    radar_data = json.dumps(scores)

    # Retention risk bar
    risk_bar_html = ""
    for seg in risk_segs:
        risk_bar_html += f'''
        <div class="risk-seg" style="background:{risk_color(seg.get('risk','low'))}"
             title="{seg.get('label','')} | {seg.get('reason','')} | Fix: {seg.get('fix','')}">
          <span>{seg.get("time","")}</span>
        </div>'''

    # Viral formula cards
    sf = viral.get("script_formula", {})
    ef = viral.get("emotion_formula", {})
    af = viral.get("algorithm_formula", {})

    formula_html = f'''
    <div class="formula-grid">
      <div class="formula-card">
        <h4>📝 脚本公式</h4>
        <ol>{"".join(f"<li>{s}</li>" for s in sf.get("steps",[]))}</ol>
        <div class="fill-template"><strong>填空模板：</strong>{sf.get("fill_template","")}</div>
      </div>
      <div class="formula-card">
        <h4>💫 情绪公式</h4>
        <div class="node-flow">{"→".join(ef.get("nodes",[]))}</div>
        <ul>{"".join(f"<li>{p}</li>" for p in ef.get("key_principles",[]))}</ul>
      </div>
      <div class="formula-card">
        <h4>📊 算法公式</h4>
        <ul>{"".join(f"<li>{d}</li>" for d in af.get("drivers",[]))}</ul>
        <div class="tips">{"".join(f"<span class='tag'>{t}</span>" for t in af.get("weight_tips",[]))}</div>
      </div>
    </div>'''

    # Learning path
    learn_html = ""
    for lp in learn_path[:3]:
        learn_html += f'''
        <div class="learn-card">
          <div class="learn-rank">#{lp.get("rank",0)}</div>
          <h4>{lp.get("technique","")}</h4>
          <span class="diff-tag">{lp.get("difficulty","")}</span>
          <p>{lp.get("why","")}</p>
          <ul>{"".join(f"<li>{e}</li>" for e in lp.get("exercises",[]))}</ul>
          <small>参考：{lp.get("reference","")}</small>
        </div>'''

    # Template section
    shot_rows = ""
    for shot in template.get("shot_list", []):
        shot_rows += f"<tr><td>{shot.get('order','')}</td><td>{shot.get('duration','')}</td><td>{shot.get('shot_type','')}</td><td>{shot.get('content','')}</td></tr>"

    template_html = f'''
    <div class="template-section">
      <div class="struct-formula"><strong>结构公式：</strong>{template.get("structure","")}</div>
      {f'<table class="mini-table"><tr><th>#</th><th>时长</th><th>镜头</th><th>内容</th></tr>{shot_rows}</table>' if shot_rows else ""}
      <div class="script-tpl"><strong>文案模板：</strong><pre>{template.get("script_template","")}</pre></div>
    </div>'''

    # VTT as base64 data URL for track element
    vtt_data_url = ""
    if webvtt:
        vtt_b64 = base64.b64encode(webvtt.encode("utf-8")).decode("ascii")
        vtt_data_url = f"data:text/vtt;base64,{vtt_b64}"

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} - 爆款视频拆解报告</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#1a1a2e;color:#e0e0e0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.6;padding:20px}}
.container{{max-width:1200px;margin:0 auto}}
h1{{font-size:1.8em;margin-bottom:8px}}
h2{{font-size:1.3em;margin:32px 0 16px;padding-bottom:8px;border-bottom:1px solid #333}}
h3{{font-size:1.1em;margin:20px 0 10px}}
h4{{font-size:1em;margin:12px 0 8px}}
.card{{background:#16213e;border-radius:12px;padding:20px;margin:12px 0;box-shadow:0 4px 12px rgba(0,0,0,0.3)}}
.header-card{{text-align:center;padding:30px}}
.overall-score{{font-size:3em;font-weight:bold;margin:10px 0}}
.summary{{font-size:1.1em;color:#aaa;max-width:600px;margin:0 auto}}

/* Video + Sync Panel */
.video-panel{{display:grid;grid-template-columns:1fr 400px;gap:16px;margin:16px 0}}
@media(max-width:800px){{.video-panel{{grid-template-columns:1fr}}}}
.video-wrapper video{{width:100%;border-radius:8px;background:#000}}
.sync-panel{{max-height:500px;overflow-y:auto;padding:10px}}
.sync-panel::-webkit-scrollbar{{width:6px}}
.sync-panel::-webkit-scrollbar-thumb{{background:#444;border-radius:3px}}

/* Scene cards */
.scene-card{{background:#1a1a3e;border-radius:8px;padding:12px;margin:8px 0;border-left:3px solid #555;transition:border-color 0.3s}}
.scene-card.active{{border-left-color:#4ade80;background:#1e2548}}
.scene-header{{display:flex;gap:10px;align-items:center;margin-bottom:8px}}
.scene-id{{font-weight:bold;color:#4ade80}}
.scene-time{{color:#888;font-size:0.85em}}
.risk-badge{{font-size:0.75em;padding:2px 8px;border-radius:10px;color:#000;font-weight:bold}}
.scene-row{{font-size:0.9em;margin:4px 0}}
.risk-row{{color:#facc15;background:#332a00;padding:6px;border-radius:4px;margin-top:4px}}
.emo-val{{font-size:0.8em;color:#aaa;margin-left:8px}}
.scene-techniques{{display:flex;flex-wrap:wrap;gap:4px;margin-top:6px}}
.tech-tag{{font-size:0.75em;padding:2px 8px;border:1px solid;border-radius:10px}}

/* Screenshots timeline */
.ss-timeline{{display:flex;gap:8px;overflow-x:auto;padding:10px 0}}
.ss-thumb{{cursor:pointer;flex-shrink:0;position:relative;border-radius:6px;overflow:hidden}}
.ss-thumb img{{height:80px;display:block}}
.ss-thumb:hover{{opacity:0.8}}
.ss-time{{position:absolute;bottom:2px;right:4px;font-size:0.7em;background:rgba(0,0,0,0.7);padding:1px 4px;border-radius:3px}}

/* Dimension cards */
.dim-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}}
.dim-card{{background:#16213e;border-radius:8px;padding:16px}}
.dim-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}}
.dim-name{{font-weight:bold}}
.dim-score{{font-size:1.4em;font-weight:bold}}
.score-bar{{height:6px;background:#333;border-radius:3px;overflow:hidden}}
.score-fill{{height:100%;border-radius:3px;transition:width 0.5s}}
.dim-desc{{font-size:0.9em;color:#bbb;margin-top:8px}}

/* Charts */
.chart-container{{max-width:500px;margin:0 auto}}
.emotion-chart{{max-width:700px;margin:0 auto}}

/* Retention risk bar */
.risk-bar{{display:flex;gap:2px;margin:12px 0}}
.risk-seg{{flex:1;padding:6px 4px;border-radius:4px;font-size:0.75em;text-align:center;cursor:help;color:#000;font-weight:bold}}

/* Formula grid */
.formula-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}}
.formula-card{{background:#16213e;border-radius:8px;padding:16px}}
.formula-card h4{{margin-bottom:8px}}
.fill-template,.script-tpl{{background:#111;padding:10px;border-radius:6px;margin-top:8px;font-size:0.9em}}
.node-flow{{font-size:1.1em;color:#f472b6;margin:8px 0}}

/* Platform cards */
.platform-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px}}
.platform-card{{background:#16213e;border-radius:8px;padding:16px;text-align:center}}
.platform-name{{font-weight:bold;font-size:1.1em}}
.platform-score{{font-size:2em;font-weight:bold;margin:8px 0}}
.rec-badge{{background:#4ade80;color:#000;padding:2px 10px;border-radius:10px;font-size:0.85em}}

/* Learn cards */
.learn-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}}
.learn-card{{background:#16213e;border-radius:8px;padding:16px;position:relative}}
.learn-rank{{position:absolute;top:10px;right:14px;font-size:2em;color:#333;font-weight:bold}}
.diff-tag{{font-size:0.8em;background:#333;padding:2px 8px;border-radius:8px}}

/* Metrics dashboard */
.metrics-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:12px 0}}
@media(max-width:600px){{.metrics-grid{{grid-template-columns:repeat(2,1fr)}}}}
.metric-card{{background:#16213e;border-radius:8px;padding:16px;text-align:center}}
.metric-val{{font-size:1.6em;font-weight:bold;color:#4ade80}}
.metric-label{{font-size:0.85em;color:#888}}

/* Tags and tables */
.tag-list{{display:flex;flex-wrap:wrap;gap:4px;margin-top:6px}}
.tag{{font-size:0.8em;background:#333;padding:2px 8px;border-radius:8px}}
.mini-table{{width:100%;margin-top:8px;border-collapse:collapse;font-size:0.85em}}
.mini-table th,.mini-table td{{padding:6px 8px;border:1px solid #333;text-align:left}}
.mini-table th{{background:#222}}

/* Top 3 */
.top3{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:12px 0}}
@media(max-width:600px){{.top3{{grid-template-columns:1fr}}}}
.top3-card{{background:#16213e;border-radius:8px;padding:16px}}
.top3-card h3{{margin-bottom:10px}}
.top3-card li{{margin:6px 0;padding-left:4px}}
.top3-card.strengths li::marker{{color:#4ade80}}
.top3-card.improvements li::marker{{color:#facc15}}

/* Template section */
.struct-formula{{font-size:1.1em;margin-bottom:12px}}
pre{{background:#111;padding:12px;border-radius:6px;white-space:pre-wrap;font-size:0.9em}}
.tips{{display:flex;flex-wrap:wrap;gap:4px;margin-top:6px}}

/* Algorithm metrics */
.algo-metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}
@media(max-width:600px){{.algo-metrics{{grid-template-columns:repeat(2,1fr)}}}}
</style>
</head>
<body>
<div class="container">

<!-- Header -->
<div class="card header-card">
  <h1>🎬 {title}</h1>
  <div class="summary">{analysis.get("summary","")}</div>
  <div class="overall-score" style="color:{score_color(overall)}">{overall:.1f}</div>
  <div style="color:#888">综合评分 / 10 | 时长 {format_time(duration)}</div>
</div>

<!-- TOP 3 -->
<div class="top3">
  <div class="card top3-card strengths">
    <h3>✅ TOP 3 亮点</h3>
    <ol>{"".join(f"<li>{s}</li>" for s in strengths)}</ol>
  </div>
  <div class="card top3-card improvements">
    <h3>💡 TOP 3 改进建议</h3>
    <ol>{"".join(f"<li>{s}</li>" for s in improvements)}</ol>
  </div>
</div>

<!-- Video + Sync Panel -->
<h2>🎥 视频 + 场景同步解读</h2>
<div class="video-panel">
  <div class="video-wrapper">
    <video id="mainVideo" controls preload="metadata">
      <source src="{video_data_url}" type="video/mp4">
      {f'<track id="sceneTrack" kind="metadata" src="{vtt_data_url}" default>' if vtt_data_url else ""}
    </video>
  </div>
  <div class="sync-panel" id="syncPanel">
    {scene_cards_html}
  </div>
</div>

<!-- Screenshots Timeline -->
{f"""<h2>📸 截图时间线</h2>
<div class="ss-timeline">{screenshots_html}</div>""" if screenshots else ""}

<!-- Radar Chart -->
<h2>📊 8维度雷达图</h2>
<div class="card">
  <div class="chart-container">
    <canvas id="radarChart"></canvas>
  </div>
</div>

<!-- 8 Dimension Detail Cards -->
<h2>📋 8维度详细分析</h2>
<div class="dim-grid">
  {dim_cards_html}
</div>

<!-- Emotion Arc -->
{f"""<h2>💫 情绪弧线</h2>
<div class="card">
  <p><strong>弧线类型：</strong>{emo_arc.get("arc_type","")} — {emo_arc.get("arc_description","")}</p>
  <div class="emotion-chart"><canvas id="emotionChart"></canvas></div>
</div>""" if curve_pts else ""}

<!-- Retention Risk -->
{f"""<h2>⚠️ 留存风险热力条</h2>
<div class="card">
  <div class="metrics-grid">
    <div class="metric-card"><div class="metric-val">{retention.get("hook_rate_3s","--")}</div><div class="metric-label">3秒留存</div></div>
    <div class="metric-card"><div class="metric-val">{retention.get("retention_30s","--")}</div><div class="metric-label">30秒留存</div></div>
    <div class="metric-card"><div class="metric-val">{retention.get("midpoint_retention","--")}</div><div class="metric-label">中段留存</div></div>
    <div class="metric-card"><div class="metric-val">{retention.get("completion_rate","--")}</div><div class="metric-label">完播率</div></div>
  </div>
  <div class="risk-bar">{risk_bar_html}</div>
</div>""" if risk_segs else ""}

<!-- Viral Formulas -->
<h2>🔥 爆款公式提取</h2>
<div class="card">{formula_html}</div>

<!-- Algorithm Fitness -->
{f"""<h2>📱 算法适配度</h2>
<div class="card">
  <div class="metrics-grid">
    <div class="metric-card"><div class="metric-val">{algo.get("metrics",dict()).get("completion_rate","--")}</div><div class="metric-label">完播率</div></div>
    <div class="metric-card"><div class="metric-val">{algo.get("metrics",dict()).get("interaction_rate","--")}</div><div class="metric-label">互动率</div></div>
    <div class="metric-card"><div class="metric-val">{algo.get("metrics",dict()).get("share_rate","--")}</div><div class="metric-label">分享率</div></div>
    <div class="metric-card"><div class="metric-val">{algo.get("metrics",dict()).get("save_rate","--")}</div><div class="metric-label">收藏率</div></div>
  </div>
  <div class="platform-grid" style="margin-top:16px">{platform_html}</div>
</div>""" if algo else ""}

<!-- Learning Path -->
{f"""<h2>📚 学习路径</h2>
<div class="learn-grid">{learn_html}</div>""" if learn_html else ""}

<!-- Replicable Template -->
<h2>📋 可复制模板</h2>
<div class="card">{template_html}</div>

</div><!-- /.container -->

<script>
// Radar Chart
const radarCtx = document.getElementById('radarChart').getContext('2d');
new Chart(radarCtx, {{
  type: 'radar',
  data: {{
    labels: {radar_labels},
    datasets: [{{
      label: '评分',
      data: {radar_data},
      backgroundColor: 'rgba(74,222,128,0.2)',
      borderColor: '#4ade80',
      borderWidth: 2,
      pointBackgroundColor: '#4ade80'
    }}]
  }},
  options: {{
    scales: {{
      r: {{
        min: 0, max: 10,
        ticks: {{ stepSize: 2, color: '#888' }},
        grid: {{ color: '#333' }},
        angleLines: {{ color: '#333' }},
        pointLabels: {{ color: '#e0e0e0', font: {{ size: 12 }} }}
      }}
    }},
    plugins: {{ legend: {{ display: false }} }}
  }}
}});

// Emotion Chart
{f"""
const emoCtx = document.getElementById('emotionChart').getContext('2d');
new Chart(emoCtx, {{
  type: 'line',
  data: {{
    labels: {emo_labels},
    datasets: [
      {{
        label: '情绪效价',
        data: {emo_valence},
        borderColor: '#f472b6',
        backgroundColor: 'rgba(244,114,182,0.1)',
        yAxisID: 'y',
        tension: 0.3,
        fill: true
      }},
      {{
        label: '唤醒度',
        data: {emo_arousal},
        borderColor: '#38bdf8',
        backgroundColor: 'rgba(56,189,248,0.1)',
        yAxisID: 'y1',
        tension: 0.3,
        fill: true
      }}
    ]
  }},
  options: {{
    scales: {{
      y: {{ type: 'linear', position: 'left', min: -5, max: 5, title: {{ display: true, text: '效价', color: '#f472b6' }}, ticks: {{ color: '#888' }}, grid: {{ color: '#333' }} }},
      y1: {{ type: 'linear', position: 'right', min: 0, max: 10, title: {{ display: true, text: '唤醒度', color: '#38bdf8' }}, ticks: {{ color: '#888' }}, grid: {{ drawOnChartArea: false }} }},
      x: {{ ticks: {{ color: '#888' }}, grid: {{ color: '#333' }} }}
    }},
    plugins: {{ legend: {{ labels: {{ color: '#e0e0e0' }} }} }}
  }}
}});
""" if curve_pts else ""}

// Video sync
const video = document.getElementById('mainVideo');
const sceneCards = document.querySelectorAll('.scene-card');

function parseTimeRange(tr) {{
  const parts = tr.split('-');
  if (parts.length !== 2) return null;
  return {{ start: timeToSec(parts[0]), end: timeToSec(parts[1]) }};
}}

function timeToSec(t) {{
  const p = t.trim().split(':').map(Number);
  if (p.length === 3) return p[0]*3600 + p[1]*60 + p[2];
  if (p.length === 2) return p[0]*60 + p[1];
  return p[0] || 0;
}}

function seekVideo(t) {{
  video.currentTime = t;
  video.play();
}}

video.addEventListener('timeupdate', () => {{
  const ct = video.currentTime;
  sceneCards.forEach(card => {{
    const range = parseTimeRange(card.dataset.timeRange || '');
    if (range && ct >= range.start && ct < range.end) {{
      if (!card.classList.contains('active')) {{
        sceneCards.forEach(c => c.classList.remove('active'));
        card.classList.add('active');
        card.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
      }}
    }}
  }});
}});

// Click scene card to seek
sceneCards.forEach(card => {{
  card.addEventListener('click', () => {{
    const range = parseTimeRange(card.dataset.timeRange || '');
    if (range) seekVideo(range.start);
  }});
}});
</script>
</body>
</html>'''

    return html


def generate_lite(html):
    """Generate lite version by replacing base64 video with file reference."""
    return re.sub(
        r'data:video/mp4;base64,[A-Za-z0-9+/=]+',
        'video.mp4',
        html
    )


def generate_meta(bundle, analysis, thumb_b64=""):
    """Generate meta.json for archive index."""
    return {
        "title": bundle.get("title", ""),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "duration": bundle.get("duration", 0),
        "overall_score": analysis.get("overall_score", 0),
        "summary": analysis.get("summary", ""),
        "top3_strengths": analysis.get("top3_strengths", []),
        "thumbnail_base64": thumb_b64,
    }


def generate_index_html(archive_dir):
    """Generate/update index.html that lists all reports."""
    reports = []
    for name in sorted(os.listdir(archive_dir), reverse=True):
        meta_path = os.path.join(archive_dir, name, "meta.json")
        if os.path.isfile(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            meta["folder"] = name
            reports.append(meta)

    cards = ""
    for r in reports:
        sc = r.get("overall_score", 0)
        col = "#4ade80" if sc >= 8 else "#facc15" if sc >= 6 else "#fb923c" if sc >= 4 else "#f87171"
        thumb = f'<img src="{r["folder"]}/thumb.jpg" style="width:100%;border-radius:6px;margin-bottom:8px">' if os.path.exists(os.path.join(archive_dir, r["folder"], "thumb.jpg")) else ""
        cards += f'''
        <a href="{r["folder"]}/report.html" class="report-card" style="text-decoration:none;color:inherit">
          {thumb}
          <div class="rc-score" style="color:{col}">{sc:.1f}</div>
          <div class="rc-title">{r.get("title","Untitled")}</div>
          <div class="rc-date">{r.get("date","")}</div>
          <div class="rc-summary">{r.get("summary","")[:80]}</div>
        </a>'''

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>视频拆解报告汇总</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#1a1a2e;color:#e0e0e0;font-family:-apple-system,sans-serif;padding:24px}}
h1{{text-align:center;margin-bottom:24px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px;max-width:1200px;margin:0 auto}}
.report-card{{background:#16213e;border-radius:12px;padding:16px;transition:transform 0.2s;display:block}}
.report-card:hover{{transform:translateY(-4px)}}
.rc-score{{font-size:2em;font-weight:bold}}
.rc-title{{font-size:1.1em;font-weight:bold;margin:4px 0}}
.rc-date{{font-size:0.85em;color:#888}}
.rc-summary{{font-size:0.9em;color:#aaa;margin-top:6px}}
</style>
</head>
<body>
<h1>🎬 视频拆解报告汇总</h1>
<div class="grid">{cards}</div>
</body>
</html>'''

    index_path = os.path.join(archive_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
    log(f"Updated index: {index_path}")


def main():
    parser = argparse.ArgumentParser(description="HTML报告生成器")
    parser.add_argument("bundle_json", help="分析bundle JSON路径")
    parser.add_argument("--video", required=True, help="视频文件路径")
    parser.add_argument("--archive-dir", default="./outputs/reports", help="归档目录")
    args = parser.parse_args()

    # Load bundle
    with open(args.bundle_json, "r", encoding="utf-8") as f:
        bundle = json.load(f)

    analysis = bundle["analysis"]
    title = bundle.get("title", "Untitled")

    # Create archive directory
    date_str = datetime.now().strftime("%Y%m%d")
    slug = ascii_slug(title)
    folder_name = f"{date_str}_{slug}"
    folder_path = os.path.join(args.archive_dir, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    # Copy video
    import shutil
    video_dest = os.path.join(folder_path, "video.mp4")
    shutil.copy2(args.video, video_dest)

    # Generate video data URL for full report
    log("Encoding video for full report...")
    video_data_url = to_base64_data_url(args.video)

    # Generate HTML
    log("Generating HTML report...")
    html = generate_html(bundle, video_data_url)

    # Write full report
    report_path = os.path.join(folder_path, "report.html")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)
    log(f"Full report: {report_path}")

    # Write lite report
    lite_html = generate_lite(html)
    lite_path = os.path.join(folder_path, "report-lite.html")
    with open(lite_path, "w", encoding="utf-8") as f:
        f.write(lite_html)
    log(f"Lite report: {lite_path}")

    # Generate meta.json
    thumb_b64 = ""
    screenshots = bundle.get("screenshots", [])
    if screenshots:
        thumb_b64 = screenshots[0].get("base64", "")
    meta = generate_meta(bundle, analysis, thumb_b64)
    meta_path = os.path.join(folder_path, "meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    # Update index
    generate_index_html(args.archive_dir)

    # Output result
    print(json.dumps({
        "status": "success",
        "report": report_path,
        "report_lite": lite_path,
        "meta": meta_path,
        "folder": folder_path
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
