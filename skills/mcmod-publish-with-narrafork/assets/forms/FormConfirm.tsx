/**
 * 提交前确认：把即将上传/提交的数据全部摆出来，允许改关键项，确认后执行。
 * 复制本文件与 data.ts 到 .narrafork/gen_ui/<名称>/ 后 render({path, wait: true}) 该目录。
 */
import { useState } from "react";
import {
	Alert,
	Badge,
	Box,
	Button,
	Card,
	Divider,
	Grid,
	Group,
	Stack,
	Tabs,
	Text,
	Textarea,
	TextInput,
	Title,
} from "@mantine/core";
import { DATA } from "./data";

type Release = {
	minecraft: string;
	loader: string;
	javaVersion: string;
	displayName: string;
	releaseType: string;
	artifact: string;
	sha256?: string;
	changelog: string;
};

type FormData = {
	project: {
		name: string;
		projectId: string;
		slug: string;
		/** 项目还没建时，确认后会先建再传 */
		category?: string;
		license?: string;
		pending?: boolean;
	};
	releases: Release[];
	/** 百科提交内容；不发百科时留空 */
	wiki?: {
		name: string;
		modid: string;
		cfprojectid: string;
		intro: string;
		targets: string[];
		content: string;
		author?: string;
		license?: string;
	};
	warnings?: string[];
};

const D = DATA as FormData;

export default function App() {
	const [releases, setReleases] = useState<Release[]>(D.releases);
	const [wiki, setWiki] = useState(D.wiki);

	const setRelease = (index: number, patch: Partial<Release>) =>
		setReleases((list) => list.map((r, i) => (i === index ? { ...r, ...patch } : r)));

	const submit = () => {
		(globalThis as any).genUI?.submit(
			{ payload: JSON.stringify({ project: D.project, releases, wiki: wiki ?? null }) },
			`确认发布 ${releases.length} 个文件${wiki ? " 并提交百科" : ""}`,
		);
	};

	const tabs = wiki ? ["cf", "wiki"] : ["cf"];
	const [tab, setTab] = useState<string | null>("cf");

	return (
		<Box p="lg">
			<Group justify="space-between" align="flex-start" mb="md">
				<Stack gap={2}>
					<Title order={3}>发布前确认</Title>
					<Text size="sm" c="dimmed">
						{D.project.name} · {D.project.slug || "未设置 slug"}
					</Text>
				</Stack>
				<Badge variant="light" size="lg">
					{releases.length} 个文件
				</Badge>
			</Group>

			{D.warnings?.length ? (
				<Alert color="orange" title="需要留意" mb="md">
					<ul style={{ margin: 0, paddingLeft: 18 }}>
						{D.warnings.map((item) => (
							<li key={item}>{item}</li>
						))}
					</ul>
				</Alert>
			) : null}

			<Tabs value={tab} onChange={setTab} variant="pills" radius="md">
				<Tabs.List mb="md">
					<Tabs.Tab value="cf">CurseForge</Tabs.Tab>
					{wiki && <Tabs.Tab value="wiki">MC百科</Tabs.Tab>}
				</Tabs.List>

				<Tabs.Panel value="cf">
					<Stack gap="md">
						<Card withBorder shadow="sm" radius="md" p="md">
							<Group justify="space-between" mb="xs">
								<Text fw={600}>CurseForge 项目</Text>
								{D.project.pending ? (
									<Badge color="orange" variant="light">待创建</Badge>
								) : (
									<Badge color="teal" variant="light">已存在</Badge>
								)}
							</Group>
							<Grid gutter="sm">
								<Grid.Col span={6}>
									<Text size="xs" c="dimmed">项目名</Text>
									<Text size="sm">{D.project.name}</Text>
								</Grid.Col>
								<Grid.Col span={6}>
									<Text size="xs" c="dimmed">slug</Text>
									<Text size="sm">{D.project.slug || "建好后确认"}</Text>
								</Grid.Col>
								<Grid.Col span={6}>
									<Text size="xs" c="dimmed">分类</Text>
									<Text size="sm">{D.project.category || "未填"}</Text>
								</Grid.Col>
								<Grid.Col span={6}>
									<Text size="xs" c="dimmed">许可证</Text>
									<Text size="sm">{D.project.license || "未填"}</Text>
								</Grid.Col>
							</Grid>
							{D.project.pending && (
								<Text size="xs" c="orange" mt="xs">
									确认后先创建项目，再上传下列文件
								</Text>
							)}
						</Card>
						{releases.map((release, index) => (
							<Card key={index} withBorder shadow="sm" radius="md" p="md">
								<Group justify="space-between" mb="sm">
									<Group gap="xs">
										<Text fw={600}>
											{release.minecraft} · {release.loader}
										</Text>
										<Badge size="sm" variant="light">
											{release.releaseType}
										</Badge>
										<Badge size="sm" variant="default">
											{release.javaVersion}
										</Badge>
									</Group>
								</Group>
								<Grid gutter="sm">
									<Grid.Col span={7}>
										<TextInput
											label="版本显示名"
											value={release.displayName}
											onChange={(e) =>
												setRelease(index, { displayName: e.currentTarget.value })
											}
										/>
									</Grid.Col>
									<Grid.Col span={5}>
										<Text size="xs" c="dimmed" mb={4}>
											JAR
										</Text>
										<Text size="sm" ff="monospace">
											{release.artifact}
										</Text>
										<Text size="xs" c="dimmed">
											sha256 {release.sha256 ? `${release.sha256.slice(0, 16)}…` : "未计算"}
										</Text>
									</Grid.Col>
									<Grid.Col span={12}>
										<Textarea
											label="更新说明"
											description="英文块 + --- + 中文块"
											minRows={3}
											autosize
											value={release.changelog}
											onChange={(e) =>
												setRelease(index, { changelog: e.currentTarget.value })
											}
										/>
									</Grid.Col>
								</Grid>
							</Card>
						))}
					</Stack>
				</Tabs.Panel>

				{wiki && (
					<Tabs.Panel value="wiki">
						<Card withBorder shadow="sm" radius="md" p="md">
							<Grid gutter="sm">
								<Grid.Col span={6}>
									<Text size="xs" c="dimmed">主要名称</Text>
									<Text size="sm">{wiki.name}</Text>
								</Grid.Col>
								<Grid.Col span={6}>
									<Text size="xs" c="dimmed">MODID</Text>
									<Text size="sm" ff="monospace">{wiki.modid}</Text>
								</Grid.Col>
								<Grid.Col span={6}>
									<Text size="xs" c="dimmed">CurseForge Project ID</Text>
									<Text size="sm">{wiki.cfprojectid || "未填"}</Text>
								</Grid.Col>
								<Grid.Col span={6}>
									<Text size="xs" c="dimmed">作者</Text>
									<Text size="sm">{wiki.author || "未填"}</Text>
								</Grid.Col>
								<Grid.Col span={6}>
									<Text size="xs" c="dimmed">许可证</Text>
									<Text size="sm">{wiki.license || "未填"}</Text>
								</Grid.Col>
								<Grid.Col span={12}>
									<Text size="xs" c="dimmed">运作方式与版本</Text>
									<Group gap={4} mt={4}>
										{wiki.targets.map((item) => (
											<Badge key={item} size="sm" variant="light" tt="none">
												{item}
											</Badge>
										))}
									</Group>
								</Grid.Col>
								<Grid.Col span={12}>
									<Divider my="xs" />
									<Text size="xs" c="dimmed">正文</Text>
									<Textarea
										minRows={4}
										autosize
										value={wiki.content}
										onChange={(e) => setWiki({ ...wiki, content: e.currentTarget.value })}
									/>
								</Grid.Col>
							</Grid>
							<Text size="xs" c="dimmed" mt="sm">
								提交后还需要在页面上填验证码，脚本会另外取一张图给你。
							</Text>
						</Card>
					</Tabs.Panel>
				)}
			</Tabs>

			<Group mt="lg" justify="space-between" align="center">
				<Text size="xs" c="dimmed">
					确认后开始上传与提交，这一步之后就是对外发布
				</Text>
				<Button onClick={submit} radius="md">
					确认并执行
				</Button>
			</Group>
		</Box>
	);
}
