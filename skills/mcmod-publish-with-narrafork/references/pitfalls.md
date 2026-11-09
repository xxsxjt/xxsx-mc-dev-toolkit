# 踩坑记录

都是实际遇到并修过的。每条写清症状、原因、正确做法。

## 网络与凭据

### CF 请求返回 `Just a moment...`

**症状**：`curl`、PowerShell、Python `urllib` 请求 `minecraft.curseforge.com/api/...` 拿到 HTML 而不是 JSON，解析报错；换代理返回 000。

**原因**：Cloudflare 按 TLS/HTTP2 指纹识别非浏览器客户端，与令牌无关。

**做法**：只用 `curl_cffi` 的 `impersonate='chrome'`，即 `scripts/cf/cfhttp.py`。不涉及破解验证码，只改网络层特征。

### 拿 Studio 令牌查项目，返回 403

**症状**：用 `CURSEFORGE_API_TOKEN` 当 `x-api-key` 调 `api.curseforge.com/v1/mods/search`，返回 `{"errorCode":403,"errorMessage":"API Key missing or invalid"}`。

**原因**：这是两种凭据。Studio 令牌只能拉 Game Versions 和上传文件。

**做法**：要按名字查项目，得去 `console.curseforge.com` 申请 API Key。否则只能问用户或读 `curseforge/project.json`。

### CF 项目页抓不到

**症状**：`Browser` 打开项目页是 `Just a moment...`；`curl_cffi` 也 403。

**原因**：公开页面和网页内部 API 的防护比 Studio API 更严。

**做法**：不要在这个方向反复试。项目标识只能来自本地记录或用户。**但**文件列表例外：`GET https://www.curseforge.com/api/v1/mods/{id}/files` 免令牌可用。

### `setx` 设的环境变量读不到

**症状**：`setx CURSEFORGE_API_TOKEN` 之后，脚本仍报 `Missing CURSEFORGE_API_TOKEN`。

**原因**：已经运行的进程不会继承新设的环境变量。

**做法**：脚本里加了回退——环境变量读不到时从 `HKCU\Environment` 读。见 `scripts/cf/cfhttp.py` 的 `system_env()`。

### 上传到一半断了，重跑又传了一次

**症状**：线上出现两个同名文件。

**原因**：请求发出但没收到响应，本地没记下结果。

**做法**：上传前先写 `upload-attempt-<版本>.json`，成功后写 `upload-result-<版本>.json`。有 attempt 没 result 就拒绝重传，要求先核对线上。

### 把「这次没登录」当成「工具读不到」

**症状**：`eval document.cookie` 只回 5–6 项、`request` 里的 `cookie:` 也只有那几项，于是断定这套工具拿不到完整登录态，跳过浏览器直接让用户手动粘贴。

**原因**：三条依据被串成了一个结论——

- 文档写「httpOnly 读不到」，说的是 **`document.cookie` 这个接口**受限，不是工具整体受限
- 一次 `eval` 结果少，验证的只是文档那句话，不是工具的能力上限
- `request` 里没有凭证，多半是**当时页面根本没登录**（页头无用户名、`loggedIn: false`），属状态问题

把「接口限制」+「一次失败样本」当成「工具不行」，就会漏掉 `requests`、`snapshot`、CDP 这些还在手上的路子。

**做法**：**先分状态，再谈能力**。看页头有没有用户名、`document.cookie` 里有没有 `*_auth`，确认登录着再判断；仍不行就换读法（`document.cookie` → 浏览器 store → `cookies.py` 的 CDP），而不是用一个样本给工具下结论。

## CurseForge

### 有 MCP 却让人手填建项目表单

**症状**：环境里有 browsermcp，agent 还是把脚本丢给用户粘贴，或者干脆让用户一项项填。

**原因**：把 `create_project.py` 的产物当成「只能给用户粘贴的东西」，忘了 MCP 可以直接 `eval`。

**做法**：`goto` 打开 Create A Project → `eval` 整段脚本 → `console` 读 `report` 和 `projectId` 核验。只有 report 明确说某个字段没填上时，才手动补那一项，不要整表手填。

### 更新日志只写了一种语言

**症状**：`make_manifest.py` 报「更新日志必须中英双语」，或 `create_project.py` 报「项目描述必须中英双语」。

**原因**：CF 的描述和更新日志都要求英文块 + `---` + 中文块，只写中文或只写英文都会被拒。

**做法**：按「英文块、空行、`---`、空行、中文块」组织。脚本已内置校验，单语直接报错，不会放行。

### 编了一个 CF 不存在的分类

**症状**：建项目时 Main category 填了 `Decoration` 之类，页面下拉里根本选不到，提交被拒。

**原因**：凭记忆写分类名。CF 没有能用的分类 API（要 `x-api-key`，上传令牌调用返回 403），页面选项才是准的。

**做法**：只用 `FormFull` 的 `CF_CATEGORIES`——2026-11 从建项目页实读的 51 项。页面改版后按 [CurseForge](curseforge.md#分类只能从页面读) 里的方法重抓，别自己补名字。

### 版本名格式搞错

**症状**：CF 上显示成 `1.21.1-NeoForge-模组名-0.0.1`，或者显示名里带着 `+build.44`，和 jar 文件名对不上。

**原因**：按「MC-加载器-名字-版本」自己拼了；或者把 Gradle `version` 原值直接当发布版本号——那里面含 build 编号。

**做法**：`displayName` 取上传 jar 的文件名去掉 `.jar`。装了 style skill 时它就是 `<modid>-<mod_version>-<mc版本>`；`mod_version` 从 `gradle.properties` 读，不带 MC 版本和 `+build.N`。用 `make_manifest.py` 生成就不会错。

### gameVersions 传名称被拒

**症状**：上传报 400 `Expected Integer but got String. Path 'gameVersions[0]'`。

**原因**：接口要整数 ID；名称在 `game-versions.json` 里还可能有同名多条、分属不同版本组（`1.20.1` 就有三条）。

**做法**：manifest 里继续写名称，`upload.py` 发请求前自动换成 ID。不要手写 ID，也别删 `game-versions.json`——缺了它转换不了。

### JAR 路径猜错

**症状**：找不到构建产物。

**原因**：以为文件名一定是 `${mod_id}-${version}.jar`。

**做法**：看 `build.gradle` 的 `base { archivesName }`。配了 `archivesName = mod_id` 时产物前缀是 modid（`adcore-…`），没配时用工程目录名。

### 拿 alpha 包去发布

**症状**：CurseForge 上的文件名带 `+build.5` 这类后缀，或者和同版本线的其他产物对不上。

**原因**：`build/libs` 里同时躺着普通 `build` 和 `buildAlpha` 的产物，选错了。`zershyan-mcmod-style` 规范里，带 `+build.<N>` 的是 alpha 测试构建。

**做法**：装了 style skill 且构建脚本符合其规范时，**禁止上传任何文件名带 `+build.N` 的 jar**，没有例外。挑了也不许，只剩这种包的分支直接停下报告，等正式构建完成再来。候选里都没编号时按版本号取最新。

### 依赖漏声明

**症状**：CF 上玩家装了模组但缺前置报错。

**原因**：只看 `jarJar`（内嵌，不用声明），忽略了 `localImpl` 的外部依赖。

**做法**：按 `curse.maven:` 坐标提取项目 ID；`jarJar` 和 `localRuntime` 不声明。

### 没有依赖却传了空 `relations`

**症状**：上传 body 里带着 `"relations": {}` 或 `"relations": {"projects": []}`，被接口当无效数据。

**原因**：metadata 里无条件塞了这个字段，没依赖时就成了空壳。

**做法**：**要么有内容，要么字段不存在**。`make_manifest.py` 只在真有依赖时才加 `relations`，`upload.py` 上传前会再摘一次空壳——手写或历史 manifest 带下来的也能兜住。

## MC百科

### tagsinput 直接改 `value` 不生效

**症状**：`$('#class-modid').val('<你的 modid>')` 之后，页面显示空，提交时 MODID 也是空。

**原因**：`#class-modid`、`#class-cfprojectid`、`#class-mrprojectid`、`#class-tags`、`#class-keys` 是 bootstrap-tagsinput，原 input 被 `display:none`，页面不认直接赋值。

**做法**：`$(el).tagsinput('removeAll'); $(el).tagsinput('add', 值)`。

### 勾选加载器后 MC 版本列表没出现

**症状**：脚本设 `checked = true` 勾了 NeoForge，但页面上的 MC 版本复选框不显示，以为数据没进去。

**原因**：MC 版本 input **一开始就全在 DOM 里**，按加载器分组隐藏。那个「勾选后才出现」只是 UI 显示切换。

**做法**：数据收集不看可见性，直接置 `checked = true` 就能提交。实测：

```json
"mcversion": { "13": { "0": "78" }, "1": { "0": "58" } }
```

走浏览器点击路线时才需要先让它显示。

### 作者搜不到

**症状**：拿一个数字 ID 搜作者，返回 `state: 109` 找不到。

**原因**：用户中心 ID（`center.mcmod.cn/<ID>/`）不是作者 ID，两者不同。搜索框只认名字。

**做法**：用名字搜，从结果行取 `data-id`，那个才是提交用的作者 ID。

### 编辑已有条目却自己拼外层字段

**症状**：提交体里 `action` 写成 `class_add`、`redo-id` 写 `0`，条目没改或者改的不是那条。

**原因**：编辑页的提交按钮上写着 `data-type="class_edit"`、`edit-id="<模组ID>"`、`redo-id="<编辑版本号>"`。那个 `redo-id` 每次编辑都不一样（条目 30945 实测是 `816324`），套用新增流程的 `0` 指不到条目。

**做法**：别手写外层。登录后在编辑页控制台执行 `JSON.stringify(getEditorData())`，导出的整份就是提交体；只有裸 `class-data` 时用 `--redo-id` 补，值取地址 `/class/edit/<模组ID>-<redo-id>/` 的后半段。

### 拿 `www` 的页头判断登录态

**症状**：打开 `https://www.mcmod.cn/` 页头没看到用户名，判定没登录，转去让用户登录或手动粘贴 cookie。

**原因**：`www` 那边的页面状态常和登录态对不上，页头干净不代表没登录。

**做法**：改开 `https://center.mcmod.cn/`，登录着会自动跳到 `https://center.mcmod.cn/<user_id>`，看地址就能定。登着再读 `document.cookie`。地址里那个数字不是作者 ID，别拿去用。

### 拿到的 cookie 用不了

**症状**：复制了 `document.cookie`，Python 请求添加页还是未登录状态。

**原因**：站点改版前后不一样——

- **现在（2026-11 实测）**：`document.cookie` 有 6 个，其中 `Example_auth` 就是登录凭证，且不是 httpOnly。拿它跑 `submit.py --dry-run` 能正常读出添加页版本列表，**够用**。
- **早前**：登录凭证叫 `dSit_2132_auth` 且是 httpOnly，页面只给 5 个、实际有 11 个，必须走 CDP。

**做法**：先按「够用」试。不灵时用 `scripts/mcmod/cookies.py` 的 CDP 读法对比两边数量，就能判断是不是又移回 httpOnly 了。

### 登录一直失败

**症状**：`doLogin` 返回 `logreg_password_incorrect`，但密码没错。

**原因**：登录页有图形验证码，脚本传了空 `captcha`，服务端校验失败后统一返回密码错误。

**做法**：先拿验证码再登录，或走浏览器人工登录后导 cookie。

### 枚举值写错

**症状**：提交失败或字段变成默认值。

**原因**：凭印象写，没从页面取。

**做法**：全部从页面实测，见 `assets/mcmod-enums.json`。之前写错过 5 处：

| 字段 | 错的 | 对的 |
|---|---|---|
| 官方状态 | 活跃/停更/合并/重制/分割 | 不确定/活跃/半弃坑/停更 |
| 开源状态 | 开源/闭源/部分开源 | 不显示/开源/闭源 |
| 核心元素 | 缺魔改、辅助 | 9 个 |
| 作者职位 | 开发者/音乐/测试/搬运/鸣谢 | 程序/音效/建筑/贡献者/吉祥物/自定义 |
| 许可协议 | 完全没写 | 见下 |

### 许可协议字段找不到

**症状**：抓 `#license-frame` 是空的，没有 `.license-list`。

**原因**：要先点「新建协议组」（`.license-group-add`），再点「[添加]」（`.license-add-button`），结构才出现。

**做法**：两次点击之后才有 `select.license-type-select` 和 `select.license-name-select`。注意 `type` 提交时是**数组**，`name` 是字符串。

### 取了验证码又去请求页面

**症状**：取了验证码、用户也认对了，提交却返回 `117`。

**原因**：中间又请求了一次添加页。验证码每次请求都会重新生成，之前那张就作废了。

**做法**：取图和提交必须连着做，中间不碰添加页。版本映射提前缓存到 `.narrafork/mcmod-mcversions.json`，提交时读缓存。

### 以为再编辑会新建一条

**症状**：改了一条已提交的资料，审核列表里变成两条。

**原因**：提交时没带 `redo-id`，被当成新条目。

**做法**：改已有资料必须带 `redo-id=<资料ID>`，带上之后是**替换**，不会产生第二条。资料 ID 从审核列表的「再编辑」链接里取。

### 弹窗挡住操作

**症状**：点不到页面元素。

**原因**：CF 有头像裁剪框；百科有「编辑规范」弹窗。

**做法**：先关掉弹窗，或用 `stopPropagation` 处理。

## 表单 UI

### data.ts 里外置变量放错位置

**症状**：表单白屏，控制台报 `Cannot access 'DESCRIPTION' before initialization`。

**原因**：`const DESCRIPTION = "…"` 写在 `export const DATA` 之后，而 `DATA` 里引用了它。`const` 有暂时性死区，声明前访问直接抛错。

**做法**：外置常量一律写在 `DATA` 之前；长文本也可以直接内联进 `DATA`，不用变量。

### 同一行的控件对不齐

**症状**：Switch 比旁边的输入框低一截。

**原因**：`TextInput` 只有 label，`Switch` 带 description，两者高度不同，控件起点自然错开。

**做法**：同一行的字段保持相同的描述行数；Switch 用 `Input.Wrapper` 包成和输入框一样的结构，说明文字放到开关右侧。

### Badge 显示成大写

**症状**：`NeoForge 26.1.2` 显示成 `NEOFORGE 26.1.2`。

**原因**：Mantine Badge 默认 `text-transform: uppercase`。

**做法**：加 `tt="none"`。

### 折叠面板初始不展开

**症状**：`Collapse` 设 `in={true}` 但内容不显示。

**原因**：初始渲染时测不到高度。

**做法**：用条件渲染 `{open && (...)}` 代替 Collapse。

### 提交的字段莫名少了几项

**症状**：`genUI.submit` 传了 7 个字段，拿回来只剩 5 个，而且不报错。

**原因**：键名不是纯 ASCII 标识符。中文键、`"kebab-key"`、`"spaced key"` 都会被静默丢弃。

**做法**：字段名只用字母、数字、下划线。嵌套对象会被序列化成字符串，要嵌套结构就拿到后自己 `JSON.parse`。

## 流程与授权

### 重复问表单里已经填过的选项

**症状**：用户在 `FormFull` 里勾了或没勾「同时发布到 MC百科」，agent 又口头问一遍；或者在问「要不要新建 CF 项目」的同一轮里顺带问。

**原因**：把「第 7 步：MC百科（`wiki` 为 true 才做）」读成了「要先问用户发不发」。

**做法**：`payload.wiki` 就是答案，true 就走、false 就跳，不再确认。项目存在性是另一回事——那个不在表单里，需要单独问。

### 用普通消息索要用户输入

**症状**：发一条「验证码是多少」，然后结束本轮等用户主动回复。

**原因**：把需要用户输入的东西当成普通信息汇报。

**做法**：验证码、令牌、cookie、作者名这类必须由用户提供的内容，一律用交互式提问（AskUserQuestion）发起，而不是口头问完就结束。

### GenUI 调用不了就卡住

**症状**：环境没有 GenUI，或者 `render` 报错，agent 停下来问用户要不要回退、再检查一次、然后结束会话。

**原因**：把「有表单工具」当成硬前提。

**做法**：直接降级成逐项询问——有交互式提问就按字段分组问，没有就用普通消息列成清单。skill 不依赖 NarraFork 也能跑，只是慢一点。

### 表单发出去就接着往下跑

**症状**：用 `show` 画完表单，同一回合就开始构建或上传，用户还没点提交。

**原因**：`show` 不阻塞，画完就能接着跑，于是把「已经展示」当成了「已经确认」。

**做法**：用 `render({path, wait: true})` 代替 `show`，它会停在表单上直到用户提交。没收到提交结果就当没确认；用户迟迟不提交就报告停在哪一步，不要挑默认值顶上。

### 搜索关键词塞了一堆不是别名的词

**症状**：百科搜索里冒出和模组无关的描述性词汇。

**原因**：为了「利于搜索」自己加了一堆词。百科写明它只用于**别名、外号、分词**，并明确禁止滥用。

**做法**：只填用户给的，不清楚就留空。脚本会拦下过长的单条（中文按两倍宽度算，上限 24）并限制最多 10 条。

### 简写名称自己编了一个

**症状**：百科条目上的简写和社区常用对不上，或者是主名称的截断。

**原因**：从 README、源码或搜索结果里凑一个「看着像缩写」的词填进去。百科要求它**已在社区频繁使用或由作者提供**，不是随便缩一下就行。

**做法**：只能问用户，没给就留空。`submit.py` / `console.py` 会拦下含非字母数字符号、与主/次名称相同、或超过 16 字符的值。

### 次要名称跟着英文名一起填了

**症状**：百科提交后弹「主要名称与次要名称重复」之类的警告。

**原因**：主要名称本身就是英文，次要名称又填了同一个英文名。

**做法**：主要名称没有中文时，次要名称必须留空。`submit.py` 和 `console.py` 都做了判断（`name` 里没有中文就强制清空 `ename`），填 `data.ts` 时也按这条来。

### 百科标签变成了数字

**症状**：条目提交后，模组标签显示成 `1`、`2` 这种数字。

**原因**：`tags` / `keys` 传了 `{0: "标签"}` 这种多值对象，页面把对象的**键**当成了标签值。它们和 `category`、`platform` 不是同一类字段——后者才是 `{序号: 值}`。

**做法**：传**英文逗号分隔的字符串**，`submit.py` 的 `join_field` 负责转换。实测（添加页）：`tagsinput('items')` 是数组，`el.value` 就是 `"标签甲,标签乙,标签丙"`，表单序列化取的是 `el.value`。

### heredoc 里内联 Python 转义被吞

**症状**：`python - <<'PYEOF'` 里处理含反引号或反斜杠的文本，报 `SyntaxError: unterminated string literal`。

**原因**：多层 shell 与 heredoc 的转义规则叠加，反斜杠在传递过程中被吃掉。

**做法**：把脚本落地成 `.py` 文件再执行。非要在 heredoc 里写，就用 `chr(92)` 表示反斜杠、`chr(96)` 表示反引号。

### 表单返回的 payload 被截断

**症状**：拿到的 payload 到某个字段就断了，后面的百科字段和 `versions` 全都不在。

**原因**：工具显示层对长内容会截断，几千字的 `cfDescription` 足以把后面的内容挤掉。

**做法**：FormFull 只回传用户改过的字段（`changed`），其余从 `data.ts` 补。拿到 payload 先落盘再核对字段是否齐全；缺了就去查 `data.ts`，**不要凭默认值猜用户填了什么**。

### 表单返回值到手就变形

**症状**：`render` 回来的 `versions` 是 `["{\"modVersion\":…}"]` 这样的字符串数组；或者某个字段整条不见了。

**原因**：`genUI.submit` 不是原样传递——非 ASCII 的 key 会被静默丢弃，对象和数组里的对象会被转成 JSON 字符串。长度本身不截断，几 KB 的字符串能完整回来。

**做法**：模板里一律 `submit({ payload: JSON.stringify(数据) }, 消息)`，agent 侧 `JSON.parse(values.payload)` 还原。写新表单时不要直接提交嵌套结构。

### 跨域调接口被拦

**症状**：GenUI 表单里 `fetch('https://www.mcmod.cn/object/CommonSelect/')` 失败。

**原因**：响应头 `access-control-allow-origin: https://www.mcmod.cn`，只放行自家域名。

**做法**：浏览器端调不了。要么先用脚本查好写进 `data.ts`，要么走 Python。

### 本地端口收不到 cookie

**症状**：部署环境下让用户访问 `127.0.0.1:端口`，浏览器报 `ERR_CONNECTION_REFUSED`。

**原因**：NarraFork 跑在服务器上，`127.0.0.1` 指向服务器，用户的浏览器在另一台机器。

**做法**：放弃本地端口方案，用 CDP 从浏览器进程读。

### 回填时第一个分支没改动就中断

**症状**：多分支回填，第一个分支的 `mod_version` 已经等于目标值，脚本在 `git commit` 处报「nothing to commit」并退出，后面几个分支一个没处理。

**原因**：内容没变也照样执行 `git add` + `git commit`，git 直接报错。

**做法**：`version.py` 现在会先比对文本，相同就跳过该分支并继续。自己写批量改文件的脚本时也要注意：**先判断有没有实际改动，再去提交**。

### 没过确认表单就建项目

**症状**：用户说「发布一下」，脚本直接把项目建了，项目名、分类、许可证都是猜的。

**原因**：跳过了 `FormConfirm`。建项目是整条流程唯一不可逆的动作。

**做法**：项目信息由 `FormFull` 收集，`FormConfirm` 里摆出来让用户确认，提交后才建。表单没提交就不要动手——它本身就是确认环节，不用再单独问一遍。

### 上传成功就汇报「已发布」

**症状**：跟用户说发布成功，实际还在审核。

**原因**：把 HTTP 200 和文件 ID 当成过审。

**做法**：只说「上传已受理」，附文件链接和 ID，不承诺审核耗时。
