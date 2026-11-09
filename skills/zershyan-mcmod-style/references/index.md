# 参考文档索引

先读 [Skill 入口](../SKILL.md)，再按任务选文档。本页只维护路由，不重复主题规则。

## 阅读方式

- 默认只加载一个主题主文档；涉及注册、语言、兼容等相邻职责时，再读关联文档。
- 代码示例按文档标注的 MC / 加载器版本使用。完整实现链接到 `templates/`，不把占位示例当作可直接编译的源码。
- 本索引覆盖全部参考主题；新增主题时补充路由。保持 `references/` 扁平，不建立层层转发的文档链。

## 主题路由

| 分组 | 主题与关键词 | 主文档 | 按需关联 |
|---|---|---|---|
| 工程 | 包结构、类名、`util`、`Handler` | [包结构与命名](naming-and-layout.md) | [注册](registry.md) |
| 工程 | `@Mod`、构造器、Dist、双端隔离 | [主类与双端](architecture.md) | [配置](config.md)、[Mixin](mixin.md) |
| 工程 | 对外门面、`Api`、helper、兼容 API、调用关系 | [对外 API](api.md) | [兼容](compat.md) |
| 工程 | `LOGGER`、`id()`、ResourceLocation、工具类 | [日志与工具](logging-and-util.md) | [包结构](naming-and-layout.md) |
| 注册与逻辑 | 注册项、`doRegister`、registry、自定义注册表 | [注册](registry.md) | [包结构](naming-and-layout.md) |
| 注册与逻辑 | 命令、子命令、权限、反馈消息 | [命令](commands.md) | [注册](registry.md)、[Datagen](datagen.md) |
| 注册与逻辑 | payload、packet、StreamCodec、SimpleChannel | [网络](network.md) | [注册](registry.md)、[兼容](compat.md) |
| 注册与逻辑 | ModConfigSpec、ForgeConfigSpec、三类配置、配置界面 | [配置](config.md) | [Datagen](datagen.md) |
| 注册与逻辑 | Attachment、Capability、持久化、同步 | [附件与能力](attachments.md) | [注册](registry.md)、[网络](network.md) |
| 兼容 | forgeattachment、玩家持久化、sigh Maven、版本探测、用户告知、发布链接 | [ForgeAttachment](forgeattachment.md) | [附件](attachments.md)、[构建](build.md) |
| 兼容 | 可选依赖、ICompatUtils、CompatFactory、类链接 | [第三方兼容](compat.md) | [注册](registry.md)、[API](api.md) |
| 兼容 | MixinPlugin、refmap、兼容 Mixin、IMixin 接口 | [Mixin](mixin.md) | [包结构](naming-and-layout.md) |
| 资源与构建 | Datagen、GatherDataEvent、Lang、Provider、模型、标签 | [Datagen 与资源](datagen.md) | [注册](registry.md) |
| 资源与构建 | 工程模板、Gradle、运行配置、元数据、依赖声明、ProGuard、构建请求、发布 | [构建与发布](build.md) | [版本号](versioning.md) |
| 资源与构建 | mod_version、mod_build_number、buildAlpha、jar 命名、发布版本 | [版本号与产物](versioning.md) | [构建](build.md) |
| 资源与构建 | example、开发环境、production、示例开关 | [示例代码](example.md) | [双端结构](architecture.md) |

## 常见任务

| 任务 | 阅读顺序 |
|---|---|
| 新建模组 | 构建 → 包结构 → 主类 → 注册；先确认 MC 版本与 API 需求，玩家持久化数据优先用 ForgeAttachment |
| 新增注册项 | 注册 → Datagen（需要资源时） |
| 新增网络包 | 网络 → 注册；包含可选依赖时再读兼容 |
| 新增命令 | 命令 → Datagen（反馈文本） |
| 执行构建 | 构建与发布；异步问是否需要正式版，先走 `buildAlpha`，确认后再 `build` |
| 接入 ForgeAttachment | 附件 → ForgeAttachment；先探测 sigh Maven 版本，再履行用户告知与链接要求 |
| 可选依赖或兼容 Mixin | 兼容 → Mixin（需要注入时） |
| 排查专用服务器类缺失 | 主类与双端 → 对应功能文档，检查客户端类和可选依赖的加载路径 |

这些主题名称对应上表的直接链接，不要求顺序读完全部文档。