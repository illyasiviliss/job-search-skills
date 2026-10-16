#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""多版一页简历生成器（示例骨架 —— 请把所有 <占位符> 换成你自己的事实）

一份事实，多套讲法：版本差异只落在三处 —— **抬头下的定位语、个人项目的顺序与详略、
技能栏首行（含条数）**；其余段落各版共用同一份字符串。

用法：
    python3 gen_cv_versions.py            # 出全部版本
    python3 gen_cv_versions.py V1 V3      # 只出指定版本（先出一版给用户看，跑通再全量）

依赖：Google Chrome（headless print-to-pdf）＋ pypdf（数页数）＋ pymupdf/fitz（量填满度）。
验收：每版 1 页 A4 ＋ 填满度 92–96% ＋ PDF 文本里不含不该出现的整节（如 SUMMARY / COURSE PROJECTS）。

约定（别破坏）：
  · 机器上只留这一份生成逻辑。别处若需要入口，放三行 runpy.run_path(...) 转发脚本。
  · 改内容改本文件里的 dict，不要手工改产出的 HTML —— 下次重跑手工改动全丢。
  · 共用段落（教育、实习）一改，其余版本的 PDF 立刻过期：要么马上全量重跑，要么明确告知用户。
"""
import os
import shutil
import subprocess
import sys

# ---------- 路径与常量 ----------
OUT = os.path.expanduser("~/Documents/Career/投递/_多版本简历")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
DATE = "<YYYYMMDD>"

# 抬头里的「可验证链接」（GitHub / 作品集）。数据类简历把它列为必备项。
GITHUB = "github.com/<你的用户名>/<仓库名>"

# 字号/行高：内容增减后跑一次看 fill 值再调（阈值非线性，逐档试、别插值猜）。
# 字号与页边距是下限：正文 ≥10pt、页边距 ≥12.7mm（见 references/resume-format-standards.md）。
CSS = """
  @page { size: A4; margin: 11mm 13mm 11mm 13mm; }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; }
  /* 中文字体必须选「PDF 里能正确提取」的，否则 ATS 读不到关键词（见 SKILL.md「中文字体与 ATS」） */
  body { font-family: "Times New Roman", "STHeiti", "Arial Unicode MS", sans-serif; color: #000;
         font-size: 9.5pt; line-height: 1.34; }
  .name { text-align: center; font-size: 19pt; font-weight: 700; letter-spacing: 1px; }
  .name .en { font-size: 13pt; font-weight: 400; letter-spacing: 0.5px; margin-left: 8px; }
  .tagline { text-align: center; font-size: 10.2pt; font-weight: 700; margin-top: 6px; }
  .contact { text-align: center; font-size: 9pt; margin-top: 4px; line-height: 1.45; }
  .rule { border-bottom: 1.6px solid #000; margin: 8px 0 8px; }
  h2 { font-size: 11pt; font-weight: 700; margin: 10px 0 5px; padding-bottom: 2px;
       border-bottom: 1.5px solid #000; letter-spacing: 1.2px; }
  h2 .cn { font-weight: 400; font-size: 9.4pt; letter-spacing: 0.5px; }
  .entry { margin-bottom: 6px; }
  .row { display: flex; justify-content: space-between; align-items: baseline; }
  .org { font-weight: 700; font-size: 10pt; }
  .date { font-size: 9.2pt; font-weight: 700; white-space: nowrap; }
  .role { font-style: italic; font-size: 9.2pt; margin-top: 1px; }
  .sub { font-style: italic; font-weight: 700; margin-top: 4px; }
  p { margin: 3px 0 0; }
  ul { margin: 2px 0 0; padding-left: 14px; }
  li { margin: 2px 0; }
  .plain { margin: 0 0 4px; }
  .tight { margin-top: 2px; }
"""

HEAD = ('<div class="name"><你的姓名><span class="en"><Your Name></span></div>\n'
        '<div class="tagline">{tagline}</div>\n'
        '<div class="contact"><电话> &nbsp;|&nbsp; <邮箱> &nbsp;|&nbsp; <城市><br>\n'
        '<身份/签证（可选）> &nbsp;|&nbsp; 意向地点：<香港 / 内地 / 海外><br>\n'
        'GitHub：{github}</div>\n'
        '<div class="rule"></div>\n')

EDU = """<h2>EDUCATION <span class="cn">教育经历</span></h2>
<div class="entry">
  <div class="row"><span class="org"><学校 A></span><span class="date">20XX.09 – 20XX.07（在读）</span></div>
  <div class="role"><学位>（<Program>）｜ <城市> ｜ <20XX 届></div>
  <p>相关课程：<只列与目标岗位相关的 3–5 门，压在一行内></p>
</div>
<div class="entry">
  <div class="row"><span class="org"><学校 B></span><span class="date">20XX.09 – 20XX.06</span></div>
  <div class="role"><学位>｜ GPA <X.XX / 4.0></div>
  <p>相关课程：<与目标岗位最相关的课，分数只挂在相关的课上></p>
</div>
"""

# ---------- 实习（各版共用）----------
# 写法：抬到「我定过口径 / 我做过分群」这一层，不写实现细节。
# 数字只用原始材料里能佐证的，缺就写 [待补：XXX]，不要填猜的数字。
INT = """<h2>INTERNSHIP <span class="cn">实习经历</span></h2>
<div class="entry">
  <div class="row"><span class="org"><公司全称></span><span class="date">20XX.XX – 20XX.XX</span></div>
  <div class="role"><部门> · <职位> ｜ <城市></div>
  <div class="sub"><业务线 A> · <项目名></div>
  <ul>
    <li><动作动词> <具体工作>，<方法/工具>，<可量化结果>。</li>
    <li><动作动词> <具体工作>，<方法/工具>，<可量化结果>。</li>
  </ul>
  <div class="sub"><业务线 B> · <项目名></div>
  <ul>
    <li><动作动词> <具体工作>，<方法/工具>，<可量化结果>。</li>
    <li><动作动词> <具体工作>，<方法/工具>，<可量化结果>。</li>
  </ul>
</div>
"""

AWD = """<h2>AWARDS &amp; LANGUAGES <span class="cn">获奖与语言</span></h2>
<p class="plain"><奖项全称> <b><等级></b>（20XX.XX）｜ <奖项全称> <b><等级></b>（20XX.XX）</p>
<p class="plain tight"><语言考试> <分数> &nbsp;|&nbsp; <其他语言>：母语</p>
"""


def proj(org, date, role, bullets):
    lis = "".join("<li>%s</li>" % b for b in bullets)
    return ('<div class="entry">\n  <div class="row"><span class="org">%s</span>'
            '<span class="date">%s</span></div>\n  <div class="role">%s</div>\n'
            '  <ul>%s</ul>\n</div>\n') % (org, date, role, lis)


# ---------- 个人项目（两个，类型必须不同：一分析型 ＋ 一工程/产品型）----------

# 分析型：落点是「我从数据里得出了什么结论」
A_ANALYSIS = dict(
    org="<项目名> · <一句话定位>", date="20XX.XX – 至今",
    role="个人数据分析项目 · SQL / <工具>",
    bullets=[
        "<动作动词> <采集/整合范围>，经清洗去重后建库（<存储>），"
        "数据集 <N> 条记录 × <M> 个字段、覆盖 <K> 家主体。",
        "<动作动词> <分析维度> 分析，输出 <结论/报告/看板>，"
        "据此 <带来的决策变化>。",
    ])

# 工程/产品型：落点是「我做了一个能跑起来、别人能看的东西」
A_ENGINEERING = dict(
    org="<项目名>", date="20XX.XX – 至今",
    role="个人项目 · <技术栈/方法> · 开源在 GitHub",
    bullets=[
        "<动作动词> <端到端流程>：<输入> → <清洗> → <入库> → <分析/输出>。",
        "已结构化 <N> 条数据、覆盖 <K> 家主体；代码与方法说明开源在 GitHub，全流程可复现。",
    ])
A_ENGINEERING_SHORT = dict(
    org="<项目名>", date="20XX.XX – 至今",
    role="个人项目 · <技术栈/方法> · 开源在 GitHub",
    bullets=[
        "<动作动词> <端到端流程>：<输入> → <清洗> → <入库> → <分析/输出>。",
        "已结构化 <N> 条数据；代码与数据管道开源在 GitHub，全流程可复现。",
    ])

# ---------- 技能栏（分类：内容；不要做成表格）----------
_S_TOOLS = "SQL、Python（pandas / NumPy）、Excel、Power Query、Power BI、Tableau、Git"
_S_STAT = "描述统计与分组对比、假设检验、回归与预测建模、分类与聚类、A/B 实验、漏斗与归因、用户分群"
_S_ENG = "数据清洗与多源对齐、指标口径定义与校验、KPI 体系搭建、SQL 建库、看板交付"

VERSIONS = {
    "V1-<方向 A>": dict(
        tagline="数据分析 / 商业分析 / 应用统计",
        projects=[A_ANALYSIS, A_ENGINEERING_SHORT],
        skills=[("语言与工具", _S_TOOLS),
                ("分析方法", _S_STAT),
                ("数据工程与交付", _S_ENG),
                ],
    ),
    "V2-<方向 B>": dict(
        tagline="<岗位方向 B 的岗位名打头>",
        projects=[A_ENGINEERING, A_ANALYSIS],
        skills=[("<该方向最想被看到的一类>", "<按招聘启事里的词写>"),
                ("语言与工具", _S_TOOLS),
                ("分析方法", "<按该方向重排>"),
                ],
    ),
}


def build_html(v):
    parts = ['<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><style>%s</style></head><body>' % CSS]
    parts.append(HEAD.format(tagline=v["tagline"], github=GITHUB))
    # 不输出 SUMMARY、不输出 COURSE PROJECTS（课程项目降级为面试弹药，不进一页版）。
    # 不要用「字段为空就不渲染」的开关把它们开回来 —— 开关会在某次改写里被静默填回，
    # 而源码看着仍是「已关闭」。要恢复就显式加回整节。
    parts.append(EDU)
    parts.append(INT)
    parts.append('<h2>PROJECT EXPERIENCE <span class="cn">项目经历</span></h2>\n')
    for p in v["projects"]:
        parts.append(proj(p["org"], p["date"], p["role"], p["bullets"]))
    parts.append('<h2>SKILLS <span class="cn">技能</span></h2>\n')
    for k, val in v["skills"]:
        parts.append('<p class="plain"><b>%s：</b>%s</p>\n' % (k, val))
    parts.append(AWD)
    parts.append('</body></html>')
    return "".join(parts)


def fill_ratio(pdf_path):
    """量填满度：正文最低点 / 版心底部。A4 = 842pt 高，下边距 11mm ≈ 31pt。"""
    try:
        import fitz
    except ImportError:
        return None
    doc = fitz.open(pdf_path)
    page = doc[0]
    bottom = 842 - 31.0
    lowest = 0.0
    for b in page.get_text("blocks"):
        lowest = max(lowest, b[3])
    doc.close()
    return lowest / bottom


def main(argv=None):
    """argv 里给版本名前缀（如 V1）则只出那几版，不给就出全部。"""
    want = [a for a in (argv if argv is not None else sys.argv[1:]) if not a.startswith("-")]
    todo = [(n, v) for n, v in VERSIONS.items()
            if not want or any(n.startswith(w) for w in want)]
    if not todo:
        print("没有匹配的版本。可选：%s" % " / ".join(VERSIONS))
        return 1
    os.makedirs(OUT, exist_ok=True)
    results = []
    for name, v in todo:
        html_path = os.path.join(OUT, "%s.html" % name)
        pdf_path = os.path.join(OUT, "%s-%s.pdf" % (name, DATE))
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(build_html(v))
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                        "--user-data-dir=/tmp/cvchrome_multi",
                        "--print-to-pdf=" + pdf_path, html_path], capture_output=True)
        try:
            from pypdf import PdfReader
            pages = len(PdfReader(pdf_path).pages)
        except Exception as e:
            pages = "ERR %s" % e
        fr = fill_ratio(pdf_path)
        results.append((name, pages, fr, pdf_path))
        print("%-24s pages=%s  fill=%s" % (name, pages, ("%.0f%%" % (fr * 100)) if fr else "n/a"))
    bad = [r for r in results if r[1] != 1]
    if bad:
        print("\n⚠️ 不是 1 页的版本：")
        for n, p, _, _ in bad:
            print("   %s -> %s 页" % (n, p))
    else:
        print("\n✅ 全部 %d 版均 1 页 A4" % len(results))
    low = [r for r in results if r[2] and r[2] < 0.90]
    if low:
        print("⚠️ 填满度不足 90%（底部留白偏多）：")
        for n, p, fr, _ in low:
            print("   %s -> %.0f%%" % (n, fr * 100))
    return 0


if __name__ == "__main__":
    sys.exit(main())
