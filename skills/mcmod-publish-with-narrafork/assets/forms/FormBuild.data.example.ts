/**
 * 构建前确认表单的数据。复制为同目录 data.ts 后按工程填。
 * branches 从 `git branch -a` 取，去掉 remotes/ 前缀。
 */
export const DATA = {
	projectName: "模组英文名 · 目录名",
	branches: ["master", "1.20.1", "1.21.1"] as string[],
	/** 初始行；用户可以增删 */
	rows: [{ branch: "master", version: "0.0.1" }],
	/** 「是否回填至项目」的默认勾选状态 */
	writeBack: false,
	/** 需要特别说明时写在这里，会替换默认的提示文案 */
	hints: [] as string[],
};
