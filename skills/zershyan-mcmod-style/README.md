# zershyan-mcmod-style

为 Zershyan 的 `io.zershyan` 系列 Minecraft 模组提供项目约定和可复用工程模板：包结构、注册入口、双端隔离、API、兼容、网络、配置、Mixin、Datagen 与构建发布。

通用 Forge / NeoForge API 仍以目标版本的官方文档和依赖源码为准；不要求安装其他模组规范 skill。

## 阅读入口

- [SKILL.md](SKILL.md)：使用流程、核心边界、用户决策项与模板说明。
- [主题索引](references/index.md)：按任务加载主文档及必要的关联主题，不必一次读完全部参考资料。

## 工程模板

| 目标 | 构建入口 | 基线 |
|---|---|---|
| NeoForge 1.21.1 | [构建脚本](templates/neoforge1.21.1/build.gradle) | Java 21、CustomPacketPayload、DataComponents |
| Forge 1.20.1 | [构建脚本](templates/forge1.20.1/build.gradle) | Forge 47.3.4、Java 17、LegacyForge、SimpleChannel、NBT |

两套模板的 modid 均为 `examplemod`。先确认目标版本，再替换标识并裁剪演示功能，步骤见 [构建与发布](references/build.md)。Forge 模板含附件演示：**需要玩家持久化数据时优先保留并使用 ForgeAttachment（先探测 sigh Maven 版本）**，不需要再裁剪依赖与调用，规则见 [用户告知与依赖规则](references/forgeattachment.md)。

其他 MC 版本暂无对应模板，但包结构、命名、API 调用、兼容与 Datagen 等约定仍应尽量遵守；入口、元数据与加载器 API 须按目标版本核实，不能直接套用 1.21.1 的写法。

## 维护约定

- 规则影响实现时，文档与两套模板同步；完整实现链接模板，避免多处复制后漂移。
- 模板改动后运行 `compileJava`、`runData`，构建或打包改动另查最终 jar；只报告实际执行的结果。
- 发现已有工程与规范不符时先核对原因和迁移范围，不擅自改造旧代码。
- 纯措辞与路由调整校验文档、链接和关键约定，不把历史构建记录写成长期保证。
