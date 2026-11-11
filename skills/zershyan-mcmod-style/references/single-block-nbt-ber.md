# 单核心 NBT 驱动的伪多方块与越界 BER 渲染架构（Single-BlockEntity + Oversized BER）

适用于水车/风车组、大型仪式圣坛、修真阵盘、高阶工业设备等「视觉体量大于 1×1×1、但希望服务端保持单方块 O(1) 开销」的场景。

---

## 1. 核心设计思想

1. **合成/交互期拼装 NBT（或 `DataComponents`）**：
   - 不强制玩家在世界中逐格摆放几十个多方块组件；
   - 玩家可在合成台/锻造台中将扩展组件（如水车扇叶、轴承、祈祷烛台、供盘、阵旗、符石）与核心方块合成，或手持组件直接右键核心方块将其**吸收**进核心的 `DataComponents.CUSTOM_DATA`（1.21+ / 26.x）或 `CompoundTag`（1.20.1）中。
2. **服务端单核心 O(1) 结算**：
   - 世界中实际只存在 **1 个核心方块（`BlockPos`）与 1 个 `BlockEntity`**；
   - 服务端 `serverTick` 直接读取核心 NBT 中的组件计数、品阶、半径与拓扑参数计算产出/转速/圣域加成：
     `output = base * f(moduleCount, tier, environmentSample)`
   - 环境采样（如大水车检测底部/侧面水流）只需在 `serverTick` 低频（如每 20 tick）抽样 `pos.offset(...)` 几个关键坐标的 `FluidState` / `BlockState`。
3. **客户端越界 BER 渲染（Oversized `BlockEntityRenderer`）**：
   - 客户端 `BlockEntityRenderer<T>` 读取同步过来的 BlockEntity NBT 数据，使用 `PoseStack` 循环/矩阵变换，在中心方块四周直接渲染多个并列水车、3×3 台阶基座、四角烛台、悬浮法阵与旋转星环。
4. **核心定位与高亮线框（Core Highlight Outline）**：
   - 由于视觉模型远大于实际占据的 1×1×1 中心格，当玩家处于渲染范围内、准星靠近或手持对应工具（扳手、法杖、朝圣杖、罗盘）时，客户端在 `RenderLevelStageEvent`（或 `RenderHighlightEvent.Block`）中对中心 `BlockPos` 绘制醒目的高亮边框（以及可选的整体越界外框虚线），解决"找不到核心方块"的交互痛点。

---

## 2. 数据流总览

```
[合成台 / 手持组件右键]
        |  写入组件清单
        v
ItemStack(DataComponents.CUSTOM_DATA / BlockEntityTag)
        |  Block#setPlacedBy 或 吸收逻辑
        v
BlockEntity(server, 1 个)  --- getUpdateTag / getUpdatePacket --->  Client BlockEntity
        |                                                              |
        | serverTick: 读 NBT 计算产出（O(1)）                            | BER: 读 NBT 渲染 N 个部件
        v                                                              v
   物品栏/状态同步                                            PoseStack 多部件 + 越界 AABB
```

---

## 3. 落地必守的 4 条工程防坑规约

### 3.1 防视野剔除（Frustum Culling —— 转视角时大模型凭空消失）
- **病根**：Minecraft 默认仅按 `1×1×1` 方块碰撞箱做视锥体裁剪，当中心方块移出屏幕边缘时，尚在屏幕中央的 3×3/5×5 越界模型会瞬间消失。
- **强制写法**：
  - 在 `BlockEntity`（或 NeoForge 21.x/26.x 的 `IBlockEntityRendererExtension#getRenderBoundingBox`）中，根据当前 NBT 拼装半径动态膨胀渲染包围盒：
  ```java
  @Override
  public AABB getRenderBoundingBox() {
      int radius = Math.max(1, this.getModuleRadius());
      int height = Math.max(1, this.getModuleHeight());
      return new AABB(this.worldPosition).inflate(radius, height, radius);
  }
  ```
  - 同时在 `BlockEntityRenderer#shouldRenderOffScreen`（如适用）或 `getViewDistance()` 中保持充足可视距离。

### 3.2 放置与挖掘的数据闭环（`DataComponents` <-> `BlockEntity`）
- **放置时（Item -> BlockEntity）**：在 `Block#setPlacedBy` 中读取 `ItemStack` 的 `DataComponents.CUSTOM_DATA`（或自定义 `DataComponentType`），写入 `BlockEntity` 并调用 `setChanged()` + `level.sendBlockUpdated(pos, state, state, Block.UPDATE_CLIENTS)`。
- **同步时（Server -> Client）**：`BlockEntity` 必须完整实现 `getUpdateTag(HolderLookup.Provider)` 与 `getUpdatePacket()`（返回 `ClientboundBlockEntityDataPacket.create(this)`），确保客户端 BER 拿到最新拼装 NBT。
- **拆下时（BlockEntity -> Item Drop）**：在 `Block#playerWillDestroy` 或 LootTable `copy_components` 中将已拼装的 NBT/组件完整写回掉落物（或分拆退还已吸收的组件），严禁玩家一镐子拆掉后所有已拼装组件凭空蒸发。

### 3.3 碰撞与交互寻址（纯视觉虚体 vs 实体机械）
- **模式 A（纯单格核心 + 高亮引导，推荐用于法阵、圣坛虚影、小型组合水车）**：
  - 物理上只占中心 1 格；
  - 当玩家在中心 8 格内且屏幕视锥内包含该核心（或手持本模组交互物品/潜行）时，客户端自动给中心 1×1×1 核心方块绘制高对比度发光线框，让玩家一眼看到交互/挖掘点。
- **模式 B（中心核心 + 零 TileEntity 隐形占位块，用于不可穿模的巨型机械）**：
  - 若需要外圈具备实体碰撞且点击任意部位都能交互，只注册 1 个无 `BlockEntity` 的轻量占位块，右键/破坏占位块时通过相对偏移直接转发给中心 `BlockPos`。

### 3.4 渲染性能守则
- `BlockEntityRenderer#render` 每帧调用，**严禁**在 `render` 内每帧解析复杂 JSON、反射或新建大量集合对象；
- 将 NBT 解析结果缓存在 `BlockEntity` 的瞬态字段（`transient` 渲染快照）中，仅在 `loadAdditional` / `onDataPacket` 时更新一次；
- 静态子部件优先复用已烘焙的 `BakedModel`（`BlockRenderDispatcher#getBlockModel`），动态旋转部件（如水车轮、悬浮圣物、旋转阵盘）再用 `PoseStack#mulPose` 叠加旋转角。

---

## 4. 代码骨架

### 4.1 组件清单（服务端权威数据）

```java
public record ModuleSpec(String id, int count, int tier, float scale) {
    public static final Codec<ModuleSpec> CODEC = RecordCodecBuilder.create(i -> i.group(
            Codec.STRING.fieldOf("id").forGetter(ModuleSpec::id),
            Codec.INT.optionalFieldOf("count", 1).forGetter(ModuleSpec::count),
            Codec.INT.optionalFieldOf("tier", 0).forGetter(ModuleSpec::tier),
            Codec.FLOAT.optionalFieldOf("scale", 1.0F).forGetter(ModuleSpec::scale)
    ).apply(i, ModuleSpec::new));

    public static final Codec<List<ModuleSpec>> LIST_CODEC = CODEC.listOf();
}
```

写入物品（合成/吸收时）：

```java
public static ItemStack withModules(ItemStack stack, List<ModuleSpec> modules) {
    CompoundTag tag = new CompoundTag();
    tag.put("modules", ModuleSpec.LIST_CODEC.encodeStart(NbtOps.INSTANCE, modules).getOrThrow());
    stack.set(DataComponents.CUSTOM_DATA, CustomData.of(tag));
    return stack;
}
```

### 4.2 核心方块：放置继承 NBT

```java
@Override
public void setPlacedBy(Level level, BlockPos pos, BlockState state,
                        LivingEntity placer, ItemStack stack) {
    super.setPlacedBy(level, pos, state, placer, stack);
    if (level.getBlockEntity(pos) instanceof WaterWheelCoreBlockEntity be) {
        CustomData data = stack.get(DataComponents.CUSTOM_DATA);
        if (data != null) {
            be.readModules(data.copyTag());
            be.setChanged();
            level.sendBlockUpdated(pos, state, state, Block.UPDATE_CLIENTS);
        }
    }
}
```

### 4.3 核心 BlockEntity：NBT 读写 + 同步 + O(1) tick

```java
public class WaterWheelCoreBlockEntity extends BlockEntity {
    private List<ModuleSpec> modules = List.of();
    private int cachedRadius = 1;
    private int cachedHeight = 1;
    private int tickCounter;

    public WaterWheelCoreBlockEntity(BlockPos pos, BlockState state) {
        super(MyBlockEntities.WATER_WHEEL_CORE.get(), pos, state);
    }

    public void readModules(CompoundTag tag) {
        modules = ModuleSpec.LIST_CODEC
                .parse(NbtOps.INSTANCE, tag.getList("modules", Tag.TAG_COMPOUND))
                .resultOrPartial(err -> LOGGER.warn("bad modules: {}", err))
                .orElse(List.of());
        recomputeBounds();
    }

    private void recomputeBounds() {
        int radius = 1;
        int height = 1;
        for (ModuleSpec m : modules) {
            radius = Math.max(radius, Math.round(2.0F * m.scale() * Math.max(1, m.count())));
            height = Math.max(height, Math.round(3.0F * m.scale()));
        }
        cachedRadius = Math.min(radius, 16);
        cachedHeight = Math.min(height, 16);
    }

    public int getModuleRadius() { return cachedRadius; }
    public int getModuleHeight() { return cachedHeight; }

    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.saveAdditional(tag, registries);
        tag.put("modules", ModuleSpec.LIST_CODEC
                .encodeStart(NbtOps.INSTANCE, modules).getOrThrow());
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.loadAdditional(tag, registries);
        readModules(tag);
    }

    @Override
    public CompoundTag getUpdateTag(HolderLookup.Provider registries) {
        CompoundTag tag = new CompoundTag();
        saveAdditional(tag, registries);
        return tag;
    }

    @Override
    public Packet<ClientGamePacketListener> getUpdatePacket() {
        return ClientboundBlockEntityDataPacket.create(this);
    }

    public static void serverTick(Level level, BlockPos pos, BlockState state,
                                  WaterWheelCoreBlockEntity be) {
        if (level.isClientSide()) return;
        if (++be.tickCounter % 20 != 0) return;   // 低频环境采样
        int flow = sampleWaterFlow(level, pos);
        int output = computeOutput(be.modules, flow);
        if (output != be.lastOutput) {
            be.lastOutput = output;
            be.setChanged();
            level.sendBlockUpdated(pos, state, state, Block.UPDATE_CLIENTS);
        }
    }
}
```

### 4.4 客户端 BER：多部件 + 越界包围盒

```java
public class WaterWheelCoreRenderer implements BlockEntityRenderer<WaterWheelCoreBlockEntity> {
    public WaterWheelCoreRenderer(BlockEntityRendererProvider.Context ctx) {}

    @Override
    public void render(WaterWheelCoreBlockEntity be, float partialTick, PoseStack pose,
                       MultiBufferSource buffers, int packedLight, int packedOverlay) {
        List<ModuleSpec> modules = be.modulesSnapshot();   // 预解析快照，勿在 render 内解析 NBT
        float spin = (be.getLevel().getGameTime() + partialTick) * 0.6F;

        for (int i = 0; i < modules.size(); i++) {
            ModuleSpec m = modules.get(i);
            pose.pushPose();
            pose.translate(0.5, 0.5, 0.5);
            pose.mulPose(Axis.YP.rotationDegrees(i * (360.0F / Math.max(1, modules.size()))));
            pose.translate(0.0, 0.0, 1.5 * m.scale());
            pose.mulPose(Axis.ZP.rotationDegrees(spin));
            pose.scale(m.scale(), m.scale(), m.scale());
            renderWheelBlades(pose, buffers, packedLight, packedOverlay, m.tier());
            pose.popPose();
        }
    }

    @Override
    public AABB getRenderBoundingBox(WaterWheelCoreBlockEntity be) {
        return new AABB(be.getBlockPos()).inflate(be.getModuleRadius(), be.getModuleHeight(),
                be.getModuleRadius());
    }

    @Override
    public int getViewDistance() { return 128; }
}
```

注册（客户端事件）：

```java
@SubscribeEvent
static void onRegisterRenderers(EntityRenderersEvent.RegisterRenderers event) {
    event.registerBlockEntityRenderer(MyBlockEntities.WATER_WHEEL_CORE.get(),
            WaterWheelCoreRenderer::new);
}
```

### 4.5 核心高亮边框（近距 / 视野内 / 手持工具）

```java
@SubscribeEvent
static void onRenderLevelStage(RenderLevelStageEvent event) {
    if (event.getStage() != RenderLevelStageEvent.Stage.AFTER_TRANSLUCENT_BLOCKS) return;
    Minecraft mc = Minecraft.getInstance();
    LocalPlayer player = mc.player;
    if (player == null) return;

    Vec3 eye = player.getEyePosition();
    boolean holdingTool = player.getMainHandItem().is(MyTags.CORE_TOOLS)
            || player.getOffhandItem().is(MyTags.CORE_TOOLS);

    PoseStack pose = event.getPoseStack();
    Vec3 cam = event.getCamera().getPosition();
    pose.pushPose();
    pose.translate(-cam.x, -cam.y, -cam.z);

    for (BlockPos core : CoreLocator.visibleCores(player.level(), eye, 32.0)) {
        double dist = eye.distanceTo(Vec3.atCenterOf(core));
        boolean inView = mc.getEntityRenderDispatcher().camera.getFrustum()
                .isVisible(new AABB(core).inflate(2.0));
        if (!inView) continue;
        if (dist > 24.0 && !holdingTool) continue;   // 远处只在手持工具时提示

        float pulse = 0.55F + 0.25F * (float) Math.sin(player.tickCount * 0.15F);
        RenderType lines = RenderType.lines();
        VertexConsumer vc = event.getLevelRenderer().renderBuffers.bufferSource().getBuffer(lines);
        ShapeRenderer.renderLineBox(pose, vc, new AABB(core).inflate(0.02),
                pulse, 0.85F, 0.35F, 0.9F);
        if (dist <= 8.0) {   // 近距再加一层越界虚线，指出整组结构范围
            int r = CoreLocator.radiusOf(player.level(), core);
            ShapeRenderer.renderLineBox(pose, vc,
                    new AABB(core).inflate(r + 0.1, r * 0.5 + 0.1, r + 0.1),
                    0.45F, 0.9F, 1.0F, 0.45F);
        }
    }
    pose.popPose();
}
```

要点：

- 高亮只在客户端绘制，不参与碰撞、不影响服务端 tick；
- `AFTER_TRANSLUCENT_BLOCKS` 阶段可保证线框不被方块遮挡得太干净，也不会盖住 GUI；
- 线框颜色取高对比暖色（橙/青），避免与圣坛金色、法阵蓝色混淆；
- 距离阈值建议：8 格内常显核心框 + 结构虚框；8~24 格仅核心框；24 格外仅手持对应工具时显示。

### 4.6 拆下时归还组件

```java
@Override
public BlockState playerWillDestroy(Level level, BlockPos pos, BlockState state, Player player) {
    if (!level.isClientSide() && level.getBlockEntity(pos) instanceof WaterWheelCoreBlockEntity be) {
        ItemStack drop = new ItemStack(this);
        CompoundTag tag = new CompoundTag();
        tag.put("modules", ModuleSpec.LIST_CODEC
                .encodeStart(NbtOps.INSTANCE, be.modulesSnapshot()).getOrThrow());
        drop.set(DataComponents.CUSTOM_DATA, CustomData.of(tag));
        Block.popResource(level, pos, drop);
    }
    return super.playerWillDestroy(level, pos, state, player);
}
```

---

## 5. 门禁与自检清单

| 检查项 | 判定 |
|---|---|
| 世界内核心方块数量 | 拼装后仍为 1 个方块 + 1 个 BlockEntity |
| `getUpdateTag` / `getUpdatePacket` | 均实现，且 `saveAdditional` 覆盖全部拼装字段 |
| 渲染包围盒 | `getRenderBoundingBox` 按 NBT 半径/高度膨胀，不写死 1×1×1 |
| `render` 内 NBT 解析 | 0 次；全部走瞬态快照 |
| 拆下归还 | 组件数守恒：放下前 N 个，拆下后掉落物仍为 N 个 |
| 高亮触发 | 近距 / 视野内 / 手持工具三条件之一命中即显示，且不写服务端状态 |
| 服务端 tick | 环境采样降频（>= 20 tick），无每 tick 全量扫描 |

---

## 6. 与 3D 方块物品规约的衔接

- 该核心方块的物品模型必须直接指向 `<mod>:block/<core>`，不再画 2D 物品图（见 playbook 11.3）；
- 若核心方块本身是多方块拼装产物，创造栏只保留"空核心"，不提供已预装组件的变体；
- 预览图可用 `tools/render_block_models_preview.py --root <workspace>` 离线生成，不启动游戏。

