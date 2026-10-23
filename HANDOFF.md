# 交接文档 — CET 六级听力精听 Web App

> 给接手的 AI 看：把背景、现状、待办、账号、坑都写清楚了，照着做即可，不用从头摸索。

## 1. 这是什么
一个**纯前端 + Python 标准库**的六级听力精听网页应用。用户（年妤）用来练六级听力，要求**部署到公网、不用每次开自己电脑**。
- 前端：静态 HTML/JS，播放器 + 原文/翻译/倍速。
- 后端：`server.py`，仅用 Python 标准库（`http.server` 改造），零第三方依赖。
- 音频托管：**Supabase Storage 公共桶**（不进 git、不走 Render 流量，靠 302 重定向）。
- 部署：**Render Web Service**（Free 套餐）。

## 2. 在哪里
- 本地项目：`C:\Users\Siyuanl\WorkBuddy\2026-09-27-11-06-37\cet-listening\`
- GitHub 仓库（公开）：`https://github.com/Suisuimai/cet-listening` 分支 `main`
- **线上地址（已上线）**：`https://cet-listening.onrender.com`
- Supabase 项目 ref：`vuidgbmkzlnzzmrqrosf`，公共桶 `cet-audio`，音频在 `cet6/` 文件夹

## 3. 当前状态（截至 2026-10-23）
- ✅ 网站已上线，首页可访问，播放器正常载入。
- ✅ 36/37 套音频已在 Supabase，能正常播放。
- ⚠️ **`2024-12-1.mp3` 在 Supabase 上不存在 → 这一套没声音**。本地 `audio/cet6/2024-12-1.mp3` 有这个 70MB 文件，**但用户已明确决定暂不处理**（不补传），接手后无需为此动作。
- ✅ 部署配置齐全：`server.py` / `Procfile` / `render.yaml` / `DEPLOY.md` / `.env.example` / `upload_to_supabase.py`。

## 4. 音频是怎么走的（重要）
`server.py` 里：收到 `/audio/cet6/2017-12-1.mp3` 请求 → 302 重定向到
`{SUPABASE_AUDIO_BASE}/cet6/2017-12-1.mp3`。
- 已设 `SUPABASE_AUDIO_BASE = https://vuidgbmkzlnzzmrqrosf.supabase.co/storage/v1/object/public/cet-audio`
- 公共桶，直链可匿名访问（已验证 `2017-12-1.mp3` 返回 HTTP 200 audio/mpeg）。
- 文件名必须匹配 `tracks.json` 里的 id，格式 `YYYY-M-D.mp3`（如 `2017-12-1.mp3`，注意月份/日期无前导零）。

## 5. 待办（接手后优先做）
1. **（已关闭）`2024-12-1.mp3` 不补传** —— 用户明确决定暂不处理，不要为此动作。其余 36 套音频均正常。
2. 若网站需改动并重新部署：改完 `git push` 到 `main`，Render 会自动重新部署（不用手动操作）。

## 6. 部署到 Render 的要点（若需重建）
- 连 GitHub 仓库 `Suisuimai/cet-listening`，分支 `main`。
- `render.yaml` **已就绪**（branch: main / python3 / Free / start `python server.py` / 健康检查 `/cet6/` / `ALLOW_REMOTE_ADMIN=0`）。
- **手动建服务时务必改的默认值**：
  - Build Command：`echo skip-build`（项目无 requirements.txt，默认 `pip install -r requirements.txt` 会报错）
  - Start Command：`python server.py`
  - 套餐：选 **$0/month (Free)**，别用默认的 $7
  - 环境变量补一条：`SUPABASE_AUDIO_BASE = https://vuidgbmkzlnzzmrqrosf.supabase.co/storage/v1/object/public/cet-audio`
  - `PORT` 不用填（Render 自动注入，server.py 会读）。
- 管理页安全：server.py 默认只允许本机（127.x / ::1）访问 `/api/admin/*`，公网不会暴露。

## 7. 本地跑起来
```bash
cd cet-listening
python server.py          # 监听 $PORT 或默认 5173
# 浏览器开 http://localhost:5173/cet6/
```
（本地有 `audio/cet6/*.mp3` 时可直接放；部署环境靠 Supabase 重定向。）

## 8. 需要的账号（如要改动基础设施）
- **GitHub**：`Suisuimai`（仓库已建好，公开）。
- **Supabase**：项目 `vuidgbmkzlnzzmrqrosf`，公共桶 `cet-audio`。上传要用 Service Role Key（在 Project Settings → API 里）。
- **Render**：Web Service `cet-listening` 已建好并上线。

## 9. 踩过的坑（别再踩）
- 沙箱/代理环境里 `gh` 连不上 GitHub → 设 `HTTPS_PROXY=http://127.0.0.1:7897`（用户 VPN 端口）；`gh auth login` 写不进 `~/.config/gh` → 用 `GH_CONFIG_DIR` 指向工作区。详见用户级 skill `gh-proxy-login`。
- `git push` 报 `did not receive expected object` → 本地 `.git` 对象库不完整（从原作者仓库 clone 来的），重建仓库解决。
- 沙箱自带透明代理，curl 直连外部 HTTPS 会 untrusted root，**验证外部站点用 WebFetch 而非 curl**。

---
接手 AI 注：本项目已稳定运行，无实质待办（补传 mp3 已被用户关闭）。其余都是“如需改动才动”的基础设施。
