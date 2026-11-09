# 对外 API

## 创建前必须询问

**每个 mod 创建时必须明确询问用户是否需要 `api` 包**，不需要则不创建。

## 位置与命名

| 类型 | 位置 | 命名 |
|---|---|---|
| 本体 API | `api/<ModId>Api.java` | 用 `Api`（不是 `API`），与主类名前缀一致 |
| 兼容 API | `compat/<被兼容modid>/api/<Dep>Api.java` | 同上；属于兼容，**不计入本体 API** |

## 分层

**按需分层**：简单 mod 只一个 `XxxApi.java`，复杂 mod 才建 `helper/` 与 `events/` 子包。兼容 API 不放在 `api/` 下，跟随其 compat 子包。

```
// 简单
api/<ModId>Api.java

// 复杂
api/
├── <ModId>Api.java
├── helper/
│   └── <Feature>Helper.java
└── events/
    └── <Feature>Event.java

// 兼容 API
compat/<被兼容modid>/api/<Dep>Api.java
```

## 调用规则

本体 API 指 `api/`，兼容 API 指 `compat/<被兼容modid>/api/`。仅下列映射成立，其余调用一律不允许。

| 调用方 | 仅可调用 |
|---|---|
| 本体 API（`api/`） | 任意本体内容、compat（软调用） |
| 本体内部（`api/` 以外的本体包） | 任意本体内容、compat（软调用） |
| `compat/<modid>/api/` | 本体 API、本 compat 的 `api/` 与实现 |
| `compat/<modid>/` 实现 | 本体 API、本 compat 的 `api/` 与实现 |

- **本体内自由**：本体 API 与本体内部包可互相调用，不要求单向。
- **本体调用 compat 必须软调用**：本体可以引用并调用 compat 类，但本体侧的类型声明、父类、注解与静态初始化中不得出现第三方可选依赖类型；对应 mod 缺失时只降级，不抛异常、不崩溃。装配统一走 `CompatFactory`，见 [兼容](compat.md)。
- **compat 只用本体 API 和自己**：`compat/<modid>/` 只用本体 API 与本子包内的 api、实现，不引用本体内部包，也不跨 compat 调用。compat 根的 `ICompatUtils` 与工厂属基础设施，不在此限。未建 `api/` 的项目，compat 只用本子包与加载器 API 自足实现。
- `api` 仍是对外稳定面，**尽量少依赖其他包**；内部调用方再多也不改变它的签名契约。
- 内部调用 API 时注意类初始化顺序：`api` 的 `static` 常量不要引用一个初始化时会回调 `api` 的内部类，否则可能触发初始化循环。

## 写法

静态门面（用 `Api` 后缀）：

```java
public class <ModId>Api {
    public static final String MODID = <ModId>.MODID;
}
```

实例包装：

```java
public class <ModId>Api {
    private final Entity entity;

    <ModId>Api(Entity entity) {
        this.entity = entity;
    }

    public static <ModId>Api get(Entity entity) {
        return new <ModId>Api(entity);
    }
}
```

## 客户端方法

API 的客户端专属方法按项目约定标注 `@OnlyIn(Dist.CLIENT)`，并只在客户端路径调用。注解不能替代实际类加载隔离；不能在通用静态初始化中引用 Minecraft 等客户端类。以下计时 API 仅对应 NeoForge 1.21.1，其他版本核对签名：

```java
@OnlyIn(Dist.CLIENT)
public static float clientGetPartialTick() {
    return Minecraft.getInstance().getTimer().getGameTimeDeltaPartialTick(true);
}
```

## Javadoc

对外 API 使用简明中文 Javadoc，按需标注 `@param` / `@return`，说明调用端、前置条件和失败结果，不重复方法名。

## 完成前检查

- api 是否引入了不必要的内部依赖？
- 兼容 API 是否都在 `compat/<被兼容modid>/api/`，未混入本体 `api/`？
- 本体对 compat 的调用是否为软调用：本体侧无第三方可选依赖类型，缺失依赖时能降级？
- 客户端方法是否标注了 `@OnlyIn(Dist.CLIENT)`？
- `api` 与内部之间是否存在静态初始化循环？
- 公开方法签名是否稳定（改签名会同时破坏下游 mod 和内部调用方）？