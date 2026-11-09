# 附件与能力

## 选择与归属

| 场景 | 约定 |
|---|---|
| NeoForge 1.21.1 新附件 | 使用 Attachment，不为统一风格改成 Capability |
| Forge 1.20.1 需要玩家持久化数据 | 优先使用 ForgeAttachment，先探测 sigh Maven 上的可用版本；引入后为运行时必需依赖 |
| 已有 Forge Capability 工程 | 保留既有结构，不擅自迁移 |
| 其他附件需求 | 按需引入 ForgeAttachment；普通网络消息或 ItemStack NBT 不构成引入理由 |

其他 MC / 加载器版本先核实支持范围，不直接照搬模板实现；附件与能力的组织约定仍适用。需求或迁移方案不明时再向用户确认。

## 附件结构

```text
registry/
├── <ModId>Attachments.java
└── attachment/
    ├── BindStatusData.java
    ├── ChatModeData.java
    └── sub/
        ├── EntityDto.java
        └── TieStats.java
```

入口为 `<ModId>Attachments.doRegister(IEventBus)`，数据类属于注册时必需数据，放 `registry/attachment/`；嵌套辅助结构放 `sub/`。判定见 [注册](registry.md)。

ForgeAttachment 的仓库、导入、能力边界与同步细节统一见 [接入专页](forgeattachment.md)。引入时必须告知用途、运行时安装要求，并提供 GitHub / MC百科 / CurseForge 项目链接或明确未发布状态。

已有 Capability 的入口仍为 `registry/<ModId>Capabilities.java`，实现留在 `capability/`，如 `<Feature>DataCapability`。这是既有工程兼容约定，不作为新附件的第二套实现。

## 数据与同步

- 先判断数据是否需要持久化、死亡复制与客户端同步；可以推导的状态不为统一结构而额外存储。
- 服务端保持权威，客户端可见数据通过附件同步或 [网络包](network.md) 传递。
- 服务端校验客户端请求，不把客户端缓存作为权威；客户端容忍对象或数据尚未到达。

## 完成前检查

- 方案与目标世代相符，附件注册和数据位置正确？
- ForgeAttachment 是否仅在需要时引入，用户告知和依赖声明是否完整？
- 数据是否在正确端读写，已按实际启用能力验证保存、复制和同步？