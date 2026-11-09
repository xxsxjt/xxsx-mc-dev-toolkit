# Forge 1.20.1 附件依赖（ForgeAttachment）

## 接入边界

- **玩家持久化数据优先用 ForgeAttachment**：Forge 模组需要保存玩家数据（重进世界保留、死亡复制、服务端到客户端同步）时，一律先探测 sigh Maven 上的可用版本，固定具体版本后引入；不另造 Capability 或 NBT 方案。
- 其他对象按需引入；普通 SimpleChannel 消息、ItemStack NBT 不构成引入理由，不需要就裁剪模板演示及其依赖，见 [构建与发布](build.md)。
- 本页基线为 Forge 47.3.4、Java 17、LegacyForge。不要搬入 NeoForge 的附件类，也不为新附件另造 Capability 存储；已有 Capability 工程不强制迁移。
- **优先使用不等于运行时可选**：实际使用后声明为必需依赖，不放进软兼容层，不用 `mandatory=false` 掩盖依赖。
- 依赖支持实体、方块实体附件，不能由此推断区块、世界或 ItemStack 也支持。注册入口与数据类按 [附件与能力](attachments.md) 组织。

## 必须告知用户

引入时主动说明原因、使用它的功能和运行时需要单独安装匹配版本；同时提供以下三个平台的**项目链接或明确发布状态**：

| 平台 | 项目链接或已记录状态 |
|---|---|
| GitHub | [Zershyan/forgeattachment](https://github.com/Zershyan/forgeattachment) |
| MC百科（mcmod） | 暂未发布；发布后补充真实项目页 |
| CurseForge | 按实际发布状态提供项目链接；未发布时如实说明，并请用户手动提供 jar |

未发布状态来自用户提供的信息，后续接入时核实并更新。无法确认时如实说明；不编造项目页，也不把平台首页当项目链接。不能只静默修改构建脚本。

## 仓库、版本与元数据

**接入前先探测 sigh Maven 上的最新正式版**：读 `https://maven.sighs.cc/repository/maven-public/io/zershyan/forgeattachment/maven-metadata.xml`，取 `<release>` 作为最新正式版；它不匹配目标 MC 版本时，再从 `<versions>` 里筛掉带 `+build.<编号>` 的开发版，取匹配版本的最新一条。

```properties
forgeattachment_version=0.0.1-1.20.1
```

```groovy
repositories {
    maven {
        name = 'MafuyuNexus'
        url = 'https://maven.sighs.cc/repository/maven-public/'
    }
}

dependencies {
    modImplementation "io.zershyan:forgeattachment:${forgeattachment_version}"
}
```

变量必须固定具体版本，不用 `+`、范围或 `latest.release`；`+build.<编号>` 是开发版后缀，对外接入优先取正式版。

**拿不到可用正式版时不要自行降级或换镜像**：把 ForgeAttachment 的 CurseForge 项目链接发给用户，请其手动下载 jar 并发到会话，再按 [依赖声明](build.md) 的本地 jar 方式（放 `libs/`，坐标 `blank:<name>:<version>`）接入，并说明这是绕行方案。

在 Forge 的 `META-INF/mods.toml` 同时声明，不能替换成 NeoForge 的 `type="required"`：

```toml
[[dependencies."<modid>"]]
modId="forgeattachment"
mandatory=true
versionRange="[0.0.1,)"
ordering="NONE"
side="BOTH"
```

不在下游 jar 中再打包一份依赖，运行环境同时安装两个模组。

## 导入与注册

| 用途 | 类型 |
|---|---|
| 附件类型 | `io.zershyan.forgeattachment.attachment.AttachmentType` |
| 持有者接口 | `io.zershyan.forgeattachment.attachment.IAttachmentHolder` |
| 实体 / 方块实体门面 | `io.zershyan.forgeattachment.api.ForgeAttachmentApi` |
| 注册表键 | `io.zershyan.forgeattachment.registry.ForgeAttachmentRegistries.ATTACHMENT_TYPES_KEY` |
| 注册表缓冲区 | `io.zershyan.forgeattachment.network.RegistryFriendlyByteBuf` |
| 流编解码器 | `io.zershyan.forgeattachment.network.codec.StreamCodec` |
| 基础流编解码器 | `io.zershyan.forgeattachment.network.codec.ByteBufCodecs` |
| 常用对象编解码器 | `io.zershyan.forgeattachment.api.Codecs`、`StreamCodecs` |

`FriendlyByteBuf` 仍是 Minecraft 的类型；不要导入 1.21.1 的 `net.minecraft.network.codec.StreamCodec` 或 `net.minecraft.network.RegistryFriendlyByteBuf`。

注册使用 Forge 的 DeferredRegister / RegistryObject 与依赖的附件注册表键。入口 `registry/<ModId>Attachments.doRegister(IEventBus)` 由主类调用，数据类放 `registry/attachment/`。

实现：[附件注册](../templates/forge1.20.1/src/main/java/io/zershyan/examplemod/registry/ExampleModAttachments.java)、[附件数据](../templates/forge1.20.1/src/main/java/io/zershyan/examplemod/registry/attachment/ExampleStatusData.java)。

## 数据能力

以下能力分别按需求启用，不要求所有附件都同时开启：

| 配置 | 语义与约束 |
|---|---|
| `serialize(CODEC)` | 逻辑服务端持久化；稳定扩展字段时设计兼容默认值，不随意改存档键 |
| `copyOnDeath()` | 玩家死亡重生 / 生物转化时复制；先配置序列化器。依赖已处理复制事件，不重复添加 PlayerEvent.Clone 逻辑 |
| `sync(STREAM_CODEC)` | 服务端到客户端同步，不代替服务端校验请求 |

可变默认数据必须为每个 holder 创建独立实例，不能让多个玩家共享。基础数值用 Codec / ByteBufCodecs，常用对象优先复用依赖公开的 Codecs / StreamCodecs，多字段用 RecordCodecBuilder / StreamCodec.composite。涉及注册表的数据使用依赖的 RegistryFriendlyByteBuf；集合、字符串和 NBT 解码设置合理上限。

## 访问与修改

Forge 实体源码没有 `getData(...)`，不直接照搬 `player.getData(...)`。先取得持有者接口：

```java
if (player instanceof IAttachmentHolder holder) {
    ExampleStatusData data = holder.getData(ExampleModAttachments.STATUS);
    data.setValue(newValue);
    holder.syncData(ExampleModAttachments.STATUS);
}
```

或使用 `ForgeAttachmentApi.getData(entity, type)`；不支持该对象时返回 null，调用者必须处理。

| 操作 | 行为 |
|---|---|
| `getData(type)` | 不存在则创建默认值，创建触发已配置的同步 |
| `getExistingData(type)` / `getExistingDataOrNull(type)` | 只取已有数据，不创建 |
| `setData(type, value)` | 替换数据、返回旧值，触发已配置的同步 |
| `removeData(type)` | 移除附件，触发已配置的移除同步 |
| 对数据对象原地修改 | 不会自动检测，必须显式 `syncData(type)` |

方块实体修改后还要调用 `setChanged()`，同步不能代替区块保存标记。

## 同步与验证

- 默认同步面向相关客户端，不等于只发送给所属玩家；私密数据用带过滤器的重载限定接收者。
- 依赖处理跟踪 / 观察开始时的初始同步；客户端仍需容忍对象或数据尚未到达，服务端保持权威。
- 只在变更或确有刷新需求时同步，不每 tick 无条件发包。普通模组消息仍用 [SimpleChannel](network.md)。
- 检查依赖、版本变量（取自 Maven 探测结果）与必需元数据对应，用户告知完整，注册经 `doRegister` 接入。
- 按启用能力验证重进世界持久化、死亡复制、初始与后续同步，以及客户端缺数据和专用服务器场景。
- 执行 `compileJava`、`runData`；依赖下载失败如实记录，不把离线源码核对当成构建通过。
