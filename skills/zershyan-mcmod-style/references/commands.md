# 命令

## 位置与入口

- 注册入口为 `registry/<ModId>Commands.java`，通过 `doRegister(...)` 挂监听。
- 子命令放 `registry/command/`，需要的命令异常辅助类型放 `registry/command/exception/`。
- RegisterCommandsEvent 属于游戏总线：NeoForge.EVENT_BUS 或 MinecraftForge.EVENT_BUS，不是 mod 总线。

| 模板 | 入口 |
|---|---|
| NeoForge 1.21.1 | `doRegister(IEventBus neoBus)` |
| Forge 1.20.1 | 既有模板为 `doRegister(IEventBus forgeBus, IEventBus modBus)`，命令监听仍只挂 forgeBus |

保留目标工程已有的接入签名，不因为多传了 mod 总线就把命令监听挂错。

## 子命令组织

根字面量使用 modid 或功能名；每个子命令一个类，以 `static register(builder)` 接入共同根节点。例如：

```java
public static void commonCommandRegister(RegisterCommandsEvent event) {
    LiteralArgumentBuilder<CommandSourceStack> builder = Commands.literal(<ModId>.MODID);
    ChatModeCommand.register(builder);
    event.getDispatcher().register(builder);
}
```

复杂业务放对应领域方法，子命令负责参数读取、权限与前置条件校验、调用和反馈。危险操作设置匹配的权限，不因有根节点就默认所有子命令安全。

完整实现：[NeoForge 命令入口](../templates/neoforge1.21.1/src/main/java/io/zershyan/examplemod/registry/ExampleModCommands.java)、[Forge 命令入口](../templates/forge1.20.1/src/main/java/io/zershyan/examplemod/registry/ExampleModCommands.java)。

## 反馈与检查

- 反馈用可翻译组件，语言声明走 [Datagen](datagen.md)，不散落硬编码文案。
- 检查注册总线、执行端和线程，验证权限不足、参数边界与执行对象缺失。
- 验证成功与失败反馈，并确认所有子命令接入预期根节点。