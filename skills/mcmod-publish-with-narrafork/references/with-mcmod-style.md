# 与 zershyan-mcmod-style 同装时

> **本文只适用于同时满足以下两个条件的情况：**
>
> 1. 装了 `zershyan-mcmod-style` skill
> 2. 工程的构建脚本**基本符合**该 skill 的规范 —— `buildAlpha` 任务、`<mod_version>-<mc>+build.<N>` 的版本拼法、`finalizeArtifacts` 任务，三项都要对上
>
> **任一条件不满足，本文全部条款都不适用**，按 [字段来源](field-sources.md) 的通用规则处理。不要拿本文的单条规则去套不符合规范的工程。

工程通常同时装了两套 skill：`zershyan-mcmod-style` 管开发和构建，本 skill 管发布。两者对**产物命名**和**资源位置**有约定，发布时必须按工程的实际情况来，不能套用通用假设。

## 先确认这两个条件

```bash
# 条件一：skill 装了没
ls ~/.agents/skills/zershyan-mcmod-style/ 2>/dev/null && echo 已安装

# 条件二：工程是否符合规范
grep -cE "buildAlpha|finalizeArtifacts" build.gradle
grep -E "^version =|baseVersion" build.gradle
```

条件一有输出、条件二里 `buildAlpha` 与 `finalizeArtifacts` 都在、`version` 由 `<mod_version>-<minecraft_version>+build.<N>` 拼成 —— 三条都对上才继续往下读。

任何一条对不上，就按 [字段来源](field-sources.md) 的通用规则处理，产物选择以 `build.gradle` 的实际命名为准。

## 发布前先问版本和分支

用户说要上传或发布时，**第一步不是读产物，是问清楚这次发什么**：

```bash
git branch -a | sed 's|remotes/origin/||;s|^[* ]*||' | sort -u
```

用 [FormBuild](../assets/forms/README.md) 出表单，逐行收集分支与版本：

| 项 | 说明 |
|---|---|
| `mod_version` | 只写模组版本，不带 MC 版本和 build 编号 |
| 要发布的分支 | 多选，每个分支单独构建、单独上传 |

**构建由 agent 触发**，但要分清两个任务的差别：

| 任务 | 能否由 agent 跑 | 原因 |
|---|---|---|
| `./gradlew build` | ✅ 可以，默认这么做 | 沿用已记录编号，不改 `gradle.properties` |
| `./gradlew buildAlpha` | ❌ **禁止** | 递增 `mod_build_number` 并回写属性，属开发动作 |

发布流程里只跑 `build`。构建失败就如实报告并停下，不要改用 `buildAlpha` 换个路子绕过。

勾了「回填至项目」时，第 1 步先执行 `python scripts/project/version.py <branch>=<version> ...`，构建留到第 5 步——那时图标已定稿，才会被打进包。

## 产物：禁止使用带构建编号的 jar

`versioning.md` 规定两种构建：

| 构建 | 最终 jar 名 | 性质 |
|---|---|---|
| `build` | `examplemod-0.0.1-1.21.1.jar` | 正式包，**只有这种能上传** |
| `buildAlpha` | `examplemod-0.0.1-1.21.1+build.5.jar` | 带编号的测试构建，**禁止上传** |

**任何文件名带 `+build.N` 的 jar 一律不允许上传**，没有例外。

- 挑包时直接跳过带编号的
- 某个分支只有带编号的包 → 那个分支还没跑过正式构建，停下来报告，等构建完成再来
- `build/libs/obfuscate/`、`build/libs/origin/` 是中间产物，同样不碰

如何确认工程符合这套规范：`build.gradle` 里有 `buildAlpha` 任务、`version` 由 `<mod_version>-<minecraft_version>+build.<N>` 拼成、有 `finalizeArtifacts`。三者对上才适用本节。

包内元数据两种构建都带编号，但对外显示名和最终 jar 名都不带。

## 版本号

三个来源拼成完整版本，各自职责不同：

| 来源 | 内容 |
|---|---|
| `mod_version` | 模组自身版本，新工程从 `0.0.1` 起步，之后由人按发布计划改 |
| `minecraft_version` | 目标 MC 版本，单独维护 |
| `mod_build_number` | 构建编号，由 `buildAlpha` 递增并回写 |

Gradle 的 `version` 是 `<mod_version>-<minecraft_version>+build.<N>`，例如 `0.0.1-1.21.1+build.5`。

`mod_version` 里**不写 MC 版本**，那由 `minecraft_version` 负责。`0.0.1` 只是新建工程时的初始值，不是固定值。

表单里填的 mod 版本是 `mod_version`（`0.0.1`），不是 Gradle `version`。发布时的 `displayName` 拼成 `<modid>-<mod_version>-<mc版本>`（`examplemod-0.0.1-1.21.1`），与正式 jar 文件名一致，不带 `+build.N`。

## 语言文件

Datagen 输出在 `src/generated/resources/assets/<modid>/lang/`，语言由 `<ModId>Lang` 基类聚合，注册项名称在 `RegistryLang`。百科的名称、英文名都从这里取。

改动过的语言要先跑：

```bash
./gradlew runData
```

再读文件，不要读旧的生成结果。

## 构建命令

工程默认用 `buildAlpha`（会递增编号并回写属性）。发布前要正式包时：

```bash
./gradlew build
```

它会产出不带编号的最终包，同时把带编号的原包归档进 `build/libs/origin/`。

改了构建逻辑或资源处理时，按 `build.md` 的要求核对产物本身，不能只看任务退出码。

## 不要做的

- 不要为了「版本号好看」去改 `mod_version` 或 Gradle `version` 的格式
- 不要把 `+build.N` 写进 `displayName` 或 jar 文件名
- 不要清理 `build/libs` 里的历史产物，工程默认保留
- 不要在没有 `api/` 包的工程里假设它有，依赖声明以 `build.gradle` 为准
