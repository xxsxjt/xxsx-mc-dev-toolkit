# CurseForge

发布的主平台。这里写令牌、版本标签、建项目、上传清单、依赖声明与状态语义。

所有请求都要走 `cfhttp` 的 `curl_cffi`（Chrome TLS 指纹），普通 HTTP 客户端会被 Cloudflare 挑战页挡下。

## 令牌

上传用 **API Token**，不是 API Key：

```
https://authors.curseforge.com/#/settings/api-tokens
```

生成后只显示一次。设进环境变量：

```powershell
setx CURSEFORGE_API_TOKEN "…"
```

脚本读环境变量，Windows 上读不到时会回退到注册表的用户环境变量（`setx` 设的值新进程未必继承）。

没有令牌时**停下来给链接等用户**，不要尝试其它途径。

## 请求必须用 curl_cffi

```python
from cfhttp import requests, BrowserOpener
```

`curl`、`urllib`、PowerShell 直连 `minecraft.curseforge.com/api/...` 一律返回 `<title>Just a moment...</title>`，因为 Cloudflare 按 TLS 指纹识别。`scripts/cf/cfhttp.py` 用 `curl_cffi` 的 `impersonate='chrome'` 解决。

首次使用：

```bash
python -m pip install --target <目录> curl_cffi
export CF_HTTP_RUNTIME=<目录>
```

## Studio API 能做什么

实测边界（2026-11）：

| 端点 | 结果 |
|---|---|
| `GET /api/game/versions` | ✅ 200 |
| `POST /api/projects/{id}/upload-file` | ✅ 可用 |
| `GET /api/projects` | ❌ 404 |
| `GET /api/projects/{id}` | ❌ 404 |
| `GET /api/me` | ❌ 404 |

**没有「按名字查项目」的接口。** 社区 API（`api.curseforge.com/v1`）要另一种 `x-api-key`，Studio 令牌调它返回 403。

## 版本标签

```bash
python scripts/cf/upload.py query curseforge
```

结果在 `curseforge/game-versions.json`。拉到的结构里：

- 每个 MC 大版本系列一个 `gameVersionTypeID`，`26.1.x` 是 `83806`，`1.21.x` 是 `77784`
- 加载器统一在 `68441`（Forge / Fabric / NeoForge / Quilt / Rift）
- Java 版本在 `2`（`Java 8` ~ `Java 25`）
- 环境在 `75208`（`Client` / `Server`）

`gameVersions` 要同时给四类：MC 版本、加载器、Java 版本、Client/Server。

**manifest 里写名称**，照抄 `game-versions.json` 的 `name` 就行——`upload.py` 发请求前自己换成整数 ID：

```
["1.20.1", "Forge", "Java 17", "Client", "Server"]
→ [9990, 7498, 8326, 9638, 9639]
```

**别手写 ID**。接口只认整数（传名称会 400：`Expected Integer but got String. Path 'gameVersions[0]'`），同名条目按版本组挑，挑不出来脚本会报错并列候选。

要手工核对某条时，按名称查它落在哪个版本组：

```bash
python - <<'EOF'
import json
data = json.load(open('curseforge/game-versions.json', encoding='utf-8'))
for name in ['1.20.1', 'Forge', 'Java 17', 'Client', 'Server']:
    print(name, [(d['id'], d['gameVersionTypeID']) for d in data if d['name'] == name])
EOF
```

`1.20.1` 在类型 `75125`（1.20.x 组）下是 `9990`，同名的 `9993`、`9994` 属于别的类型组，别选错。

## 项目创建

**建项目排在 `FormConfirm` 之后**——项目名、分类、许可证在确认表单里一并给用户过目，确认后脚本才动手。它是整条流程里唯一不可逆的动作。

CF 没有建项目的 API，只能网页填表：生成一段控制台脚本，在**已登录的作者后台**里执行。

```bash
python scripts/cf/create_project.py curseforge/cf_create_project.json
node --check curseforge/cf_create_project_fill.js
```

**默认用 browsermcp 跑，全程脚本执行，不要手填**——手填既慢又容易和脚本状态打架。MCP 连的是用户已登录的 Chrome，登录态现成：

```
goto https://authors.curseforge.com/#/projects/create
eval <curseforge/cf_create_project_fill.js 的全部内容>
console
```

脚本自己过 Choose Game、填 General / Description / License，最后点创建，并打印每个字段的 `report` 与 `projectId` / `slug`。

**跑完核验一次就够**：

- `console` 里 `report` 有没有标「未找到，需手动」或「点击后仍未勾选」的项
- `projectId` 打出来了没有、URL 有没有跳到 `/projects/<ID>/files`

两项都过就继续下一步；有异常才处理——补一次脚本，或按报告里指出的字段手动补。**不要从头手填整张表。**

执行前确认：**界面切英文、关闭浏览器翻译**，否则字段匹配不到。中途停在某一步时，处理完页面提示**再执行一次**，会从当前步骤接着走。

**没有 browsermcp** 时回落到人工粘贴：

```bash
powershell -NoProfile -Command "Get-Content -Raw -Encoding UTF8 'curseforge/cf_create_project_fill.js' | Set-Clipboard"
```

用户在 Create A Project 页面 F12 粘贴运行。

用别的浏览器自动化工具注入时（非 MCP），注意 https 页面 `fetch('http://127.0.0.1:…')` 会被私有网络访问策略拦掉（预检 501，补 `OPTIONS` 也没用）。可行通道是把脚本文本写进 `window.name`，导航到目标站后执行：

```html
<!-- loader.html：本地静态服务目录里 -->
<script>
  fetch('cf_create_project_fill.js').then(r => r.text()).then(t => {
    window.name = t;
    document.title = 'loaded ' + t.length;
  });
</script>
```

```js
// 在 authors.curseforge.com 页面执行，执行完刷新页面清掉
(0, eval)(window.name);
```

MCP 的 `eval` 直接把脚本塞进页面，不需要这一套。

**建项后拿不到 slug**：创建成功跳转的地址是 `/projects/<ID>/files`，从 URL 取会得到 `files`。slug 去作者后台项目设置页看，或问用户；公开页有 Cloudflare 人机校验，抓不到。

脚本体积的大头是图标 base64。MCP 的 `eval` 传不动时，用 `--no-icon` 出瘦脚本，图标改用 `upload` 或页面上手动传：

```bash
python scripts/cf/create_project.py curseforge/cf_create_project.json --no-icon
```

自动化工具会把跑得久的任务误判成超时（但页面里其实还在跑）。这时用单步模式，一次只推进一页，每次执行完打印当前步骤，反复执行即可：

```bash
python scripts/cf/create_project.py curseforge/cf_create_project.json --no-icon --step
```

`autoCreate` 默认 true，脚本会自己点创建按钮并读回 `projectId`/`slug`——FormConfirm 已经确认过内容，不需要再问一遍。想自己按最后一下，就在配置里把 `autoCreate` 设成 false。

**Project Pages**：脚本会在 General 页勾上对应开关；向导里没有这一项时报告里会写「请到项目设置启用」，建好后手动开一次。

**项目链接（Source / Issues / Wiki）不在建项向导里**，建完再补：

```bash
python scripts/cf/set_links.py --source https://github.com/<user>/<repo>
```

产物是 `curseforge/cf_set_links.js`，在项目设置页 `eval` 执行，`console` 看每项是否填上，最后手动点保存。字段靠文案匹配（source / issue / wiki），页面改版时会提示「没找到输入框」。

失败时跑 `scripts/cf/dom_probe.js` 抓页面结构，按实际结构改模板。

### 分类只能从页面读

CF 没有可用的分类 API：`api.curseforge.com` 那套要 `x-api-key`（`console.curseforge.com` 申请），上传令牌调它返回 403。**建项目页里下拉出来的选项才是唯一准的**。

2026-11 实读结果：

- **Class**（9 项）：Bukkit Plugins、Modpacks、Customization、Addons、Shaders、**Mods**、Resource Packs、Data Packs、Worlds。模组固定选 `Mods`
- **Main category**（Class=Mods 时 **51 项**）：完整列表在 `assets/forms/FormFull.tsx` 的 `CF_CATEGORIES`

页面改版后重抓：打开建项目页 → 选 Minecraft 进 General → 对 Class / Main category 的 `[role=combobox]` 派发 **`mousedown`**（MUI Select 只认 mousedown，`click()` 不展开）→ 读 `[role=option]` 的文本。

以前表单里写过 `Decoration` 这种页面根本没有的分类，agent 照着填，提交时才被拒——**别凭记忆补名字**。

## 上传

**构建完成之后才出清单**：它要用真实的 jar 算 sha256，而构建必须排在图标定稿之后。

清单由脚本生成，不要手写：

```bash
python scripts/cf/make_manifest.py <表单 payload.json> --out curseforge/release-manifest.json
```

它按工程实际情况挑包、算 sha256、拼 `displayName` 与 `gameVersions`：

- **装了 style skill 且符合规范**：取 `build/libs/<modid>-<mod_version>-<mc>.jar`
- **其他工程**：在 `build/libs` 里按版本号找主包，`displayName` 就是文件名去掉 `.jar`

生成结果（核对时看这几项）：

```json
{
  "files": [{
    "minecraft": "1.21.1",
    "artifact": "build/libs/examplemod-2.0.0-1.21.1.jar",
    "sha256": "…",
    "metadata": {
      "changelog": "英文块\n\n---\n\n中文块",
      "changelogType": "markdown",
      "displayName": "examplemod-2.0.0-1.21.1",
      "releaseType": "release",
      "gameVersions": ["1.21.1", "NeoForge", "Java 21", "Client", "Server"],
      "relations": { "projects": [{ "projectId": 309927, "type": "requiredDependency" }] }
    }
  }]
}
```

```bash
python scripts/cf/upload.py upload curseforge/release-manifest.json \
  --project-id <ID> --slug <slug>

# 只看线上已有哪些文件
python scripts/cf/upload.py list curseforge --project-id <ID>
```

- `displayName` = 上传的 jar 文件名去掉 `.jar`。装了 style skill 的工程里正式包是 `<modid>-<mod_version>-<mc版本>.jar`，其他工程按 `build.gradle` 的实际命名
- 只有符合 style 规范的工程才因为 `+build.` 被拒；那类工程的正式包本来就不带编号
- `artifact` 上传前校验 sha256
- 一个 JAR 只对应一组「MC 版本 + 加载器」，多个组合要拆成多条
- `relations.projects[].type` 常用 `requiredDependency`、`optionalDependency`、`incompatible`
- **`relations` 要么有内容，要么整个字段不出现**。没有依赖就别写 `"relations": {}` 或 `"projects": []`，空壳传上去会被接口当无效数据。`make_manifest.py` 只在该有内容时才加这个字段，`upload.py` 上传前也会把空壳摘掉

三层去重，命中任一层就跳过：

1. `upload-result-<版本>.json` 里已有 ID
2. 线上文件列表里 displayName 相同
3. 有 `upload-attempt-<版本>.json` 但没结果 → 拒绝重传，先核对线上

线上文件列表（免令牌）：

```
GET https://www.curseforge.com/api/v1/mods/{projectId}/files?pageIndex=0&pageSize=50
```

返回 `id`、`displayName`、`fileName`、`releaseType`、`status`。审核中的文件可能不在列表里，所以本地记录仍要看。

## 依赖

从 `build.gradle` 解析，写进 `relations.projects`：

| 写法 | 处理 |
|---|---|
| `curse.maven:<名>-<项目ID>:<文件ID>` | 取项目 ID |
| `jarJar` | 内嵌打包，玩家不用装，**不声明** |
| `localRuntime` | 只用于开发测试，**不声明** |
| `localImpl` / `implementation` | 通常 requiredDependency |
| `compileOnly` | 视情况 optionalDependency |

非 CF 坐标关联不到 projectId，只在描述里说明。

## 描述与更新说明

项目描述和每个版本的更新日志都**必须同时有英文和中文**，只有一边的内容脚本会直接拒绝：

- 英文块在上、`---`、中文块在下，不交替
- `create_project.py` 校验描述文件，`make_manifest.py` 校验每个 `changelog`，单语直接报错
- MC 版本、加载器、Java 放版本标签，不重复塞进描述
- 衍生作品两个语言块开头各写一次原作名、作者、链接、「非官方」声明
- 衍生作品加 `## Credits` / `## 鸣谢`，只写感谢与来源，不写暗示原作者背书的措辞

## 状态语义

HTTP 200 和文件 ID 只代表**上传被受理**。`Processing`、`Baking`、`Under Review` 都不是 Approved。

查状态的地址：

```
公开文件列表  https://www.curseforge.com/minecraft/mc-mods/<slug>/files
作者后台      https://authors.curseforge.com/#/projects/<projectId>/files
```

**审核中的文件不出现在公开列表里**，只能从作者后台看，所以公开列表为空不等于上传失败。

- 400 对照字段错误
- 401/403 区分权限与网络拦截
- 响应不明时先查作者后台，别重传

最终汇报文件链接、ID、目标版本、实际状态。不承诺审核耗时。
