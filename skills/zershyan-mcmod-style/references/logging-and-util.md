# 日志与工具

## 日志

统一使用 SLF4J 的 `LoggerFactory.getLogger(本类.class)`，变量名为 `LOGGER`，不改用 LogUtils、`log` 或 `LOG`。

- 主类声明 `public static final Logger LOGGER`，供项目引用。
- 其他类确需独立日志时声明 `private static final Logger LOGGER`，绑定本类，而不是复制主类的类型。

```java
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public static final Logger LOGGER = LoggerFactory.getLogger(<ModId>.class);
```

这里保留项目约定即可，无需为选择 LoggerFactory 引入额外包装或日志依赖。

## ResourceLocation 与 `id()`

主类提供 `id(String path)`，调用形式为 `<ModId>.id("ride_player")`，资源路径使用 `lower_snake_case`。

| 目标 | `id` 方法的返回表达式 |
|---|---|
| NeoForge 1.21.1 | `ResourceLocation.fromNamespaceAndPath(MODID, path)` |
| Forge 1.20.1 | `new ResourceLocation(MODID, path)` |

其他版本核实构造接口后使用。全项目复用主类的 MODID，不在其他类重复定义，也不另建同义的资源门面。主类结构见 [双端结构](architecture.md)。

## 工具包

- 通用工具放 `util/`（单数），不用 `utils/`；按用途细分，如 `util/data/`。
- Mixin 接口放 `util/mixin/`，并镜像目标 Mixin 的子包，见 [Mixin](mixin.md)。
- Datagen 专属辅助类型留在 `datagen/util/`，不为“集中工具”破坏功能内聚。

## 完成前检查

- LOGGER 的命名、可见性和绑定类型正确？
- ResourceLocation API 与目标版本匹配，是否复用了主类的 MODID 与 `id()`？
- 工具是否有明确用途，是否确实需要抽取而非增加无意义门面？