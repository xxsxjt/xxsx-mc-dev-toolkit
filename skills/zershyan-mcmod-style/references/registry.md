# 注册与 registry

## 范围与入口

**所有注册相关内容归 `registry/`，事件驱动的注册也不例外。** 例如 overlay 由 `<ModId>Overlays.doRegister(...)` 挂监听，不改用独立 `@EventBusSubscriber` 把入口藏起来。

| 内容 | 归属 |
|---|---|
| 注册项、其属性 / 行为定义 | `registry/` 及对应子包 |
| 注册时必需的数据，如附件数据与辅助结构 | `registry/` 及对应子包 |
| 注册动作、自定义注册表及其条目 | `registry/` |
| 只使用已注册对象的业务逻辑 | 所属功能域，不因使用注册对象就搬入 registry |

每个注册领域维护一个入口类，唯一公共接入方法名为 **`doRegister`**。参数明确表达所需上下文：mod / 游戏总线、ModContainer 或实际注册事件；无上下文需求时可无参。

- 主类只编排入口，不散落 `addListener`、`registerConfig` 或 `DeferredRegister.register`。
- 有的 API 直接提供注册事件，既有工程可使用 `doRegister(RegisterLayerDefinitions event)` 等形式，仍不改变归属。
- 可选依赖独有注册放 `compat/<依赖modid>/registry/`，经 [兼容工厂](compat.md) 接线；已有 Capability 结构见 [附件与能力](attachments.md)。
- 边界不清，或遇到清单之外的注册类型时，先询问用户，不擅自扩大清单或挪入 handler。

## 常见注册领域

| 入口类后缀 | 对应内容或子包 |
|---|---|
| Items、Blocks、BlockEntityTypes、Entities、Sounds、Attributes | 物品、方块、方块实体、实体、声音、属性；如 `item/`、`block/`、`block/entity/` |
| Packets | `packet/`，见 [网络](network.md) |
| Configs | `config/`，见 [配置](config.md) |
| Commands | `command/`，见 [命令](commands.md) |
| Attachments | `attachment/`，见 [附件](attachments.md) |
| DataComponents | `data_component/`，仅适用支持该系统的目标版本 |
| CreativeTab、Overlays、KeyMappings、EntityLayers | 创造标签页与客户端注册；如 `overlay/`、`renderer/` |
| Registries | 只管理自定义注册表声明，不收容杂项注册 |

未混淆项目用 `<ModId>*` 前缀，混淆项目用 `Mod*`，见 [命名规范](naming-and-layout.md)。这是参考清单，不是每个项目都要创建的文件列表。

## 自定义注册表

```text
registry/
├── <ModId>Registries.java
├── <ModId>CustomRegistries.java
└── custom_registry/
    ├── builder/IExampleStyle.java
    └── SimpleExampleStyle.java
```

- 注册表名同时作为资源路径与子包名。
- 类型接口放该子包的 `builder/`，具体实现平铺在子包内。
- 注册表声明和具体条目分开：`<ModId>Registries` 创建注册表，对应条目入口维护 DeferredRegister。
- 语言键用 `toLanguageKey("<注册表名>", "desc")`，由语言基类提供辅助方法，见 [Datagen](datagen.md)。

| 目标 | 自定义注册表方式 |
|---|---|
| NeoForge 1.21.1 | 用目标版本 RegistryBuilder 构造 Registry，在 mod 总线的 NewRegistryEvent 注册；条目通过 `DeferredRegister.create(该注册表, MODID)` 加入 |
| Forge 1.20.1 | 在 NewRegistryEvent 调用 `event.create(new RegistryBuilder<T>().setName(key.location()))`，保留 `Supplier<IForgeRegistry<T>>`，事件后才访问；条目通过 `DeferredRegister.create(key, MODID)` 注册 |

完整实现：

- [NeoForge 注册表声明](../templates/neoforge1.21.1/src/main/java/io/zershyan/examplemod/registry/ExampleModRegistries.java)、[NeoForge 条目注册](../templates/neoforge1.21.1/src/main/java/io/zershyan/examplemod/registry/ExampleModCustomRegistries.java)
- [Forge 注册表声明](../templates/forge1.20.1/src/main/java/io/zershyan/examplemod/registry/ExampleModRegistries.java)、[Forge 条目注册](../templates/forge1.20.1/src/main/java/io/zershyan/examplemod/registry/ExampleModCustomRegistries.java)

## Forge 1.20.1 差异

- DeferredRegister、RegistryObject、ForgeRegistries 来自 `net.minecraftforge.registries`，不用 NeoForge 的 DeferredItem / DeferredBlock。
- ItemStack 自定义数据用 NBT，不建 DataComponents 注册类或 `registry/data_component/`。
- Overlay 使用 RegisterGuiOverlaysEvent / IGuiOverlay，仍经 `<ModId>Overlays.doRegister(modBus)` 挂监听。
- 只有需要附件时才通过 ForgeAttachment 注册表键注册，见 [依赖接入](forgeattachment.md)。

## 完成前检查

- 注册入口、注册项与必需数据是否集中，主类是否只调用 `doRegister`？
- 事件是否挂在正确总线，客户端注册是否隔离？
- 新类型的归属是否明确，自定义注册表是否与条目入口分离？