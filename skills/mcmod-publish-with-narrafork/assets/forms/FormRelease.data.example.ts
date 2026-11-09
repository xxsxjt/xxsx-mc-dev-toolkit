/**
 * 版本发布表单数据。复制本文件为同目录的 data.ts，按项目改这里。
 * 字段来源见 ../../references/field-sources.md。
 */
export const DATA = {
	project: {
		name: "ADCore",
		slug: "adcore",
		projectId: "0000000",
		license: "AGPL 3.0",
	},

	/** 已发布版本摘要，只用于展示；从 curseforge/remote-files-*.json 取，version 是线上 displayName */
	released: [
		{ version: "adcore-0.0.1-26.1.2", mc: "26.1.2", loader: "NeoForge", date: "2026-10-20" },
	],

	/** 从 Game Versions API 拉到的版本列表；省略时用模板内置候选 */
	mcVersions: ["26.1.2", "26.1", "1.21.11", "1.21.1", "1.20.1"] as string[],

	/** 待发布的版本；modVersion 填 gradle.properties 的 mod_version */
	versions: [
		{
			modVersion: "0.0.2",
			mcVersions: ["26.1.2"],
			loaders: ["NeoForge"],
			javaVersion: "Java 25",
			releaseType: "release",
			env: "双端",
			changelog: "",
		},
	],
};
