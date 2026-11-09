/**
 * 版本发布表单：已经在 CurseForge 有项目，只发新版本时用。
 * 复制本文件与 data.ts 到 .narrafork/gen_ui/<名称>/ 后 render({path, wait: true}) 该目录。
 */
import { useState } from "react";
import {
	ActionIcon,
	Badge,
	Box,
	Button,
	Card,
	Grid,
	Group,
	MultiSelect,
	Select,
	Stack,
	TagsInput,
	Text,
	Textarea,
	TextInput,
	Title,
	UnstyledButton,
} from "@mantine/core";
import { DATA } from "./data";

type Version = {
	modVersion: string;
	mcVersions: string[];
	loaders: string[];
	javaVersion: string;
	releaseType: string;
	env: string;
	changelog: string;
};

type FormData = {
	project: { name: string; slug: string; projectId: string; license: string };
	/** 已发布版本摘要，只做展示 */
	released?: { version: string; mc: string; loader: string; date?: string }[];
	mcVersions?: string[];
	versions: Version[];
};

const D = DATA as FormData;

const LOADERS = ["NeoForge", "Forge", "Fabric"];
const RELEASE_TYPES = ["release", "beta", "alpha"];
const ENVS = ["双端", "仅客户端", "仅服务端"];
const JAVA_VERSIONS = ["Java 8", "Java 11", "Java 17", "Java 21", "Java 25"];

/** 兜底版本候选，正常应从 Game Versions API 取后写进 data.ts */
const FALLBACK_MC = ["1.21.11", "1.21.1", "1.21", "1.20.1", "1.20", "1.19.2", "1.12.2"];
const MC_VERSIONS = D.mcVersions ?? FALLBACK_MC;

const emptyVersion = (): Version => ({
	modVersion: "",
	mcVersions: [],
	loaders: [],
	javaVersion: "Java 21",
	releaseType: "release",
	env: ENVS[0],
	changelog: "",
});

export default function App() {
	const [versions, setVersions] = useState<Version[]>(
		D.versions.length ? D.versions : [emptyVersion()],
	);
	const [expanded, setExpanded] = useState<boolean[]>(versions.map(() => true));

	const setVersion = (index: number, patch: Partial<Version>) =>
		setVersions((list) => list.map((v, i) => (i === index ? { ...v, ...patch } : v)));
	const addVersion = () => {
		setVersions((list) => [...list, emptyVersion()]);
		setExpanded((list) => [...list, true]);
	};
	const removeVersion = (index: number) => {
		setVersions((list) => list.filter((_, i) => i !== index));
		setExpanded((list) => list.filter((_, i) => i !== index));
	};
	const toggle = (index: number) =>
		setExpanded((list) => list.map((open, i) => (i === index ? !open : open)));

	const comboCount = versions.reduce(
		(sum, v) => sum + Math.max(v.mcVersions.length, 1) * Math.max(v.loaders.length, 1),
		0,
	);

	const submit = () => {
		(globalThis as any).genUI?.submit(
			{ payload: JSON.stringify({ project: D.project, versions }) },
			`发布 ${versions.length} 个版本（${comboCount} 个文件）`,
		);
	};

	return (
		<Box p="lg">
			<Group justify="space-between" align="flex-start" mb="md">
				<Stack gap={2}>
					<Title order={3}>发布新版本</Title>
					<Text size="sm" c="dimmed">
						{D.project.name}
						{D.project.slug ? ` · ${D.project.slug}` : ""}
					</Text>
				</Stack>
				<Badge variant="light" size="lg">
					{D.project.license}
				</Badge>
			</Group>

			{D.released?.length ? (
				<Card withBorder shadow="sm" radius="md" p="sm" mb="md">
					<Group justify="space-between" mb={4}>
						<Text size="sm" fw={500}>
							已发布 {D.released.length} 个版本
						</Text>
						<Text size="xs" c="dimmed">
							最近：{D.released[0].version}
						</Text>
					</Group>
					<Group gap="xs">
						{D.released.slice(0, 6).map((item) => (
							<Badge key={item.version} size="sm" variant="default" tt="none">
								{item.version} · {item.loader} · {item.mc}
							</Badge>
						))}
					</Group>
				</Card>
			) : null}

			<Card withBorder shadow="sm" radius="md" p="md">
				<Group justify="space-between" mb="sm">
					<Group gap="xs">
						<Text fw={600}>待发布</Text>
						<Badge size="sm" variant="light">
							{versions.length} 个版本 · {comboCount} 个文件
						</Badge>
					</Group>
					<Button size="compact-sm" variant="light" onClick={addVersion}>
						+ 添加版本
					</Button>
				</Group>

				<Stack gap="sm">
					{versions.map((item, index) => (
						<Card key={index} withBorder radius="sm" p="sm">
							<Group justify="space-between" mb={expanded[index] ? "xs" : 0}>
								<UnstyledButton onClick={() => toggle(index)}>
									<Group gap="xs">
										<Text size="sm" fw={500}>
											版本 {index + 1}
										</Text>
										<Text size="xs" c="dimmed">
											{item.modVersion || "未填版本号"}
											{item.mcVersions.length ? ` · ${item.mcVersions.join(" / ")}` : ""}
											{item.loaders.length ? ` · ${item.loaders.join("+")}` : ""}
										</Text>
									</Group>
								</UnstyledButton>
								{versions.length > 1 && (
									<ActionIcon
										size="sm"
										variant="subtle"
										color="red"
										onClick={() => removeVersion(index)}
										aria-label="删除版本"
									>
										×
									</ActionIcon>
								)}
							</Group>

							{expanded[index] && (
								<Grid gutter="sm">
									<Grid.Col span={4}>
										<TextInput
										label="mod 版本"
										placeholder="0.0.1"
											value={item.modVersion}
											onChange={(e) => setVersion(index, { modVersion: e.currentTarget.value })}
										/>
									</Grid.Col>
									<Grid.Col span={4}>
										<TagsInput
											label="MC 版本"
											data={MC_VERSIONS}
											value={item.mcVersions}
											onChange={(val) => setVersion(index, { mcVersions: val })}
											clearable
										/>
									</Grid.Col>
									<Grid.Col span={4}>
										<MultiSelect
											label="加载器"
											data={LOADERS}
											value={item.loaders}
											onChange={(val) => setVersion(index, { loaders: val })}
											clearable
										/>
									</Grid.Col>
									<Grid.Col span={4}>
										<Select
											label="Java 版本"
											data={JAVA_VERSIONS}
											value={item.javaVersion}
											onChange={(val) => setVersion(index, { javaVersion: val ?? "Java 21" })}
										/>
									</Grid.Col>
									<Grid.Col span={4}>
										<Select
											label="发布类型"
											data={RELEASE_TYPES}
											value={item.releaseType}
											onChange={(val) => setVersion(index, { releaseType: val ?? "release" })}
										/>
									</Grid.Col>
									<Grid.Col span={4}>
										<Select
											label="运行环境"
											data={ENVS}
											value={item.env}
											onChange={(val) => setVersion(index, { env: val ?? ENVS[0] })}
										/>
									</Grid.Col>
									<Grid.Col span={12}>
										<Textarea
											label="更新说明"
											description="必须中英双语：英文块 + --- + 中文块；留空则由 agent 按 git 记录整理成双语"
											placeholder="可选"
											minRows={2}
											autosize
											value={item.changelog}
											onChange={(e) => setVersion(index, { changelog: e.currentTarget.value })}
										/>
									</Grid.Col>
								</Grid>
							)}
						</Card>
					))}
				</Stack>
			</Card>

			<Group mt="lg" justify="space-between" align="center">
				<Text size="xs" c="dimmed">
					每个「MC 版本 × 加载器」组合会单独上传一个文件
				</Text>
				<Button onClick={submit} radius="md">
					提交配置
				</Button>
			</Group>
		</Box>
	);
}
