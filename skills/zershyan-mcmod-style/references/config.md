# 配置

## 位置与类型

注册入口为 `registry/<ModId>Configs.java`，配置定义放 `registry/config/`：

```text
registry/
├── <ModId>Configs.java
└── config/
    ├── ClientConfig.java
    ├── CommonConfig.java
    └── ServerConfig.java
```

按 CLIENT / COMMON / SERVER 分文件，每类维护独立 SPEC；只注册需要的配置类型。Forge 模板保留这三类，不因示例开关额外添加 Startup 配置。

## 配置项

- 配置键使用 `lower_snake_case`，不要为整理措辞修改已发布配置键。
- **路径不写字符串字面量**：`define`、`defineInRange` 等一律取 `ConfigLangEntry.name()`，如 `define(ExampleModConfigLang.EnableFeature.name(), true)`；`name` 即配置键，路径与语言条目不会漂移。
- 在静态初始化中构造 Builder、配置值与 SPEC；`comment(...)` 使用简明中文。
- 显示名由 ConfigLang 提供：Forge 经 `.translation(langEntry.key())` 显式关联，NeoForge 使用默认 `<modid>.configuration.<path>` 键。见 [Datagen](datagen.md)。

## NeoForge 1.21.1

使用 `ModConfigSpec` 和 `ModContainer.registerConfig(...)`。入口为 `doRegister(ModContainer)`，在内部区分公共配置与客户端配置，而不是让调用者漏掉客户端注册。

```java
public static void doRegister(ModContainer container) {
    if (FMLLoader.getDist().isClient()) registerClient(container);
    registerCommon(container);
}
```

- `registerCommon` 注册 COMMON、SERVER。
- `registerClient` 注册 CLIENT，并通过 `container.registerExtensionPoint(IConfigScreenFactory.class, ConfigurationScreen::new)` 接入配置界面。
- 客户端专属类的访问仍须保持端侧隔离，不在通用静态初始化中执行客户端逻辑。

完整实现：[NeoForge 配置入口](../templates/neoforge1.21.1/src/main/java/io/zershyan/examplemod/registry/ExampleModConfigs.java)。

## Forge 1.20.1

- 使用 `ForgeConfigSpec`，入口为 `doRegister()`。
- 经 `ModLoadingContext.get().registerConfig(...)` 注册；客户端配置先检查物理客户端，如 `FMLLoader.getDist().isClient()`。
- 不移植 NeoForge 的配置界面工厂，不擅自添加额外界面依赖。

完整实现：[Forge 配置入口](../templates/forge1.20.1/src/main/java/io/zershyan/examplemod/registry/ExampleModConfigs.java)。

## 完成前检查

- 配置类型与实际生效范围一致，CLIENT 配置仅在客户端注册？
- 配置 path 是否取自 `ConfigLangEntry.name()`，没有硬编码字符串？
- 显示名和注释已登记，语言键与配置键一致？
- 已发布的键名、默认值或约束若有变化，是否明确兼容影响？