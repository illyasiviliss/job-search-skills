#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""量一份「简历 HTML」的真实内容高度，判断它会不会溢出到第 2 页。

用法：python3 measure_content_height.py <某版.html> [更多.html ...]
输出：内容高度(pt) | 版心(pt) | 余量(pt, 折合行数)

原理：Chrome 无头 dump-dom 之前，先把 document.body 的高度写进 <title>，再读回来。
      px → pt 乘 0.75。A4 = 842pt，上下边距各 11mm ≈ 31pt ⇒ 版心 780pt。

判据：余量 < 20pt（≈1.5 行）就一定会翻页 —— 屏幕上看着「没溢」也没用，
      打印重排会把它挤出去（实测 776pt/780pt 就翻页了）。
      fill_ratio() 只告诉你满不满，这个脚本告诉你「还差几行」，
      差 1 行改一条 bullet，差 3 行才值得动字号。
"""
import os
import re
import subprocess
import sys

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PAGE_PT = 842.0                 # A4 高
MARGIN_PT = 31.0                # 11mm
BODY_PT = PAGE_PT - 2 * MARGIN_PT   # 780pt 版心
SAFE_PT = 20.0                  # 必须留的余量
LINE_PT = 13.2                  # 9.5pt / 1.34 行高下的一行


def measure(html_path):
    html = open(html_path, encoding="utf-8").read()
    if "</body>" not in html:
        raise RuntimeError("%s 里没有 </body>，量不了" % html_path)
    html = html.replace(
        "</body>",
        "<script>document.title=String(document.body.getBoundingClientRect().height)"
        "</script></body>")
    tmp = "/tmp/_measure_cv.html"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(html)
    r = subprocess.run(
        [CHROME, "--headless", "--disable-gpu", "--virtual-time-budget=2000",
         "--user-data-dir=/tmp/_measure_cv", "--dump-dom", "file://" + tmp],
        capture_output=True, text=True)
    m = re.search(r"<title>([\d.]+)</title>", r.stdout)
    if not m:
        raise RuntimeError("读不到高度：Chrome 路径变了，或页面没渲染出来")
    return float(m.group(1)) * 0.75


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    for p in sys.argv[1:]:
        p = os.path.expanduser(p)
        h = measure(p)
        margin = BODY_PT - h
        ok = margin >= SAFE_PT
        print("%-42s 内容 %6.0f pt | 版心 %.0f pt | 余量 %+6.0f pt (≈%+.1f 行)  %s"
              % (os.path.basename(p), h, BODY_PT, margin, margin / LINE_PT,
                 "✅ 安全" if ok else "❌ 会翻页，还要省 %.0f pt" % (SAFE_PT - margin)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
