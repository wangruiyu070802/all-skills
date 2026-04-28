# 浏览器 Fallback 下载方案

当 yt-dlp 被反爬（412/403）或平台本身不支持 yt-dlp（小红书/抖音）时使用。

使用 `browse` skill 或 `gstack` 的浏览器能力执行以下操作。

---

## B站 (bilibili.com)

1. 打开页面（可能需两次过验证码）：
```
browser navigate <url>
```

2. 提取视频/音频流地址：
```javascript
const playinfo = window.__playinfo__.data.dash;
const videoUrl = playinfo.video.sort((a,b) => b.bandwidth - a.bandwidth)[0].baseUrl;
const audioUrl = playinfo.audio.sort((a,b) => b.bandwidth - a.bandwidth)[0].baseUrl;
```

3. 下载（必须带 Referer）：
```bash
curl -o video.m4s -H "Referer: https://www.bilibili.com" "<videoUrl>"
curl -o audio.m4s -H "Referer: https://www.bilibili.com" "<audioUrl>"
```

4. 合并：
```bash
ffmpeg -y -i video.m4s -i audio.m4s -c copy output.mp4
rm video.m4s audio.m4s
```

---

## YouTube (youtube.com)

1. 打开页面：
```
browser navigate <url>
```

2. 提取流地址：
```javascript
const playerResp = ytInitialPlayerResponse.streamingData;
// 优先 formats（音视频合一）
const combined = playerResp.formats?.sort((a,b) => (b.height||0) - (a.height||0))[0];
if (combined?.url) {
  // 直接下载
  return combined.url;
}
// 否则 adaptiveFormats（分离下载）
const video = playerResp.adaptiveFormats.filter(f => f.mimeType.startsWith('video/')).sort((a,b) => b.bitrate - a.bitrate)[0];
const audio = playerResp.adaptiveFormats.filter(f => f.mimeType.startsWith('audio/')).sort((a,b) => b.bitrate - a.bitrate)[0];
```

3. 下载 + 合并（同B站流程）

---

## 小红书 (xiaohongshu.com)

**不需要 yt-dlp，直接浏览器方案。**

1. 打开笔记页面：
```
browser navigate <url>
```

2. 提取视频地址：
```javascript
const state = window.__INITIAL_STATE__;
const noteKey = Object.keys(state.note.noteDetailMap)[0];
const note = state.note.noteDetailMap[noteKey].note;
const streams = note.video.media.stream.h264;
const masterUrl = streams[0].masterUrl;
```

3. 直接下载（CDN公开，无需认证头）：
```bash
curl -L -o output.mp4 "<masterUrl>"
```

**特点**：音视频合一 MP4，不需要 ffmpeg 合并。

---

## 抖音 (douyin.com)

**不需要 yt-dlp，直接浏览器方案。**

1. 从URL提取视频ID：
   - 标准URL: `https://www.douyin.com/video/7xxxxxxxxx` → ID = 7xxxxxxxxx
   - 短链接: 先 navigate 让它跳转，从最终URL提取

2. 在浏览器上下文中调用内部API：
```javascript
const awemeId = '<视频ID>';
const resp = await fetch(`https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id=${awemeId}&aid=6383&cookie_enabled=true`, {
  headers: { 'Referer': 'https://www.douyin.com/' }
});
const data = await resp.json();
const videoUrl = data.aweme_detail.video.play_addr.url_list[0];
```

3. 下载（需带 Referer）：
```bash
curl -L -o output.mp4 -H "Referer: https://www.douyin.com/" "<videoUrl>"
```

---

## 通用注意事项

- 下载完成后，统一命名为 `source.mp4` 放入工作目录
- 下载后继续执行压缩→分析→报告流程
- 如果 curl 下载失败（CDN 限制），尝试在浏览器中用 `URL.createObjectURL` + `a.download` 触发浏览器原生下载
