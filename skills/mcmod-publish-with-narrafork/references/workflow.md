# 产物与数据流

**这里只写每一步留下什么文件、下一步读什么，不重复动作描述。**怎么执行看 [SKILL.md](../SKILL.md)，整体走向看 [总流程图](flow.md)，三份文档职责不重叠。

## 产物清单

| 文件 | 谁产生 | 谁使用 | 内容 |
|---|---|---|---|
| `curseforge/project.json` | 建项目后写入，或从用户给的项目页抄 | 第 3–6 步 | `projectId`、`slug` |
| `curseforge/game-versions.json` | `upload.py query` | `make_manifest` / `upload` | 版本名、ID、`gameVersionTypeID` |
| `curseforge/release-manifest.json` | `make_manifest.py` | `upload.py` | 每个「MC 版本 × 加载器」一条 |
| `curseforge/upload-result-<版本>.json` | `upload.py` | 去重、汇报 | 文件 ID 与链接 |
| `curseforge/upload-attempt-<版本>.json` | `upload.py` | 断点保护，防重复上传 | 上传中标记 |
| `curseforge/upload-response-<版本>.txt` | `upload.py` | 排查 400 | 接口原始响应 |
| `curseforge/cf_create_project.json` | agent 按工程事实写 | `create_project.py` | 建项目表单数据 |
| `curseforge/cf_create_project_fill.js` | `create_project.py` | 浏览器执行 | 建项目控制台脚本 |
| `curseforge/cf_set_links.js` | `set_links.py` | 浏览器执行 | 补填 Source/Issues/Wiki |
| `docs/mcmod/mod-config.json` | 由表单 payload 转换 | `submit.py` / `console.py` | 百科提交配置 |
| `docs/mcmod/entries.json` | 百科提交后 | 再编辑 | 条目与资料 ID 映射 |
| `.narrafork/mcmod-cookie.txt` | `cookies.py dump` 或用户粘贴 | `submit.py` | 百科登录态 |
| `.narrafork/mcmod-mcversions.json` | `submit.py` | 提交时用（避免刷新验证码） | 版本名 → 版本 ID |
| `.narrafork/mcmod-captcha.png` / `-4x.png` | `submit.py --captcha-url` | 用户识别 | 验证码原图与放大图 |
| `.narrafork/icon-style.json` | 图标面板「保存为默认」 | `make_icon.py` | 占位图标样式 |
| `src/main/resources/logo.png` | `make_icon.py` | `./gradlew build`、建项目上传图标 | 占位图标 |
| `.narrafork/gen_ui/<名称>/` | 复制模板 + 改 `data.ts` | GenUI `render` | `App.tsx` + `data.ts` |
| `.narrafork/gen_ui/publish/payload.json` | 表单提交结果还原 | `make_manifest.py` | 用户填过的配置 |

## 数据怎么流转

```
preflight.py
   └─ 工程事实 → 填进 data.ts 的 defaults

FormBuild ──► 分支 + mod_version ──► version.py ──► gradle.properties

FormFull ──► payload.json ──┬─► make_icon.py ──► logo.png
                            └─► mod-config.json

logo.png 定稿 ──► ./gradlew build ──► build/libs/*.jar ──► make_manifest.py ──► release-manifest.json

FormConfirm ──► 用户确认 ──┬─► create_project.py ──► project.json
                          ├─► set_links.py
                          └─► upload.py ──► upload-result-*.json

console.py / submit.py ──► 百科条目 ──► entries.json
```

## 各步失败后留下什么

| 情况 | 留下的东西 | 怎么接着走 |
|---|---|---|
| 上传被拒（4xx） | `upload-response-<版本>.txt`；attempt 记录已自动清掉 | 修好后直接重传，不会被挡 |
| 上传中途中断 | 残留 `upload-attempt-<版本>.json` | 脚本会拒绝重传，先核对线上文件列表 |
| 建项目脚本停在某一步 | 页面停在当前步骤 | 处理完页面提示再执行一次，从当前步骤继续 |
| 百科验证码过期 | 无 | 重新 `--captcha-url` 取图 |
| 回填版本号失败 | 已改的分支（多分支时每改完一个就提交） | 看输出定位卡在哪个分支 |
| 构建失败 | 无新产物，`payload.json` 已经存好 | 修好后重跑 `./gradlew build`，表单不用重填 |

## 百科已有条目时改什么

不要整条重提，先对比：

| 对比项 | 有变化时怎么办 |
|---|---|
| 名称、简介、模组元素 | 走再编辑 |
| 支持版本 / 运作方式 | 更新版本组合 |
| 作者、链接、许可证 | 按实际改 |
| 正文 | 有实质改动才改 |
| 资料条目数量 | 新增物品才补条目 |

没有条目就直接新建。

## 审核链接

发布结束汇报时必须附上，不让用户自己找：

```
CurseForge 公开列表  https://www.curseforge.com/minecraft/mc-mods/<slug>/files
CurseForge 作者后台  https://authors.curseforge.com/#/projects/<projectId>/files
MC百科审核列表       https://www.mcmod.cn/verify.html?order=createtime&selfonly=1
已通过再编辑         /item/edit/<资料ID>/
待审再编辑           /item/add/<模组ID>-<资料ID>/
```

CF 的文件在审核中不会出现在公开列表，要看作者后台；百科条目在审核列表里能看到状态和退回附言。
