# 单核心 NBT 驱动的伪多方块与越界 BER 渲染架构（Single-BlockEntity + Oversized BER）

适用于水车/风车组、大型仪式圣坛、修真阵盘、高阶工业设备等「视觉体量大于 1×1×1、但希望服务端保持单方块 O(1) 开销」的场景。

---

## 1. 核心设计思想

1. **合成/交互期拼装 NBT（或 `DataComponents`）**：
   - 不强制玩家在世界中逐格摆放几十个多方块组件；
   - 玩家可在合成台/锻造台中将扩展组件（如水车扇叶、轴承、祈祷烛台、供盘、阵旗、符石）与核心方块合成，或手持组件直接右键核心方块将其**吸收**进核心的 `DataComponents.CUSTOM_DATA`（1.21+ / 26.x）或 `CompoundTag`（1.20.1）中。
2. **服务端单核心 $O(1)$ 结算**：
   - 世界中实际只存在 **1 个核心方块（`BlockPos`）与 1 个 `BlockEntity`**；
   - 服务端 `serverTick` 直接读取核心 NBT 中的组件计数、品阶、半径与拓扑参数计算产出/转速/圣域加成：
     `output = base * f(moduleCount, tier, environmentSample)`
   - 环境采样（如大水车检测底部/侧面水流）只需在 `serverTick` 低频（如每 20 tick）抽样 `pos.offset(...)` 几个关键坐标的 `FluidState` / `BlockState`。
3. **客户端越界 BER 渲染（Oversized `BlockEntityRenderer`）**：
   - 客户端 `BlockEntityRenderer<T>` 读取同步过来的 BlockEntity NBT 数据，使用 `PoseStack` 循环/矩阵变换，在中心方块四周直接渲染多个并列水车、3×3 台阶基座、四角烛台、悬浮法阵与旋转星环。
4. **核心定位与高亮线框（Core Highlight Outline）**：
   - 由于视觉模型远大于实际占据的 1×1×1 中心格，当玩家处于渲染范围内、准星靠近或手持对应工具（扳手、法杖、朝圣杖、罗盘）时，客户端在 `RenderLevelStageEvent`（或 `RenderHighlightEvent.Block`）中对中心 `BlockPos` 绘制醒目的高亮边框（以及可选的整体越界外框虚线），解决“找不到核心方块”的交互痛点。

---

## 2. 落地必守的 4 条工程防坑规约

### 2.1 防视野剔除（Frustum Culling —— 转视角时大模型凭空消失）
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

### 2.2 放置与挖掘的数据闭环（`DataComponents` <-> `BlockEntity`）
- **放置时（Item -> BlockEntity）**：在 `Block#setPlacedBy` 中读取 `ItemStack` 的 `DataComponents.CUSTOM_DATA`（或自定义 `DataComponentType`），写入 `BlockEntity` 并调用 `setChanged()` + `level.sendBlockUpdated(pos, state, state, Block.UPDATE_CLIENTS)`。
- **同步时（Server -> Client）**：`BlockEntity` 必须完整实现 `getUpdateTag(HolderLookup.Provider)` 与 `getUpdatePacket()`（返回 `ClientboundBlockEntityDataPacket.create(this)`），确保客户端 BER 拿到最新拼装 NBT。
- **拆下时（BlockEntity -> Item Drop）**：在 `Block#playerWillDestroy` 或 LootTable `copy_components` 中将已拼装的 NBT/组件完整写回掉落物（或分拆退还已吸收的组件），严禁玩家一镐子拆掉后所有已拼装组件凭空蒸发。

### 2.3 碰撞与交互寻址（纯视觉虚体 vs 实体机械）
- **模式 A（纯单格核心 + 高亮引导，推荐用于法阵、圣坛虚影、小型组合水车）**：
  - 物理上只占中心 1 格；
  - 当玩家在中心 8 格内且屏幕视锥内包含该核心（或手持本模组交互物品/潜行）时，客户端自动给中心 1×1×1 核心方块绘制高对比度发光线框，让玩家一眼看到交互/挖掘点。
- **模式 B（中心核心 + 零 TileEntity 隐形占位块，用于不可穿模的巨型机械）**：
  - 若需要外圈具备实体碰撞且点击任意部位都能交互，只注册 1 个无 `BlockEntity` 的轻量占位块，右键/破坏占位块时通过相对偏移直接转发给中心 `BlockPos`。

### 2.4 渲染性能守则
- `BlockEntityRenderer#render` 每帧调用，**严禁**在 `render` 内每帧解析复杂 JSON、反射或新建大量集合对象；
- 将 NBT 解析结果缓存在 `BlockEntity` 的瞬态字段（`transient` 渲染快照）中，仅在 `loadAdditional` / `onDataPacket` 时更新一次；
- 静态子部件优先复用已烘焙的 `BakedModel`（`BlockRenderDispatcher#getBlockModel`），动态旋转部件（如水车轮、悬浮圣物、旋转阵盘）再用 `PoseStack#mulPose` 叠加旋转角。
