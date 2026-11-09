---
name: zershyan-mcmod-style
description: 为 Minecraft 模组工程提供包结构、注册入口、网络、配置、Mixin、Datagen、软兼容与构建约定。兼容新建模组（io.zershyan 或 com.xxsx）及 mc-agent 多版本子目录存量模组的开发、迁移、排错、代码审查及工程模板维护；先确认目标版本，再按主题加载参考文档。
---

# Minecraft 模组工程规范（zershyan-mcmod-style 本地化适配版）

本 skill 维护该系列模组的项目约定与可复用模板，不替代加载器文档。通用 API 按目标 Minecraft / 加载器版本查官方文档及依赖源码，不依赖其他 skill。

## 工作顺序

1. **确认项目事实**：先读工作区指令（如 `mc-agent/AGENTS.md`）、目标仓库的 `gradle.properties`、`build.gradle`、模组元数据与相关代码。存量工程支持单仓库根目录或多版本子目录（如 `neoforge-26.1.2/`、`neoforge-26.2/`、`forge-1.20.1/`、`common/`）。
2. **按需阅读**：从 [主题索引](references/index.md) 选择主文档；只在任务跨主题时补读，不全量加载参考文档。
3. **规则不绑版本**：包结构、命名、API 调用、兼容、Datagen 等约定对任何 MC / 加载器版本都尽量遵守；示例与模板覆盖 Forge 1.20.1、NeoForge 1.21.1，**NeoForge 26.1.2 / 26.2（Java 25，`D:/Java/jdk-25`）** 等高版本先核实构造器、事件、映射和构建接口（如 `Identifier.fromNamespaceAndPath(MODID, path)`），不直接照搬示例代码。
4. **尊重已有工程（渐进式重构）**：存量仓库保留既有根包名（如 `com.xxsx.<modid>`），**不强行重命名为 `io.zershyan.<modid>`**；存量代码重构优先保留旧门面类作为轻量委托，确保已有单元测试与外部调用不断裂。
5. **硬性禁令（严禁擅自启动游戏客户端）**：未经用户在当前轮次明确要求启动游戏客户端，**绝对不得**执行 `gradlew runClient` 或拉起任何游戏进程；客户端验证一律使用编译、单元测试、静态资源门禁（如 `earth_release_gate.py`）和离线预览脚本替代。

## 核心约定

- **注册**：注册入口、注册项及注册时必需的数据归 `registry/`（或存量工程渐进抽离的注册类），入口统一 `doRegister`；事件驱动的注册也不例外。见 [注册](references/registry.md)。
- **分包与命名**：按功能分包，端侧按需嵌套；工具包用 `util/`。除主类与包名必须用完整 modid 外，类名前缀在 modid 过长时可取稳定缩写。使用非注册事件的类以 `Handler` 结尾，普通领域逻辑不强行归入 handler。见 [包结构](references/naming-and-layout.md)。
- **主类门面**：主类固定提供 `public static final String MODID`、`public static final Logger LOGGER` 以及统一的资源标识工厂方法 `public static Identifier id(String path)`（1.20.1/1.21.1 为 `ResourceLocation`）。见 [主类与双端结构](references/architecture.md)。
- **API 调用**：任意包可调用本体 API（`api/`）；兼容 API 在 `compat/<modid>/api/`，只对本 compat 可见；本体调用 compat 一律按软调用处理。见 [对外 API](references/api.md)。
- **资源**：可生成的资源优先走 Datagen 或规范化生成脚本；地球系列模组还必须通过 `python tools/earth_release_gate.py` 校验。见 [Datagen](references/datagen.md)。
- **版本与元数据**：`gradle.properties` 应规范声明 `mod_id`、`mod_name`、`mod_version`、`minecraft_version`、`neo_version`（或 `forge_version`）、`mod_license`、`mod_authors`、`mod_description`，确保与发布工具 `preflight.py` 无缝对接。见 [版本号](references/versioning.md) 与 [构建与发布](references/build.md)。
- **构建请求**：存量工程若未接入 `buildAlpha`，直接运行 `./gradlew test jar`（或对应子模块 `:neoforge-26.2:test :neoforge-26.2:jar`）；接入 `buildAlpha` 的工程按正式版/开发版流程区分。见 [构建与发布](references/build.md)。
- **可选兼容（重点落地）**：第三方可选依赖（如 Curios、Waystones、Lootr、Create、FTB、JEI）的调用收在 `compat/`，包含 `ICompatUtils` 与 `<ModId>CompatFactory`，经 `testLoadedAndRun` / `testLoadedAndCall` 检查，并隔离实际 API 引用或反射调用；缺少依赖仍须能正常启动。本体可调用 compat，但须软调用（本体侧不出现第三方可选依赖类型，缺失依赖不崩溃）；各 compat 子包互不引用。见 [兼容](references/compat.md)。
- **玩家持久化数据选型**：
  - **NeoForge 21.x / 26.x**：优先使用 NeoForge 原生 `AttachmentType` 与 `DataComponentType`，**不强绑 1.20.1 的 `ForgeAttachment`**；
  - **Forge 1.20.1**：需要玩家持久化数据时，可按 [ForgeAttachment](references/forgeattachment.md) 接入。
- **依赖声明**：必需依赖除构建脚本外，还要写进 `mods.toml` / `neoforge.mods.toml` 的 `[[dependencies]]`；可选依赖在 `neoforge.mods.toml` 中声明为 `type="optional"` 或不声明，代码层一律走 `compat/` 软调用。见 [构建与发布](references/build.md)。
- **不擅自扩展工具链**：未经用户要求不启用混淆，不引入本 skill 未列出的依赖或工具。

## 需要用户决定

- 新建模组的目标 MC 版本（未指定时），以及是否需要 `api/` 包（尚未明确时）。
- 未列举注册类型的归属，或其他尚未覆盖、无法从现有约定确定的项目规范。

通用 API 疑问先查目标版本资料；项目规范的缺口再向用户确认，不猜测约定。

## 工程模板

| 目标 | 模板 | 技术基线 |
|---|---|---|
| Forge 1.20.1 | `templates/forge1.20.1/` | Java 17、LegacyForge、SimpleChannel、NBT |
| NeoForge 1.21.1 | `templates/neoforge1.21.1/` | Java 21、ModDevGradle、CustomPacketPayload |
| NeoForge 26.1.2 / 26.2 | `neoforge-26.1.2/` 或 `neoforge-26.2/` | Java 25 (`D:/Java/jdk-25`)、ModDevGradle、`Identifier`、`AttachmentType` / `DataComponents` |

模板的 modid 为 `examplemod`，用来演示常见结构，不是新模组的必选功能清单。复制后替换标识并裁剪不用的代码；Forge 模板含附件演示，需要玩家持久化数据时保留并按 [ForgeAttachment](references/forgeattachment.md) 探测版本，不需要再连同依赖配置一起裁剪。其他 MC 版本没有对应模板，但上述约定仍适用，只按目标版本核实注册入口、元数据与加载器 API。创建步骤见 [构建与发布](references/build.md)。

## 维护与验证

规则影响代码时同步模板；完整实现优先链接模板，不在多份文档中复制。模板改动后运行 `compileJava`、`runData`；构建或打包改动还要检查产物。只记录实际执行的验证，不把历史通过或静态核对当作本轮测试结果。
