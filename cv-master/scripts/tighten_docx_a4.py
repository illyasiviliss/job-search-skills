#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 pandoc 生成的简历 docx 收紧成「A4 ＋ 一页」版式（cv-master 配套脚本）。

为什么需要它：pandoc 默认输出 Letter (12240×15840)、正文 12pt、段后 10pt，
中文简历几乎必然溢出到第 2 页，且没有任何页边距控制接口。
本脚本直接改 docx 内部的 styles.xml / document.xml，不需要 python-docx。

用法:
    python3 tighten_docx_a4.py in.docx [out.docx]
        [--size 20]          正文半磅字号（20 = 10pt，默认 20；19 = 9.5pt）
        [--margin-lr 850]    左右页边距 twips（850 ≈ 1.5cm，默认 850）
        [--margin-tb 680]    上下页边距 twips（680 ≈ 1.2cm，默认 680）
        [--font "Songti SC"] 东亚字体名（默认 Songti SC；Windows 会自行替换）
        [--latin Calibri]    西文字体名（默认 Calibri）

退出码 0 = 成功。改完务必用 LibreOffice 转 PDF 并数页数验证：
    soffice --headless --convert-to pdf --outdir <dir> out.docx
"""
import argparse
import os
import re
import shutil
import sys
import tempfile
import zipfile

A4_W, A4_H = 11906, 16838  # twips

# styleId -> 处理函数
def _resize(b, half):
    b = re.sub(r'<w:sz w:val="\d+"\s*/>', '<w:sz w:val="%d" />' % half, b)
    b = re.sub(r'<w:szCs w:val="\d+"\s*/>', '<w:szCs w:val="%d" />' % half, b)
    return b


def patch_styles(xml: str, size_half: int, font: str, latin: str) -> str:
    body = size_half
    # docDefaults
    xml = re.sub(
        r'<w:rFonts w:asciiTheme="minorHAnsi"[^/]*/>',
        '<w:rFonts w:ascii="%s" w:hAnsi="%s" w:cs="%s" w:eastAsia="%s" />'
        % (latin, latin, latin, font),
        xml,
    )
    xml = re.sub(r'<w:sz w:val="\d+" />\s*\n\s*<w:szCs w:val="\d+" />',
                 '<w:sz w:val="%d" />\n        <w:szCs w:val="%d" />' % (body, body), xml)
    xml = xml.replace('<w:spacing w:after="200" />',
                      '<w:spacing w:after="20" w:line="240" w:lineRule="auto" />')

    def setstyle(sid, fn):
        nonlocal xml
        pat = re.compile(r'(<w:style [^>]*w:styleId="%s".*?</w:style>)' % sid, re.S)
        m = pat.search(xml)
        if not m:
            return
        xml = xml[:m.start(1)] + fn(m.group(1)) + xml[m.end(1):]

    setstyle('Title', lambda b: _resize(b.replace(
        '<w:spacing w:after="80" w:line="240" w:lineRule="auto" />',
        '<w:spacing w:after="40" w:before="0" w:line="240" w:lineRule="auto" />'), 34))
    setstyle('Subtitle', lambda b: _resize(b.replace(
        '<w:spacing w:val="15" />', '<w:spacing w:after="60" w:before="0" />'), body + 1))
    setstyle('Heading1', lambda b: _resize(b.replace(
        '<w:spacing w:after="80" w:before="360" />',
        '<w:spacing w:after="40" w:before="140" />'), body + 5))
    setstyle('Heading2', lambda b: _resize(b.replace(
        '<w:spacing w:after="80" w:before="160" />',
        '<w:spacing w:after="20" w:before="80" />'), body + 1))
    setstyle('BodyText', lambda b: b.replace(
        '<w:spacing w:after="180" w:before="180" />',
        '<w:spacing w:after="40" w:before="40" w:line="240" w:lineRule="auto" />'))
    setstyle('Compact', lambda b: _resize(b.replace(
        '<w:spacing w:after="36" w:before="36" />',
        '<w:spacing w:after="10" w:before="10" w:line="230" w:lineRule="auto" />'), body - 1))
    setstyle('BlockText', lambda b: b.replace(
        '<w:spacing w:after="100" w:before="100" />',
        '<w:spacing w:after="40" w:before="40" />'))
    return xml


def patch_document(xml: str, lr: int, tb: int) -> str:
    new_sect = (
        '<w:sectPr><w:footnotePr><w:numRestart w:val="eachSect" /></w:footnotePr>'
        '<w:pgSz w:w="%d" w:h="%d" />'
        '<w:pgMar w:top="%d" w:right="%d" w:bottom="%d" w:left="%d"'
        ' w:header="0" w:footer="0" w:gutter="0" /></w:sectPr>' % (A4_W, A4_H, tb, lr, tb, lr)
    )
    if re.search(r'<w:sectPr>.*?</w:sectPr>', xml, re.S):
        return re.sub(r'<w:sectPr>.*?</w:sectPr>', new_sect, xml, flags=re.S)
    # 没有 sectPr 时插到 body 末尾
    return xml.replace('</w:body>', new_sect + '</w:body>')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('dst', nargs='?')
    ap.add_argument('--size', type=int, default=20)
    ap.add_argument('--margin-lr', type=int, default=850)
    ap.add_argument('--margin-tb', type=int, default=680)
    ap.add_argument('--font', default='Songti SC')
    ap.add_argument('--latin', default='Calibri')
    a = ap.parse_args()
    dst = a.dst or a.src

    tmp = tempfile.mkdtemp(prefix='tighten_')
    try:
        with zipfile.ZipFile(a.src) as z:
            z.extractall(tmp)
        sp = os.path.join(tmp, 'word', 'styles.xml')
        dp = os.path.join(tmp, 'word', 'document.xml')
        with open(sp, encoding='utf-8') as f:
            s = f.read()
        with open(dp, encoding='utf-8') as f:
            d = f.read()
        s = patch_styles(s, a.size, a.font, a.latin)
        d = patch_document(d, a.margin_lr, a.margin_tb)
        with open(sp, 'w', encoding='utf-8') as f:
            f.write(s)
        with open(dp, 'w', encoding='utf-8') as f:
            f.write(d)

        if os.path.exists(dst):
            os.remove(dst)
        with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(tmp):
                for fn in files:
                    p = os.path.join(root, fn)
                    z.write(p, os.path.relpath(p, tmp))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print('已收紧: %s -> %s (A4 %d×%d twips, 正文 %s磅, 页边距 %d/%d twips)'
          % (a.src, dst, A4_W, A4_H, a.size / 2, a.margin_lr, a.margin_tb))
    return 0


if __name__ == '__main__':
    sys.exit(main())
