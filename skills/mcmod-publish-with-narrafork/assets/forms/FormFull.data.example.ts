/**
 * 表单数据。复制本文件为同目录的 data.ts，只改这里，App.tsx 不用动。
 * 字段含义见 README.md，取值规则见 ../../references/field-sources.md。
 *
 * 要外置长文本（比如整段 cfDescription）就写成常量放在 DATA 之前——
 * 放后面再被 DATA 引用会触发 TDZ：Cannot access '…' before initialization
 */
export const DATA = {
	/** 模组英文名，显示在标题 */
	modName: "SnowyCrescentCore",
	/** 右上角角标，一般是许可证简称 */
	badge: "GPL-3.0",
	/** 项目特有许可证，追加到内置列表 */
	extraLicenses: ["GPL-3.0-with-additional-terms"],
	/**
	 * 从 CurseForge Game Versions API 拉到的 MC 版本列表，优先于模板内置候选。
	 * 正常流程先跑 `scripts/cf/upload.py query`，把返回的版本写进来；拿不到时才省略。
	 */
	mcVersions: [] as string[],
	iconHint: "默认 logo.png（64×64）",
	coverHint: "logo 仅 64×64，需放大加底色",
	/** 默认勾选「没有图标就自动生成」：白底黑字写模组英文名 */
	autoIcon: true,
	/** 占位图标样式；agent 从 skill 的 .narrafork/icon-style.json 读出来后填这里 */
	iconStyle: {
		font: "segoeuib.ttf",
		lines: ["auto"],
		stacked: true,
		fontSize: 56,
		lineGap: 1.12,
		letterSpacing: 0,
		align: "center",
		uppercase: false,
		border: 0,
		padding: 0.04,
		fg: "#111111",
		bg: "#ffffff",
		canvas: 400,
	},
	/** 没有资料条目时显示的说明 */
	entriesEmptyText: "本项目是纯库模组，语言文件里没有物品、方块与实体，百科资料条目会自动跳过。",

	/** 所有字段的 placeholder，即调研值；留空的项按这些值执行 */
	defaults: {
		cfName: "SnowyCrescentCore",
		cfSummary: "A lib from zershyan.",
		cfDescription: "按工程 README 与源码整理，英文块 + --- + 中文块",
		cfLicense: "GPL-3.0-with-additional-terms",
		cfCategory: "API and Library",
		cfExtraCategories: [] as string[],
		cfSourceUrl: "https://github.com/Zershyan/SnowyCrescentCore",
		/** 建项时启用 Project Pages；建好后到项目设置里开启也可以 */
		cfProjectPages: true,

		wName: "（待确认）",
		/** 只有主要名称是中文时才填；主要名称本身是英文就留空 */
		wEname: "",
		wSname: "",
		wIntro: "供其他模组使用的库，提供能力注册、玩家动画与数据生成 API",
		wModid: "sccore",
		wCfId: "建完 CF 项目后填入",
		wMrId: "没有就留空",
		wRelations: "代码联动的前置或附属",
		wCore: "LIB",
		wExtra: [] as string[],
		wStatus: "活跃",
		wLicenseType: "源码",
		wLicenseName: "ARR",
		wTags: [] as string[],
		wKeys: [] as string[],
		wAuthorName: "Zershyan",
		wLinks: "https://github.com/Zershyan/SnowyCrescentCore",
	},

	/** 版本条目：modVersion 填 gradle.properties 的 mod_version，只写模组版本，不带 MC 版本和 build 编号 */
	versions: [
		{
			modVersion: "1.0.1",
			mcVersions: ["1.20.1"],
			loaders: ["Forge"],
			javaVersion: "Java 17",
			releaseType: "release",
			env: "双端",
			changelog: "",
		},
		{
			modVersion: "2.0.0",
			mcVersions: ["1.21.1"],
			loaders: ["NeoForge"],
			javaVersion: "Java 21",
			releaseType: "release",
			env: "双端",
			changelog: "",
		},
	],

	authors: [{ id: "", name: "Zershyan", role: "所有者" }],

	/** 资料条目；没有内容物时留空数组。分类取 ENTRY_CATEGORIES 里的值 */
	entries: [] as {
		name: string;
		ename: string;
		regname: string;
		category: string;
		type: string;
		damage: string;
		stack: string;
	}[],

	/**
	 * CurseForge 依赖关系。从 build.gradle 的 `curse.maven:<名>-<项目ID>:<文件ID>` 解析，
	 * jarJar 内嵌与 localRuntime 的不用声明。没有就留空数组。
	 */
	dependencies: [] as { name: string; projectId: string; type: string }[],
};
