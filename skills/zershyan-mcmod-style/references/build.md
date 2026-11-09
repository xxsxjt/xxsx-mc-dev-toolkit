# 构建与发布

本页维护工程创建、加载器差异与构建检查。版本计算和 jar 命名统一见 [版本号与产物](versioning.md)，不要在多个文档中维护另一套脚本。

## 先确认目标环境

- 用户未指定新模组的 MC 版本时，先询问；是否需要 `api/` 包也须明确。
- 按目标版本选择加载器、Java、Gradle 和映射。已有工程以实际配置为准，不为整理规范顺带升级。
- 新建项目时查询官方发布源中适用的最新 ModDevGradle 版本，再固定具体版本；模板中的插件版本是已保存的基线，不等于永远最新。

| MC | 加载器与 Java | 工程入口 |
|---|---|---|
| 1.20.1 | Forge 47.x、Java 17 | [Forge 构建脚本](../templates/forge1.20.1/build.gradle)、[属性](../templates/forge1.20.1/gradle.properties) |
| 1.21.1 | NeoForge 21.1.x、Java 21 | [NeoForge 构建脚本](../templates/neoforge1.21.1/build.gradle)、[属性](../templates/neoforge1.21.1/gradle.properties) |
| 26.1.2 / 26.2 | NeoForge 26.x、Java 25 (`D:/Java/jdk-25`) | 支持 `neoforge-26.1.2/` 或 `neoforge-26.2/` 子目录结构；`gradle.properties` 需配置 `org.gradle.java.installations.paths=D:/Java/jdk-21,D:/Java/jdk-25` 及标准 `mod_*` 元数据 |

## 从模板创建

两套模板包含 wrapper、运行配置、常见注册类型、Datagen 和占位资源；modid 均为 `examplemod`。优先复制对应模板，再裁剪，不凭记忆重写整套构建脚本。

1. 替换 `io.zershyan.examplemod`、类名前缀 `ExampleMod*`（modid 过长时换用缩写，主类与包名仍用完整 modid）、`mod_id` 与资源命名空间，同时修改 Mixin 配置和引用。
2. 填写名称、版本、作者、许可证与说明。`mod_license`、`mod_description` 必须明确；模板计算所需的 MC / 加载器 / 映射 / 版本属性也不能删除。`mod_credits`、`mod_url` 按需填写。
3. 移除不用的注册项、演示功能与依赖；用户不需要 API 时移除模板中的 API 门面。不因模板包含某功能就让新模组依赖它。
4. 重新生成资源并核对命名空间、资源引用和元数据；占位贴图生成器仅用于模板，不能替代正式素材。

### ForgeAttachment 取舍

Forge 模板实际使用附件演示，因此保留 forgeattachment。**需要玩家持久化数据的新模组应保留并使用它**；确实不需要附件时再裁剪。

- 需要玩家持久化数据时：先按 [ForgeAttachment](forgeattachment.md) 探测 sigh Maven 上的最新正式版并固定；拿不到可用正式版就把 CurseForge 项目链接发给用户，请其手动提供 jar 后按本地 jar 依赖接入。
- 不需要附件时：先移除或改写附件注册、数据类、事件处理及网络包中的附件调用，再移除 `modImplementation`、`forgeattachment_version` 和 `mods.toml` 中对应依赖。仅为其服务的 Maven 仓库配置一并移除，共享仓库按其他依赖需求保留。

**不使用附件的模组不得照搬此依赖。** 不要仅删除依赖而留下无法编译的 API 引用。

## 两代构建差异

| 项目 | NeoForge 1.21.1 | Forge 1.20.1 |
|---|---|---|
| 插件 | `net.neoforged.moddev` | `net.neoforged.moddev.legacyforge` |
| 扩展块 | `neoForge` | `legacyForge` |
| 元数据源 | `src/main/templates/META-INF/neoforge.mods.toml` | `src/main/resources/META-INF/mods.toml` |
| 展开任务 | `generateModMetadata`，输出纳入资源源集与 IDE 同步 | `processResources` |
| 必需依赖字段 | `type="required"` | `mandatory=true` |
| 自定义 ItemStack 数据 | DataComponents | NBT |
| 普通网络消息 | CustomPacketPayload | SimpleChannel |
| Mixin | 不声明 refmap | 生成 refmap，并写入 jar manifest |

两种元数据展开都使用 Gradle 的 `version`，不能直接用不含 MC 版本和构建号的 `mod_version`。字段须与占位符一一对应，成品中不得残留 `${...}`。

### Forge Mixin 打包

LegacyForge 自带 Mixin 集成，不另加 MixinGradle。除 [Mixin 配置](mixin.md) 外，构建脚本必须包含：

```groovy
legacyForge {
    mixin {
        add sourceSets.main, "${mod_id}.refmap.json"
        config "${mod_id}.mixins.json"
    }
}

dependencies {
    annotationProcessor 'org.spongepowered:mixin:0.8.5:processor'
}

tasks.named('jar', Jar).configure {
    manifest.attributes('MixinConfigs': "${mod_id}.mixins.json")
}
```

版本随目标环境核实；此处处理器版本对应现有 Forge 模板。不能只验证开发运行时的 `--mixin.config`，还要检查最终 jar 内的 manifest、配置文件与非空 SRG refmap。

## 依赖声明

- **必需依赖**：除了构建脚本里的依赖，还要写进 `META-INF/mods.toml`（Forge，`mandatory=true`）或 `META-INF/neoforge.mods.toml`（NeoForge，`type="required"`）的 `[[dependencies."<modid>"]]`，并给出实际可用的版本范围。只加构建依赖而不写元数据，玩家端会因缺库直接崩溃；完整写法见 [ForgeAttachment](forgeattachment.md)。
- **可选依赖**：不需要写进元数据；调用收在 `compat/`，经检查入口后缺失依赖仍能启动，见 [兼容](compat.md)。
- **本地 jar 依赖**：Maven 拿不到的自定义依赖放 `libs/`，用 `flatDir { dir 'libs' }` 解析，坐标固定写 `blank:<name>:<version>`，jar 文件名须为 `<name>-<version>.jar`；Forge 1.20.1 外面再包 `fg.deobf(...)`，NeoForge 直接 `implementation(...)`。仅编译期使用的 jar 放 `libs/compileOnly/`，由 `compileOnly(fileTree("libs/compileOnly"))` 统一引入。

```groovy
repositories {
    flatDir { dir 'libs' }
}

dependencies {
    // libs/examplelib-1.20.1-1.0.0.jar
    implementation fg.deobf("blank:examplelib-1.20.1:1.0.0")
}
```

## 运行配置

标准配置为 `client1`、`client2`、`server`、`gameTestServer`、`data`：

- 两个客户端使用独立游戏目录和用户名，便于联机测试。
- 服务端使用 `--nogui`；GameTest 命名空间匹配 modid，属性前缀按加载器区分。
- Datagen 输出 `src/generated/resources`，把 `src/main/resources` 作为已有资源输入；资源源集排除 `.cache` 与 `.bbmodel`。
- 完整任务声明直接取对应模板，不混用两代构建扩展。

## ProGuard：仅在用户要求时接入

模板默认不启用混淆，也未附带完整 ProGuard 工具链。不要复制依赖缺失的脚本片段，或仅添加 `enableProguard=true` 就声称已启用。

需要接入时，先读取目标仓库的既有流程并核对：

- ProGuard Gradle 依赖、`proguard-rules.pro`、`obfuscate/dict.txt` 与 `ZipEntryEncodingFixer` 是否存在；缺少时先确认方案，不擅自增加工具。
- Java toolchain、`jmods` 与编译 classpath 是否取自实际目标环境，不能一律写 Java 21。
- 保留 `jar → proguard → proguardUtf8Fix → finalizeArtifacts` 的处理顺序。Forge 还需核对 `reobfJar` 与混淆的先后关系，不能直接套 NeoForge 流程。
- 混淆输出保留在 `build/libs/obfuscate/`，复制而非移动该任务的输出；原包归档到 `build/libs/origin/`，避免破坏输出追踪。
- 扩展现有 `finalizeArtifacts`，不要重复注册同名任务；仍保持普通构建与 `buildAlpha` 的命名、编号和成功后回写语义。
- 启用混淆的注册类使用 `Mod*` 前缀，见 [命名规则](naming-and-layout.md)。

## 构建请求

用户提出构建时按以下流程，不把等待回答做成阻塞：

1. 异步提问是否需要正式版，不阻塞当前工作。
2. 立即执行 `buildAlpha`，得到带编号产物并回写 `mod_build_number`。
3. 用户回答需要正式版，再执行 `build`，产出不带编号的发布包。

回答不需要时到此为止；工程已有先例或用户明确要求普通 `build` 时按第 3 步处理。版本语义见 [版本号与产物](versioning.md)。

## 发布

对外发布使用正式版本号，不带内部构建编号：

- Maven publication 的 `version` 默认取正式版本号，由 `gradle.properties` 的 `maven_publish_release_version` 控制；置 `false` 时才发布带编号版本。
- 包内元数据始终带 `+build.N`，发布文件名与包内版本不一致属预期行为。
- 上传平台（CurseForge、Modrinth、MC百科）填写版本号时同样用正式版本号。

## 验证与维护

```bash
./gradlew test jar
```

> **硬性禁令**：未经用户在当前轮次明确要求启动游戏客户端，**严禁执行 `gradlew runClient`** 或拉起任何游戏进程；客户端验证一律通过编译、单元测试、资源门禁脚本（如 `python tools/earth_release_gate.py`）和离线预览完成。

构建逻辑或资源处理有变化时，还应执行对应的构建任务（按 [构建请求](#构建请求) 流程，默认 `buildAlpha`），检查产物而不只看任务退出码：

- Java、MC、加载器与映射匹配；依赖可解析，版本明确。
- Datagen 资源正确入包，没有缓存目录、未展开的元数据占位符或缺失的 Mixin 文件。
- jar 文件名、包内版本与构建号行为符合 [版本号约定](versioning.md)。
- 涉及双端或可选依赖时，补做客户端 / 专用服务器及依赖缺失场景测试。

修改规则若影响实现，必须同步模板，并复跑 `compileJava`、`runData`；只改措辞或路由时检查文档与链接即可。依赖下载失败须如实报告，不把静态检查写成构建通过。历史 HTTP 连通性、生成文件数量和一次性测试结论不作为长期保证。

开发态日志可能出现 refmap 读取提示：必须结合该次任务结果与成品检查判断，不笼统忽略所有相关警告。
