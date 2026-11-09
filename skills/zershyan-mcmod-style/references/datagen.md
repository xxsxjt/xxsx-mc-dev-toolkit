# Datagen 与资源

本页维护资源声明和生成流程，完整实现以对应版本模板为准。`<ModId>` 表示主类名前缀，`<modid>` 表示命名空间；不要把占位代码直接复制为源码。

## 核心规则

- 能由 Datagen 生成的资源必须通过 Provider 生成，不直接修改 `src/generated/resources`。
- 修改语言声明、注册项缓存或 Provider 后重新运行 `runData`，核对生成结果。
- 生成目录纳入资源源集，排除 `.cache`、`.bbmodel`；纹理、音频等原始素材仍放 `src/main/resources`。
- 只注册实际需要的 Provider。没有合法 ogg 的声音示例不启用 `ModSoundProvider`，不生成假音频绕过检查。

## 结构与入口

```text
datagen/
├── DataGeneratorHandler.java
├── lang/
│   ├── <ModId>Lang.java
│   ├── <ModId>KeyLang.java
│   ├── <ModId>ConfigLang.java
│   └── <ModId>RegistryLang.java
├── provider/
└── util/
    ├── LazyComponent.java
    └── ConfigLangEntry.java
```

`DataGeneratorHandler` 收拢数据生成事件。它不是运行时注册入口的替代品；运行时注册仍遵守 [registry 规则](registry.md)。

| 版本 | 事件与 Provider 注册 |
|---|---|
| NeoForge 1.21.1 | 使用模板中的 `GatherDataEvent`，以 `event.createProvider(...)` 或 `event.addProvider(...)` 注册，并按签名提供 PackOutput、lookup、ExistingFileHelper |
| Forge 1.20.1 | 使用 `@Mod.EventBusSubscriber(..., bus = Bus.MOD)` 与 Forge 的 GatherDataEvent，通过 `event.getGenerator().addProvider(event.includeClient() / event.includeServer(), provider)` 注册 |

不要把 `createProvider` 理解成“只用于无参构造器”：模板也用它传递 `PackOutput` 等参数。使用方法取决于**目标版本的实际函数签名**。条目标签依赖方块标签内容时，先创建方块标签 Provider，再传入其 `contentsGetter()`，不要独立构造而丢失依赖。

入口实现：[NeoForge 数据生成](../templates/neoforge1.21.1/src/main/java/io/zershyan/examplemod/datagen/DataGeneratorHandler.java)、[Forge 数据生成](../templates/forge1.20.1/src/main/java/io/zershyan/examplemod/datagen/DataGeneratorHandler.java)。

## 语言数据源

### 四类职责

| 类 | 职责 |
|---|---|
| `<ModId>Lang` | 基类，定义 Entry、FinalEntry、双语 Lang，并聚合所有语言来源 |
| `<ModId>KeyLang` | 命令、错误、提示、说明、消息、按键等通用文本 |
| `<ModId>ConfigLang` | 配置项路径与显示名 |
| `<ModId>RegistryLang` | 物品、方块、声音、属性、自定义注册项等对象的语言 |

基类保留 `stringEntry`、`addEntry`、`addFinalEntry`、`getAllLang()` 和两种 `init` 钩子：无参 `init()` 登记本类条目，`init(entries)` 合并已有列表。新增语言子类时，把它加入 `getAllLang()` 的聚合列表，不能只建类而不接入。

实现参考：[NeoForge 语言基类](../templates/neoforge1.21.1/src/main/java/io/zershyan/examplemod/datagen/lang/ExampleModLang.java)、[Forge 语言基类](../templates/forge1.20.1/src/main/java/io/zershyan/examplemod/datagen/lang/ExampleModLang.java)。

### 通用文本与键

命令、错误、tooltip、description、message 等前缀集中定义，不在调用点散落中英文文案。资源相关键优先通过 `ResourceLocation.toLanguageKey(...)` 及语言基类辅助方法构造。

| 登记方法 | 返回值 | 适用场景 |
|---|---|---|
| `entryString` | `String` | 只需要语言键，例如按键名称 |
| `entry` | `MutableComponent` | 即时可翻译组件 |
| `entryLazy` | `LazyComponent` | 调用时提供 `%s` 等参数 |

按领域补充 `getSoundDesc(location)`、`getKeyDesc(name)`、`getAttributeDesc(location)` 等辅助方法，避免重复拼键。

示例：[通用语言声明](../templates/neoforge1.21.1/src/main/java/io/zershyan/examplemod/datagen/lang/ExampleModKeyLang.java)。

### 配置语言

`ConfigLangEntry` 的 `name` 就是配置项 path，统一生成 `<modid>.configuration.<name>`。配置类用 `define(ExampleModConfigLang.EnableFeature.name(), ...)` 取路径，不写字符串字面量；`name` 用 `lower_snake_case`，与已发布的配置键保持一致。

实现：[配置语言声明](../templates/neoforge1.21.1/src/main/java/io/zershyan/examplemod/datagen/lang/ExampleModConfigLang.java)、[ConfigLangEntry](../templates/neoforge1.21.1/src/main/java/io/zershyan/examplemod/datagen/util/ConfigLangEntry.java)。

### 注册项语言

按类型提供 `entryItem`、`entryBlock`、`entrySound` 等私有登记方法，内部调用 `addFinalEntry`。声音字幕使用 `getSoundDesc`；自定义注册项使用与注册表名一致的描述键。

- NeoForge 的 DeferredItem、DeferredBlock 与 Holder 按模板取对象值。
- Forge 使用 RegistryObject，不导入 NeoForge 注册封装。
- 新增类型时扩展对应登记方法和 Provider 分发，而不是把所有对象一律转成字符串。

实现：[NeoForge 注册项语言](../templates/neoforge1.21.1/src/main/java/io/zershyan/examplemod/datagen/lang/ExampleModRegistryLang.java)、[Forge 注册项语言](../templates/forge1.20.1/src/main/java/io/zershyan/examplemod/datagen/lang/ExampleModRegistryLang.java)。

### 延迟组件

`LazyComponent` 用 `get(Object... args)` 构造可翻译组件；`getNumber2f` / `getNumber1f` 对浮点参数按 `#.##` / `#.#` 格式化，使用 Locale.US 与 HALF_UP，整数参数不做浮点格式化。

实现：[LazyComponent](../templates/neoforge1.21.1/src/main/java/io/zershyan/examplemod/datagen/util/LazyComponent.java)。

## Provider 职责

完整构造器和 API 差异从对应模板取用，不在文档中维护另一份实现。

| Provider | 项目约定 |
|---|---|
| `ModLangProvider` | `runEnUs`、`runZhCn` 两个工厂，按语言输出聚合条目；按 Item、Block、String、ItemStack、MobEffect、EntityType、TagKey 等类型分发 |
| `ModSoundProvider` | 遍历声音注册，subtitle 使用语言基类的声音键；多个音频变体按同一资源路径的后缀逐个加入 |
| `ModItemModelProvider` | 简单物品使用 `basicItem`；动态贴图等不适用条目显式排除 |
| `ModBlockStateProvider` | 简单方块用 `simpleBlock` / `cubeAll`；有方向等状态时生成对应变体和 rotation，并生成方块物品模型 |
| `ModItemTagProvider` / `ModBlockTagProvider` | 从注册类维护的标签缓存输出，不在 Provider 中重复写业务判定 |
| `ModLootTableProvider` | 通过 BlockLootSubProvider 定义方块掉落；`getKnownBlocks` 只返回本模组方块，避免误生成其他命名空间的掉落 |
| `PackMetadataProvider` | 包说明使用 KeyLang 的资源描述组件；pack format 取目标版本信息，不硬编码另一 MC 版本的数字 |

常用实现入口：

- [NeoForge 语言 Provider](../templates/neoforge1.21.1/src/main/java/io/zershyan/examplemod/datagen/provider/ModLangProvider.java)
- [NeoForge 方块状态 Provider](../templates/neoforge1.21.1/src/main/java/io/zershyan/examplemod/datagen/provider/ModBlockStateProvider.java)
- [NeoForge 战利品 Provider](../templates/neoforge1.21.1/src/main/java/io/zershyan/examplemod/datagen/provider/ModLootTableProvider.java)
- [Forge 语言 Provider](../templates/forge1.20.1/src/main/java/io/zershyan/examplemod/datagen/provider/ModLangProvider.java)
- [Forge 战利品 Provider](../templates/forge1.20.1/src/main/java/io/zershyan/examplemod/datagen/provider/ModLootTableProvider.java)

Forge 1.20.1 使用 Java 17：类型分发用 `instanceof`，不复制 Java 21 的模式匹配 switch；LootTableProvider / BlockLootSubProvider 构造器也不能照搬 1.21.1 的 lookup 参数。包版本接口按目标 MC 核实。

## 可选依赖与命名

- 第三方 Provider 使用 `Mod<Dep>DataProvider`，继承依赖提供的基类；只在该依赖存在时经兼容入口注册，避免缺少依赖时链接第三方类。见 [兼容规则](compat.md)。
- Provider 放 `datagen/provider/`，通用 Provider 使用 `Mod*Provider`；包元数据类保留 `PackMetadataProvider`。

## 完成前检查

- 改动来自声明源或 Provider，生成文件由 `runData` 更新？
- 新语言来源已接入聚合，双语键与占位符一致？
- 配置语言的 `name` 就是配置 path，配置类未硬编码字符串；标签与掉落仅涉及预期注册项？
- Provider 只在需要时注册，音频与纹理引用存在，可选依赖缺失时不会被加载？
- 生成资源已纳入最终 jar，而非只存在于源码目录？