# Mixin 与 MixinPlugin

## 版本与 refmap

| 目标 | 配置与打包 |
|---|---|
| NeoForge 1.21.1 | `JAVA_21`，不声明 refmap，由加载器处理映射转换 |
| Forge 1.20.1 | `JAVA_17`，声明 `<modid>.refmap.json`，配置注解处理器生成映射，成品 manifest 包含 `MixinConfigs` |

Forge 使用 LegacyForge 的 `mixin.add` / `mixin.config`，不额外引入 MixinGradle。完整构建写法见 [构建与发布](build.md)；不能只配置开发运行参数而遗漏发布 jar 的清单项。

## 插件与加载条件

必须使用 `<ModId>MixinPlugin implements IMixinConfigPlugin`，在 `shouldApplyMixin` 中统一判断：

1. `example.mixin.` 路径始终不加载，见 [示例代码](example.md)。
2. 去掉插件所在 Mixin 根包与类名后，逐段检查相对包名。
3. 非 `client` / `server` / `common` 的包名段按 modid 检查；任一依赖未安装即拒绝加载。
4. 到达 `client` / `server` / `common` 段时放行，因此依赖段必须置于这些分端段之前。

插件的包名判断不代替物理端隔离：客户端 Mixin 仍须列在配置的 `client` 项，不能因为包名含 client 就放进通用列表。

实现：[NeoForge 插件](../templates/neoforge1.21.1/src/main/java/io/zershyan/examplemod/mixin/ExampleModMixinPlugin.java)、[Forge 插件](../templates/forge1.20.1/src/main/java/io/zershyan/examplemod/mixin/ExampleModMixinPlugin.java)。LoadingModList / ModInfo 按目标加载器导入，不混用包名前缀。

## 包结构与命名

```text
mixin/
├── <本modid>/
│   ├── client/MixinMinecraft.java
│   └── common/MixinLivingEntity.java
├── <目标modid>/MixinXxx.java
└── <ModId>MixinPlugin.java
```

- Mixin 类统一 `Mixin + 目标类名`，例如 `MixinServerPlayer`。
- 以 modid 作为包名；同时依赖多个模组时嵌套，如 `mixin.moda.modb.MixinXxx`，只有两个模组都存在才加载。
- 对外桥接接口命名 `IMixin + 目标类名`，放 `util/mixin/`，并镜像 Mixin 相对于 `mixin/` 的子包。例如 `mixin/<modid>/common/MixinLivingEntity` 对应 `util/mixin/<modid>/common/IMixinLivingEntity`。
- 为兼容依赖创建的接口同样保留依赖 modid 子包，不直接丢在通用工具包。

## Mixin 配置

下面是 NeoForge 1.21.1 的结构示意；Forge 1.20.1 改为 `JAVA_17` 并补上 `"refmap": "<modid>.refmap.json"`。

```json
{
  "required": true,
  "minVersion": "0.8",
  "package": "io.zershyan.<modid>.mixin",
  "compatibilityLevel": "JAVA_21",
  "plugin": "io.zershyan.<modid>.mixin.<ModId>MixinPlugin",
  "mixins": ["<modid>.common.MixinLivingEntity"],
  "client": ["<modid>.client.MixinMinecraft"],
  "injectors": { "defaultRequire": 1 },
  "overwrites": { "requireAnnotations": true }
}
```

## 职责与检查

- Mixin 只做精确注入、桥接或传递结果；复杂逻辑放领域实现。使用非注册事件的逻辑才归 `handler/`，不能把所有玩法代码都强行放进去。
- 检查目标方法签名、注入点和版本映射，验证客户端与专用服务器路径。
- 缺少可选依赖时对应 Mixin 不加载；示例 Mixin 始终过滤。
- Forge 成品必须同时包含 Mixin 配置、非空 refmap 和 manifest 声明。