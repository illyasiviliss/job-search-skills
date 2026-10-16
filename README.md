# 求职技能包（Job-Search Skills）

一套写给 **数据分析 / 商业分析方向求职者** 的 AI Agent 技能包：从「维护一份简历母版」到「按岗位定制导出」，再到「面试分档备战与复盘」。

用 [Hermes Agent](https://hermes-agent.nousresearch.com/docs) 的 skill 格式写成（`SKILL.md` ＋ `references/` ＋ `scripts/`），**也可以当纯方法论文档直接读** —— 里面绝大多数是真踩过的坑与可执行的命令，不依赖特定工具。

> 这套东西是按「一个真实的人走完一整轮校招」的路径长出来的：先有母版，再有定制版，再有多版本，再有面试演练。所以它不是一份模板合集，而是**一条流水线**。

---

## 包含什么

| 技能 | 干什么 | 主要产出 |
|---|---|---|
| **`cv-master`** | 简历母版维护 ＋ 能力汇总 ＋ 按 JD 定制 ＋ 排版导出 ＋ 机器校验 | `母版.md`、定制版 Markdown/DOCX/PDF、体检报告 |
| **`interview-prep`** | 面试分档备战（P0–P2 ＋ 明确不准备清单）＋ 60/150 分答法 ＋ 复盘回填 | 面经拷打指南、技能追问演练表 |
| **`job-search-method`** | 双边画像（偏好画像 / 真实画像）＋ 岗位线索池 ＋ 招聘信息检索与落库 | 偏好画像、真实画像、岗位线索池、投递台账 |

三个技能互相引用，建议整套拿走。

---

## 安装

### 用 Hermes Agent

```bash
git clone https://github.com/<你的用户名>/job-search-skills.git
cp -R job-search-skills/cv-master          ~/.hermes/skills/career/
cp -R job-search-skills/interview-prep     ~/.hermes/skills/career/
cp -R job-search-skills/job-search-method ~/.hermes/skills/career/
```

（`~/.hermes/skills/career/` 不存在就先建目录。）

### 当文档读

直接从 `*/SKILL.md` 开始。每个技能的 `references/` 是深挖细节的地方，`scripts/` 是可直接跑的脚本。

---

## 依赖

**必需（只有排版导出用得上）**

| 工具 | 用途 | 装法 |
|---|---|---|
| Google Chrome | HTML → PDF（headless 打印，版式最可控） | 官网下载 |
| `pypdf` | 数页数 | `pip install pypdf` |
| `pymupdf` | 量版面填满度 | `pip install pymupdf` |
| pandoc | Markdown → DOCX | `brew install pandoc` |
| LibreOffice | DOCX → PDF（pandoc 自身没有 PDF 引擎） | `brew install --cask libreoffice` |

**可选**：`textutil`（macOS 自带，HTML → DOCX）。

只用文本流程、不做导出的话，**一个依赖都不用装**。

> ⚠️ **跑生成器 / 量页数请用系统 python 的 `terminal`，不要用受限沙箱**：沙箱里 `import pypdf` 会 `ModuleNotFoundError`，页数与填满度会静默变成 `ERR` —— 不报错，最容易漏看。

---

## 快速开始（三步）

**1. 建母版**

照 `cv-master/references/master-profile-template.md` 建一份 `~/Documents/Career/母版.md`，把经历、数字、素材都塞进去。**数字缺就写 `[待补：XXX]`，不要猜** —— 整套脚本的「反幻觉」检查靠的就是这个标记。

**2. 体检**

```bash
python3 cv-master/scripts/validate_profile.py ~/Documents/Career/母版.md
```

退出码 `2` = 有未清的待补项或无依据的形容词，**禁止导出**。

**3. 按 JD 出一版**

对着目标岗位 JD，按 `cv-master` 主流程 C 选条目、重写定位语与技能栏，导出 PDF：

```bash
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CH" --headless --disable-gpu --no-pdf-header-footer \
  --user-data-dir=/tmp/cvchrome --print-to-pdf="输出.pdf" "cv.html"
```

然后用视觉看一眼 + `pypdf` 数页数，确认一页、填满。

---

## 这套东西里最值钱的几条（都是踩出来的）

- **中文字体决定 ATS 能不能读到关键词。** 宋体系字体（`Songti SC` / `STSong` / `SimSun`）出的 PDF 里，约 4–5% 汉字会被抽成 Kangxi 部首码位（`⼤学`、`⼯作`、`项⽬`）—— **肉眼完全看不出来，但 ATS 一个关键词都匹配不到**。用 `STHeiti` 这类，并跑一遍码位检查。
- **页边距与字号是下限，不是可调参数。** 正文 ≥10pt、页边距 ≥12.7mm。塞不下时**先砍内容，再定字号**，不是压字号去迁就内容。
- **溢出前先量「差几行」，再决定砍什么。** 肉眼看着「没溢」不代表打印不翻页 —— 打印重排会把临界内容挤出去，必须留 ≥20pt（约 1.5 行）余量。
- **同一件事实不要在两条经历里各写一遍。** 重复是「看不出差异」的头号来源。
- **教育段的「相关课程」按「课程 → 哪段经历」对齐，分数只挂在相关的课上。** 把最高分但不相关的课放上去，等于把最显眼的位置浪费掉。
- **面试官照着简历问。** 简历就是出题范围；写了就必须 100% 准备。

---

## 目录结构

```
job-search-skills/
├── cv-master/
│   ├── SKILL.md                    # 主流程 A–E ＋ 版式 ＋ 写法 ＋ 简历策略
│   ├── references/
│   │   ├── master-profile-template.md    # 母版空白模板
│   │   ├── writing-playbook.md           # 写作法则
│   │   ├── layout-and-pdf.md             # HTML ＋ Chrome 出版、填满度、字体
│   │   ├── resume-format-standards.md    # 外部硬指标摘编
│   │   ├── ability-taxonomy.md           # 能力族分类
│   │   └── resume-claims-audit.md        # 主张一致性审计 ＋ 占位符兑现法
│   └── scripts/
│       ├── validate_profile.py           # 反幻觉校验器（退出码 2 = 阻断）
│       ├── gen_cv_versions.py            # 多版一页简历生成器（示例骨架）
│       ├── measure_content_height.py     # 量内容高度，判断会不会翻页
│       ├── tighten_docx_a4.py            # pandoc 产物收紧成 A4 一页
│       └── backup_profile.sh             # 写入前备份
├── interview-prep/
│   ├── SKILL.md
│   └── references/data-analyst-question-bank.md
└── job-search-method/
    ├── SKILL.md
    └── references/
        ├── job-listing-research.md       # 检索通道、聚合页坑、中小企业四条通道、海投纪律
        └── agent-ecosystem-roles.md      # AI / Agent 岗位地图
```

---

## 设计原则

1. **一份母版，唯一真相源。** 所有版本从它派生，**绝不能**从某个投递版回写母版。
2. **对外 / 对内分离。** 母版是对外材料；「能拿到面试吗 / 值不值得投」这类判断住在**另一份文件**里，两边永不互相回写。
3. **不新增编造内容。** 没有证据的数字、头衔、时间不写。数字缺失就写 `[待补]`，脚本会在导出前拦住。
4. **先定内容，再做版式。** 内容没定稿就排版，等于把返工写在前面。
5. **改完必须看产出，不能只看源码。** 只改生成器不看 PDF，是「以为改了其实没改」的唯一来源。

## 关于「写到多满」

`cv-master` 里写了两种路线（**饱和式** 与 **保守式**），并明确说明各自代价 —— 但要说明白：

- 这套体系**不鼓励编造**。唯一硬约束是「不新增未发生的事」。
- 饱和式写法的**必要配套**是「技能追问演练」：把简历里每句话拆成三档（名词 / 机制 / 取舍），标出答不到哪一层，再用真实面试当校准器去补。
- **选哪条是用户自己的决定**，agent 的职责是把代价讲清楚、然后干净地执行。

---

## 许可

MIT。随便用、随便改。

`references/` 里的外部方法论来源已在各文件内注明（Dataquest、William & Mary Career Center、若干开源 job-search skill 项目等）。
