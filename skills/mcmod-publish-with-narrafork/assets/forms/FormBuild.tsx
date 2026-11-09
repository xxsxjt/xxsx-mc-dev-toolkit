/**
 * 构建前确认：每行一个「分支 + 版本号」，可增删。
 * 只用于装了 zershyan-mcmod-style 的工程；提交后由 agent 跑 ./gradlew build。
 * 复制本文件与 data.ts 到 .narrafork/gen_ui/<名称>/ 后 render({path, wait: true}) 该目录。
 */
import { useState } from "react";
import {
	ActionIcon,
	Alert,
	Autocomplete,
	Badge,
	Box,
	Button,
	Card,
	Checkbox,
	Divider,
	Grid,
	Group,
	Stack,
	Text,
	TextInput,
	Title,
} from "@mantine/core";
import { DATA } from "./data";

type Row = { branch: string; version: string };

type FormData = {
	projectName: string;
	/** git 分支列表，作为候选；可自由输入 */
	branches: string[];
	/** 初始行 */
	rows: Row[];
	/** 默认是否勾选「回填至项目」 */
	writeBack?: boolean;
	hints?: string[];
};

const D = DATA as FormData;

const emptyRow = (version: string): Row => ({ branch: "", version });

export default function App() {
	const [rows, setRows] = useState<Row[]>(D.rows.length ? D.rows : [emptyRow("")]);
	const [writeBack, setWriteBack] = useState(D.writeBack ?? false);

	const setRow = (index: number, patch: Partial<Row>) =>
		setRows((list) => list.map((r, i) => (i === index ? { ...r, ...patch } : r)));

	const addRow = () =>
		setRows((list) => [...list, emptyRow(list[list.length - 1]?.version ?? "")]);

	const removeRow = (index: number) => setRows((list) => list.filter((_, i) => i !== index));

	const filled = rows.filter((r) => r.branch.trim() && r.version.trim());
	const ready = filled.length > 0;

	const submit = () => {
		(globalThis as any).genUI?.submit(
			{
				payload: JSON.stringify({
					rows: filled.map((r) => ({ branch: r.branch.trim(), version: r.version.trim() })),
					writeBack,
				}),
			},
			`按 ${filled.map((r) => `${r.branch}=${r.version}`).join('、')} 构建`,
		);
	};

	return (
		<Box p="lg">
			<Group justify="space-between" align="flex-start" mb="md">
				<Stack gap={2}>
					<Title order={3}>发布前确认</Title>
					<Text size="sm" c="dimmed">
						{D.projectName}
					</Text>
				</Stack>
				<Badge variant="light" size="lg">
					{ready ? `${filled.length} 个分支` : "待填写"}
				</Badge>
			</Group>

			<Card withBorder shadow="sm" radius="md" p="md">
				<Group justify="space-between" mb="sm">
					<Text fw={600}>分支与版本</Text>
					<Button size="compact-sm" variant="light" onClick={addRow}>
						+ 添加一行
					</Button>
				</Group>

				<Grid gutter="sm" mb={4}>
					<Grid.Col span={5}>
						<Text size="xs" c="dimmed">
							分支
						</Text>
					</Grid.Col>
					<Grid.Col span={5}>
						<Text size="xs" c="dimmed">
							版本号（mod_version）
						</Text>
					</Grid.Col>
				</Grid>

				<Stack gap="xs">
					{rows.map((row, index) => (
						<Grid key={index} gutter="sm" align="center">
							<Grid.Col span={5}>
								<Autocomplete
									data={D.branches}
									value={row.branch}
									onChange={(val) => setRow(index, { branch: val })}
									placeholder="master"
								/>
							</Grid.Col>
							<Grid.Col span={5}>
								<TextInput
									value={row.version}
									onChange={(e) => setRow(index, { version: e.currentTarget.value })}
									placeholder="0.0.1"
								/>
							</Grid.Col>
							<Grid.Col span={2}>
								<ActionIcon
									variant="subtle"
									color="red"
									onClick={() => removeRow(index)}
									disabled={rows.length === 1}
									aria-label="删除这行"
								>
									×
								</ActionIcon>
							</Grid.Col>
						</Grid>
					))}
				</Stack>

				<Divider my="sm" />
				<Checkbox
					checked={writeBack}
					onChange={(e) => setWriteBack(e.currentTarget.checked)}
					label="是否回填至项目"
					description="勾选后把各行版本号写进对应分支的 gradle.properties（mod_version），改动不提交，由你决定何时 commit"
					mb="xs"
				/>
				<Text size="xs" c="dimmed">
					版本号只写模组版本，不要带 MC 版本或 build 编号。空行会被忽略。
				</Text>
			</Card>

			<Alert color="blue" title="接下来" mt="md">
				{D.hints?.length ? (
					<ul style={{ margin: 0, paddingLeft: 18 }}>
						{D.hints.map((item) => (
							<li key={item}>{item}</li>
						))}
					</ul>
				) : (
					<Text size="sm">
						提交后会在各分支自动运行 <code>./gradlew build</code>（不跑 buildAlpha），
						然后用 <code>build/libs</code> 里不带 build 编号的 jar 继续发布。
					</Text>
				)}
			</Alert>

			<Group mt="lg" justify="flex-end">
				<Button onClick={submit} disabled={!ready} radius="md">
					确认
				</Button>
			</Group>
		</Box>
	);
}
