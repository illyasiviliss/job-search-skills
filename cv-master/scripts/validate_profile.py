#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""简历母版校验器 —— cv-master 技能的机器兜底层。

对应 SKILL.md「主流程 D：体检 + 校验」。把「不得编造」从口号变成能失败的检查:
对 Markdown 简历做四类只读检查, 不写任何文件。

用法:
    python3 validate_profile.py [简历.md]
    (默认 ~/Documents/Career/母版.md; 不给参数也用默认)

退出码: 0 = 无阻断问题; 2 = 有阻断问题(待补未清 / 编造风险词 / 事实冲突);
        1 = 文件读不到。
"""

import re
import sys
from pathlib import Path
from collections import defaultdict

DEFAULT = Path.home() / "Documents/Career" / "母版.md"

# --- 无证据的"形容词式成果" (LeonZou 反幻觉思路的中文版) ---
UNSUPPORTED_ADJ = [
    "显著", "大幅", "极大", "有效提升", "有效降低", "良好", "优秀", "出色",
    "丰富", "大量", "充分", "卓越", "亮眼", "突出贡献", "明显改善", "全面提升",
    "业界领先", "行业领先", "名列前茅", "极大提升", "有效改善",
]

# --- 占位符 / 待补标记 ---
PLACEHOLDER_RE = re.compile(r"\[\s*待补[：:][^\]]*\]")
# --- 数字 + 单位 (需带单位, 或逗号分组, 或 >=3 位整数, 或小数) ---
UNIT = r"(?:万|亿|%|％|条|家|个|人|次|倍|天|月|年|元|美元|ms|s)"
NUM_RE = re.compile(rf"\d[\d,]*(?:\.\d+)?\s*{UNIT}|\b\d{{1,3}}(?:,\d{{3}})+\b|\b\d{{3,}}\b|\b\d+\.\d+\b")
DATE_RE = re.compile(r"^(19|20)\d{2}(\.\d{1,2})?\s*年?$")
# --- 实体启发式: 后缀锚定(长后缀优先) + 前导成分剔除 ---
ENTITY_RE = re.compile(r"[\u4e00-\u9fa5A-Za-z0-9]{2,20}(?:股份有限公司|有限公司|研究院|事务所|集团|大学|学院|银行|基金|中心)")
LEAD_PARTICLES = ("在", "的", "及", "与", "和", "为", "于", "由", "至", "向", "对", "从", "到")
LEAD_VERBS = ("开展", "举办", "参加", "就读", "进入", "来自", "走访", "调研", "合作")
BARE_SUFFIX_RE = re.compile(r"^(?:股份|管理|产业|科技|集团|投资|控股|实业)?(?:有限)?公司$|^(?:产业|私募|投资)?基金$")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:\+?86[-\s]?)?1[3-9]\d{9}|\(\d{3,4}\)\s?\d{6,8}")
SEC_RE = re.compile(r"^##\s*(\d+)\.\s*(.+)$", re.M)


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"[错误] 找不到文件: {path}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    text = read(path)
    lines = text.splitlines()
    blocking = 0

    print("=" * 60)
    print(f"简历校验: {path}")
    print("=" * 60)

    # 0) 维护说明区间 (## 0 ... 下一节): 其中的 [待补：XXX] 是约定示例, 不算正文
    sec0_end = len(text)
    for m in SEC_RE.finditer(text):
        if m.group(1) == "0":
            nxt = SEC_RE.search(text, m.end())
            sec0_end = nxt.start() if nxt else len(text)
            break

    # 1) 待补标记 —— 阻断项
    marks = []
    for i, l in enumerate(lines):
        abs_pos = sum(len(x) + 1 for x in lines[:i])
        for m in PLACEHOLDER_RE.finditer(l):
            if abs_pos >= sec0_end:  # 跳过维护说明里的约定示例
                marks.append((i + 1, m.group(0)))
    print(f"\n[1] 待补标记（阻断导出）: {len(marks)} 处")
    for ln, m in marks:
        print(f"    L{ln}: {m}")
    if marks:
        blocking += 1

    # 2) 编造风险词 —— 需人工确认
    risky = []
    for i, l in enumerate(lines):
        if l.strip().startswith(">") or l.strip().startswith("|") or l.strip().startswith("#"):
            continue
        for w in UNSUPPORTED_ADJ:
            if w in l:
                risky.append((i + 1, w, l.strip()))
    print(f"\n[2] 无证据形容词（需确认有数字支撑，否则改写）: {len(risky)} 处")
    for ln, w, l in risky:
        print(f"    L{ln} 「{w}」: {l[:60]}")

    # 3) 量化事实清单（供人工比对，非阻断）
    nums = set()
    for l in lines:
        s = l.strip()
        if s.startswith("|") or s.startswith("#") or re.match(r"^\s*[-*]\s*$", s):
            continue
        for m in NUM_RE.finditer(s):
            tok = m.group(0).strip()
            if DATE_RE.match(tok) or re.match(r"^\d{1,2}$", tok):
                continue
            nums.add(tok)
    nums = sorted(nums)
    print(f"\n[3] 量化事实清单（{len(nums)} 个，改写时逐一对齐、不得新增）:")
    print("    " + "  ".join(nums))

    # 4) 实体清单（改写时不得新增实体）
    ents = set()
    for l in lines:
        for m in ENTITY_RE.finditer(l):
            e = m.group(0)
            for v in LEAD_VERBS:  # 在「开展…某某大学」里只保留动词之后的实体
                if v in e and not e.endswith(v):
                    e = e.split(v)[-1]
            while len(e) > 2 and e[0] in LEAD_PARTICLES:
                e = e[1:]
            for suf in ("大学", "学院", "公司", "基金", "中心", "集团"):  # 折叠重复后缀
                e = e.replace(suf + suf, suf)
            if len(e) >= 4 and not BARE_SUFFIX_RE.match(e) and "大学" not in e[:2]:
                ents.add(e)
    ents = sorted(ents)
    print(f"\n[4] 实体清单（{len(ents)} 个，只读锁）:")
    for e in ents:
        print(f"    - {e}")

    # 5) 联系方式一致性
    emails = sorted({m.group(0) for m in EMAIL_RE.finditer(text)})
    phones = sorted({m.group(0).strip() for m in PHONE_RE.finditer(text)})
    print(f"\n[5] 联系方式: 邮箱 {emails}｜电话 {phones}")

    # 6) 分节统计
    secs = SEC_RE.findall(text)
    print(f"\n[6] 分节（{len(secs)} 节）:")
    bounds = [(int(n), t, text.index(m.group(0))) for m in SEC_RE.finditer(text) for n, t in [(m.group(1), m.group(2))]]
    for idx, (n, t, pos) in enumerate(bounds):
        end = bounds[idx + 1][2] if idx + 1 < len(bounds) else len(text)
        seg = text[pos:end]
        bullets = len(re.findall(r"^\s*[-*]\s", seg, re.M))
        chars = len(re.sub(r"\s", "", seg))
        print(f"    {n}. {t}  ·  {chars} 字  ·  {bullets} 条分点")

    print("\n" + "=" * 60)
    if blocking:
        print(f"结论: 阻断（{blocking} 类问题）—— 导出前必须处理")
    else:
        print("结论: 通过 —— 无阻断项")
    print("=" * 60)
    sys.exit(2 if blocking else 0)


if __name__ == "__main__":
    main()
