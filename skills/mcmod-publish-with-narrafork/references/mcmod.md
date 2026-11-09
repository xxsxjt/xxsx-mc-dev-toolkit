# MC百科

百科没有公开 API，所有提交都走页面自己的 AJAX 接口。拿到登录 cookie 之后可以完全用脚本，不需要浏览器。

## 登录与凭据

本地脚本优先，所以整条链路的**唯一目标就是拿到一份能用的 cookie**。按下面四步走，任何一步拿到就回到第 1 步。

### 1. 先看手上的 cookie 还能不能用

```bash
python scripts/mcmod/submit.py docs/mcmod/mod-config.json --dry-run
```

能打印 JSON 就是有效，直接用 `submit.py`，结束。报未登录或登录态失效，就是过期了，往下走。

### 2. 让 MCP 看看浏览器里还登着没

```
goto https://center.mcmod.cn/
```

**开 `center` 而不是 `www`**：`www` 的页面状态常和登录态对不上，页头没用户名不等于没登录。`center` 登录着会自动跳转，回查地址就能确定：

```
get url
```

- 变成 `https://center.mcmod.cn/<user_id>` → 登录着
- 停在登录页 → 没登录，往下走

地址里那个数字**不是作者 ID**，别拿去搜作者；搜索框只认名字，见后文「作者」。

登录着就读 cookie：

```js
document.cookie
```

把结果写进 `.narrafork/mcmod-cookie.txt`，回第 1 步。

**别把「没登录」读成「读不到」**：未登录时 `document.cookie` 里本来就没有 `*_auth`，请求头里也没有凭证，那是状态问题；工具能不能读是另一回事。先按第 3 步登录回来再看，不要凭这一次空结果去让用户手动粘贴。

### 3. 有 `Browser` 工具：开个窗口让用户登录

launch 一个可见会话打开登录页，用交互式提问请用户在里面登录（QQ 扫码或账号密码），登完再回来确认。然后从浏览器进程读完整 cookie：

```bash
python scripts/mcmod/cookies.py dump --profile <profile目录> --out .narrafork/mcmod-cookie.txt
```

拿到回第 1 步。没有 `Browser` 工具就往下走。

### 4. 都没有：让用户自己来，二选一

用交互式提问让用户选：

**A. 只给 cookie** —— 他在百科页面按 F12，控制台执行 `copy(document.cookie)`，把结果贴给你；写进文件后回第 1 步。

**B. 整条流程都在他浏览器里跑** —— 生成控制台脚本，用户自己粘贴、填验证码、点提交：

```bash
python scripts/mcmod/console.py docs/mcmod/mod-config.json
```

把脚本复制到剪贴板（或让用户自己复制），再给添加条目页的链接 `https://www.mcmod.cn/class/add/`。

| 优点 | 限制 |
|---|---|
| 不经过本地，不用把 cookie 交出来 | 一次只能在当前页面处理，切页要重跑 |
| 页面控件用它们自己的 API 填，不会失效 | 结果只在控制台里，拿不到结构化文件 |
| 验证码由用户在页面上填，无需额外交互 | 页面改版时模板要跟着改 |

模板在 `scripts/mcmod/console/`：`module.js` 是模组条目，`item.js` 是资料条目。数据格式见脚本头部注释。

### 为什么 `document.cookie` 现在够用

实测（2026-11）：`document.cookie` 能读到 6 个，其中 **`Example_auth` 就是登录凭证，而且不是 httpOnly**。用这份 cookie 跑 `--dry-run` 能正常读出添加页的版本列表。

早前「只有 5 个、缺 httpOnly 的 `dSit_2132_auth`」已经不成立——站点 cookie 前缀换成了 `Example_`，凭证也移出了 httpOnly。哪天又不灵了，用 CDP 对比一次 `document.cookie` 与 `Storage.getCookies` 的数量就能判断。

### 账号密码登录

```
POST https://www.mcmod.cn/action/doLogin/
data={"username":"…","password":"…","remember":1,"captcha":""}
→ {"state":0} 成功
→ {"state":"logreg_password_incorrect"} 失败
```

**登录页有图形验证码**，纯脚本走不通，必须先拿到验证码。QQ 登录是 OAuth 跳转，必须人工扫码。两种情况都要用户参与。

## 提交接口

```
POST https://event.mcmod.cn/action/edit/doEdit/
Content-Type: application/x-www-form-urlencoded
data=<URL 编码的 JSON>

{"state": 0}    成功
{"state": 117}  已登录，数据有问题
{"state": 122}  未登录
```

### 编辑已有条目

改已上架的模组条目：登录后打开 `https://www.mcmod.cn/class/edit/<模组ID>/`（会跳到 `.../<模组ID>-<redo-id>/`），控制台执行

```js
JSON.stringify(getEditorData())
```

得到的整份对象就是提交体，存成文件直接喂给脚本：

```bash
python scripts/mcmod/edit.py --class-id <模组ID> --payload class-data.json
python scripts/mcmod/edit.py --class-id <模组ID> --payload class-data.json --content-file new.html
```

实测（2026-11，条目 30945）`getEditorData()` 返回五个键：

| 键 | 值 | 哪来的 |
|---|---|---|
| `action` | `class_edit` | 提交按钮 `data-type` |
| `edit-id` | 模组 ID | 提交按钮 `edit-id` |
| `class-id` | 模组 ID | — |
| `redo-id` | 编辑版本号（如 `816324`） | 编辑页地址尾段 |
| `class-data` | 22 个字段 | `getCommonFormData(jQuery('#edit-form'))` |

**`redo-id` 不能猜**：每次编辑都不一样，写死 `0` 会指错条目。手上只有裸 `class-data` 时必须给 `--redo-id`，否则脚本直接拒绝。

`--dry-run` 先看提交体。需要验证码的用户组（页面不提示「免验证码」的那种）带 `--captcha`。

`--draft` 存草稿，走 `doSave`，参数 `actionType=class_edit` + `actionID=<模组ID>` + `data=<整份>`，与页面 `editSave()` 一致。

`state` 非 0 时提交体没被消费，改完可以直接重跑。

## 封面

页面上的「上传封面」是文件输入框，裁剪确认后结果写进隐藏字段 `[data-multi-id=cover-data]`，值是 `data:image/png;base64,…`。**两条路径都能带封面**：

| 路径 | 做法 |
|---|---|
| `submit.py` | 配置里给 `coverPath`，脚本按 16:10 居中裁切、缩放到 480×300，转 data URL 写进 `class-data["cover-data"]` |
| 控制台脚本 | 同样给 `coverPath`，`console.py` 转 base64 塞进脚本，页面里注入文件输入框并自动点「更新封面」 |

**16:10 是硬要求**：百科封面只收 480×300 / 240×150 这类比例，脚本统一居中裁切再缩放，原图比例不对也不会变形。

实测（2026-11，添加页）：

```
上传 → 裁剪框打开（cover-canvas 变 data URL）→ 点 #cover-update-button
→ 隐藏字段 #class-cover[data-multi-id=cover-data] 值变成 data:image/png;base64,…（18K 字符）
```

`cover-data` 提交时用的形态（字符串还是 `{序号: 值}`）尚未实测，脚本按字符串提交；不生效就改用控制台脚本，那条是页面内注入，行为确定。

## 提交结构

```json
{
  "action": "class_add",
  "edit-id": "0",
  "class-id": "0",
  "redo-id": "0",
  "class-data": {
    "name": "主要名称", "ename": "次要名称", "sname": "简写",
    "intro": "一句话简介", "modid": "modid",
    "cfprojectid": "", "mrprojectid": "",
    "content": "<p>[ban:title_menu]</p>…",
    "category":  { "0": "1,7" },
    "platform":  { "0": "1" },
    "api":       { "0": "13" },
    "mcversion": { "13": { "0": "78" } },
    "mode-1":    { "0": "1" },
    "mode-2":    { "0": "1" },
    "status":    { "0": "1" },
    "source":    { "0": "1" },
    "tags":      "标签1,标签2",
    "keys":      "关键词1,关键词2",
    "link":   { "0": { "title": "curseforge", "custom": "", "href": "地址", "text": "" } },
    "license": { "0": { "title": "", "list": { "0": { "type": ["source"], "name": "AGPL-3.0", "link": "", "text": "" } } } },
    "author": { "link": { "0": { "select": ["owner"], "id": "<作者ID>" } }, "add": {} }
  }
}
```

类型陷阱：

| 字段 | 类型 |
|---|---|
| `api`、`platform`、`category`、`status`、`source`、`mode-*` | `{序号: 值}`，序号只是遍历下标，服务端只认值 |
| `tags`、`keys` | 英文逗号分隔的**字符串**。实测：`tagsinput('items')` 是数组，`el.value` 是 `"甲,乙,丙"`，表单序列化取 `el.value`；传 `{序号: 值}` 会把键当成标签显示 |

两者语义不同：`tags` 是「把相似模组归到一起」的通用词（科技、魔法），`keys` 只用于**别名、外号、分词**，百科写明「禁止滥用，不清楚用法请留空」。`submit.py` / `console.py` 都会清洗 `keys`：单条过宽或超过 10 条就丢掉。
| `mcversion` | `{加载器ID: {序号: 版本ID}}`，两层嵌套 |
| `license.0.list.0.type` | **数组** |
| `license.0.list.0.name` | 字符串 |
| `license.0.title` | 字符串，页面「通用」时提交空串 |
| `author.link.0.select` | **数组** |

## MC 版本怎么选

三组 MC 版本 input 一开始就全在 DOM 里，按加载器分组隐藏：

```
input[name="class-mcversion-1"]    Forge     86 个
input[name="class-mcversion-2"]    Fabric
input[name="class-mcversion-13"]   NeoForge
```

每个 input 的 `value` 是版本 ID，父元素文本是版本号。**数据收集不看可见性**，所以纯脚本置 `checked = true` 即可，不需要触发「勾选加载器后显示」那个联动。

版本 ID 每次可能变，从页面现取：

```
页面里有 var arrMCVer = $.parseJSON('[{"id":"78","name":"26.1.2"}, …]')
```

`scripts/mcmod/submit.py` 会自动解析并映射。

## 枚举

全部在 `assets/mcmod-enums.json`，键是提交值，值是页面文本。

- `platform` 1=JAVA版 2=基岩版
- `api` 1=Forge 2=Fabric 11=Quilt 13=NeoForge 5=数据包 10=其他
- `mode` 0=待考证 1=需装 2=可选 3=无效
- `status` 0=不确定 1=活跃 2=半弃坑 3=停更
- `source` 0=不显示 1=开源 2=闭源
- `category` 核心元素 9 个 `1,x`；世界生成器 5 个 + 杂项 21 个，共 26 个 `0,x`
- `role` owner/programmer/artist/sound/planner/writer/builder/contributor/mascot/other
- `licenseType` source/asset/artifact/other

## 作者

搜索接口免登录：

```
POST https://www.mcmod.cn/object/CommonSelect/
data={"key":"作者名","type":"author"}
→ {"state":0,"html":"<tr data-id=\"<作者ID>\"><td><b>主要名</b> - <i>别名1 / 别名2</i></td></tr>"}
```

```bash
python scripts/mcmod/author.py <作者名>
```

`state:109` 表示没找到。**搜索框只认名字**，用户中心 ID（`center.mcmod.cn/<ID>/`）不是作者 ID，拿它搜会返回 109。

## 提交

**百科提交需要图形验证码**，纯脚本也躲不过：

```
输入框  #edit-captcha-value
图片    https://www.mcmod.cn/frame/edit/EditCaptcha/?id=class_add_0
```

验证码每次请求都会刷新，所以必须「取图 → 用户识别 → 立刻提交」一气呵成，中间不能再去请求添加页。

```bash
# 1. 取图（同时缓存版本映射，避免提交时再请求添加页）
python scripts/mcmod/submit.py docs/mcmod/mod-config.json --captcha-url

# 2. 把 .narrafork/mcmod-captcha.png 给用户看，拿到字符

# 3. 带验证码提交
python scripts/mcmod/submit.py docs/mcmod/mod-config.json --captcha <字符>
```

没有验证码时可先 `--dry-run` 只看提交体。

配置里写页面上的中文文本，脚本按枚举表转成代码值。`state: 0` 表示成功。

**`117` 是数据错误和验证码错误共用的码**，靠返回值区分不了。拿到 117 时先核对字段，再重新取一张验证码试。

## 资料条目

资料条目是另一套页面和字段，地址 `/item/add/<模组ID>/`。链路已实测跑通。

### 分类

`data-multi-name="item-data"`、`data-multi-id="category"` 的 `a` 元素，`data-multi-value` 取值：

| 值 | 分类 |
|---|---|
| 1 | 物品/方块 |
| 2 | 群系/群落 |
| 3 | 世界/维度 |
| 4 | 生物/实体 |
| 5 | 附魔/魔咒 |
| 6 | BUFF/DEBUFF |
| 7 | 多方块结构 |
| 8 | 自然生成 |
| 9 | 绑定热键 |
| 10 | 游戏设定 |

页面上的 `(数字)` 是该项目已有的资料数量，不是分类编号。

### 字段

提交对象是 `item-data`，键名来自控件的 `data-multi-id`：

| 键 | 对应 |
|---|---|
| `name` | 主要名称 |
| `ename` | 次要名称 |
| `remark` | 改动附言 |
| `category` | 分类，`{序号: 分类值}` |
| `type` | 资料类型（`#item-type-select` 或自定义 `#item-type-custom`） |
| `regname` | 注册名 `modid:path` |
| `damage` | 最大耐久 |
| `maxstack` | 最大堆叠 |
| `oredict` | 矿物词典 |
| `metadata` | 元数据 |
| `icon-32x-data` / `icon-128x-data` | 图标 base64 |
| `cover-data` | 资料封面 |
| `content` | 正文 HTML |
| `tools` | 关联工具，可空 |

### 提交

```json
{
  "action": "item_add",
  "edit-id": "<模组ID>",
  "class-id": "<模组ID>",
  "redo-id": "0",
  "captcha": "…",
  "item-data": { "name": "…", "category": { "0": "1" }, "content": "…" }
}
```

端点与模组条目相同（`event.mcmod.cn/action/edit/doEdit/`）。验证码图片的 `id` 是 `item_add_<模组ID>`，取图 URL：

```
https://www.mcmod.cn/frame/edit/EditCaptcha/?id=item_add_<模组ID>
```

页面上的提交按钮：`#edit-submit-button`，`data-type="item_add"`、`edit-id="<模组ID>"`、`redo-id="0"`。

### 脚本支持

配置里写 `"kind": "item"` 就走资料条目，验证码 id 自动按 `item_add_<模组ID>` 取：

```bash
python scripts/mcmod/submit.py docs/mcmod/item-test.json --dry-run
python scripts/mcmod/submit.py docs/mcmod/item-test.json --captcha-url
python scripts/mcmod/submit.py docs/mcmod/item-test.json --captcha <字符>
```

配置示例：

```json
{
  "kind": "item",
  "classId": "3828",
  "name": "中文名",
  "ename": "English Name",
  "category": "物品/方块",
  "type": "道具",
  "regname": "modid:path",
  "maxstack": "64",
  "damage": "",
  "content": "<p>[ban:title_menu]</p><p>正文</p>"
}
```

`category` 写中文，脚本按 [mcmod-enums.json](../assets/mcmod-enums.json) 的 `itemCategory` 转成数字。

### 新建与再编辑

| 场景 | `edit-id` | `redo-id` |
|---|---|---|
| 新建资料 | 模组 ID | `0` |
| 修改已有资料 | 模组 ID | 资料 ID |

再编辑地址是 `/item/add/<模组ID>-<资料ID>/`。资料 ID 从审核列表的「再编辑」链接里取。

**带 `redo-id` 提交会替换原条目，不会新建第二条。** 实测：给已提交的 814471 发再编辑，审核列表仍然只有这一条，名称和内容被覆盖。

### 验证状态

2026-11 实测成功（给 ManAbove 提交了一个「绑定热键」条目）：

| 环节 | 结果 |
|---|---|
| `/item/add/<模组ID>/` 页面 | ✅ 200，含 editor 与 10 个分类 |
| 验证码图片 | ✅ 200，`image/png`，约 4KB |
| 完整数据 + 正确验证码 | ✅ **`{"state": 0, "url": "/verify.html?..."}`** |
| 条目是否真的创建 | ✅ 审核列表出现「在模组 X 中添加 Y 绑定热键」 |

**成功时返回的 `url` 是审核列表，不是条目地址。** 条目通过前，添加页上的分类计数不会变。

失败返回 `117`，数据错误和验证码错误共用这个码，靠返回值区分不了。所以拿到 117 时先核对字段，再重新取一张验证码试。

### 还没确认的

- `item-data` 里未列出的键（图标 lock/delete 标记）在什么场景下需要
- 批量提交时验证码是否每条都要重新取（大概率是，因为每次请求都刷新）

## 审核

```
自己的审核列表  https://www.mcmod.cn/verify.html?order=createtime&selfonly=1
已通过再编辑    /item/edit/<资料ID>/
待审再编辑      /item/add/<模组ID>-<资料ID>/
```

附言由用户提供。已知退回原因：

- 生物/实体没填注册名
- 表格缺标题行（首行要用 `<th>`）
- 能成套的盔甲没建「XX套装」汇总条目
- 抽象资料（套装、套具）带了图标
- 正文出现裸网址

本地源码里新增但没发布的内容不写进百科，等新版本上线再补。
