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
| 建模工程文件（`.bbmodel`）与预览图归档目录 | `D:/PRIVATE_RESTRICTED/Assets/Blockbench/<mod_id>/` | 与 `D:/PRIVATE_RESTRICTED/Assets/Blender` 同级集中存放，不分散塞进各 Mod 源码 git 仓库 |

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


## 11. 已知限制

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
