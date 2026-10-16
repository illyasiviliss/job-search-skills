# 版式还原与 PDF 导出（HTML ＋ Chrome headless 路线）

用于要**像素级还原某个版式**的中文简历（默认路线）。纯 Markdown 场景仍可走 pandoc → `scripts/tighten_docx_a4.py`。

## 为什么走 HTML

pandoc 只能选样式名，控制不了「机构名靠左 ＋ 日期右对齐同一行」「节标题加下划线」这类结构；
textutil/LibreOffice 转出来的版式又会被文档默认样式吃掉。HTML ＋ CSS 全部可控，且中文字体可以直接指定。

## 生成命令

```bash
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CH" --headless --disable-gpu --no-pdf-header-footer \
  --user-data-dir=/tmp/cvchrome --print-to-pdf="输出.pdf" "cv.html"

# 需要可编辑副本时，从同一份 HTML 转，避免两份内容漂移
textutil -convert docx -output "输出.docx" "cv.html"
```

- `--user-data-dir` 建议给：桌面 Chrome 常年开着时，不给会与在跑的实例抢 profile 并报 `CVDisplayLinkCreateWithCGDisplay failed`（该报错无害）。
- `--no-pdf-header-footer` 去掉默认的页眉页脚（日期、file:// 路径），否则 PDF 会多出两行垃圾。

## 页数验收（要求一页 A4 时）

```bash
python3 -c "from pypdf import PdfReader; print(len(PdfReader('输出.pdf').pages))"
sips -s format jpeg --resampleWidth 1100 输出.pdf --out /tmp/preview.jpg   # 然后自己看图
```

**必须真的数页数，并且真的看图**（`mdls kMDItemNumberOfPages` 在 macOS 上常返回 null，别用）。
溢出到第 2 页时按这个顺序收，不要一上来就砍内容：

1. `@page` 外边距 → `9mm 12mm 8mm 12mm`
2. `body` 字号 9.4pt → 8.7pt、行高 1.38 → 1.26
3. 各 `h2` 的 `margin` 收到 `5.5px 0 2px`、`padding-bottom: 1px`
4. `.entry` 的 `margin-bottom` 收到 `3.2px`
5. 最后才考虑减少项目条数或删 `[按需]` 段

## 一页填满度：量出来，不要用眼睛猜

删掉整节内容（Summary、课程项目）后，同一套 CSS 会只剩四成高度。**先量，再决定字号往上调多少：**

```python
import pymupdf
p = "输出.pdf"
d = pymupdf.open(p); pg = d[0]
bottom = max(b[3] for b in pg.get_text("blocks"))
print("pages=%d  填满度=%.0f%%" % (d.page_count, 100 * bottom / pg.rect.height))
```

- 目标：**1 页 且 填满度 92–96%**。低于 ~80% 就往上调字号（一次 0.4–0.8pt），超过 100% 就往回收。
- 这个阈值**非线性**：实测（A4、11mm 边距）9.6pt 正好一页、10.4pt 立刻两页。逐档试，别插值猜。
- 预览图必须从**产出 PDF** 渲染，不能截 HTML：

```python
pymupdf.open("输出.pdf")[0].get_pixmap(dpi=160).save("预览.png")  # 发给用户的就是这张
```

### 两个会让你误判的坑

- **不要用 Chrome `--screenshot` 截 HTML 判断填充度。** HTML 没有 `@page` 约束，截图里的比例与 PDF 里的比例根本不是一回事 —— 曾据此报「只填了四成」，而同一份 PDF 实测 95%。要判断版面，只量 PDF、只看 PDF 渲染出来的图。
- **逐档试字号时不要把测试输出写进正式产出目录。** 写进去的话，最后一档测试结果会冒充正式产物（曾把校准跑出来的「2 页」当成结论报给用户）。要么写到临时目录，要么**试完必须重跑一次真正的生成器再验收**。

## 可直接改用的 CSS

当前生效值（**无 Summary ＋ 无课程项目**的一页版，正好填满 94–96%）。内容变少时按上面的「填满度」往上调字号；内容变多时按上面的收紧顺序往下走。

```css
@page { size: A4; margin: 11mm 13mm 11mm 13mm; }
html, body { margin: 0; padding: 0; }
/* ⚠️ 中文字体必须选「PDF 里能正确提取」的，否则 ATS 读不到关键词 —— 见 SKILL.md「中文字体与 ATS」 */
body { font-family: "Times New Roman", "STHeiti", "Arial Unicode MS", sans-serif; color: #000;
       font-size: 9.6pt; line-height: 1.38; }
.name { text-align: center; font-size: 19pt; font-weight: 700; letter-spacing: 1px; }
.name .en { font-size: 13pt; font-weight: 400; margin-left: 8px; }
.tagline { text-align: center; font-size: 10.2pt; font-weight: 700; margin-top: 6px; }
.contact { text-align: center; font-size: 9pt; margin-top: 4px; line-height: 1.45; }
.rule { border-bottom: 1.6px solid #000; margin: 8px 0 8px; }
h2 { font-size: 11pt; font-weight: 700; margin: 10px 0 5px; padding-bottom: 2px;
     border-bottom: 1.5px solid #000; letter-spacing: 1.2px; }
h2 .cn { font-weight: 400; font-size: 9.4pt; letter-spacing: 0.5px; }
.entry { margin-bottom: 6px; }
.row { display: flex; justify-content: space-between; align-items: baseline; }  /* 机构名左、日期右 */
.org { font-weight: 700; font-size: 10pt; }
.date { font-size: 9.2pt; font-weight: 700; white-space: nowrap; }
.role { font-style: italic; font-size: 9.2pt; margin-top: 1px; }
.sub { font-style: italic; font-weight: 700; margin-top: 4px; }
p { margin: 3px 0 0; }
ul { margin: 2px 0 0; padding-left: 14px; }
li { margin: 2px 0; }
.plain { margin: 0 0 4px; }
.tight { margin-top: 2px; }
```

结构约定：

- 节标题写 `<h2>EDUCATION <span class="cn">教育经历</span></h2>` —— 英文大写做视觉锚点，中文小字跟在后面。
- 每段经历用 `<div class="entry">`，标题行用 `<div class="row"><span class="org">…</span><span class="date">…</span></div>`。
- **技能栏不要用表格**：中文技能只占几行，满宽表格右侧会空出一大片，看着像没填完。用 `<p class="plain"><b>分类：</b>内容</p>` 三行。

## 中文字体

- 正文用 **`STHeiti`**（配 `"Times New Roman"` 走 Latin）。原因见 SKILL.md 的「中文字体与 ATS」：宋体系字体（`Songti SC` / `STSong` / `SimSun`）出的 PDF 里约 4–5% 汉字会抽成 Kangxi 部首码位，**肉眼看不出、ATS 全读不到**。
- **不要用 `SimSun`**：`fc-match SimSun` 在 macOS 上解析成 Times New Roman，中文会掉字体。

## 生成后的自检

**先查文本，再看图。** 文本层查「该没有的东西真的没有」，这一层不能省 —— 视觉上看不出某一段是「被删了」还是「被挤到第二页以下」：

```python
import pymupdf
d = pymupdf.open("输出.pdf")
t = "".join(pg.get_text() for pg in d)
print(d.page_count, [k for k in ["SUMMARY", "个人总结", "COURSE", "课程项目", "**"] if k in t])
```

判据：**1 页 ＋ 填满度 92–96% ＋ 禁用词列表为空**。禁用词按当前口径替换（不再写 Summary、不再写课程项目时，它们出现在正文里就说明生成器没改干净）。改过生成器后必须走这一遍 —— 只改源码、不看产出，是「以为改了其实没改」的唯一来源。

再看图（从 PDF 渲染，不是 HTML 截图）确认：中文无乱码；节标题与机构名有层级差；机构名与日期确实左右分列；要点各自独立成行；底部留白不超过约 10%。
