# Minecraft Mod 开发操作手册（全机共享）

本文件是**跨 Agent 共享的 MC 开发操作经验**，属于 PUBLIC 核心区，位于 `<INSTANCE_ROOT>/CORE`。
它补充 `WORKSPACE-INDEX.md` 的 MC 路由，不改变任何路径、隐私或迁移标准。

- 适用对象：所有在本机做 Minecraft Mod 开发的 Agent（Codex、Claude、Pi、OpenCode 等）
- 适用范围：**仅 MC Mod 开发任务**。非 MC 任务不需要读本文件
- 维护：内容随验证更新；结论必须带验证日期

## 1. 权威顺序

1. 安全边界：`<INSTANCE_ROOT>/USER_POLICY.md`
2. 全机标准：`<INSTANCE_ROOT>/CORE/WORKSPACE-INDEX.md`
3. 本手册：MC 开发操作经验
4. 单个 mod 仓库：该仓库自己的 `README.md` / `docs/` / `ACCEPTANCE.md`

项目文档与手册冲突时，以项目当前状态为准；手册只提供通用做法与已验证结论。

## 2. 工具入口

工作区工具位于 `tools/`，纯标准库、只读。

```bash
# 扫描所有 mod 仓库的多版本工程配置
python tools/mcver.py audit

# 校验构建产物：split package、modId 一致性
python tools/mcver.py jars
python tools/mcver.py jars <模块>/build/libs

# 输出 MC 版本 x loader x mod 支持矩阵
python tools/mcver.py matrix

# 体检游戏实例：loader 版本、依赖、冲突、已移除 API
python tools/mcver.py doctor <实例目录>

# 对比两个 NeoForge universal jar 的类差异
python tools/mcver.py diff <旧 jar> <新 jar>
```

退出码 0 = 通过，1 = 有问题。全部只读，不修改任何文件。

## 3. 多版本工程结构

### 目录约定

```
<mod>/
├── common/src/main/java/          # 与版本无关的源码
├── neoforge-26.2/                 # 一个 target 一个目录
├── neoforge-26.1.2/
└── gradle.properties              # 代理与 JDK 路径，不放版本号
```

每个 target 独立 `gradlew`，互不影响。`common` 通过 `srcDirs` 引入。

### 新增 target

```bash
python tools/mcver_target.py <repo> --name neoforge-26.3 \
    --mc 26.3 --loader neoforge --loader-version 26.3.0.1 \
    --java 25 --moddev 2.0.148 --dry-run
```

确认替换项后去掉 `--dry-run`。它会复制最近的同类 target，改写 `build.gradle` 的版本号、
产物名、ModDevGradle 版本，以及 `neoforge.mods.toml` 的 `versionRange`。不会覆盖已存在的 target。

### 已验证组合

| MC | NeoForge | ModDevGradle | Gradle | Java |
|---|---|---|---|---|
| 26.2 | 26.2.0.93 | 2.0.140 / 2.0.148 | 9.2.1 | 25 |
| 26.1.2 | 26.1.2.124 | 2.0.140 / 2.0.148 | 9.2.1 | 25 |
| 1.20.1 | Forge 47.4.20 | ForgeGradle 6.x | 8.8 | 17 |

## 4. 双 jar 结构（核心 + 扩展）

### 包不能重叠

核心 jar 与扩展 jar 导出同一个 Java 包会触发 JPMS split package：

```
java.lang.module.ResolutionException: Modules A and B export package X to module Y
```

做法：

- 桥接 API 单独一个包，只由核心 jar 提供
- 处理器与 entrypoint 放另一个包，只由扩展 jar 提供
- 核心通过静态 `register` / `unregister` 与扩展连接，编译期不依赖扩展类

### 扩展 jar 必须自带 mod 元数据

扩展 jar 也要有 `META-INF/neoforge.mods.toml`，并声明对核心的依赖：

```toml
[[dependencies.<扩展 modid>]]
modId="<核心 modid>"
type="required"
versionRange="[<最低版本>,)"
ordering="AFTER"
side="CLIENT"
```

`ordering="AFTER"` 必须写：扩展的 `@Mod` 构造器会调用核心的桥接 `register`。

### modId 一致性

`mods.toml` 的 `modId` 与 `@Mod` 注解常量必须是同一个字符串。
不一致时编译通过、构建成功，只在运行时崩溃。用 `mcver.py jars` 检查。

## 5. NeoForge 版本差异

升级 NeoForge 前必须确认删除的 API：

```bash
python tools/mcver.py diff \
  "<libraries>/net/neoforged/neoforge/<旧版本>/neoforge-<旧版本>-universal.jar" \
  "<libraries>/net/neoforged/neoforge/<新版本>/neoforge-<新版本>-universal.jar"
```

### 26.2.0.7-beta → 26.2.0.93（实测）

类数 1,698 → 1,741，删除 4 个、新增 37 个。

| 删除 | 替代 |
|---|---|
| `client.event.ContainerScreenEvent` | `client.event.ScreenEvent$Render$Background` / `$Foreground` |
| `client.gui.ModListScreen` | `client.gui.modlist.ModListScreen` |
| `client.gui.widget.ModListWidget` | `client.gui.widget.*` |
| `event.entity.player.PlayerInteractEvent$EntityInteractSpecific` | `PlayerInteractEvent$EntityInteract` |

注意：`ContainerScreenEvent` 在 26.1.2 与 26.2.0.7-beta 都存在，只在 26.2.0.93 起被删除；
`ScreenEvent` 三个版本都有。不要凭印象判断迁移方向。

### 26.1.2.124 → 26.2.0.7-beta（实测）

类数 1,716 → 1,698，删除 18 个、新增 7 个。跨 MC 版本还伴随 asset index 30 → 32。

## 6. 游戏实例

### 位置

```
<INSTANCE_ROOT>/_Games/MC/xxxxxx/.minecraft/versions/<实例名>/
```

`<INSTANCE_ROOT>` 属受限根：读取与写入都需要**当前任务明确授权**，不能从历史任务推断。

### NeoForge 升级流程（PCL 实例）

PCL 的实例 JSON 是自包含的（无 `inheritsFrom`），由 vanilla JSON + NeoForge 库合并而成。

1. 备份实例 JSON、`PCL/Setup.ini`、`.minecraft/PCL.ini`
2. 下载 `neoforge-<ver>-installer.jar`，用 `--install-client` 装到 `.minecraft`
3. 合并 `vanilla.libraries + neo.libraries`、`vanilla.arguments + neo.arguments`
4. 写回原实例 JSON，`id` 保持原实例名
5. 更新 `PCL/Setup.ini` 的 `VersionNeoForge` 与 `Info`（GBK 编码）
6. 运行 `mcver.py doctor <实例目录>` 核对

### 常见报错

| 现象 | 原因 | 处理 |
|---|---|---|
| `Missing or unsupported mandatory dependencies` | mod 要求更高 NeoForge | 升级 loader |
| `NoClassDefFoundError: net/neoforged/...` | mod 用了被移除的 API | 该 mod 需按新 API 重编 |
| 资源缺失 | 新 MC 版本 asset index 未下载 | 按 index 补 `assets/objects/<hash[0:2]>/<hash>` |
| PCL 不显示新实例 | 缺 `PCL/Setup.ini` | 按同格式写一份 |

### 版本选择的现实约束

同一 MC 版本下，mod 生态与 loader API 会互相拉扯。实例报“需要更高 loader”时，
先确认**所有** mod 在新 loader 上仍能加载，否则会从一类错误换到另一类错误。

## 7. 验证与证据分层

> **硬性禁令：未经允许严禁擅自启动游戏客户端（2026-11-02）**
> - 除非用户在**当前任务**中明确指示“启动客户端/启动游戏测试”，任何 Agent **绝对不得**执行 `gradlew runClient`、不得拉起启动器或游戏窗口、不得编写启动客户端的冒烟测试脚本（如 `test_client_smoke.py`）。
> - 原因：客户端窗口与音频会直接打断用户操作，且游戏内画面/交互验收由用户本人执行。
> - Agent 侧的客户端代码验证应通过编译检查、AST/正则静态树核对（如核对 `addOrReplaceChild` 与 `getChild`）、字节码反编译（`javap -c`）、资源 JSON 校验或无窗口单元测试完成；部署后将状态如实记为“已部署，待用户启动客户端验证”。

| 层 | 证据 | 能得出的结论 |
|---|---|---|
| 源码/静态 | 编译通过、静态检查 | 源码完成、构建通过 |
| 构建/部署 | `build/libs` 产物、SHA-256、实例文件 | 构建通过、已部署 |
| 运行/发布 | 启动日志、游戏内操作、远端页面 | 已启动、功能验证通过、已发布 |

`mcver.py doctor` 只是静态检查，**不能替代启动验证**。

建议顺序：注册 → 创造栏 → `/give` → 放置/破坏/右键 → GUI/网络 → 库存/合成 → 可选兼容 → 日志。

## 8. 发布

- 多版本发布按 **MC 版本 / Loader / mod 版本 / jar 文件名** 写清楚
- 明确区分未更新、未测试、未发布
- GitHub Release 的 assets 数量不等于 jar 数（源码 zip/tar.gz 也计入）
- 发布后下载远端 jar 计算 SHA-256，与本地构建比对
- CurseForge：项目表单的版本 ID 优先于全局版本目录；描述走 Authors 编辑器；
  文件走 Upload API；手动发布待审核时公开页面 `404` 属预期

## 9. 图片与浏览器

- MC 贴图/Logo/GUI 美术：`image-2` 优先，无效时回退 Agnes；读取 provider 配置不得输出密钥
- 物品图标：16×16 RGBA、硬透明、透明边距 ≥1px
- 浏览器默认用 Edge 及其现有会话；Chrome 仅在用户明确要求时使用
- Computer Use 需当前任务明确授权，不得从“开发/测试/发布”推断

## 10. 物品建模（Blockbench MCP）

### 已安装

| 组件 | 位置 | 状态 |
|---|---|---|
| MCP 插件文件 | `%APPDATA%\Blockbench\plugins\mcp.js` | 已放置，v1.10.1，917,605 B |
| MCP 插件备份 | `tools/bb_mcp_client.py` | 便携版同目录备份 |
| MCP 端点 | `http://localhost:3000/bb-mcp` | 已在 4 个 Agent 配置中登记 |
| 建模 Skill | 5 个 Agent 技能目录各一个 **junction**（不是正文副本），全部指向 `skills/minecraft-modeling-item` | 34 个受版本控制文件（含 `SKILL.md`）；2026-11-02 清理了 `scripts/__pycache__` |
| 建模工程文件（`.bbmodel`）与预览图归档目录 | `<ASSET_ARCHIVE>/Blockbench/<mod_id>/` | 与 `<ASSET_ARCHIVE>/Blender` 同级集中存放，不分散塞进各 Mod 源码 git 仓库；具体根目录由本机环境决定，不写入公开仓库 |

### Agent 配置位置

| Agent | 配置文件 | 键 |
|---|---|---|
| Codex | `~/.codex/config.toml` | `[mcp_servers.blockbench]` |
| Claude | `~/.claude.json` | 顶层 `mcpServers.blockbench` |
| Pi | `~/.pi/agent/mcp.json` | `mcpServers.blockbench` |
| OpenCode | `~/.config/opencode/opencode.json` | `mcp.blockbench` |

### Skill 唯一事实源与接入

**唯一事实源**：`~/.codex/skills/minecraft-modeling-item`（git 仓库，可 `git pull` 更新）

其他 Agent 的目录**只用 junction 指向该源**，不复制正文：

| Agent | 接入方式 |
|---|---|
| Codex | 源目录本身 |
| Claude | `~/.claude/skills/minecraft-modeling-item` → junction |
| Pi | `~/.pi/agent/skills/minecraft-modeling-item` → junction |
| OpenCode | `~/.config/opencode/skills/minecraft-modeling-item` → junction |
| 通用 | `~/.agents/skills/minecraft-modeling-item` → junction |

更新方式：在源目录执行 `git pull`，所有 Agent 立即看到新版本，无需重新分发。
不得把技能正文复制到 Agent 私有目录——那会产生漂移，且违反用户既定的“唯一事实源”规则。

### 使用前提

1. Blockbench 必须**正在运行**，且 MCP 插件已加载、端口监听 3000。未启动时 `bb_doctor.py` 报 `Connection refused` 属正常。
2. Codex 需要重启会话才能加载新的 MCP 配置。
3. Skill 通过 `$minecraft-modeling-item` 调用。

### 自检命令

```bash
cd ~/.codex/skills/minecraft-modeling-item
python scripts/selftest.py        # 12 项，应全过
python scripts/bb_doctor.py       # 只读探测 MCP 连接
node scripts/test_motion.js       # 9 项断言
```

### 已知限制

- `scripts/test_workflow.py` 在 Windows 上会因缺少符号链接权限报 `WinError 1314`（1/21 失败）；这是本机权限问题，不是 Skill 缺陷。启用开发者模式或管理员权限可消除。
- 编辑器预览不等于游戏内动画支持；组件数减少不等于游戏 FPS 提升。
- 该 Skill 面向 Java 物品模型，不覆盖通用实体动画、Hytale 建模、纯服务端插件。

### 排错顺序

| 现象 | 检查 |
|---|---|
| `Connection refused` | Blockbench 是否运行、插件是否加载、端口是否 3000 |
| `404` | 端点是否 `/bb-mcp`，不是所有 MCP 都用 `/mcp` |
| 工具列表为空 | 刷新 tools/list；检查当前项目格式 |
| 截图过大 | 用 `capture_screenshot(max_size=...)` |

### 3D 方块与器物模型防错规约（2026-11-08 实战踩坑沉淀）

1. **严禁薄片/柱体强写 `[0, 0, 16, 16]` 全幅 UV（`uv_aspect_squash`）**：
   - 典型故障：`earth_lore:block/research_table` 厚度仅 1~2px 的桌沿和 2×12 的桌腿被手写填成 `"uv": [0, 0, 16, 16]`，导致整张 16×16 贴图被强行挤压 8~16 倍，出现严重错位与拉丝。
   - 规则：每个面 `uv` 的 `[u2-u1, v2-v1]` 必须与该面几何尺寸 `(fw, fh)` 保持 **1:1 像素比例**（或在标准 16×16 分层材质上直接省略 `uv` 字段，交由 Minecraft 原生按 `[from, to]` 自动做锁世界像素的 UV 映射）。
2. **严禁多部件 3D 模型共用单张立绘贴图（`multi_part_single_texture`）**：
   - 典型故障：`earth_theology`（长椅、香炉、供盘、经台）与 `xuanhuan_earth`（画符台）将 4~10 个不同朝向的部件全部绑定到唯一一张正面 PNG，把台面符纸/坐垫图案直接糊在桌腿和底座上。
   - 规则：`elements >= 4` 的 3D 器物/家具必须按物理材质拆分独立贴图通道（如 `#top`、`#front`、`#side`、`#leg`、`#metal`、`#detail`）或使用规范 Box-UV 图集。
3. **双重工具门禁拦截**：
   - 已沉淀至全机建模审计器 `skills/minecraft-modeling-item/scripts/audit_model.py`（`uv_aspect_squash`、`multi_part_single_texture`）与地球系列门禁 `tools/earth_release_gate.py`（`[MODEL-UV-SQUASH]`、`[MODEL-SINGLE-TEX]`）。
4. **`gpt-image-2.6` 动图生成与禁读防卡死**：
   - `gpt-image-2.6` 可用于生成动态贴图源或宣传动图，但支持文本/静态图的主控模型（如 Gemini4）**严禁直接 `view_image` 读取动图**；一律由脚本（Pillow `ImageSequence`）在磁盘侧拆帧转换为 MC 纵向序列帧 PNG + `.png.mcmeta`，并输出静态网格预览图。



## 11. 2026-11-11 美术规格、多方块架构与世界生成实战规约

本节把跨模组（earth_lore / earth_on_minecraft / xuanhuan_earth / fantasy_earth / earth_theology）反复踩到的六类问题固化为可执行门禁。每条按"症状 → 规则 → 检查点"组织，新增模组直接套用。

### 11.1 分层像素美术规格（16x16 基础物料 + 32x32 复杂器物）与剪影色阶门禁

**尺寸分层**

| 层级 | 尺寸 | 适用对象 |
|---|---|---|
| 基础物料 | 16x16 RGBA | 矿粉、锭、粒、板、线、简单工具、单一材质图标 |
| 复杂器物 | 32x32 RGBA | 铜钱剑等复合法剑、风水罗盘、3/4 斜向立体古籍/魔导书、符箓、乾坤袋、多材质护符 |

判定标准不是"看起来复杂"，而是**图标内是否同时出现 3 种以上材质且需要斜向立体透视**。只有 1~2 种材质、正交视图即可表达的一律留在 16x16，避免无意义放大后再降采样。

**色带与描边**

- 统一 20 阶色带：暗部取冷色相（偏蓝紫），高光取暖色相（偏黄橙），中间段色相连续偏移；禁止只在明度上线性加白，那会得到灰蒙的"塑料感"。
- 轮廓使用**深色内聚描边**（取该材质暗部再压暗 20%~30%），不描纯黑、不加外发光；描边必须闭合，四角断开视为剪影失败。
- 不透明色阶 >= 12~18 色。低于 12 色视为平涂占位图。

**剪影与唯一性**

- 物品图标四角必须 alpha=0，且透明背景像素充足：16x16 至少 24 个 alpha=0 像素，32x32 至少 96 个。铺满整格的"无背景方块图"一律判失败（`no-alpha-silhouette`）。
- 透明边距 >= 1px（16x16）/ >= 2px（32x32），保证在物品栏格子里不贴边。
- 每张 PNG 的 SHA-256 在**全模组范围**内唯一；跨模组复用同一张图也算重复，必须重绘而不是复制。

**门禁命令**

```bash
# 尺寸 / 透明 / 边距 / 四角（16x16 基础物料）
python tools/validate_pixel_assets.py <mod>/textures/item/*.png --size 16 --min-margin 1

# 复杂器物按 32x32 校验，允许更高色阶
python tools/validate_pixel_assets.py <mod>/textures/item/<complex_item>.png \
    --size 32 --min-margin 2 --min-colors 12
```

色阶下限与哈希重复由 `tools/earth_release_gate.py` 统一把关：`[TEXTURE-FLAT-PALETTE]`（不透明色阶不足）、`no-alpha-silhouette`（透明背景不足）、`[TEXTURE-DUP]`（SHA-256 重复组）、`[TEXTURE-DIM]`（尺寸不是 16/32/64/128/256 或纵向序列帧）。

### 11.2 多通道 ItemTintSource 叠加（保留主封面色调 + 局部高光掩模表达 Tier）

**症状**：文献、护符、器物既要区分学科/流派，又要区分 T0–T4 品阶。直接对整张贴图做两次染色，会把纸张纹理、封面压印、金属高光一起染成单色，品阶越高越像一块色板。

**规则**：染色只作用于**该层自己的像素**，层与层之间靠 alpha 叠加，严禁整图重染覆盖。

| 层 | 贴图 | 内容 | 染色 |
|---|---|---|---|
| layer0 | `<item>.png` | 纸张/底材原色，含纹理与暗部 | `minecraft:constant` = -1（不染） |
| layer1 | `<item>_cover.png` | 皮革封面主体、书脊，纯中性灰白 | `<mod>:discipline` 按学科取色 |
| layer2 | `<item>_tier_trim.png` | 护角、书扣、卷轴轴头、火漆章环的高光灰度掩模 | `<mod>:tier` 按 T0–T4 取色 |

要点：

1. layer2 必须是**中性灰度**（R≈G≈B），只保留明度信息，染色时才能得到干净的高光；带彩的 trim 会与 tier 颜色相乘出脏色。
2. layer2 只覆盖局部装饰，面积超过图标 35% 视为"重染整图"的变体，判失败。
3. 没有 tier 概念的单品只保留 layer0 + layer1 两层，不要为了统一硬加空 trim 层（空层参与 alpha 混合，边缘发灰）。
4. 未提供数据时必须有 `default` 颜色，且默认值取中性色，避免物品栏出现纯黑或纯白。

**物品定义骨架**（1.21+/26.x 的 `assets/<mod>/items/<item>.json`）：

```json
{
  "model": {
    "type": "minecraft:model",
    "model": "<mod>:item/manuscript",
    "tints": [
      { "type": "minecraft:constant", "value": -1 },
      { "type": "<mod>:discipline", "default": 8421504 },
      { "type": "<mod>:tier", "default": 9203014 }
    ]
  }
}
```

**模型骨架**（`assets/<mod>/models/item/manuscript.json`）：

```json
{
  "parent": "minecraft:item/generated",
  "textures": {
    "layer0": "<mod>:item/manuscript",
    "layer1": "<mod>:item/manuscript_cover",
    "layer2": "<mod>:item/manuscript_tier_trim"
  }
}
```

**TintSource 骨架**（只依赖客户端可读的数据组件，避免双端分歧）：

```java
public record TierTint(int defaultColor) implements ItemTintSource {
    public static final MapCodec<TierTint> MAP_CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
            ExtraCodecs.RGB_COLOR_CODEC.optionalFieldOf("default", 0x8C6D46).forGetter(TierTint::defaultColor)
    ).apply(i, TierTint::new));

    public static int colorForTier(int tier) {
        return switch (tier) {
            case 1 -> 0xCD7F32;   // T1 铜
            case 2 -> 0xCFD8DC;   // T2 银
            case 3 -> 0xFFD54F;   // T3 金
            case 4 -> 0xB388FF;   // T4 灵
            default -> 0x8C6D46;  // T0 / 未定阶
        };
    }

    @Override
    public int calculate(ItemStack stack, ClientLevel level, LivingEntity owner) {
        int tier = stack.getOrDefault(MyComponents.TIER.get(), 0);
        return ARGB.opaque(colorForTier(tier));
    }

    @Override
    public MapCodec<TierTint> type() { return MAP_CODEC; }
}
```

注册：NeoForge 的 `RegisterColorHandlersEvent.ItemTintSources` 中 `event.register(TierTint.MAP_CODEC, id("<mod>:tier"))`，学科染色同理。

**检查点**：items JSON 的 `tints` 数量必须等于模型 `layer0..layerN` 的数量；`_tier_trim.png` 必须近灰；三者缺一即报错。

### 11.3 3D 方块物品直指模型 & 多方块核心禁单格合成

**3D 方块物品**

已有 3D 方块模型的功能方块，物品栏必须直接渲染该方块模型：

```json
{ "model": { "type": "minecraft:model", "model": "<mod>:block/research_table" } }
```

- 严禁再画一张 2D `textures/item/<block>.png`（`[BLOCK-REDUNDANT-ITEM-PNG]`）；
- 严禁把物品模型写成 `item/generated` 的平面图（`[BLOCK-ITEM-FLAT-2D]`）；
- 方块模型改动后清理不再被引用的 `textures/block/*.png`（`[BLOCK-ORPHAN-PNG]`）。

**多方块核心成型**

圣坛、法阵核心这类结构走"摆件 + 祝圣"，而不是单格合成：

1. 玩家在世界中摆好基座与周边器物（烛台、供盘、阵旗、符石）；
2. 手持法器右键基座，服务端扫描周围结构模板，匹配则**原位**替换为核心方块（保留朝向与玩家归属）；
3. 移除该核心的单方块工作台配方与创造栏单方块入口，避免玩家跳过摆件直接放成品。

造型上严禁用"同心递减的白方块"堆圆锥塔（白色冰淇淋效应）。按真实台座拆解：宽底座 → 收腰立柱 → 宽挑台面 → 垂布/幡幔，每一段用独立材质通道，避免整塔共用一张贴图。

### 11.4 单核心方块 + NBT 拼装 + 客户端多部件 BER 渲染

面向大型水车组、连排风车、巨型法阵环等"视觉体量远大于 1×1×1"的结构：

- 合成/拼装期把组件规格写入核心的 `DataComponents`（1.21+）或 `CompoundTag`（1.20.1）；
- 世界内只放 **1 个方块 + 1 个 BlockEntity**，服务端 tick 恒为 O(1)；
- 客户端 `BlockEntityRenderer` 读同步 NBT，在中心格四周用 `PoseStack` 渲染多部件；
- 必须扩展 `getRenderBoundingBox()`，否则转视角时整组模型被视锥剔除；
- 玩家靠近或屏幕内含核心时绘制高亮边框，解决"找不到交互点"。

完整代码骨架、数据闭环（放置/同步/拆下）、碰撞模式与性能守则见 `skills/zershyan-mcmod-style/references/single-block-nbt-ber.md`。三条硬约束：

1. `getUpdateTag()` 与 `getUpdatePacket()` 必须完整，否则客户端 BER 拿到空 NBT，模型只剩中心格；
2. `playerWillDestroy` / 掉落物必须把已拼装组件写回，禁止一镐拆掉后组件蒸发；
3. `render()` 内禁止每帧解析 JSON 或反射，解析结果缓存在瞬态字段，仅在 `loadAdditional` / `onDataPacket` 时刷新。

### 11.5 地质露头与地表找矿（裸岩蚀变晕 vs 地表散落矿砾分离）

**症状**：矿化蚀变晕（`*_halo`）为了"看起来明显"，把草方块、泥土、灰化土一起替换成蚀变岩，导致草原与村庄地面出现大片异色斑块，破坏地貌与建筑。

**规则**

1. `*_halo` 只允许替换**天然裸岩露头**：`stone`、`deepslate`、`tuff`、`granite`、`diorite`、`andesite`、`calcite`、`sandstone` 等。
2. 严禁出现在 `BlockTags.SUBSTRATE_OVERWORLD`（草方块、泥土、灰化土、缠根泥土、苔藓）以及 `farmland`、村庄/农田地面、`dirt_path` 的替换目标里。
3. 草地、河滩、山麓的前期找矿引导改用**地表碎矿石子**（Surface Float / Loose Pebble）：低矮 3D 小模型，放在地面**上方一格**（不替换地面方块），低密度散落。
4. 生成时避让村庄：与村庄结构 AABB、`POI` 或已放置的建筑方块距离过近则放弃该点。

**生成参数建议**：每 chunk 最多 1 处信号，概率 0.3~0.5；单处 2~3 个 pebble；只在 `Heightmap.Types.WORLD_SURFACE_WG` 采样，且要求下方为可站立实心方块。

**检查点**：扫 `data/<mod>/worldgen/configured_feature/*halo*.json` 与 `placed_feature`，若 replaceable/targets 中出现草方块、泥土、耕地，直接失败；pebble 的 `from/to` 必须整体在 y>=1 且下方方块可站立。

### 11.6 同名本地化键拦截（[LANG-DUP-NAME]）与聚落村民确定性就业

**同名拦截**

`zh_cn.json` / `en_us.json` 中，不同注册 ID 的物品或方块不允许译成完全相同的显示名。典型故障：`item.<mod>.copper_sword` 与 `item.<mod>.bronze_sword` 都叫"铜剑"，玩家无法区分，JEI 里也查不出差异。门禁按"同前缀 + 同值"分组，命中即失败，要求改名或加限定词（材质/品阶/用途）。

**村民就业**

原版新生成成年 `Villager` 的职业默认是 `minecraft:none`。接管聚落生态时若不处理，会出现整村无业游民、没有交易、聚落看起来是空壳。

1. 首次绑定聚落时，对成年且职业为 `none` 的村民，按**确定性种子**决定是否引导就业，比例约 75%~80%；
2. 种子由聚落 ID 与实体 UUID 派生，保证同一村民多次加载结果一致、不会反复改职业；
3. 已是具体职业或 `nitwit` 的村民不动；幼年村民不处理；
4. 分配后同步职业与交易表，交易内容与该聚落产业匹配。

```java
private static final float EMPLOY_RATIO = 0.78F;

public static void guideEmployment(ServerLevel level, Villager villager, String settlementId) {
    if (villager.isBaby()) return;
    VillagerData data = villager.getVillagerData();
    if (!data.profession().is(VillagerProfession.NONE)) return;

    long seed = settlementId.hashCode() * 31L + villager.getUUID().getMostSignificantBits();
    RandomSource random = RandomSource.create(seed);
    if (random.nextFloat() >= EMPLOY_RATIO) return;

    VillagerProfession profession = pickProfession(level, settlementId, random);
    villager.setVillagerData(data.setProfession(profession).setLevel(1));
    villager.setVillagerXp(0);
    refreshOffers(level, villager);   // 只在职业确定后写交易
}
```

门禁对应：`[VILLAGER-NONE-TRADES]`（向无业村民写交易）、`[LANG-DUP-NAME]`（同名不同 ID）。已有 `ResidentProfileManager` 的实现必须保留"先判职业再写交易"的顺序，否则打开交易界面时服务端 offer 列表为空。


## 12. 已知限制

- `mcver.py` 的 API 断点检测是常量池字节匹配，可能误报，报告为 failure 时应人工确认
- `mcver.py doctor` 的内嵌依赖版本来自内层 jar 的 `mods.toml`，内层缺元数据时记为空
- 本手册记录的是**本机已验证**的结论，不保证适用于其他机器或其他 MC 版本

## 变更记录

| 日期 | 内容 |
|---|---|
| 2026-10-30 | 建立；汇总 `mcver.py` 五个子命令、多版本结构、双 jar、版本差异、实例升级、验证分层 |
| 2026-10-30 | 新增第 10 节：Blockbench MCP 插件、端点、建模 Skill 安装位置与自检命令 |
| 2026-11-02 | 第 7 节新增硬性禁令：未经用户当前任务明确允许，严禁擅自运行 `runClient` 或启动游戏客户端测试 |
| 2026-11-08 | 第 10 节沉淀 3D 模型 UV 挤压（`uv_aspect_squash`）与单图糊全模（`multi_part_single_texture`）防错规约并同步写入 `audit_model.py` 与 `earth_release_gate.py`；登记 `gpt-image-2.6` 动图安全拆帧规范 |
| 2026-11-11 | 新增第 11 节：分层像素美术（16x16/32x32）与剪影色阶门禁、多通道 ItemTintSource（discipline + tier_trim）叠加、3D 方块物品直指模型与多方块祝圣成型、单核心 NBT + BER 多部件渲染、裸岩蚀变晕与地表碎砾分离、[LANG-DUP-NAME] 与村民确定性就业；同步 `tools/earth_release_gate.py`、`tools/render_block_models_preview.py`、`tools/validate_pixel_assets.py` 与 `single-block-nbt-ber.md` |
