# 字段来源

每个字段从哪取都写在这。表里没有的、或标「问用户」的，停下来问，不许猜。

## 工程事实

| 字段 | 取自 |
|---|---|
| modid | `gradle.properties` → `mod_id` |
| 英文名 | `gradle.properties` → `mod_name` |
| 中文名 | **问用户**（语言文件里通常没有） |
| mod 版本 | `gradle.properties` → `mod_version`；没有这个属性时取 `build.gradle` 的 `version`（只含模组版本，不带 MC 版本与 build 编号） |
| 显示名 | 上传的 jar 文件名去掉 `.jar`；装了 style skill 时即 `<modid>-<mod_version>-<mc版本>` |
| MC 版本 | `gradle.properties` → `minecraft_version` |
| 加载器 | 有 `neo_version` → NeoForge；有 `forge_version` → Forge |
| Java 版本 | `build.gradle` → `java.toolchain.languageVersion` |
| 许可证 | `gradle.properties` → `mod_license` |
| 作者 | `gradle.properties` → `mod_authors` |
| 简介 | `gradle.properties` → `mod_description` |
| JAR 名 | `base { archivesName }`，没配时用工程目录名 |

装了 `zershyan-mcmod-style` 的工程，**禁止使用文件名带 `+build.N` 的 jar**，细节见 [与 zershyan-mcmod-style 同装时](with-mcmod-style.md)。没装的按 `build.gradle` 实际命名判断。上传脚本只在工程符合 style 规范时才拒绝带 `+build.` 的 jar 名与显示名。

**Gradle `version` 不直接当发布版本号**。装 style skill 时它是 `${mod_version}-${minecraft_version}+build.${n}`，只用于包内元数据与默认 jar 名；没装的工程按 `build.gradle` 的实际命名走。表单里填 `mod_version`，显示名取 jar 文件名。多分支工程逐个分支读。

## CurseForge 项目

| 字段 | 取自 |
|---|---|
| 项目名 | `mod_name` |
| 简介 | `mod_description`，1～256 字符 |
| 详细描述 | 按 README 与源码整理 |
| 图标 | `src/main/resources/logo.png`；没有时按表单勾选项用 `make_icon.py` 生成占位图（样式读 skill 的 `.narrafork/icon-style.json`，可在表单弹窗里调），没勾就问用户 |
| Class | 固定 `Mods` |
| 主分类 | **问用户**；候选取 `FormFull` 的 `CF_CATEGORIES`（建项目页实读的 51 项），不要自己造名字 |
| 附加分类 | **问用户**，候选同上 |
| 许可证 | `mod_license` |
| 允许第三方分发 | 闭源关、开源开，可覆盖 |
| 允许评论 | `true` |
| 源码链接 | git remote |

## CurseForge 版本

| 字段 | 取自 |
|---|---|
| JAR 路径 | 装 style skill：`build/libs/<archivesName>-<mod_version>-<mc>.jar`（不带构建编号）；通用：`build/libs/<archivesName>-<version>.jar` |
| 显示名 | 上传的 jar 文件名去掉 `.jar`（`make_manifest.py` 生成） |
| 更新说明 | `git log` 整理，英文块 + `---` + 中文块 |
| 发布类型 | 默认 `release`，不确定时问 |
| 游戏版本标签 | 第 3 步拉的 Game Versions |
| 运行环境 | 按注册项与 `Dist` 代码判断，判断不了问用户 |
| 依赖 | `build.gradle` 的 `curse.maven:` 坐标 |

## 百科模组条目

| 字段 | 取自 |
|---|---|
| 主要名称 | **问用户** |
| 次要名称 | 主要名称**有中文**时才填（通常是 `mod_name`）；主要名称本身是英文就留空，否则百科会弹重复警告 |
| 简写名称 | **只能问用户**（社区通用缩写，如 GT6、TiC2）；用户没给就留空，**不要自己造**。百科只收字母数字符号 |
| 搜索辅助关键词 | **只能问用户**（别名、外号、分词）；不清楚就留空，百科明文禁止滥用 |
| 一句话简介 | `mod_description` |
| MODID | `mod_id` |
| CF Project ID | `curseforge/project.json` |
| Modrinth Project ID | 有则填，没有留空 |
| 模组元素 | **问用户** |
| 支持平台 | 固定 JAVA版 |
| 运作方式 + MC 版本 | 从 CF 的「加载器 × MC 版本」组合聚合 |
| 客户端/服务端 | 按注册项与 `Dist` 代码判断 |
| 官方状态 | 按项目现状判断，多数在维护的填「活跃」；不确定时问用户 |
| 开源状态 | 按 `mod_license` 判断，ARR 类填「闭源」 |
| 许可证协议 | `mod_license` 映射到 SPDX 代码；找不到对应项时留空或填 `ARR` |
| 作者 | **问名字**，脚本查 ID |
| 相关链接 | git remote + CF 项目页 |
| 封面 | `logo.png` 转 16:10（`submit.py` / `console.py` 都吃 `coverPath`），没有则问用户 |
| 正文 | 按源码整理 |

## 百科资料条目

| 字段 | 取自 |
|---|---|
| 提交范围 | 工程内全部物品与方块 |
| 颜色变体 | 每个颜色单独一条 |
| 资料分类 | 按注册表类型（方块/物品 → 物品/方块） |
| 名称 | `zh_cn.json` |
| 英文名 | `en_us.json` |
| 注册名 | 注册表 ID `modid:path` |
| 耐久 / 堆叠 | 运行时导出 |
| 资料类型 | 按物品用途判断 |
| 图标 | 平面取 `layer0` 放大；方块走 3D 渲染 |
| 正文 | 按源码与 [正文模板](../assets/content-templates.md) |
| 改动附言 | 默认留空 |

## 只有这四类必须问用户

1. **中文名**
2. **CF 主分类 / 附加分类**
3. **百科模组元素**
4. **百科作者名**

其余都能从工程或接口拿到。用户回答后记进配置，不要重复问。
