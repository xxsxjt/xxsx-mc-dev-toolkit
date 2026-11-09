# 版本号与产物

新工程使用本页约定；已有工程格式不同，先确认迁移范围，不顺带重写历史版本。完整任务实现见 [NeoForge 构建脚本](../templates/neoforge1.21.1/build.gradle) 与 [Forge 构建脚本](../templates/forge1.20.1/build.gradle)。

## 版本组成

| 位置 | 格式 |
|---|---|
| `mod_version` 属性 | 仅模组版本，例如 `0.0.1` |
| Gradle `version` 与包内元数据 | `<mod_version>-<minecraft_version>+build.<编号>` |
| Gradle 默认 jar 名 | `<modid>-<Gradle version>.jar` |
| 普通 `build` 的最终 jar 名 | `<modid>-<mod_version>-<minecraft_version>.jar` |
| `buildAlpha` 的最终 jar 名 | `<modid>-<mod_version>-<minecraft_version>+build.<编号>.jar` |
| Maven 发布版本 | 默认 `<mod_version>-<minecraft_version>`，不带编号 |

`modid` 来自 `mod_id`，通过 `archivesName` 用作文件名前缀，不拼进包内版本。`build` 后必须有点：`+build.2`，不能写成 `+build2`。

```properties
minecraft_version=1.21.1
mod_id=examplemod
mod_version=0.0.1
mod_build_number=0
```

- `mod_version` 不重复填写 MC 版本；MC 版本由 `minecraft_version` 单独维护。更换 MC 时仍须同步加载器、映射等兼容配置。
- `mod_build_number` 初始为 `0`，后续由 `buildAlpha` 维护；**不是每次编译或普通构建都递增**。
- **对外发布用正式版本号**（`<mod_version>-<minecraft_version>`），不带 `+build.<编号>`；`+build.N` 只进包内元数据与 alpha 包名。发布版本由 `maven_publish_release_version` 控制，默认 `true`，置 `false` 才沿用带编号版本。
- Forge 的 `mods.toml` 与 NeoForge 的 `neoforge.mods.toml` 都必须展开 Gradle `version`，而非原始 `mod_version`。

## 两种构建行为

设属性中的构建编号为 `N`：

| 行为 | `build` | `buildAlpha` |
|---|---|---|
| 使用编号 | `N` | `N + 1` |
| 包内版本 | 恒带所用编号 | 恒带所用编号 |
| 最终 jar 名 | 不带编号 | 带所用编号 |
| 成功后回写属性 | 否 | 写入 `N + 1` |
| 失败后改变属性 | 否 | 否 |

`buildAlpha` 用于生成新编号产物，普通 `build` 沿用已记录编号；重复普通构建不消耗编号。协议版本取包内版本时，也遵守这一行为，不是每次运行构建都会变化。

例如从 `mod_build_number=0` 开始：

| 操作 | 包内构建后缀 | 操作后属性 |
|---|---|---|
| `build` | `+build.0` | `0` |
| `buildAlpha` | `+build.1` | `1` |
| `build` | `+build.1` | `1` |
| `buildAlpha` | `+build.2` | `2` |

默认选择按以下顺序判断：

- **构建任务**：用户提出构建时，先异步提问是否需要正式版（不阻塞），同时直接执行 `buildAlpha`；用户确认需要正式版后再执行 `build`。工程已有沿用编号的先例、或用户明确要求普通 `build` 时，按先例与要求处理。
- **历史产物**：用户明确要求清理，或工程已有清理先例时才删除旧 jar；否则保留已有构建版本，不主动清空 `build/libs`。

## 实现要求

```groovy
def isAlphaBuild = gradle.startParameter.taskNames.any { it.endsWith('buildAlpha') }
def buildNumber = mod_build_number.toInteger() + (isAlphaBuild ? 1 : 0)
def baseVersion = "${mod_version}-${minecraft_version}"
version = "${baseVersion}+build.${buildNumber}"
```

- 新编号在内存中计算，不在构建前修改 `gradle.properties`。
- `buildAlpha` 依赖 `build`，只有构建成功后才在自身 `doLast` 中回写**同一个**所用编号，保证属性与产物一致。
- 任务名保持 `buildAlpha`，与模板的任务名检测逻辑一致。
- `finalizeArtifacts` 始终挂到 `build`，不能仅在启用混淆时才整理产物。
- 普通构建保留不带编号的最终包，把带编号原包归档到 `build/libs/origin/`。重复构建时支持从已归档原包恢复，不能假设原包始终位于顶层。
- Alpha 最终包保留带编号的名字；包内版本不因整理文件名而改变。
- Maven 发布显式设置 publication 的 `version`，不继承带编号的 `project.version`。

完整实现从对应模板取用，不另写一份不同语义的编号或收尾逻辑。涉及混淆时按 [构建与发布](build.md) 扩展既有收尾任务，保持混淆输出、原包与最终包各自用途，不重复注册 `finalizeArtifacts`。

## 验证

- 检查最终 jar 文件名与包内版本，确认 modid 只作文件名前缀，MC 版本没有重复。
- 连续执行普通 `build`，确认编号不变，最终包仍可生成。
- 执行 `buildAlpha`，确认产物编号等于构建后属性；失败路径不得提前消耗编号。
- 对 Forge / NeoForge 分别验证元数据展开和整理任务，不能仅凭一种模板通过就推断另一种通过。