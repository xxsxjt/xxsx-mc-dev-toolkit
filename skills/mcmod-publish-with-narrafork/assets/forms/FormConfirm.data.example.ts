/**
 * 提交前确认表单的数据。复制为同目录 data.ts 后按实际情况填。
 * releases 对应 curseforge/release-manifest.json 的 files 展开结果，
 * wiki 对应 docs/mcmod/mod-config.json；不发百科时删掉 wiki 字段。
 */
export const DATA = {
	project: {
		name: "模组英文名",
		projectId: "0000000",
		slug: "project-slug",
		/** 项目还没建时填这三项，确认后会先建再传 */
		category: "API and Library",
		license: "MIT",
		pending: false,
	},

	/** 一个「MC 版本 × 加载器」一条；displayName 就是 artifact 文件名去掉 .jar */
	releases: [
		{
			minecraft: "1.21.1",
			loader: "NeoForge",
			javaVersion: "Java 21",
			displayName: "examplemod-1.2.0-1.21.1",
			releaseType: "release",
			artifact: "build/libs/examplemod-1.2.0-1.21.1.jar",
			sha256: "",
			changelog: "英文说明\n\n---\n\n中文说明",
		},
	],

	/** 不发百科时整段删掉 */
	wiki: {
		name: "模组中文名",
		modid: "examplemod",
		cfprojectid: "0000000",
		intro: "一句话简介",
		targets: ["NeoForge 1.21.1"],
		content: "<p>[ban:title_menu]</p><p>正文…</p>",
		author: "作者名",
		license: "许可协议",
	},

	/** 需要提醒用户的点，会显示成橙色提示条 */
	warnings: [] as string[],
};
