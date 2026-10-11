# 把「六级听力精听」部署到网上（Render + Supabase Storage）

目标：让你不用每次开电脑跑服务，浏览器直接打开网址就能练听力。

架构（最省事、零跨域坑）：
- **Render**：托管前端 + 后端（同一个服务，同源，不需要处理跨域）
- **Supabase Storage**：存放那 830MB 的 37 个音频（免费额度 1GB，刚好装下）
- **GitHub**：存放代码（已自动忽略音频，仓库只有 ~8MB）

> 为什么不用 Vercel 当后端？Vercel 免费版跑不了这种常驻 Python 服务，硬塞要改造成 serverless，麻烦且易出跨域问题。Render 直接跑原版 server.py，最稳。

---

## 第一步：把 37 个音频上传到 Supabase（你在浏览器里点就行）

1. 打开 https://supabase.com ，登录你的账号，进入一个项目（没有就新建一个，免费）。
2. 左侧菜单 → **Storage（存储）** → 右上角 **New bucket（新建桶）**
   - 名字填：`cet-audio`
   - 勾选 **Public bucket（公共桶）**（必须勾，否则网页拉不到音频）
   - 点 Create
3. 进入 `cet-audio` 桶，点 **Upload（上传）**，把音频按下面的结构传上去：
   - 先在桶里建一个文件夹 `cet6`
   - 把你电脑上 `C:\baidunetdiskdownload\` 里的 37 个 `.mp3` 全部拖进 `cet6` 文件夹
   - 上传完，桶里应该是 `cet6/2017-12-1.mp3`、`cet6/2017-12-2.mp3` …… 共 37 个
4. 记下你的「项目 ref」：
   - 浏览器地址栏长这样 `https://supabase.com/dashboard/project/<这一段就是ref>/...`
   - 例如 `abcdefghijklmnopqrst.supabase.co` 里 `abcdefghijklmnopqrst` 就是 ref
5. 你的音频公共基础地址就是：
   ```
   https://<你的ref>.supabase.co/storage/v1/object/public/cet-audio
   ```
   把它复制下来，第三步要用。（这就是 `SUPABASE_AUDIO_BASE`）

> 嫌一个个拖麻烦？也可以用项目里的 `upload_to_supabase.py` 脚本批量传（需要你的 service_role key），详见文件内说明。但网页拖拽最直观，推荐。

---

## 第二步：把代码推到你自己的 GitHub 仓库

> 注意：本地仓库现在指向的是**原作者**的仓库，你不能往那推。要建一个**你自己的**仓库。
> 这一步需要在**你自己的电脑**上跑（因为你的 GitHub 登录态在那边，我这边的环境没有你的令牌，推不了）。

1. 打开 https://github.com → 右上角 **+** → **New repository**
   - 名字：`cet-listening`
   - 选 **Public**（私有也行，Render 都能连）
   - **不要**勾 "Add a README"（保持空仓库）
   - 点 Create repository
2. 在你**自己电脑**的终端（进入项目目录 `cet-listening`）依次执行：

```bash
# 把远程地址改成了你自己的仓库（把下面的 你的用户名 换成真实的）
git remote set-url origin https://github.com/你的用户名/cet-listening.git

# 提交这次的部署改动（音频已被 .gitignore 忽略，不会进仓库）
git add -A
git commit -m "deploy: Supabase 音频代理 + Render 配置"

# 推上去（注意分支是 main，不是 master）
git push -u origin main
```

推完之后，GitHub 上你的 `cet-listening` 仓库里就有代码了（没有那 830MB 音频，正常）。

---

## 第三步：在 Render 上部署

1. 打开 https://render.com ，用 GitHub 登录。
2. 右上角 **New** → **Web Service**
3. 连接你的 GitHub，选中 `cet-listening` 仓库
4. 配置（大部分默认即可，重点填这几项）：
   - **Name**：`cet-listening`
   - **Runtime**：`Python 3`
   - **Build Command**：`echo skip-build`（纯标准库，无需安装依赖）
   - **Start Command**：`python server.py`
   - **Instance Type**：`Free`（免费）
5. 展开 **Advanced → Environment Variables（环境变量）**，添加一条：
   - Key：`SUPABASE_AUDIO_BASE`
   - Value：第一步第 5 点那个地址，例如 `https://abcdefghijklmnopqrst.supabase.co/storage/v1/object/public/cet-audio`
   - （`PORT` 和 `ALLOW_REMOTE_ADMIN` 不用管，代码/配置已处理）
6. 点 **Create Web Service**，等它 build + deploy（几分钟）。
7. 部署完成后，Render 会给你一个网址，类似 `https://cet-listening.onrender.com`
   - 直接访问 `https://cet-listening.onrender.com/cet6/` 就能练听力了！

---

## 第四步：验证

打开 `https://你的网址/cet6/`，随便点一套 → 能播放、能看到原文高亮、能单句循环，就成功了。

如果音频播不出来，八成是这两个原因：
- Supabase 桶没勾 **Public**（回去第一步第 2 点检查）
- `SUPABASE_AUDIO_BASE` 填错（确认是 `.../public/cet-audio`，末尾不要带斜杠，也不要带文件名）

---

## 常见问题

**Q：Render 免费版会休眠吗？**
A：会。15 分钟没访问就休眠，下次打开要等几秒唤醒。个人用完全够；想一直在线就升付费档。

**Q：以后想加更多真题/换剧怎么办？**
A：把新的 mp3 传到 Supabase 对应文件夹，并确保 `tracks.json` 里有对应条目即可（tracks.json 改完要重新 git push + Render 自动重新部署）。

**Q：本地还想继续用怎么办？**
A：本地 `server.py` 不设 `SUPABASE_AUDIO_BASE` 时，自动读你机器上的 `audio/cet6/`，行为完全不变。
