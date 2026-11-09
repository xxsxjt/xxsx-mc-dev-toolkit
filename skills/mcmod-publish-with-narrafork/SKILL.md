---
name: mcmod-publish-with-narrafork
description: 把 Minecraft 模组发布到 CurseForge，可选同步到 MC百科：体检工程、构建正式包、判断或创建 CF 项目、上传版本文件、填写百科条目与资料、处理登录与验证码、跟进审核退回。用户要求发布模组或新版本、建 CurseForge 项目、更新补全百科条目与资料、处理审核退回时使用；不用于模组代码开发。
---

# 模组发布

一条流水线：CurseForge 必发，MC百科可选。信息从工程读，读不到的才问用户。

每步都写了「做什么」和「卡住怎么办」，照着做即可。

## 开局：一条命令拿到全部状态

```bash
python scripts/preflight.py
```

它一次给出工程事实、构建规范、可用凭据、已有记录，末尾列出「下一步」。**按那个顺序做，做完再跑一次，直到没有 ✗。**

三个判断到这里就定完了，后面不再分支：

| 情况 | 做法 |
|---|---|
| 构建规范「符合」 | 只上传不带 `+build.N` 的 jar；不符合就按 `build.gradle` 的实际产物命名 |
| 要出表单 | 用 `render` 带 `wait: true`；没有 GenUI 或调用失败就逐项询问 |
| preflight 里有 ✗ | 按「下一步」逐条补 |

表单的两个细节：**`show` 不支持 `wait`**，画完就能接着跑，流程里不用；没有 GenUI 时不要停，有交互式提问就按字段分组问（每次不超过 4 项），没有就用普通消息把问题列成清单——这条让 skill 不依赖 NarraFork 也能跑完。

## 第 1 步：版本

**这一步只问版本并回填，不构建**——图标要到第 4 步才可能生成，先构建出来的 jar 里就没有它。构建在第 5 步。

| preflight 结果 | 做什么 |
|---|---|
| 构建规范「符合」 | 用 `FormBuild` 问分支与 `mod_version` → 勾了回填就 `version.py` |
| 不符合 | 不用问：版本号沿用 `build.gradle` 里的值 |

```bash
git branch -a | sed 's|remotes/origin/||;s|^[* ]*||' | sort -u
```

### 符合 style 时：先问版本

用 `assets/forms/FormBuild.tsx` 出表单，让用户逐行填分支和 `mod_version`：

```bash
mkdir -p .narrafork/gen_ui/build
cp assets/forms/FormBuild.tsx .narrafork/gen_ui/build/App.tsx
cp assets/forms/FormBuild.data.example.ts .narrafork/gen_ui/build/data.ts
# 改 data.ts 的 branches / rows，然后
# GenUI render({path: '.narrafork/gen_ui/build', wait: true})
```

拿到提交结果（`JSON.parse(values.payload)`）后，勾了「回填至项目」就跑：

```bash
python scripts/project/version.py main=0.0.1 1.20.1=0.0.1 --commit
```

**多分支必须加 `--commit`**：git 不允许带着未提交的 `gradle.properties` 切分支。版本已经是目标值的分支会自动跳过，不产生空提交。

## 第 2 步：项目存不存在

```bash
cat curseforge/project.json 2>/dev/null || echo "无记录"
```

| 结果 | 做法 |
|---|---|
| 有记录 | 直接用里面的 `projectId` / `slug`，跳到第 3 步 |
| 无记录 | 问用户「这个模组在 CurseForge 上有现成项目吗？」 |
| 用户说没有 | **记成「待建」，先不动手**，项目名/分类/许可证由第 4 步表单收集，第 6 步确认后再建 |
| 用户说有 | 要项目页地址：从地址取 slug，从页面抄 Project ID，写进 `project.json` |

**不要自己去 CurseForge 搜项目**，公开页有 Cloudflare 人机校验。

建项目是唯一不可逆的动作，所以它排在第 6 步 `FormConfirm` 之后——用户确认清单时才一并授权。

## 第 3 步：版本标签

```bash
python scripts/cf/upload.py query curseforge
```

产物 `curseforge/game-versions.json`。manifest 的 `gameVersions` **写名称**（`"1.20.1"`），`upload.py` 上传前自己换成整型 ID——照抄 `name`，别编 ID，`1.21.1` 和 `1.21.11` 是两个东西。

## 第 4 步：出配置表单

一次问全，不要逐条追问：

```bash
mkdir -p .narrafork/gen_ui/publish
cp assets/forms/FormFull.tsx .narrafork/gen_ui/publish/App.tsx
cp assets/forms/FormFull.data.example.ts .narrafork/gen_ui/publish/data.ts
# 改 data.ts：defaults 填 preflight 的工程事实作为 placeholder，versions 填版本条目
# GenUI render({path: '.narrafork/gen_ui/publish', wait: true})
```

- **只改 `data.ts`，不动 `App.tsx`**（GenUI 只认这个文件名）
- 已有项目只发新版本时改用 `assets/forms/FormRelease.tsx`
- 字段说明见 [表单模板](assets/forms/README.md)

**没收到提交结果**（超时、被中断、用户关掉表单）＝还没确认：不构建、不上传、不提交百科，也不要发普通消息问一遍来代替等待。用户迟迟不提交就报告停在哪一步，不要挑默认值继续。

### 占位图标

工程没有图标时用它，样式可以在表单面板里调：

1. 出表单前先读 skill 的 `.narrafork/icon-style.json`，有内容就填进 `data.ts` 的 `iconStyle`
2. 用户在图标那行点「编辑样式」打开面板：左侧实时预览，右侧两行文本、两行排版开关、字体（Segoe UI / Arial / Calibri / Impact / Bahnschrift / Georgia / Consolas）、字号、行距、字距、对齐、全部大写、边框、导出尺寸、文字色与背景色
3. 用户点「保存为默认」会发来一条 `保存图标样式：{…}`，直接喂给脚本存档，不要手写文件：

```bash
python scripts/project/save_icon_style.py '<表单发来的整段文本>'
```

存进 skill 的 `.narrafork/icon-style.json`，下次发布其他模组直接复用；`--reset` 回到默认。
4. 提交结果里带 `cfAutoIcon` 与 `cfIconStyle`，勾着且工程确实没有图标时生成 PNG：

```bash
python scripts/project/make_icon.py <模组英文名> --out src/main/resources/logo.png
```

目标已存在时会拒绝覆盖（工程本来就有图标就不该跑这个脚本）；确认要用占位图替换才加 `--force`。

样式文件会被自动读取；要临时覆盖就加 `--font georgiab.ttf --font-size 56 --fg "#3b1f0e"` 这类参数，加 `--save-style` 则一并写回配置。多行用 `--lines "Forge|Attachment"`。

**图标必须在构建之前定稿**：第 5 步的 `./gradlew build` 会把它打进包，构建之后再生成，包里就没有它。

### 提交结果怎么还原

表单返回 `{"payload": "<JSON 字符串>"}`，还原后存成 `.narrafork/gen_ui/publish/payload.json`。

里面 `changed` **只装用户改过的字段**，没改的沿用 `data.ts` 里的默认值——把两者合并成完整配置再往下走。不整份回传是因为工具显示层会截断长内容，几千字的描述一塞进去，后面的字段就看不见了。

清单要等第 5 步构建完才出得来，`make_manifest.py` 要用真实的 jar 算 sha256。

## 第 5 步：构建，然后出清单

- **自己跑 `./gradlew build`**，绝不跑 `buildAlpha`（后者递增编号并回写属性，属开发动作）
- 构建失败就如实报告停下，不要改用 `buildAlpha` 绕过；表单结果已经落在 `payload.json` 里，修好接着跑，不用重填
- 多分支工程逐个分支构建，`mod_version` 与 `minecraft_version` 可能不一样

```bash
python scripts/cf/make_manifest.py .narrafork/gen_ui/publish/payload.json \
  --out curseforge/release-manifest.json
```

它按工程实际情况挑包、算 sha256、拼 `displayName`（= jar 文件名去掉 `.jar`）与 `gameVersions`。**不要手写 manifest**。

每个 `changelog` 必须中英双语（英文块 + `---` + 中文块），脚本会校验，只有单语直接报错。项目描述同理，`create_project.py` 也会拦。

## 第 6 步：确认，然后建项目、上传

**先过 `FormConfirm`**——它是整个流程唯一的确认点。清单里要有项目名、分类、许可证、项目是否待建、每个要上传的文件：

```bash
mkdir -p .narrafork/gen_ui/confirm
cp assets/forms/FormConfirm.tsx .narrafork/gen_ui/confirm/App.tsx
cp assets/forms/FormConfirm.data.example.ts .narrafork/gen_ui/confirm/data.ts
# 改 data.ts 后
# GenUI render({path: '.narrafork/gen_ui/confirm', wait: true})
```

用户提交后才动手，顺序固定：

**① 建项目**（仅当 `project.json` 不存在）

按 [建项目](references/curseforge.md#项目创建) 走。**全程用 MCP 执行脚本，不要手填**，跑完看 `report` 和 `projectId` 核验一次即可。

脚本会顺手勾上 Project Pages，向导里没这一项就在报告里提示。

**② 补项目链接**（向导里没有 Source / Issues / Wiki）

```bash
python scripts/cf/set_links.py --source <GitHub 地址>
```

在项目设置页 `eval` 生成的脚本，`console` 看结果，填完手动点保存。

**③ 上传**

```bash
python scripts/cf/upload.py upload curseforge/release-manifest.json \
  --project-id <ID> --slug <slug>
```

- 自动三层去重：本地结果 → 线上列表 → 遗留 attempt 记录，命中就跳过
- 上传被拒会直接打印 `errorMessage` 并清掉 attempt，修好后可以立刻重传
- 想看线上已有文件：`python scripts/cf/upload.py list curseforge --project-id <ID>`（这个端点可能被 Cloudflare 挡，失败不影响上传）

**返回文件 ID 只代表受理，不是过审。**汇报时说「已受理」，不要承诺审核耗时。

## 第 7 步：MC百科（表单里 `wiki` 为 true 才做）

看第 4 步表单结果的 `payload.wiki`：`true` 就走这段，`false` 直接跳到第 8 步。

**不要再问一遍要不要发百科**——那个开关就是用户的选择，和第 2 步问「有没有现成 CF 项目」是两回事，不要在同一轮一起问。

### 7.1 先弄到一份能用的 cookie

本地脚本优先，所以整条链路的目标就是拿到 cookie。**四步，任何一步拿到就回到表格第一行重试。**

| 步骤 | 情况 | 做法 |
|---|---|---|
| 1 | 手上有 cookie 文件 | `submit.py --dry-run` 能打印 JSON 就有效，直接提交，结束 |
| 2 | 过期了 | browsermcp 开 `center.mcmod.cn`（不是 `www`，状态对不上）：地址跳成 `center.mcmod.cn/<user_id>` 就是登录着，`eval "document.cookie"` 存进文件，回 1 |
| 3 | MCP 里也没登录 | 有 `Browser` 工具就开窗口让用户登录，`cookies.py dump` 后回 1；没有就往下 |
| 4 | 都没有 | 交互式提问二选一：**A** 用户 F12 执行 `copy(document.cookie)` 贴给你；**B** 给控制台脚本 + 添加页链接，他自己粘贴提交 |

细节见 [MC百科](references/mcmod.md#登录与凭据)。

**任何修改也一样**：都走本地脚本。**模组条目本身**用 `edit.py`，**资料条目**用 `submit.py` 带 `redo-id`。

### 7.2 有没有现成条目

问用户或看他给的项目地址。已有条目**先对比差异**再改，不要整条重提。

### 7.3 提交（要验证码）

**有 cookie 时**走 `submit.py` 本地提交：

```bash
python scripts/mcmod/submit.py docs/mcmod/mod-config.json --captcha-url
```

把 `.narrafork/mcmod-captcha.png`（同时出 4 倍放大图 `mcmod-captcha-4x.png`）给用户看，**用交互式提问索要验证码**，拿到后立刻：

```bash
python scripts/mcmod/submit.py docs/mcmod/mod-config.json --captcha <字符>
```

验证码每次请求都刷新，取图和提交之间不要再请求添加页，版本映射走缓存。

**没 cookie 时**走控制台脚本：验证码由用户直接在页面上填，不用取图也不用问。

两种方式的成功标志都是 `{"state": 0, "url": "/verify.html?..."}`——**这个 url 是审核列表，不是条目地址**。

**封面**：两条路径都给 `coverPath` 就行。`submit.py` 会按 16:10 居中裁切、缩放到 480×300 后写进隐藏字段 `cover-data`；控制台脚本则在页面里注入文件输入框并自动确认裁剪。原图比例不对也不会变形。

### 7.4 资料条目（可选）

配置写 `"kind": "item"`，验证码换成 `item_add_<模组ID>`。改已有资料带 `redo-id=<资料ID>`，会**替换**而不是新建。字段与正文见 [mcmod](references/mcmod.md#资料条目)、[正文模板](assets/content-templates.md)。

## 第 8 步：处理审核退回

用户把退回附言贴过来，按资料 ID 找到条目再改：已通过的走 `/item/edit/<资料ID>/`，待审的走 `/item/add/<模组ID>-<资料ID>/`。

改**模组条目**本身：登录后打开 `/class/edit/<模组ID>/`，控制台执行 `JSON.stringify(getEditorData())` 存成文件，再

```bash
python scripts/mcmod/edit.py --class-id <模组ID> --payload class-data.json --content-file new.html
```

整份导出里已经带了 `redo-id`，只有裸 `class-data` 才要手动给。改动前 `--dry-run` 核一遍提交体。

资料条目仍走 `submit.py` 带 `redo-id`。

常见的退回原因见 [mcmod](references/mcmod.md#审核)。审核列表链接见下一节。

## 汇报必须带三条链接

每次结束都附上，不让用户自己找：

| 渠道 | 链接 |
|---|---|
| CurseForge 公开文件列表 | `https://www.curseforge.com/minecraft/mc-mods/<slug>/files` |
| CurseForge 作者后台 | `https://authors.curseforge.com/#/projects/<projectId>/files` |
| MC百科审核列表 | `https://www.mcmod.cn/verify.html?order=createtime&selfonly=1` |

- **CurseForge**：审核中的文件不在公开列表，要从作者后台看；文件 ID 只代表受理
- **MC百科**：条目在审核列表里能看到状态和退回附言

## 什么时候停下来问

只有这几种情况停，其余自己往下走：

- preflight 里的 ✗ 补不上（令牌、依赖、cookie）
- 构建失败（如实报告失败本身，不要换 `buildAlpha` 绕过）
- 工程里读不到的四类信息：中文名、CF 分类、百科模组元素、百科作者名（能放进表单的一律放进表单问）
- 需要验证码或登录凭据
- 线上已有同名条目但内容不同
- 某个「MC 版本 × 加载器」组合找不到 JAR

**需要用户输入的一律用交互式提问**，不要发普通消息等回复。

## 参考

| 文档 | 什么时候看 |
|---|---|
| [总流程图](references/flow.md) | 想先看懂整体走向 |
| [产物与数据流](references/workflow.md) | 每一步留下什么文件、下一步读什么 |
| [CurseForge](references/curseforge.md) | 令牌、建项目、上传、依赖、版本标签、状态语义 |
| [MC百科](references/mcmod.md) | 登录、提交接口、字段结构、枚举、审核 |
| [字段来源](references/field-sources.md) | 某个字段该从哪取 |
| [踩坑记录](references/pitfalls.md) | 报错或行为不符预期时先查这里 |
| [与 zershyan-mcmod-style 同装时](references/with-mcmod-style.md) | 工程符合 style 规范时的产物、版本与资源约定 |
| [表单模板](assets/forms/README.md) | 四个 GenUI 表单的用途与数据格式 |
| [正文模板](assets/content-templates.md) | 百科资料条目的正文怎么写 |
