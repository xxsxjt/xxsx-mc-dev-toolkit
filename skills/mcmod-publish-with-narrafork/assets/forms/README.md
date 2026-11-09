# GenUI 表单模板

四个数据驱动的表单，共用同一套用法：复制 `.tsx` 和对应的 `.data.example.ts` 到 `.narrafork/gen_ui/<名称>/`，把后者改名成 `data.ts`，只改数据，然后 `GenUI render({path: 该目录, wait: true})`。

```bash
mkdir -p .narrafork/gen_ui/<名称>
cp assets/forms/FormFull.tsx .narrafork/gen_ui/<名称>/App.tsx
cp assets/forms/FormFull.data.example.ts .narrafork/gen_ui/<名称>/data.ts
```

**不要把 `App.tsx` 改名成别的** —— GenUI 只认这个文件名。

## 有哪几个

| 文件 | 用途 | 何时用 |
|---|---|---|
| `FormBuild.tsx` | 逐行填「分支 + 版本号」，可选回填 | 装了 `zershyan-mcmod-style`，发布流程的**第一步**（只回填版本，不构建） |
| `FormFull.tsx` | CurseForge 与百科的全部字段 | 第一次发布 |
| `FormRelease.tsx` | 只填 JAR、版本号、更新说明 | 已有项目发新版本 |
| `FormConfirm.tsx` | 把将要上传/提交的内容整块摆出来确认 | 上传或提交前的最后一道门 |

`FormConfirm` 依赖前三个的产出，不单独使用。

## 各表单的数据

文件名的 `.data.example.ts` 后缀对应各自的 `data.ts`。

### FormBuild.data.example.ts

| 字段 | 内容 |
|---|---|
| `projectName` | 显示在标题 |
| `branches` | 分支候选（Autocomplete，可自由输入） |
| `rows` | 初始行，每行 `{ branch, version }` |
| `writeBack` | 默认是否勾选「回填至项目」 |
| `hints` | 覆盖默认提示文案 |

提交结果：`JSON.parse(values.payload)` 得到 `{ rows: [{branch, version}], writeBack }`。

勾了回填就把各行写进对应分支的 `gradle.properties`：

```bash
python scripts/project/version.py master=0.0.1 1.21.1=1.0.0
```

脚本会检查工作区干净、逐分支改完回到原分支，**只改文件不提交**。

构建不在这里做：等 `FormFull` 的图标定稿之后，agent 再逐分支跑 `./gradlew build`，用产出的正式包继续。反过来先构建，包里就不会有后来生成的图标。

**只跑 `build`，不跑 `buildAlpha`**：前者沿用已记录编号、不改工程状态；后者会递增 `mod_build_number` 并回写 `gradle.properties`，属于开发动作。构建失败如实报告，不要改用 `buildAlpha` 绕过。

产出的 jar **禁止使用文件名带 `+build.N` 的**，那类属于测试构建。

### FormFull.data.example.ts

见文件内注释。核心是 `defaults`（各字段的 placeholder，即调研值）和 `versions` / `authors` / `entries` / `dependencies`。

图标那一行右侧有「没有就自动生成」勾选框和「编辑样式」按钮。面板里左侧是实时预览，右侧可改：两行文本、两行排版开关、字体、字号、行距、字距、对齐、全部大写、边框、导出尺寸（128/256/400/512）、文字色与背景色。

预览用 DOM + CSS 排版（flex 垂直居中、`lineHeight` 控行距、`letterSpacing` 控字距），和最终 PNG 的排版参数一一对应。

提交结果里是 `cfAutoIcon` 与 `cfIconStyle`；点「保存为默认」会把样式以消息发给 agent，agent 用 `scripts/project/save_icon_style.py` 存进 skill 的 `.narrafork/icon-style.json`，下次换模组直接复用。生成用 `scripts/project/make_icon.py`。图标要在出清单前定稿——构建会把它打进包。

`versions[].modVersion` 填 `gradle.properties` 里的 `mod_version`（如 `0.0.1`），**不要填 Gradle `version`**，也不带 MC 版本与 `+build.N`。发布时的显示名由 `make_manifest.py` 按 jar 文件名生成。

提交结果里 `changed` 只装用户改过的字段，其余沿用 `defaults` 的值——工具显示层会截断长内容，整份回传会让后面的字段消失。

`cfProjectPages` 控制建项时是否勾上 Project Pages；`cfSourceUrl` 由建项后的 `set_links.py` 填进项目设置，向导里没有这一项。

### FormRelease.data.example.ts

见文件内注释。核心是 `project`、`released`（已发布摘要，`version` 填线上 displayName）、`versions`（待发布，`modVersion` 同样填 `mod_version`）。

### FormConfirm.data.example.ts

见文件内注释。核心是 `project`、`releases`（每个「MC 版本 × 加载器」一条，`displayName` 就是该条 `artifact` 文件名去掉 `.jar`）、`wiki`（不发百科时整段删掉）、`warnings`。

## 公共约定

- **优先用 GenUI 生成**：没有这个工具或调用失败时不要停，改成逐项询问（有提问工具就按字段分组问，没有就用普通消息列清单）
- **外置的常量写在 `DATA` 之前**：`const DESCRIPTION = "…"` 放在 `export const DATA` 后面、又被 `DATA` 引用，会触发 TDZ 错误（`Cannot access 'DESCRIPTION' before initialization`），表单直接白屏
- **必须用 `render` 带 `wait`**：它会停在表单上直到用户点提交，`genUI.submit` 的结果直接回传。`show` 只画界面、不阻塞，流程里不要用；没收到提交结果不要自己继续
- **提交统一走 `payload`**：模板里写 `genUI.submit({ payload: JSON.stringify(数据) }, 消息)`，agent 侧 `JSON.parse(values.payload)` 还原。直接提交嵌套结构会变形——非 ASCII 的 key 会被静默丢弃，对象和数组里的对象会被转成 JSON 字符串
- **提交字段名只用 ASCII 字母、数字、下划线**：中文键、带连字符或空格的键会被 `submit` 静默丢掉，不报错；嵌套对象会被序列化成字符串，要嵌套就在拿到后自己 `JSON.parse`
- 所有调研值放 **placeholder**（灰色提示），用户留空就按提示值执行
- **枚举类字段要实选**，否则用户看不出会提交什么
- 同一行的字段保持相同的描述行数，否则控件对不齐
- 文件选择用 `FileButton`，沙箱里只能拿到文件名
