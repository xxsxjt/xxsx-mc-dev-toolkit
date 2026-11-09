/**
 * 发布配置表单模板。
 * 复制本文件与同目录的 data.ts 到 .narrafork/gen_ui/<名称>/ 后 render({path, wait: true}) 该目录。
 * 项目差异全部写在 data.ts，本文件不需要改动。
 */
import { useState } from "react";
import {
	ActionIcon,
	Autocomplete,
	Badge,
	Box,
	Button,
	Card,
	Checkbox,
	ColorInput,
	FileButton,
	Grid,
	Group,
	Input,
	Modal,
	MultiSelect,
	SegmentedControl,
	Select,
	Slider,
	Stack,
	Switch,
	Table,
	Tabs,
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
	/** CurseForge 版本标签中的 Java 版本，如 "Java 21" */
	javaVersion: string;
	releaseType: string;
	env: string;
	changelog: string;
};
type Author = { id: string; name: string; role: string };
type Dependency = { name: string; projectId: string; type: string };
type Entry = {
	name: string;
	/** 百科次要名称，取自 en_us.json */
	ename: string;
	regname: string;
	/** 百科资料分类，取值见 ENTRY_CATEGORIES */
	category: string;
	type: string;
	damage: string;
	stack: string;
};
type IconStyle = {
	font: string;
	lines: string[];
	stacked: boolean;
	fontSize: number;
	lineGap: number;
	letterSpacing: number;
	align: string;
	uppercase: boolean;
	border: number;
	padding: number;
	fg: string;
	bg: string;
	canvas: number;
};

const DEFAULT_ICON_STYLE: IconStyle = {
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
};

/** 与 make_icon.py 的 FONTS 一一对应；css 用于 canvas 近似预览 */
const ICON_FONTS = [
	{ value: "segoeuib.ttf", label: "Segoe UI Bold", css: "Segoe UI" },
	{ value: "arialbd.ttf", label: "Arial Bold", css: "Arial" },
	{ value: "calibrib.ttf", label: "Calibri Bold", css: "Calibri" },
	{ value: "impact.ttf", label: "Impact", css: "Impact" },
	{ value: "bahnschrift.ttf", label: "Bahnschrift", css: "Bahnschrift" },
	{ value: "georgiab.ttf", label: "Georgia Bold", css: "Georgia" },
	{ value: "consolab.ttf", label: "Consolas Bold", css: "Consolas" },
];

/** ForgeAttachment → Forge / Attachment，和 make_icon.py 的拆词一致 */
const splitWords = (name: string) =>
	name.match(/[A-Z]+(?![a-z])|[A-Z][a-z]+|[a-z]+|\d+/g) ?? [name];

const autoLines = (name: string) => {
	const words = splitWords(name);
	if (words.length < 2) return [name];
	const mid = Math.ceil(words.length / 2);
	return [words.slice(0, mid).join(" "), words.slice(mid).join(" ")];
};

const resolveLines = (style: IconStyle, name: string) => {
	let lines =
		style.lines.length === 1 && style.lines[0] === "auto" ? autoLines(name) : style.lines;
	if (!style.stacked) lines = [lines.join(" ")];
	return lines
		.filter(Boolean)
		.map((line) => (style.uppercase ? line.toUpperCase() : line));
};

type FormData = {
	modName: string;
	badge: string;
	extraLicenses?: string[];
	mcVersions?: string[];
	iconHint: string;
	coverHint: string;
	/** 默认是否勾选「没有图标就自动生成」 */
	autoIcon?: boolean;
	/** 占位图标样式，通常由 agent 从 skill 的 .narrafork/icon-style.json 读出来填在这里 */
	iconStyle?: IconStyle;
	entriesEmptyText: string;
	defaults: Record<string, any>;
	versions: Version[];
	authors: Author[];
	entries: Entry[];
	dependencies?: Dependency[];
};

const D = DATA as FormData;

/** CurseForge 分类及中文对照 */
/**
 * CurseForge 的 Main category（Class=Mods）。
 * 2026-11 从建项目页 Choose Game → General 的 MUI 下拉里实读，共 51 项；
 * 页面改版后按同样方式重抓，不要凭记忆补。
 */
const CF_CATEGORIES: { value: string; zh: string }[] = [
	{ value: "Adventure and RPG", zh: "冒险与角色扮演" },
	{ value: "API and Library", zh: "API 与前置" },
	{ value: "Armor, Tools, and Weapons", zh: "装备与武器" },
	{ value: "Automation", zh: "自动化" },
	{ value: "Biomes", zh: "生物群系" },
	{ value: "Bug Fixes", zh: "问题修复" },
	{ value: "Cosmetic", zh: "外观装饰" },
	{ value: "Create", zh: "Create 附属" },
	{ value: "CreativeMode", zh: "创造模式" },
	{ value: "Dimensions", zh: "维度" },
	{ value: "Education", zh: "教育" },
	{ value: "Energy", zh: "能源" },
	{ value: "Energy, Fluid, and Item Transport", zh: "能源/流体/物品运输" },
	{ value: "Farming", zh: "农业" },
	{ value: "Food", zh: "食物" },
	{ value: "Genetics", zh: "基因" },
	{ value: "Horror", zh: "恐怖" },
	{ value: "KubeJS", zh: "KubeJS 附属" },
	{ value: "Magic", zh: "魔法" },
	{ value: "Map and Information", zh: "地图与信息" },
	{ value: "MCreator", zh: "MCreator" },
	{ value: "Miscellaneous", zh: "杂项" },
	{ value: "Mobs", zh: "生物" },
	{ value: "Ores and Resources", zh: "矿物与资源" },
	{ value: "Performance", zh: "性能优化" },
	{ value: "Player Transport", zh: "玩家运输" },
	{ value: "Processing", zh: "加工处理" },
	{ value: "Redstone", zh: "红石" },
	{ value: "Server Utility", zh: "服务器实用" },
	{ value: "Storage", zh: "存储" },
	{ value: "Structures", zh: "结构" },
	{ value: "Technology", zh: "科技" },
	{ value: "Twitch Integration", zh: "Twitch 集成" },
	{ value: "Utility & QoL", zh: "实用与便利" },
	{ value: "World Gen", zh: "世界生成" },
	{ value: "Addons", zh: "附属" },
	{ value: "Applied Energistics 2", zh: "AE2 附属" },
	{ value: "Blood Magic", zh: "血魔法附属" },
	{ value: "Buildcraft", zh: "Buildcraft 附属" },
	{ value: "CraftTweaker", zh: "CraftTweaker 附属" },
	{ value: "Farmer's Delight", zh: "农夫乐事附属" },
	{ value: "Forestry", zh: "林业附属" },
	{ value: "Galacticraft", zh: "星系附属" },
	{ value: "Industrial Craft", zh: "工业附属" },
	{ value: "Integrated Dynamics", zh: "集成动力附属" },
	{ value: "Refined Storage", zh: "精致存储附属" },
	{ value: "Skyblock", zh: "空岛" },
	{ value: "Thaumcraft", zh: "神秘时代附属" },
	{ value: "Thermal Expansion", zh: "热力膨胀附属" },
	{ value: "Tinker's Construct", zh: "匠魂附属" },
	{ value: "Twilight Forest", zh: "暮色森林附属" },
];
const CF_VALUES = CF_CATEGORIES.map((item) => item.value);
const CF_ZH: Record<string, string> = Object.fromEntries(
	CF_CATEGORIES.map((item) => [item.value, item.zh]),
);

const LOADERS = ["NeoForge", "Forge", "Fabric"];
const RELEASE_TYPES = ["release", "beta", "alpha"];
const ENVS = ["双端", "仅客户端", "仅服务端"];
const CORE_ELEMENTS = ["实用", "科技", "魔法", "冒险", "农业", "装饰", "LIB", "魔改", "辅助"];

/** 百科「世界生成器」与「杂项」两组的全部选项，和 mcmod-enums.json 的 categoryExtra 一致 */
const EXTRA_ELEMENTS = [
	"资源", "世界", "群系", "结构", "生物",
	"能源", "存储", "物流", "道具", "安全", "红石", "食物", "模型", "关卡",
	"指南", "破坏", "Meme", "中式", "日式", "西式", "恐怖", "建材", "生存",
	"指令", "优化", "国创",
];
const LICENSE_TYPES = ["源码", "资产", "构件", "其他"];
const LICENSE_NAMES = [
	"ARR", "MIT", "AGPL-3.0", "GPL-3.0", "GPL-2.0", "LGPL-3.0",
	"Apache-2.0", "MPL-2.0", "BSD-3-Clause", "CC-BY-4.0", "CC-BY-SA-4.0",
];
const ROLES = ["所有者", "程序", "美术", "音效", "策划", "文案", "建筑", "贡献者", "吉祥物", "自定义"];
const WIKI_STATUS = ["不确定", "活跃", "半弃坑", "停更"];
const WIKI_SOURCE = ["不显示", "开源", "闭源"];
const DEP_TYPES = [
	{ value: "required", label: "必需前置" },
	{ value: "optional", label: "可选前置" },
	{ value: "incompatible", label: "不兼容" },
];
const JAVA_VERSIONS = ["Java 8", "Java 11", "Java 17", "Java 21", "Java 25"];
/** 百科资料分类，与添加页 data-multi-value 顺序一致 */
const ENTRY_CATEGORIES = [
	"物品/方块",
	"群系/群落",
	"世界/维度",
	"生物/实体",
	"附魔/魔咒",
	"BUFF/DEBUFF",
	"多方块结构",
	"自然生成",
	"绑定热键",
	"游戏设定",
];
const BASE_LICENSES = ["GNU AGPL 3.0", "GPL 3.0", "LGPL 3.0", "MIT", "Apache 2.0", "All Rights Reserved"];

/**
 * 兜底候选：没跑 Game Versions API 时用。
 * 正常流程先 query 出真实版本列表写进 data.ts 的 mcVersions，这里只是应急。
 */
const FALLBACK_MC_VERSIONS = [
	"26.3", "26.2", "26.1.2", "26.1.1", "26.1",
	"1.21.11", "1.21.10", "1.21.9", "1.21.8", "1.21.7", "1.21.6", "1.21.5",
	"1.21.4", "1.21.3", "1.21.2", "1.21.1", "1.21",
	"1.20.6", "1.20.5", "1.20.4", "1.20.3", "1.20.2", "1.20.1", "1.20",
	"1.19.4", "1.19.3", "1.19.2", "1.19.1", "1.19",
	"1.18.2", "1.18.1", "1.18",
	"1.17.1", "1.17",
	"1.16.5", "1.16.4", "1.16.3", "1.16.2", "1.16.1", "1.16",
	"1.15.2", "1.15.1", "1.15",
	"1.14.4", "1.14.3", "1.14.2", "1.14.1", "1.14",
	"1.13.2", "1.13.1", "1.13",
	"1.12.2", "1.12.1", "1.12",
	"1.11.2", "1.11.1", "1.11",
	"1.10.2", "1.10.1", "1.10",
	"1.9.4", "1.9.3", "1.9.2", "1.9.1", "1.9",
	"1.8.9", "1.8.8", "1.8.7", "1.8.6", "1.8.5", "1.8.4", "1.8.3", "1.8.2", "1.8.1", "1.8",
	"1.7.10", "1.7.2",
	"1.6.4", "1.6.2", "1.6.1",
	"1.5.2", "1.5.1",
	"1.4.7",
	"1.3.2", "1.3.1",
	"1.2.5",
	"1.1",
	"1.0",
];

/** 优先用 API 拉到的完整列表，没提供时才退回兜底候选 */
const MC_VERSIONS = D.mcVersions ?? FALLBACK_MC_VERSIONS;

const LICENSES = Array.from(new Set([...BASE_LICENSES, ...(D.extraLicenses ?? [])]));
/** 除 All Rights Reserved 外都视为开源许可 */
const isOpenSource = (license: string) => license !== "All Rights Reserved";

const envToSides = (env: string): [string, string] => {
	if (env === "仅客户端") return ["需装", "无需"];
	if (env === "仅服务端") return ["无需", "需装"];
	return ["需装", "需装"];
};

/** 百科的标签/关键词字段要求 {下标: 值} 形式 */
const indexed = (values?: string[]) =>
	Object.fromEntries((values ?? []).filter(Boolean).map((value, i) => [String(i), value]));

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
	const [wiki, setWiki] = useState(false);
	const [tab, setTab] = useState<string | null>("cf");
	const [v, setV] = useState<Record<string, any>>({});
	const [distTouched, setDistTouched] = useState(false);
	const [versionsOpen, setVersionsOpen] = useState(true);

	const [versions, setVersions] = useState<Version[]>(D.versions);
	const [expanded, setExpanded] = useState<boolean[]>(D.versions.map(() => true));
	const [authors, setAuthors] = useState<Author[]>(D.authors);
	const [deps, setDeps] = useState<Dependency[]>(D.dependencies ?? []);
	const [cfIcon, setCfIcon] = useState<File | null>(null);
	const [autoIcon, setAutoIcon] = useState(D.autoIcon ?? true);
	const [iconOpen, setIconOpen] = useState(false);
	const [iconStyle, setIconStyle] = useState<IconStyle>({ ...DEFAULT_ICON_STYLE, ...(D.iconStyle ?? {}) });

	const iconFont = ICON_FONTS.find((f) => f.value === iconStyle.font) ?? ICON_FONTS[0];
	/** 编辑框里显示原始两行，不应用大写与合并 */
	const rawLines =
		iconStyle.lines.length === 1 && iconStyle.lines[0] === "auto"
			? autoLines(D.modName)
			: iconStyle.lines;
	const iconLines = resolveLines(iconStyle, D.modName);
	const editIconLine = (index: number, value: string) =>
		setIconStyle((s) => {
			const base =
				s.lines.length === 1 && s.lines[0] === "auto" ? autoLines(D.modName) : s.lines;
			const next = [base[0] ?? "", base[1] ?? ""];
			next[index] = value;
			return { ...s, lines: next };
		});

	const [wCover, setWCover] = useState<File | null>(null);

	const [entries, setEntries] = useState<Entry[]>(D.entries);
	const [editing, setEditing] = useState<number | null>(null);
	const [draft, setDraft] = useState<Entry | null>(null);

	const [newVersionOpen, setNewVersionOpen] = useState(false);
	const [newVersion, setNewVersion] = useState<Version>(emptyVersion());

	const [wikiTargets, setWikiTargets] = useState<string[] | null>(null);
	const [targetOpen, setTargetOpen] = useState(false);
	const [targetDraft, setTargetDraft] = useState<{ loaders: string[]; mcVersions: string[] }>({
		loaders: [],
		mcVersions: [],
	});

	const text = (k: string) => ({
		value: (v[k] as string) ?? "",
		onChange: (e: any) => setV((s) => ({ ...s, [k]: e.currentTarget.value })),
	});
	const pick = (k: string) => ({
		value: (v[k] as string) ?? null,
		onChange: (val: any) => setV((s) => ({ ...s, [k]: val })),
	});
	const multi = (k: string) => ({
		value: (v[k] as string[]) ?? [],
		onChange: (val: any) => setV((s) => ({ ...s, [k]: val })),
	});

	const license = (v.cfLicense as string) ?? D.defaults.cfLicense;
	const distribute =
		v.cfDistribute === undefined ? isOpenSource(license) : Boolean(v.cfDistribute);
	const comments = v.cfComments === undefined ? true : Boolean(v.cfComments);
	const pages = v.cfProjectPages === undefined ? true : Boolean(v.cfProjectPages);

	const allMcVersions = Array.from(new Set(versions.flatMap((item) => item.mcVersions)));
	const allLoaders = Array.from(new Set(versions.flatMap((item) => item.loaders)));
	const firstEnv = versions[0]?.env ?? ENVS[0];

	const cfTargets = Array.from(
		new Set(
			versions.flatMap((item) =>
				item.loaders.flatMap((loader) => item.mcVersions.map((mc) => `${loader} ${mc}`)),
			),
		),
	);
	const targets = wikiTargets ?? cfTargets;

	const confirmTargets = () => {
		const combos = targetDraft.loaders.flatMap((loader) =>
			targetDraft.mcVersions.map((mc) => `${loader} ${mc}`),
		);
		setWikiTargets(Array.from(new Set([...targets, ...combos])));
		setTargetDraft({ loaders: [], mcVersions: [] });
		setTargetOpen(false);
	};
	const removeTarget = (value: string) =>
		setWikiTargets(targets.filter((item) => item !== value));

	const derivedSource = isOpenSource(license) ? "开源" : "闭源";
	const [derivedClient, derivedServer] = envToSides(firstEnv);

	const onLicense = (val: string | null) => {
		const next = val ?? "";
		setV((s) => ({
			...s,
			cfLicense: next,
			cfDistribute: distTouched ? s.cfDistribute : isOpenSource(next),
		}));
	};

	const setVersion = (index: number, patch: Partial<Version>) =>
		setVersions((list) => list.map((item, i) => (i === index ? { ...item, ...patch } : item)));
	const removeVersion = (index: number) => {
		setVersions((list) => list.filter((_, i) => i !== index));
		setExpanded((list) => list.filter((_, i) => i !== index));
	};
	const toggleVersion = (index: number) =>
		setExpanded((list) => list.map((open, i) => (i === index ? !open : open)));

	const confirmNewVersion = () => {
		setVersions((list) => [...list, newVersion]);
		setExpanded((list) => [...list, true]);
		setNewVersion(emptyVersion());
		setNewVersionOpen(false);
	};

	const setAuthor = (index: number, patch: Partial<Author>) =>
		setAuthors((list) => list.map((item, i) => (i === index ? { ...item, ...patch } : item)));
	const addAuthor = () => setAuthors((list) => [...list, { id: "", name: "", role: "开发者" }]);
	const removeAuthor = (index: number) => setAuthors((list) => list.filter((_, i) => i !== index));

	const setDep = (index: number, patch: Partial<Dependency>) =>
		setDeps((list) => list.map((item, i) => (i === index ? { ...item, ...patch } : item)));
	const addDep = () =>
		setDeps((list) => [...list, { name: "", projectId: "", type: "required" }]);
	const removeDep = (index: number) => setDeps((list) => list.filter((_, i) => i !== index));

	const editEntry = (index: number) => {
		setEditing(index);
		setDraft({ ...entries[index] });
	};
	const confirmEntry = () => {
		if (editing === null || !draft) return;
		setEntries((list) => list.map((item, i) => (i === editing ? draft : item)));
		setEditing(null);
		setDraft(null);
	};
	const addEntry = () => {
		const created: Entry = {
			name: "",
			ename: "",
			regname: "",
			category: "物品/方块",
			type: "道具",
			damage: "-",
			stack: "1",
		};
		setEntries((list) => [...list, created]);
		setEditing(entries.length);
		setDraft({ ...created });
	};
	const removeEntry = (index: number) => setEntries((list) => list.filter((_, i) => i !== index));

	const submit = () => {
		// 只回传用户改过的字段：全量回传会被工具显示层截断，长描述尤其容易撑爆
		const changed: Record<string, any> = {};
		for (const [key, fallback] of Object.entries(D.defaults)) {
			if (key === "wTags" || key === "wKeys") continue; // 这两个统一转成逗号字符串，见下
			const current = v[key];
			const empty =
				current === undefined ||
				current === "" ||
				(Array.isArray(current) && current.length === 0);
			const value = empty ? fallback : current;
			if (JSON.stringify(value) !== JSON.stringify(fallback)) changed[key] = value;
		}
		// 百科的标签与关键词是逗号分隔的文本框，不是多值对象
		const joinTags = (value: any) =>
			Array.isArray(value) ? value.join(",") : value ?? "";
		const out = {
			wiki,
			changed,
			cfDistribute: distribute,
			cfComments: comments,
			cfProjectPages: pages,
			cfIcon: cfIcon?.name ?? "src/main/resources/logo.png",
			cfAutoIcon: autoIcon,
			cfIconStyle: iconStyle,
			wCover: wCover?.name ?? "src/main/resources/logo.png",
			wSource: (v.wSource as string) ?? derivedSource,
			wikiTargets: targets,
			wTags: joinTags(v.wTags ?? D.defaults.wTags),
			wKeys: joinTags(v.wKeys ?? D.defaults.wKeys),
			wClient: (v.wClient as string) ?? derivedClient,
			wServer: (v.wServer as string) ?? derivedServer,
			versions,
			authors,
			entries,
			dependencies: deps,
		};
		(globalThis as any).genUI?.submit(
			{ payload: JSON.stringify(out) },
			wiki ? "按此配置发布到 CurseForge 与 MC百科" : "按此配置发布到 CurseForge",
		);
	};

	const cfOption = ({ option }: any) => (
		<Group justify="space-between" w="100%" wrap="nowrap">
			<Text size="sm">{option.value}</Text>
			<Text size="xs" c="dimmed">
				{CF_ZH[option.value] ?? ""}
			</Text>
		</Group>
	);

	const picker = (label: string, value: File | null, onChange: any, hint: string, extra?: any) => (
		<Input.Wrapper label={label}>
			<Group gap="xs" h={36} align="center" wrap="nowrap">
				<FileButton onChange={onChange} accept="image/png,image/jpeg">
					{(props) => (
						<Button variant="default" size="xs" {...props}>
							选择文件
						</Button>
					)}
				</FileButton>
				{extra}
				<Text size="xs" c="dimmed" truncate>
					{value ? value.name : hint}
				</Text>
			</Group>
		</Input.Wrapper>
	);

	return (
		<Box p="lg">
			<Group justify="space-between" align="flex-start" mb="md">
				<Stack gap={2}>
					<Title order={3}>发布配置</Title>
					<Text size="sm" c="dimmed">
						{D.modName} · {allLoaders.join(" / ")} · {allMcVersions.join(" / ")}
					</Text>
				</Stack>
				<Badge variant="light" size="lg">
					{D.badge}
				</Badge>
			</Group>

			<Card withBorder shadow="sm" radius="md" p="md" mb="md">
				<Checkbox
					checked={wiki}
					onChange={(e) => {
						const on = e.currentTarget.checked;
						setWiki(on);
						if (!on) setTab("cf");
					}}
					label="同时发布到 MC百科"
					description="CurseForge 必发；百科条目依赖 CF Project ID，可以不发。勾选后出现百科配置。"
				/>
			</Card>

			<Tabs value={tab} onChange={setTab} variant="pills" radius="md">
				<Tabs.List mb="md">
					<Tabs.Tab value="cf">CurseForge</Tabs.Tab>
					{wiki && <Tabs.Tab value="wiki">MC百科</Tabs.Tab>}
				</Tabs.List>

				<Tabs.Panel value="cf">
					<Stack gap="md">
						<Card withBorder shadow="sm" radius="md" p="md">
							<Group justify="space-between" mb="sm">
								<Text fw={600}>项目信息</Text>
								<Badge size="xs" variant="light" color="gray">
									灰色提示为调研自动填入
								</Badge>
							</Group>
							<Grid gutter="sm">
								<Grid.Col span={4}>
									<TextInput
										label="项目名"
										placeholder={D.defaults.cfName}
										{...text("cfName")}
									/>
								</Grid.Col>
								<Grid.Col span={4}>
									<Select
										label="许可证"
										data={LICENSES}
										value={license}
										onChange={onLicense}
										searchable
									/>
								</Grid.Col>
								<Grid.Col span={4}>
									<Input.Wrapper label="允许第三方分发">
										<Group h={36} align="center" gap="xs" wrap="nowrap">
											<Switch
												checked={distribute}
												onChange={(e) => {
													setDistTouched(true);
													setV((s) => ({ ...s, cfDistribute: e.currentTarget.checked }));
												}}
											/>
											<Text size="xs" c="dimmed">
												{isOpenSource(license) ? "开源许可，默认允许" : "闭源许可，默认关闭"}
											</Text>
										</Group>
									</Input.Wrapper>
								</Grid.Col>
								<Grid.Col span={12}>
									<TextInput
										label="简介"
										description="1～256 字符"
										placeholder={D.defaults.cfSummary}
										{...text("cfSummary")}
									/>
								</Grid.Col>
								<Grid.Col span={12}>
									<Textarea
										label="详细描述"
										description="留空则按工程 README 与源码整理"
										placeholder={D.defaults.cfDescription}
										minRows={2}
										autosize
										{...text("cfDescription")}
									/>
								</Grid.Col>
								<Grid.Col span={7}>
									<Autocomplete
										label="主分类"
										withAsterisk
										data={CF_VALUES}
										renderOption={cfOption}
										placeholder={D.defaults.cfCategory}
										{...pick("cfCategory")}
									/>
								</Grid.Col>
								<Grid.Col span={5}>
									<MultiSelect
										label="附加分类"
										data={CF_VALUES}
										renderOption={cfOption}
										placeholder="可选"
										clearable
										{...multi("cfExtraCategories")}
									/>
								</Grid.Col>
								<Grid.Col span={7}>
									{picker(
										"项目图标（超过 400px 自动缩放）",
										cfIcon,
										setCfIcon,
										D.iconHint,
										<Group gap="xs" wrap="nowrap">
											<Checkbox
												size="xs"
												label="没有就自动生成"
												checked={autoIcon}
												onChange={(e) => setAutoIcon(e.currentTarget.checked)}
											/>
											<Button
												size="compact-xs"
												variant="subtle"
												disabled={!autoIcon}
												onClick={() => setIconOpen(true)}
											>
												编辑样式
											</Button>
										</Group>,
									)}
								</Grid.Col>
								<Grid.Col span={5}>
									<Input.Wrapper label="允许评论">
										<Group h={36} align="center">
											<Switch
												checked={comments}
												onChange={(e) =>
													setV((s) => ({ ...s, cfComments: e.currentTarget.checked }))
												}
											/>
										</Group>
									</Input.Wrapper>
								</Grid.Col>
								<Grid.Col span={5}>
									<Input.Wrapper
										label="启用 Project Pages"
										description="建项向导没这一项时，建好后到项目设置里开"
									>
										<Group h={36} align="center">
											<Switch
												checked={pages}
												onChange={(e) =>
													setV((s) => ({ ...s, cfProjectPages: e.currentTarget.checked }))
												}
											/>
										</Group>
									</Input.Wrapper>
								</Grid.Col>
								<Grid.Col span={12}>
									<TextInput
										label="源码链接"
										description="创建向导里没有这一项，建完项目后由 agent 到项目设置 → Links → Source 补填"
										placeholder={D.defaults.cfSourceUrl}
										{...text("cfSourceUrl")}
									/>
								</Grid.Col>
							</Grid>
						</Card>

						<Card withBorder shadow="sm" radius="md" p="md">
							<Group justify="space-between" mb="sm">
								<Group gap="xs">
									<Text fw={600}>依赖关系</Text>
									<Badge size="xs" variant="light" color="gray">
										从 build.gradle 解析，内嵌与仅运行时的不声明
									</Badge>
								</Group>
								<Button size="compact-sm" variant="light" onClick={addDep}>
									+ 添加依赖
								</Button>
							</Group>
							{deps.length === 0 ? (
								<Text size="sm" c="dimmed">
									没有需要声明的前置模组
								</Text>
							) : (
								<Stack gap="sm">
									{deps.map((dep, index) => (
										<Group key={index} align="flex-end" gap="sm" wrap="nowrap">
											<TextInput
												label={index === 0 ? "模组名" : undefined}
												placeholder="Curios"
												value={dep.name}
												onChange={(e) => setDep(index, { name: e.currentTarget.value })}
												style={{ flex: 1 }}
											/>
											<TextInput
												label={index === 0 ? "CF 项目 ID" : undefined}
												placeholder="309927"
												value={dep.projectId}
												onChange={(e) => setDep(index, { projectId: e.currentTarget.value })}
												style={{ flex: 1 }}
											/>
											<Select
												label={index === 0 ? "关系" : undefined}
												data={DEP_TYPES}
												value={dep.type}
												onChange={(val) => setDep(index, { type: val ?? "required" })}
												style={{ flex: 1 }}
											/>
											<ActionIcon
												size="lg"
												variant="subtle"
												color="red"
												onClick={() => removeDep(index)}
												aria-label="删除依赖"
											>
												×
											</ActionIcon>
										</Group>
									))}
								</Stack>
							)}
						</Card>

						<Card withBorder shadow="sm" radius="md" p="md">
							<Group justify="space-between" mb={versionsOpen ? "sm" : 0}>
								<UnstyledButton onClick={() => setVersionsOpen((open) => !open)}>
									<Group gap="xs">
										<Text fw={600}>版本与上传设置</Text>
										<Badge size="sm" variant="light">
											{versions.length} 个版本
										</Badge>
									</Group>
								</UnstyledButton>
								<Button size="compact-sm" variant="light" onClick={() => setNewVersionOpen(true)}>
									+ 添加版本
								</Button>
							</Group>

							{versionsOpen && (
								<Stack gap="sm">
									{versions.map((item, index) => (
										<Card key={index} withBorder radius="sm" p="sm">
											<Group justify="space-between" mb={expanded[index] ? "xs" : 0}>
												<UnstyledButton onClick={() => toggleVersion(index)}>
													<Group gap="xs">
														<Text size="sm" fw={500}>
															版本 {index + 1}
														</Text>
														<Text size="xs" c="dimmed">
															{item.modVersion} · {item.loaders.join("+")} ·{" "}
															{item.mcVersions.join(" / ")}
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
															onChange={(e) =>
																setVersion(index, { modVersion: e.currentTarget.value })
															}
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
															onChange={(val) =>
																setVersion(index, { javaVersion: val ?? "Java 21" })
															}
														/>
													</Grid.Col>
													<Grid.Col span={4}>
														<Select
															label="发布类型"
															data={RELEASE_TYPES}
															value={item.releaseType}
															onChange={(val) =>
																setVersion(index, { releaseType: val ?? "release" })
															}
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
															onChange={(e) =>
																setVersion(index, { changelog: e.currentTarget.value })
															}
														/>
													</Grid.Col>
												</Grid>
											)}
										</Card>
									))}
								</Stack>
							)}
						</Card>
					</Stack>
				</Tabs.Panel>

				{wiki && (
					<Tabs.Panel value="wiki">
						<Stack gap="md">
							<Card withBorder shadow="sm" radius="md" p="md">
								<Group justify="space-between" mb="sm">
									<Text fw={600}>条目信息</Text>
									<Badge size="xs" variant="light" color="gray">
										灰色提示为调研自动填入
									</Badge>
								</Group>
								<Grid gutter="sm">
									<Grid.Col span={4}>
										<TextInput
											label="主要名称"
											withAsterisk
											description="有汉化填中文名，否则填其他语言名；译名须来自官方或社区汉化"
											placeholder={D.defaults.wName}
											{...text("wName")}
										/>
									</Grid.Col>
									<Grid.Col span={4}>
										<TextInput
											label="次要名称"
											description="主要名称是中文时才填原名，否则留空"
											placeholder={D.defaults.wEname}
											{...text("wEname")}
										/>
									</Grid.Col>
									<Grid.Col span={4}>
										<TextInput
											label="简写名称"
											description="必须由用户提供的社区通用缩写，如 GT6、TiC2；没有就留空，不要自己编"
											placeholder={D.defaults.wSname || undefined}
											{...text("wSname")}
										/>
									</Grid.Col>
									<Grid.Col span={12}>
										<TextInput
											label="一句话简介"
											placeholder={D.defaults.wIntro}
											{...text("wIntro")}
										/>
									</Grid.Col>
									<Grid.Col span={4}>
										<TextInput
											label="MODID"
											withAsterisk
											placeholder={D.defaults.wModid}
											{...text("wModid")}
										/>
									</Grid.Col>
									<Grid.Col span={4}>
										<TextInput
											label="CurseForge Project ID"
											placeholder={D.defaults.wCfId}
											{...text("wCfId")}
										/>
									</Grid.Col>
									<Grid.Col span={4}>
										<TextInput
											label="Modrinth Project ID（可空）"
											placeholder={D.defaults.wMrId}
											{...text("wMrId")}
										/>
									</Grid.Col>
									<Grid.Col span={4}>
										<Select
											label="核心元素（单选）"
											withAsterisk
											data={CORE_ELEMENTS}
											placeholder={D.defaults.wCore}
											{...pick("wCore")}
										/>
									</Grid.Col>
									<Grid.Col span={8}>
										<MultiSelect
											label="杂项元素"
											data={EXTRA_ELEMENTS}
											placeholder="可选"
											clearable
											{...multi("wExtra")}
										/>
									</Grid.Col>
									<Grid.Col span={4}>
										<Select
											label="官方状态"
											data={WIKI_STATUS}
											placeholder={D.defaults.wStatus}
											{...pick("wStatus")}
										/>
									</Grid.Col>
									<Grid.Col span={4}>
										<Select
											label="开源状态"
											data={WIKI_SOURCE}
											placeholder={derivedSource}
											{...pick("wSource")}
										/>
									</Grid.Col>
									<Grid.Col span={4}>
										{picker("封面（16:10）", wCover, setWCover, D.coverHint)}
									</Grid.Col>
									<Grid.Col span={6}>
										<TagsInput
											label="模组标签"
											description="把相似模组归到一起的通用词，如 科技、魔法"
											placeholder={D.defaults.wTags}
											{...multi("wTags")}
										/>
									</Grid.Col>
									<Grid.Col span={6}>
										<TagsInput
											label="搜索关键词"
											description="只填用户给的别名、外号；百科禁止滥用，不清楚就留空"
											placeholder={D.defaults.wKeys}
											{...multi("wKeys")}
										/>
									</Grid.Col>
								</Grid>
							</Card>

							<Card withBorder shadow="sm" radius="md" p="md">
								<Group justify="space-between" mb="sm">
									<Text fw={600}>作者</Text>
									<Button size="compact-sm" variant="light" onClick={addAuthor}>
										+ 添加作者
									</Button>
								</Group>
								<Stack gap="sm">
									{authors.map((item, index) => (
										<Group key={index} align="flex-end" gap="sm" wrap="nowrap">
											<TextInput
												label={index === 0 ? "作者 ID" : undefined}
												withAsterisk={index === 0}
												placeholder="作者页 /author/数字.html 里的 ID"
												value={item.id}
												onChange={(e) => setAuthor(index, { id: e.currentTarget.value })}
												style={{ flex: 1 }}
											/>
											<TextInput
												label={index === 0 ? "作者名" : undefined}
												placeholder={
													index === 0 ? D.defaults.wAuthorName ?? "作者名" : "作者名"
												}
												value={item.name}
												onChange={(e) => setAuthor(index, { name: e.currentTarget.value })}
												style={{ flex: 1 }}
											/>
											<Autocomplete
												label={index === 0 ? "职位" : undefined}
												data={ROLES}
												filter={({ options }) => options}
												placeholder="可选择或自定义"
												value={item.role}
												onChange={(val) => setAuthor(index, { role: val })}
												style={{ flex: 1 }}
											/>
											<ActionIcon
												size="lg"
												variant="subtle"
												color="red"
												disabled={authors.length === 1}
												onClick={() => removeAuthor(index)}
												aria-label="删除作者"
											>
												×
											</ActionIcon>
										</Group>
									))}
								</Stack>
							</Card>

							<Card withBorder shadow="sm" radius="md" p="md">
								<Text fw={600} mb="sm">
									许可协议
								</Text>
								<Grid gutter="sm">
									<Grid.Col span={4}>
										<Select
											label="协议类型"
											data={LICENSE_TYPES}
											placeholder={D.defaults.wLicenseType}
											{...pick("wLicenseType")}
										/>
									</Grid.Col>
									<Grid.Col span={8}>
										<Autocomplete
											label="协议名称"
											data={LICENSE_NAMES}
											placeholder={D.defaults.wLicenseName}
											{...pick("wLicenseName")}
										/>
									</Grid.Col>
								</Grid>
								<Text size="xs" c="dimmed" mt="xs">
									留空表示不填；ARR 表示保留所有权利。版本范围默认「通用」，提交时为空。
								</Text>
							</Card>

							<Card withBorder shadow="sm" radius="md" p="md">
								<Text fw={600} mb="sm">
									运行与链接
								</Text>
								<Grid gutter="sm">
									<Grid.Col span={8}>
										<Input.Wrapper label="运作方式与版本">
											<Box
												style={{
													minHeight: 36,
													border: "1px solid var(--mantine-color-default-border)",
													borderRadius: "var(--mantine-radius-sm)",
													padding: "4px 8px",
													display: "flex",
													flexWrap: "wrap",
													gap: 6,
													alignItems: "center",
												}}
											>
												{targets.map((item) => (
													<Badge
														key={item}
														size="md"
														variant="light"
														tt="none"
														rightSection={
															<Text
																component="span"
																onClick={() => removeTarget(item)}
																style={{ cursor: "pointer" }}
															>
																×
															</Text>
														}
													>
														{item}
													</Badge>
												))}
												<ActionIcon
													size="sm"
													variant="subtle"
													onClick={() => setTargetOpen(true)}
													aria-label="添加运作方式与版本"
												>
													+
												</ActionIcon>
												{wikiTargets !== null && (
													<Button
														size="compact-xs"
														variant="subtle"
														onClick={() => setWikiTargets(null)}
													>
														恢复跟随 CurseForge
													</Button>
												)}
											</Box>
										</Input.Wrapper>
									</Grid.Col>
									<Grid.Col span={2}>
										<Select
											label="客户端"
											data={["需装", "可选", "无需"]}
											placeholder={derivedClient}
											{...pick("wClient")}
										/>
									</Grid.Col>
									<Grid.Col span={2}>
										<Select
											label="服务端"
											data={["需装", "可选", "无需"]}
											placeholder={derivedServer}
											{...pick("wServer")}
										/>
									</Grid.Col>
									<Grid.Col span={12}>
										<Textarea
											label="模组关系"
											description="代码联动的前置或附属，如「JEI（联动）、Jade（联动）」"
											placeholder={D.defaults.wRelations}
											minRows={2}
											autosize
											{...text("wRelations")}
										/>
									</Grid.Col>
									<Grid.Col span={12}>
										<Textarea
											label="相关链接"
											description="CF 项目页会自动补，其余一行一个"
											placeholder={D.defaults.wLinks}
											minRows={2}
											autosize
											{...text("wLinks")}
										/>
									</Grid.Col>
								</Grid>
								<Text size="xs" c="dimmed" mt="xs">
									默认跟随 CurseForge 的所有「加载器 × MC 版本」组合；手动增删后停止同步，可点「恢复跟随」还原。
								</Text>
							</Card>

							<Card withBorder shadow="sm" radius="md" p="md">
								<Group justify="space-between" mb="sm">
									<Group gap="xs">
										<Text fw={600}>资料条目</Text>
										<Badge size="xs" variant="light" color="gray">
											{entries.length} 条示意 · 实际由工程注册项生成
										</Badge>
									</Group>
									<Button size="compact-sm" variant="light" onClick={addEntry}>
										+ 添加条目
									</Button>
								</Group>
								{entries.length === 0 ? (
									<Text size="sm" c="dimmed">
										{D.entriesEmptyText}
									</Text>
								) : (
									<Table striped highlightOnHover withTableBorder>
										<Table.Thead>
											<Table.Tr>
												<Table.Th w={56}>图标</Table.Th>
												<Table.Th>名称</Table.Th>
												<Table.Th w={110}>分类</Table.Th>
												<Table.Th>注册名</Table.Th>
												<Table.Th w={100}>资料类型</Table.Th>
												<Table.Th w={70}>耐久</Table.Th>
												<Table.Th w={60}>堆叠</Table.Th>
												<Table.Th w={80}>操作</Table.Th>
											</Table.Tr>
										</Table.Thead>
										<Table.Tbody>
											{entries.map((entry, index) => (
												<Table.Tr key={index}>
													<Table.Td>
														<Box w={32} h={32} bg="var(--mantine-color-default-border)" />
													</Table.Td>
													<Table.Td>
														<Text size="sm">{entry.name || "未命名"}</Text>
														<Text size="xs" c="dimmed">
															{entry.ename}
														</Text>
													</Table.Td>
													<Table.Td>
														<Text size="sm">{entry.category}</Text>
													</Table.Td>
													<Table.Td>
														<Text size="xs" c="dimmed" ff="monospace">
															{entry.regname || "-"}
														</Text>
													</Table.Td>
													<Table.Td>
														<Text size="sm">{entry.type}</Text>
													</Table.Td>
													<Table.Td>
														<Text size="sm">{entry.damage}</Text>
													</Table.Td>
													<Table.Td>
														<Text size="sm">{entry.stack}</Text>
													</Table.Td>
													<Table.Td>
														<Group gap={4} wrap="nowrap">
															<ActionIcon
																size="sm"
																variant="subtle"
																onClick={() => editEntry(index)}
															>
																✎
															</ActionIcon>
															<ActionIcon
																size="sm"
																variant="subtle"
																color="red"
																onClick={() => removeEntry(index)}
															>
																×
															</ActionIcon>
														</Group>
													</Table.Td>
												</Table.Tr>
											))}
										</Table.Tbody>
									</Table>
								)}
								<Text size="xs" c="dimmed" mt="xs">
									名称与注册名取自语言文件和注册表，耐久与堆叠来自运行时导出。
								</Text>
							</Card>
						</Stack>
					</Tabs.Panel>
				)}
			</Tabs>

			<Group mt="lg" justify="space-between" align="center">
				<Text size="xs" c="dimmed">
					留空的项按灰色提示值执行
				</Text>
				<Button onClick={submit} radius="md">
					提交配置
				</Button>
			</Group>

			<Modal opened={newVersionOpen} onClose={() => setNewVersionOpen(false)} title="新建版本">
				<Stack gap="sm">
					<TextInput
						label="mod 版本"
						placeholder="0.0.1"
						value={newVersion.modVersion}
						onChange={(e) => setNewVersion({ ...newVersion, modVersion: e.currentTarget.value })}
					/>
					<TagsInput
						label="MC 版本"
						data={MC_VERSIONS}
						value={newVersion.mcVersions}
						onChange={(val) => setNewVersion({ ...newVersion, mcVersions: val })}
						clearable
					/>
					<MultiSelect
						label="加载器"
						data={LOADERS}
						value={newVersion.loaders}
						onChange={(val) => setNewVersion({ ...newVersion, loaders: val })}
						clearable
					/>
					<Select
						label="Java 版本"
						data={JAVA_VERSIONS}
						value={newVersion.javaVersion}
						onChange={(val) => setNewVersion({ ...newVersion, javaVersion: val ?? "Java 21" })}
					/>
					<Select
						label="发布类型"
						data={RELEASE_TYPES}
						value={newVersion.releaseType}
						onChange={(val) => setNewVersion({ ...newVersion, releaseType: val ?? "release" })}
					/>
					<Group justify="flex-end" mt="xs">
						<Button variant="default" onClick={() => setNewVersionOpen(false)}>
							取消
						</Button>
						<Button onClick={confirmNewVersion}>确定</Button>
					</Group>
				</Stack>
			</Modal>

			<Modal opened={targetOpen} onClose={() => setTargetOpen(false)} title="添加运作方式与版本">
				<Stack gap="sm">
					<MultiSelect
						label="加载器"
						data={LOADERS}
						value={targetDraft.loaders}
						onChange={(val) => setTargetDraft({ ...targetDraft, loaders: val })}
						clearable
					/>
					<TagsInput
						label="MC 版本"
						data={MC_VERSIONS}
						value={targetDraft.mcVersions}
						onChange={(val) => setTargetDraft({ ...targetDraft, mcVersions: val })}
						clearable
					/>
					<Text size="xs" c="dimmed">
						每个加载器与每个 MC 版本的组合都会加入列表，例如 Forge + 1.20.1/1.20 会生成两项。
					</Text>
					<Group justify="flex-end" mt="xs">
						<Button variant="default" onClick={() => setTargetOpen(false)}>
							取消
						</Button>
						<Button onClick={confirmTargets}>确定</Button>
					</Group>
				</Stack>
			</Modal>

			<Modal opened={editing !== null} onClose={() => setEditing(null)} title="编辑资料条目">
				{draft && (
					<Stack gap="sm">
						<TextInput
							label="名称"
							value={draft.name}
							onChange={(e) => setDraft({ ...draft, name: e.currentTarget.value })}
						/>
						<TextInput
							label="次要名称（英文）"
							placeholder="取自 en_us.json"
							value={draft.ename}
							onChange={(e) => setDraft({ ...draft, ename: e.currentTarget.value })}
						/>
						<TextInput
							label="注册名"
							placeholder="modid:path"
							value={draft.regname}
							onChange={(e) => setDraft({ ...draft, regname: e.currentTarget.value })}
						/>
						<Select
							label="资料分类"
							data={ENTRY_CATEGORIES}
							value={draft.category}
							onChange={(val) => setDraft({ ...draft, category: val ?? "物品/方块" })}
						/>
						<TextInput
							label="资料类型"
							value={draft.type}
							onChange={(e) => setDraft({ ...draft, type: e.currentTarget.value })}
						/>
						<Grid gutter="sm">
							<Grid.Col span={6}>
								<TextInput
									label="最大耐久"
									value={draft.damage}
									onChange={(e) => setDraft({ ...draft, damage: e.currentTarget.value })}
								/>
							</Grid.Col>
							<Grid.Col span={6}>
								<TextInput
									label="最大堆叠"
									value={draft.stack}
									onChange={(e) => setDraft({ ...draft, stack: e.currentTarget.value })}
								/>
							</Grid.Col>
						</Grid>
						<Group justify="flex-end" mt="xs">
							<Button variant="default" onClick={() => setEditing(null)}>
								取消
							</Button>
							<Button onClick={confirmEntry}>保存</Button>
						</Group>
					</Stack>
				)}
			</Modal>

			<Modal opened={iconOpen} onClose={() => setIconOpen(false)} title="占位图标样式" size="lg">
				<Stack gap="sm">
					<Group align="flex-start" gap="lg" wrap="nowrap">
						<Stack gap={4} align="center">
							<Box
								style={{
									width: 256,
									height: 256,
									background: iconStyle.bg,
									display: "flex",
									alignItems: "center",
									justifyContent:
										iconStyle.align === "left"
											? "flex-start"
											: iconStyle.align === "right"
												? "flex-end"
												: "center",
									outline: "1px solid rgba(128,128,128,0.25)",
									overflow: "hidden",
								}}
							>
								<Box
									style={{
										fontFamily: `"${iconFont.css}", sans-serif`,
										fontWeight: iconStyle.font === "impact.ttf" ? 400 : 700,
										fontSize: iconStyle.fontSize * (256 / iconStyle.canvas),
										lineHeight: iconStyle.lineGap,
										letterSpacing: iconStyle.letterSpacing * (256 / iconStyle.canvas),
										color: iconStyle.fg,
										textAlign: iconStyle.align as "center" | "left" | "right",
										textTransform: iconStyle.uppercase ? "uppercase" : "none",
										border: iconStyle.border
											? `${iconStyle.border * (256 / iconStyle.canvas)}px solid ${iconStyle.fg}`
											: undefined,
										padding: iconStyle.border ? 6 : 0,
									}}
								>
									{iconLines.map((line, index) => (
										<div key={index}>{line}</div>
									))}
								</Box>
							</Box>
							<Text size="xs" c="dimmed">
								{iconFont.label} · {iconStyle.fontSize}px · 行距 {iconStyle.lineGap.toFixed(2)} ·
								输出 {iconStyle.canvas}×{iconStyle.canvas}
							</Text>
						</Stack>

						<Stack gap="xs" style={{ flex: 1 }}>
							<TextInput
								label="第一行"
								value={rawLines[0] ?? ""}
								onChange={(e) => editIconLine(0, e.currentTarget.value)}
							/>
							<TextInput
								label="第二行"
								value={rawLines[1] ?? ""}
								onChange={(e) => editIconLine(1, e.currentTarget.value)}
							/>
							<Switch
								label="两行排版"
								checked={iconStyle.stacked}
								onChange={(e) => setIconStyle((s) => ({ ...s, stacked: e.currentTarget.checked }))}
							/>
							<Select
								label="字体"
								data={ICON_FONTS}
								value={iconStyle.font}
								allowDeselect={false}
								onChange={(value) => setIconStyle((s) => ({ ...s, font: value ?? s.font }))}
							/>
						</Stack>
					</Group>

					<Group grow align="flex-start">
						<Input.Wrapper label={`字号 ${iconStyle.fontSize}px`}>
							<Slider min={16} max={160} step={1} value={iconStyle.fontSize}
								onChange={(value) => setIconStyle((s) => ({ ...s, fontSize: value }))} />
						</Input.Wrapper>
						<Input.Wrapper label={`行距 ${iconStyle.lineGap.toFixed(2)}`}>
							<Slider min={0.8} max={2.2} step={0.05} value={iconStyle.lineGap}
								onChange={(value) => setIconStyle((s) => ({ ...s, lineGap: value }))} />
						</Input.Wrapper>
						<Input.Wrapper label={`字距 ${iconStyle.letterSpacing}px`}>
							<Slider min={-3} max={12} step={0.5} value={iconStyle.letterSpacing}
								onChange={(value) => setIconStyle((s) => ({ ...s, letterSpacing: value }))} />
						</Input.Wrapper>
					</Group>

					<Group grow align="flex-end">
						<Input.Wrapper label="对齐">
							<SegmentedControl
								data={[
									{ value: "center", label: "居中" },
									{ value: "left", label: "左" },
									{ value: "right", label: "右" },
								]}
								value={iconStyle.align}
								onChange={(value) => setIconStyle((s) => ({ ...s, align: value }))}
							/>
						</Input.Wrapper>
						<Select
							label="导出尺寸"
							data={["128", "256", "400", "512"]}
							value={String(iconStyle.canvas)}
							allowDeselect={false}
							onChange={(value) => setIconStyle((s) => ({ ...s, canvas: Number(value) }))}
						/>
					</Group>

					<Group grow>
						<ColorInput label="文字色" format="hex" value={iconStyle.fg}
							onChange={(value) => setIconStyle((s) => ({ ...s, fg: value }))} />
						<ColorInput label="背景色" format="hex" value={iconStyle.bg}
							onChange={(value) => setIconStyle((s) => ({ ...s, bg: value }))} />
					</Group>

					<Group grow align="center">
						<Switch
							label="全部大写"
							checked={iconStyle.uppercase}
							onChange={(e) => setIconStyle((s) => ({ ...s, uppercase: e.currentTarget.checked }))}
						/>
						<Input.Wrapper label={`边框 ${iconStyle.border}px`}>
							<Slider min={0} max={20} step={1} value={iconStyle.border}
								onChange={(value) => setIconStyle((s) => ({ ...s, border: value }))} />
						</Input.Wrapper>
					</Group>

					<Group justify="space-between">
						<Button size="xs" variant="default" onClick={() => setIconStyle({ ...DEFAULT_ICON_STYLE })}>
							恢复默认
						</Button>
						<Group gap="xs">
							<Button
								size="xs"
								variant="default"
								onClick={() =>
									(globalThis as any).genUI?.sendPrompt(
										`保存图标样式：${JSON.stringify(iconStyle)}`,
									)
								}
							>
								保存为默认
							</Button>
							<Button size="xs" onClick={() => setIconOpen(false)}>
								应用
							</Button>
						</Group>
					</Group>
				</Stack>
			</Modal>
		</Box>
	);
}
