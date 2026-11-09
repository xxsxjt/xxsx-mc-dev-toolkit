# 包结构与命名

## 顶层包结构

顶层包结构如下：

```
<root_pkg>/<modid>/         # 新项目可用 io/zershyan/<modid>/ 或 com/xxsx/<modid>/；存量项目保留既有 com/xxsx/<modid>/
├── <ModId>.java        主类
├── api/                对外门面（按需创建，创建前须问用户）
├── client/             顶层客户端包
├── compat/             第三方模组兼容（按被兼容 modid 分子包，子包 api/ 为兼容 API）
├── datagen/
│   ├── lang/           语言数据源
│   ├── provider/       Provider
│   └── util/           辅助类型
├── handler/
│   ├── client/
│   └── common/
├── mixin/
├── registry/           所有注册相关内容
└── util/               工具（单数）
```

- **按功能分包，端再嵌套**：顶层是功能域，需要分端时在功能域下再嵌 `client`/`common`。
- **顶层功能包可自加**：上表不是穷举。清单之外允许新增顶层包，但须**同时**满足两条——与注册无关，且是一个功能大类（如只负责动画计算的 `animation/`）。注册相关一律归 `registry`，不得借自加包名规避。
- **`util/` 用单数**，不用 `utils/`。mixin 接口固定在 `util/mixin/`。
- **`handler/{client,common}/`**：只放事件回调与业务逻辑，**不放注册**（注册一律在 `registry`）。判据是**是否使用非注册事件**：使用非注册事件的类以 `Handler` 结尾并放这里；不涉及事件、纯被调用的逻辑类留在所属功能包内即可（如 `client/`），不必为了归类而搬动并改名。
- **存量工程渐进式迁移约定**：对于已有大量代码的存量工程（如 `mc-agent` 下的 `earth-series/*`），当把兼容逻辑归入 `compat/` 或将事件监听拆入 `handler/{client,common}/` 时，保留原顶层门面类（如 `CuriosTalismanCompat`、`TheologyEvents`）作为轻量静态转发器，确保既有单元测试和外部调用零破坏。

## 命名规范

- 类名：`UpperCamelCase`；包名：`lower_snake_case`（多词用下划线，如 `data_component`、`gag_style`）。
- 缩写词统一**首字母大写**：`Api`、`Id`、`Url`，不用 `API`、`ID`、`URL`。
- **按正确英文拼写**：`animation`（不是 `animtion`）、`ServerTickHandler`（不是 `ServerTIckHandler`）。

## 前缀规范

- **注册类**：启用混淆的项目用 `Mod*`（`ModItems`、`ModSounds`）；未启用混淆的用 `<ModId>*`（`ExampleModItems`、`DSItems`）。
- **前缀可缩写，主类与包名除外**：modid 过长时，其他类的前缀可按单词取稳定缩写（如 `AbcdefghijkLmnopqrstuvWxyz` → `ALW`，得 `ALWItems`），可整体大写，同一工程内统一，`DSItems` 即此例；**主类与包名不许缩写**，须用完整 modid（`AbcdefghijkLmnopqrstuvWxyz.java`、`io/zershyan/abcdefghijklmnopqrstuvwxyz/`）。
- **Handler 类**：以 `Handler` 结尾，如 `KeyPressHandler`、`UntieLivingHandler`。
- **Provider 类**：通用 Provider 用 `Mod*Provider`，如 `ModLangProvider`、`ModSoundProvider`；包元数据保留 `PackMetadataProvider`。
- **Mixin 类**：`Mixin + 目标类名`，见 [mixin.md](mixin.md)。
- **Mixin 接口**：`IMixin + 目标类名`，见 [mixin.md](mixin.md)。

## 判断归属

| 内容 | 归属 |
|---|---|
| 注册项本身、注册项的属性/行为定义、注册时必需的数据 | `registry/` |
| 使用非注册事件的回调与业务逻辑 | `handler/{client,common}/` |
| 不使用事件的领域逻辑、客户端状态或界面 | 所属功能包，如 `client/` |
| 纯工具方法 | `util/` |
| 对外暴露的稳定能力 | `api/` |
| 兼容专属的对外能力 | `compat/<被兼容modid>/api/` |
| 第三方模组兼容 | `compat/<被兼容modid>/` |
| 数据生成源与 Provider | `datagen/{lang,provider,util}/` |

边界不清时**先问用户**，不要自行扩大 `registry` 范围。
