# 网络

## 共同约定

- 注册入口为 `registry/<ModId>Packets.java`，消息类放 `registry/packet/`，相关消息可再按功能分子包。
- 处理器是消息自身的 `handle(...)` 实例方法，注册时使用 `XxxPacket::handle`；不额外传一次 payload，也不拆公共 ClientPayloadHandler / ServerPayloadHandler。
- 复杂逻辑委托给领域方法。游戏状态只在主线程读写；服务端重新校验权限、目标、数量、距离与状态，不信任客户端字段。
- 网络注册处必须接入 `CompatFactory.registerNetwork(...)`，让可选兼容消息通过同一入口注册。见 [兼容规则](compat.md)。

## 协议版本

默认使用本模组**完整元数据版本**，不硬编码 `"1"`。NeoForge 1.21.1 的取值形态为：

```java
@NotNull
private static final String PROTOCOL_VERSION = ModList.get()
        .getModContainerById(<ModId>.MODID)
        .map(ModContainer::getModInfo)
        .map(IModInfo::getVersion)
        .map(Object::toString)
        .orElse("unknown");
```

Forge 1.20.1 使用对应加载器的 ModList / ModContainer / IModInfo，取值原则不变。

- 完整版本含 MC 版本与构建号，两端不同则拒绝连接，避免不兼容消息被解码。
- **只有 `buildAlpha` 增加编号，普通 `build` 复用编号**；协议版本不是每次编译都会变化。行为见 [版本号与产物](versioning.md)。
- 若要放宽兼容范围，先明确格式兼容策略，再选择版本粒度；不要退回无关联的固定字符串。

## NeoForge 1.21.1

### 消息与注册

使用 `record implements CustomPacketPayload`：

```java
public record RidePlayerPacket(UUID uuid) implements CustomPacketPayload {
    public static final Type<RidePlayerPacket> TYPE = new Type<>(<ModId>.id("ride_player"));
    public static final StreamCodec<ByteBuf, RidePlayerPacket> STREAM_CODEC = StreamCodec.composite(
            UUIDUtil.STREAM_CODEC, RidePlayerPacket::uuid, RidePlayerPacket::new);

    @Override
    public @NotNull Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }
}
```

`TYPE` 路径使用 `lower_snake_case`；Codec 字段顺序与 record 分量一致。无字段消息可用 `StreamCodec.unit(...)`。

`doRegister(IEventBus modBus)` 监听 `RegisterPayloadHandlersEvent`，在回调中创建 `event.registrar(PROTOCOL_VERSION)`，然后按方向注册：

```java
registrar.playToServer(ExampleRequestPacket.TYPE, ExampleRequestPacket.STREAM_CODEC, ExampleRequestPacket::handle);
registrar.playToClient(ExampleSyncPacket.TYPE, ExampleSyncPacket.STREAM_CODEC, ExampleSyncPacket::handle);
<ModId>CompatFactory.registerNetwork(registrar);
```

### 处理与发送

- 方法签名为 `public void handle(IPayloadContext context)`，通过实例字段或访问器取消息数据。
- 游戏状态操作包在 `context.enqueueWork(...)` 内；服务端先确认 `context.player()` 是 ServerPlayer，再根据服务器状态执行请求。
- 客户端专属调用只放在客户端处理路径中，不在消息的静态字段、构造器或通用初始化中访问 Minecraft。注册为 `playToClient` 不等于所有类引用自动安全，仍须验证专用服务器加载。
- 使用 NeoForge 的 `PacketDistributor.sendToPlayer`、`sendToServer`、`sendToAllPlayers` 等方法发送。

完整实现：[注册入口](../templates/neoforge1.21.1/src/main/java/io/zershyan/examplemod/registry/ExampleModPackets.java)、[请求消息](../templates/neoforge1.21.1/src/main/java/io/zershyan/examplemod/registry/packet/ExampleRequestPacket.java)、[同步消息](../templates/neoforge1.21.1/src/main/java/io/zershyan/examplemod/registry/packet/ExampleSyncPacket.java)。

## Forge 1.20.1

使用 `net.minecraftforge.network.simple.SimpleChannel`，不引入 NeoForge 的 CustomPacketPayload、PayloadRegistrar 或网络 Codec。

```java
public static final SimpleChannel INSTANCE = NetworkRegistry.newSimpleChannel(
        <ModId>.id(<ModId>.MODID), () -> PROTOCOL_VERSION,
        PROTOCOL_VERSION::equals, PROTOCOL_VERSION::equals);

public static void doRegister() {
    INSTANCE.messageBuilder(ExampleRequestPacket.class, 0, NetworkDirection.PLAY_TO_SERVER)
            .decoder(ExampleRequestPacket::new)
            .encoder(ExampleRequestPacket::encode)
            .consumerMainThread(ExampleRequestPacket::handle)
            .add();
    <ModId>CompatFactory.registerNetwork(INSTANCE);
}
```

- 消息编号互不重复且顺序稳定；兼容层共用 channel 时也不能复用已有编号。
- 每个消息实现 `encode(FriendlyByteBuf)`、解码构造器和 `handle(Supplier<NetworkEvent.Context>)`。上下文是 `net.minecraftforge.network.NetworkEvent.Context`，不是其他版本的 CustomPayloadEvent.Context。
- `consumerMainThread` 已调度到主线程并标记消息已处理，不重复 `enqueueWork`。使用网络线程消费者时，必须自行调度和标记。
- `getSender()` 可能为 null，服务端必须检查并校验请求。
- 发送到服务端用 `INSTANCE.sendToServer(message)`；发给玩家用 `INSTANCE.send(PacketDistributor.PLAYER.with(() -> player), message)`，PacketDistributor 来自 Forge。

完整实现：[注册入口](../templates/forge1.20.1/src/main/java/io/zershyan/examplemod/registry/ExampleModPackets.java)、[请求消息](../templates/forge1.20.1/src/main/java/io/zershyan/examplemod/registry/packet/ExampleRequestPacket.java)、[同步消息](../templates/forge1.20.1/src/main/java/io/zershyan/examplemod/registry/packet/ExampleSyncPacket.java)。

模板请求会读取附件，仅用于演示；**普通网络消息不构成引入 ForgeAttachment 的理由**。保留自己的业务逻辑即可，无附件需求时裁剪相关调用。附件依赖的流编解码器不改变普通消息使用 SimpleChannel 的方案。

## 完成前检查

- 编解码字段、顺序与消息方向正确，协议版本来自模组元数据？
- 状态读写位于主线程，服务端验证客户端请求，客户端专属类未提前链接？
- 可选兼容消息接入工厂，依赖缺失时不加载第三方类？
- 消息往返和边界值已验证；模板或旧版通过记录不能替代本轮测试？