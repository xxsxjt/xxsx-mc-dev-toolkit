# mcmod-publish-with-narrafork

把 Minecraft 模组发布到 CurseForge，可选同步到 MC百科：体检工程、构建正式包、判断或创建 CF 项目、上传版本文件、填写百科条目与资料、处理登录与验证码、跟进审核退回。

要执行发布，直接看 [执行手册](SKILL.md)——开局跑一条体检命令，之后按输出走。这份 README 是给维护者和第一次接触的人看的。

## 入口

先跑一条命令，后面照输出走：

```bash
python scripts/preflight.py
```

| 文档 | 内容 |
|---|---|
| [SKILL.md](SKILL.md) | 执行手册：开局一条命令，然后八步走完 |
| [总流程图](references/flow.md) | 一张图看懂整体走向与三处阻塞点 |
| [产物与数据流](references/workflow.md) | 每一步留下什么文件、下一步读什么 |
| [CurseForge](references/curseforge.md) | 令牌、建项目、上传、依赖、状态语义 |
| [MC百科](references/mcmod.md) | 登录、提交接口、字段结构、审核 |
| [字段来源](references/field-sources.md) | 每个字段从哪取 |
| [踩坑记录](references/pitfalls.md) | 症状、原因、正确做法 |
| [与 zershyan-mcmod-style 同装时](references/with-mcmod-style.md) | 工程符合 style 规范时的产物、版本与资源约定 |

## 目录

```
SKILL.md
references/          流程与平台细节
assets/
  flow.html          流程图源文件，改完按文件头注释重新截图成 flow.png
  flow.png           总流程图
  forms/             四个 GenUI 表单模板，用途见其 README
  mcmod-enums.json   百科提交的枚举对照
  content-templates.md  百科正文模板
scripts/
  preflight.py       开局体检：工程事实、构建规范、凭据、下一步
  cf/                CurseForge：请求封装、上传、清单生成、建项目、补链接
  mcmod/             百科：cookie、作者查询、条目提交与编辑
  mcmod/console/     百科控制台脚本模板（没有 cookie 时的兜底）
  project/           工程侧：版本号回填、占位图标生成与样式存档（.narrafork/icon-style.json）
```

百科**优先用本地脚本**（`submit.py`，需要一份 cookie）。四步拿到 cookie，任何一步成功就回到第一步：手上有的先试 → 过期了让 MCP 读页面 cookie → MCP 没登录就开浏览器让用户登 → 都不行才让用户自己粘贴或整条在浏览器里跑。

## 表单

四个数据驱动的 GenUI 模板，只改 `data.ts`，`App.tsx` 不动。用法与字段见 [assets/forms/README.md](assets/forms/README.md)，流程约束（必须带 `wait`、缺工具怎么降级）见 SKILL.md 开局段。

```bash
mkdir -p .narrafork/gen_ui/<名称>
cp assets/forms/FormFull.tsx .narrafork/gen_ui/<名称>/App.tsx
cp assets/forms/FormFull.data.example.ts .narrafork/gen_ui/<名称>/data.ts
```

改完 `data.ts` 用 `GenUI render({path: 该目录, wait: true})` 打开。

## 依赖

第一次用时装一次，之后所有工程共用这一份：

```bash
python scripts/setup.py          # 装到 skill 目录的 .narrafork/pylibs
python scripts/setup.py --check  # 只检查缺什么
```

| 包 | 用途 |
|---|---|
| `curl_cffi` | CurseForge 请求，伪装 Chrome 的 TLS 指纹，否则过不了 Cloudflare |
| `websocket-client` | 从浏览器进程读 cookie |
| `Pillow` | 生成占位图标、处理封面裁切 |

工程自己 `.narrafork/pylibs` 里装过依赖的话优先用工程的（老工程不受影响），没有就落到 skill 那份。`CF_HTTP_RUNTIME` 仍可强制指定。

## 凭据

| 凭据 | 来源 | 存放 |
|---|---|---|
| CurseForge 令牌 | `https://authors.curseforge.com/#/settings/api-tokens` | 环境变量 `CURSEFORGE_API_TOKEN` |
| 百科 cookie | 浏览器登录后经 CDP 导出 | `.narrafork/mcmod-cookie.txt` |

两者都不进 git。`.narrafork/` 已在 `.gitignore` 里。

## 维护

- 平台改动时先更新 `references/`，再同步脚本；不要只改一处
- 枚举、接口、字段结构都标注了实测时间，失效时按文档里的方法重新取
- 未实测的能力在文档里明确标注，不写成既有保证

> Distribution note: browser-cookie extraction helpers are intentionally excluded from this public toolkit. Use the upstream skill repository for its credential-handling implementation; never commit cookie data or browser profiles here.
