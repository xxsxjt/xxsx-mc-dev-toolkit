# 第三方模组兼容

本页只处理**可选依赖**：未安装第三方模组时，不加载其 API、不注册对应内容，主模组仍须能启动。已声明的必需依赖不因此改成可选；ForgeAttachment 的按需接入另见 [专页](forgeattachment.md)。

## 目录与职责

```text
compat/
├── ICompatUtils.java
├── <ModId>CompatFactory.java
└── <被兼容modid>/
    ├── <Dep>Compat.java
    ├── api/                 兼容 API，不是本体 API
    ├── event/
    ├── registry/
    └── util/
```

- 每个依赖按其 modid 建子包；兼容实现 `implements ICompatUtils`。compat 根只放 `ICompatUtils` 与 `<ModId>CompatFactory`，供各子包实现与主类装配。
- 兼容子包含 `api/`、`event/`、`registry/`、`util/`，工具包仍用单数。依赖独有的注册内容不散落到主模组的 `registry/`。
- 各 compat 子包互相独立：只引用本体 API 与本子包内的类（含本子包 `api/`），不引用其他 compat 的任何类。
- 本体可在任意处调用 compat，但必须是软调用：本体侧不出现第三方可选依赖类型；compat 入口类也要保持可安全链接，对应 mod 缺失时只降级，不崩溃。
- 第三方 API 引用集中在依赖专属实现中；通用入口避免在字段类型、方法签名、父类和静态初始化中提前链接可选类。
- 兼容 Mixin 的加载条件与包结构见 [Mixin](mixin.md)。

## 依赖检查入口

所有可选第三方 API 调用必须经 `testLoadedAndRun` / `testLoadedAndCall`：

| 方法 | 用途 |
|---|---|
| `isModLoaded()` | 唯一必需实现的方法，用目标加载器的 `ModList.get().isLoaded(modid)` |
| `testLoadedAndRun(Runnable)` | 依赖存在时执行，无返回值的能力入口 |
| `testLoadedAndCall(Callable<T>, errorResult)` | 依赖存在时调用，否则返回默认值 |
| 带 `elseCall` 的重载 | 依赖缺失时执行替代调用；异常时返回 `errorResult` |
| `initial(gameBus, modBus)` | 经依赖检查后初始化监听 |
| `initNetwork(network)` | 经依赖检查后注册兼容消息 |

`safelyRun` 只是异常包装，不做依赖检查，不能替代上述入口。依赖检查也不是任意类加载的保护罩：把第三方类型直接写进通用类的签名，仍可能在检查前触发链接。

完整接口直接取对应模板，不再在本文重复三套实现：

- [NeoForge ICompatUtils](../templates/neoforge1.21.1/src/main/java/io/zershyan/examplemod/compat/ICompatUtils.java)
- [Forge ICompatUtils](../templates/forge1.20.1/src/main/java/io/zershyan/examplemod/compat/ICompatUtils.java)

## 加载器差异

| 项目 | NeoForge 1.21.1 | Forge 1.20.1 |
|---|---|---|
| `IEventBus` | `net.neoforged.bus.api.IEventBus` | `net.minecraftforge.eventbus.api.IEventBus` |
| 模板客户端判断 | `FMLLoader.getDist() == Dist.CLIENT` | `FMLEnvironment.dist == Dist.CLIENT` |
| 网络注册参数 | `PayloadRegistrar` | `net.minecraftforge.network.simple.SimpleChannel` |

`addCommonListener` / `addClientListener` 由兼容实现覆写；客户端分支由接口统一判断。具体监听挂到其事件所属总线：例如 common/client setup 属于 mod 总线，不能因为方法名有 Common 或 Client 就挂到游戏总线。

## 工厂与接线

- 工厂名为 `<ModId>CompatFactory`；启用混淆时使用既有的 `CompatFactory` 命名。
- 每个实现以工厂中的 `public static final` 字段暴露，`addCompat` 使用 `Set` 去重，重复添加抛异常。
- 主类统一调用 `CompatFactory.register(gameBus, modBus)`，由工厂遍历并调用 `initial(...)`。
- 主模组网络注册处调用 `CompatFactory.registerNetwork(...)`，再由工厂调用各实现的 `initNetwork(...)`；不要漏掉兼容消息注册。
- 包处理器仍是消息自身的实例方法，遵守 [网络约定](network.md)。

接线与实现参考：

| 位置 | NeoForge 1.21.1 | Forge 1.20.1 |
|---|---|---|
| 工厂 | [ExampleModCompatFactory](../templates/neoforge1.21.1/src/main/java/io/zershyan/examplemod/compat/ExampleModCompatFactory.java) | [ExampleModCompatFactory](../templates/forge1.20.1/src/main/java/io/zershyan/examplemod/compat/ExampleModCompatFactory.java) |
| 兼容实现 | [ExampleLibCompat](../templates/neoforge1.21.1/src/main/java/io/zershyan/examplemod/compat/examplelib/ExampleLibCompat.java) | [ExampleLibCompat](../templates/forge1.20.1/src/main/java/io/zershyan/examplemod/compat/examplelib/ExampleLibCompat.java) |

## 调用与对外能力

通用调用点委托给依赖专属实现；由该实现把实际第三方调用包在 `testLoadedAndRun` 中。不要为了展示检查方法而把第三方类型直接写进通用调用点。

返回值调用使用 `testLoadedAndCall` 并提供明确默认值。需要供其他模组调用的能力写在本子包的 `api/`；compat 只用本体 API 与本子包内的类，不跨 compat 调用，也不直接调用本体其余内部包。完整调用关系见 [对外 API](api.md)。

## 完成前检查

- 第三方类型是否只在依赖专属代码中出现，调用是否经过检查入口？
- 兼容事件是否挂对总线，网络注册是否接入工厂？
- 依赖存在时功能是否可用；**实际移除可选依赖后**，客户端与专用服务器是否仍能启动？
- 是否存在跨 compat 引用，或本体对 compat 的调用未做软调用（类型泄漏、缺失依赖会崩溃）？