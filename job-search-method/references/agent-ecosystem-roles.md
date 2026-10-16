# AI / Agent 生态岗位地图（2026-10 快照）

> 用途：用户问「AI / agent 方向有什么岗位 / 值不值得投 / 怎么进」时读这份，不要临场重搜。
> 数据来源：Stanford AI Index 2026、Dexity JD 扫描（2026-07）、Gartner context engineering 定义、各家 2026 真实 JD（腾讯/美团/滴滴/PDD/阿里云/携程/TSMC、Michael Page HK、Binance、Green Tomato、D.E. Shaw/Two Sigma/Jane Street/Point72）。
> **判断顺序仍守 SKILL.md 铁律：实际交付物 → 雇主类型 → 岗位名称。**

## 生态三层（用户的入口在第三层）

| 层 | 岗位 | 交付物 | 门槛 | 对用户 |
|---|---|---|---|---|
| 造模型/基座 | Research Scientist、LLM/ML Engineer、Agent Infra | 新模型、训练/推理框架、Agent Runtime（Go/Rust + 分布式） | PhD/论文、系统底层 | ❌ 不是起点 |
| 造 agent 系统 | AI Agent Engineer、Context Engineer、Agent Architect | Agent Loop、工具调用、记忆、RAG 管道、MCP Server、Prompt/Context 工程化与评测 | 扎实后端/全栈 + LLM 原理 | ⚠️ 1–2 年可及 |
| 让 agent 落地 | Agent 评测 / AI Eval、Forward Deployed Engineer (FDE)、Applied AI Engineer、AI 解决方案工程师、Agent PM、AgentOps | 评测集与指标、可复用 agent 工作流、客户现场跑通的系统 | 业务框架 + 轻编码；portfolio-driven | ✅ 入口 |

## 关键数据（引用时给年份口径）

- Agentic AI 岗位同比 **+280%**（Stanford 2026 AI Index，美国约 9 万条）；**FDE 同比 +729%**，中位总包 $173K，Palantir $215K，OpenAI/Anthropic 中层 $350–550K。
- agentic 已跨岗位：**50% AI Engineer JD、150/399 FDE JD、28% PM JD** 要求 agent 经验（Dexity 2026-07 扫描）→ 它是技能而非单一 title。
- **Context Engineer** 已被 Gartner 2026 初正式定义；Adobe/Stripe 在用此 title 招人；美国资深 IC base $185K–245K。四支柱：指令、检索(RAG)、记忆、工具。
- 香港口径：银行 AI Engineer (RAG/LLM) 40–50K HKD/月（Michael Page）；Green Tomato 连 CV 都不收、只要 Claude Code `/insights` 截图；Binance 校招 Applied AI Agent Engineer（远程）。

## 搜索名清单（同一份活七八个名字，必须全搜）

Forward Deployed Engineer (FDSE) / Applied AI Engineer / Agentic AI Engineer / Context Engineer / AI Eval Engineer / Customer Engineer / Solutions Engineer (AI) / Deployment Strategist / AI Implementation Consultant / AI Integration Lead / AgentOps

## 金融方向 = 用户的双线交集（重点）

目标雇主正在自建 agent 研究系统：Man Group AlphaGPT（「不睡觉的三人研究组」）、Balyasny 宏观助手 2 天→30 分钟、Citadel 论文复现 agent 6–8 周→2–3 小时。招的 Applied AI Engineer **常明确不要金融背景 / 任何专业本科**（D.E. Shaw 2026 JD 原文：bachelor's degree in any field + 软件背景）。面试考代码与推理，不考金融。

## 可迁移强项 × 缺口（对齐 `04 真实画像（内部）.md`）

可迁移：数据清洗与去重 = 检索管道上游；ID 对齐 = **实体消解**（RAG 最难环节）；KPI/指标口径 = **eval 设计语言**；BI 看板 = 结果呈现。
真缺口：Git/工程协作无公开证据、无 production LLM 应用、无 A/B 与离线评测、无 ML 建模 → 其中**评测最该先补、也最省力**。

## 判断三档（沿用 SKILL.md 输出纪律）

- **值得优先**：Agent 评测/AI Eval；金融量化里的 Applied AI / AI Automation（JD 常见「不要金融背景」）。
- **可以看看**：FDE 邻接岗（Solutions Engineer AI、AI Implementation Consultant、Deployment Strategist）、Agent PM（须有技术判断力）。
- **跳过**：纯 Prompt Engineer（独立市场萎缩，并入 Context Engineer）、AI Research Scientist（要 PhD + 顶会论文）、Agent Infra（Go/Rust + 分布式内核）。

## 入场第一步（给用户的默认建议）

招聘看作品不看证书 → 第一个 30 天产出**可演示工件 + 一页复盘**：拿用户自己的 Obsidian 库当数据集做真 RAG（分块 → 检索方案 → 20 条评测集 → 失败案例记录），正好套上 JD 面试的原始问法（假设/选型/踩坑/如何验证）。第 2、3 件：Git 最小可用 + Python 走一遍 LangChain/LangGraph 与一个向量库；补一个小规模 A/B 或离线评测实验。
