# scipilot-figure-skill

> SciPilot Skills family. Scientific data **visualization advisor** 鈥?thinks first, plots second.
> SciPilot Skills 瀹舵棌鎴愬憳 鈥?绉戠爺鏁版嵁**鍙鍖栭【闂?*锛屽厛鎬濊€冨悗缁樺埗銆?
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg)](#dependencies--渚濊禆)
[![Status: v2.1.0](https://img.shields.io/badge/Status-v2.1.0-success.svg)](#)
[![Advisor Mode](https://img.shields.io/badge/Mode-Advisor%2BPlotter-c41e3a.svg)](#涓轰粈涔堣繖涓嶅彧鏄釜鐢诲浘宸ュ叿)
[![Stack](https://img.shields.io/badge/Stack-matplotlib%20%7C%20seaborn%20%7C%20plotly-orange.svg)](#)
[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-orange.svg)](https://claude.com/claude-code)

A [Claude Code](https://claude.com/claude-code) / [Codex](https://github.com/openai/codex) / Cursor Skill that does **two things in order**: (1) profiles your data and recommends the right chart for the argument you want to make, (2) renders it at publication grade for Nature / Science / IEEE / Elsevier / PNAS / Chinese journals. Built on **matplotlib + seaborn + SciencePlots** (static) and **plotly** (interactive), with **CJK font auto-configuration** so Chinese text never renders as boxes.

> [涓枃鏂囨。](#涓枃鏂囨。) | [English](#english)

---

## 涓枃鏂囨。

### 姒傝

绉戠爺宸ヤ綔鑰呮渶澶х殑鐢诲浘鐥涚偣寰€寰€涓嶆槸"涓嶄細鐢?matplotlib"锛岃€屾槸"鎵嬩笂涓€鍫嗘暟鎹紝涓嶇煡閬撹鐢ㄤ粈涔堝浘鎶婄粨璁鸿娓呮"銆俙scipilot-figure-skill` 鏄?SciPilot Skills 瀹舵棌鐨勭浜屼釜鎴愬憳锛屼笓鍋氳繖浠朵簨鈥斺€?
**瀹冪殑棣栬鑳藉姏鏄€愭€濊€冧笌鍒ゆ柇銆戯紝鍏舵鎵嶆槸銆愮粯鍒躲€戙€?*

### 涓轰粈涔堣繖涓嶅彧鏄釜鐢诲浘宸ュ叿

```
鏅€氱敾鍥惧伐鍏?          scipilot-figure-skill
鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€         鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
浣犺 "鐢绘煴鐘跺浘"  鈫?  鍏?EDA锛氭瘡鍒楃被鍨嬨€佹牱鏈噺銆佸垎甯冦€佸紓甯稿€笺€佺浉鍏虫€?鐩存帴 plt.bar()        鍐嶉棶锛?浣犳兂璁鸿瘉浠€涔堬紵缁勯棿宸紓锛熷叧绯伙紵瓒嬪娍锛?
                     鎸夋暟鎹壒寰?+ 璁鸿瘉鐩爣鏌ュ喅绛栨鏋舵帹鑽愬浘鍨?                     n=5 鎯崇敾鍧囧€兼煴鏃朵富鍔ㄦ嫤鎴?鈫?鏀圭敤 stripplot
                     缁村害 > 12 鏃跺缓璁媶鍥撅紝涓嶇‖濉?                     鏈€鍚庢墠杩涘叆缁樺埗 鈫?鏈熷垔瑙勮寖 鈫?鑷 鈫?瀵煎嚭
```

### 鏍稿績宸ヤ綔娴侊紙8 姝ワ級

```
0. 鐞嗚В浠诲姟   鈹€鈹€ 杩欏紶鍥捐璁鸿瘉浠€涔堬紵鏁版嵁鍦ㄥ摢锛?   鈫?1. 鍓栨瀽鏁版嵁   鈹€鈹€ profile_data.py锛氬垪绫诲瀷/鏍锋湰閲?鍒嗗竷/寮傚父/鐩稿叧
   鈫?2. 閫夊浘       鈹€鈹€ chart_selection.md锛氭寜鏁版嵁褰㈡€?璁鸿瘉鐩爣鍐崇瓥
   鈫?(涓诲姩鎷︽埅 鈫?viz_pitfalls.md)
3. 鏌ヨ鑼?    鈹€鈹€ journal_specs.md锛氭爮瀹?瀛楀彿/DPI/瀛椾綋
   鈫?4. 閰嶇幆澧?    鈹€鈹€ setup_style.py锛氭湡鍒婇璁?CJK瀛椾綋
   鈫?5. 缁樺埗       鈹€鈹€ plot_recipes.md锛? 绫诲浘閰嶆柟
   鈫?6. 鑷闂幆   鈹€鈹€ 绋嬪簭鑷 visual_qa + AI 璇诲浘 visual_review.md锛堢己瀛?瑁佸垏/閲嶅彔/瀵归綈鈫掑洖鏀癸級
   鈫?7. 瀵煎嚭       鈹€鈹€ export_figure.py锛氬鏍煎紡+鎸夋渶缁堝昂瀵?鐏板害棰勮
```

### v2.1 鏂板锛氬嚭鍥惧悗鐨勮瑙夎嚜妫€闂幆

鏅€氱敾鍥惧伐鍏风敾瀹屽氨缁撴潫鈥斺€旀病浜哄洖鐪嬫垚鍥撅紝浜庢槸涓枃鏂规銆佹枃瀛楄瑁併€佸浘渚嬪帇鏁版嵁銆佸瓙鍥剧紪鍙蜂贡鏀撅紝鍏ㄧ暀鍒版姇绋挎墠鏆撮湶銆倂2.1 琛ヤ笂**鍑哄浘鍚庣殑闂幆**锛?
```
缁樺埗 鈫?娓叉煋 PNG 鈫?绋嬪簭鑷(缂哄瓧/瑁佸垏/閲嶅彔) + AI 璇诲浘(閬洊/瀛愬浘瀵归綈/鐏板害)
                            鈫?鍙戠幇闂
        鍥炲埌瀵瑰簲姝ラ鏀瑰浘 鈫?閲嶆覆 鈫?鍐嶈锛岀洿鍒伴€氳繃
```

- **绋嬪簭鎶撶‘瀹氭€ч棶棰?*锛歚visual_qa.audit_layout()` 鍚屾椂鐩?warning + logging 涓ゆ潯閫氶亾鎷︽埅缂哄瓧涔辩爜锛屽苟鏌ユ枃瀛楄秺鐣岃鍒囥€佸埢搴︽爣绛鹃噸鍙犮€?- **AI 璇诲浘鎶撴劅鐭ユ€ч棶棰?*锛氭覆鎴?PNG 鍚庣敤澶氭ā鎬佽鍥捐兘鍔涙牳瀵瑰浘渚嬫槸鍚﹀帇鏁版嵁銆佸瓙鍥?a/b/c 鏄惁瀵归綈銆侀厤鑹茬伆搴﹀彲鍒嗏€斺€旇繖浜涚▼搴忔煡涓嶅嚭銆?- **瀛愬浘鏍囩涓€琛屽榻?*锛歚layout_tools.add_panel_labels(fig)` 鐢ㄧ粺涓€ figure 鍧愭爣璁?a/b/c/d 妯珫鎴愮嚎锛屼笉鍐嶆墜鎽嗘槗閿欎綅銆?- **瀛椾綋鍏滃簳**锛歚setup_style` 鍏ㄦā寮忛粯璁や慨璐熷彿鏂规 + 鑷姩閰?CJK 瀛椾綋锛屼粠婧愬ご灏戝嚭涔辩爜銆?
璇﹁ [`references/visual_review.md`](references/visual_review.md)銆?
### 浜旀潯纭€у師鍒?
1. **鎸夋渶缁堝昂瀵稿嚭鍥句笉浜屾缂╂斁** 鈥?`figsize=(3.5, 2.625)` 鐩存帴瀹?Nature 鍗曟爮
2. **鐭㈤噺浼樺厛** 鈥?鏁版嵁鍥捐蛋 PDF / SVG / EPS锛涚収鐗囨墠鐢?TIFF/PNG锛?*缁濅笉 JPEG**
3. **閰嶈壊瀵硅壊鐩插弸濂?* 鈥?榛樿 Okabe-Ito锛屽姞鍐椾綑缂栫爜锛屽嚭鍥惧墠鏌ョ伆搴?4. **瀛楀彿鍦ㄦ渶缁堝昂瀵镐笅鍙** 鈥?7-9 pt锛屾渶灏?6 pt
5. **璇樊蹇呮湁浜や唬** 鈥?鍥炬敞蹇呴』鍐欐竻 SD/SEM/95%CI + n + 妫€楠屾柟娉?
### 涓诲姩鎷︽埅鐨勭敾鍥鹃敊璇紙绮鹃€夛級

瀹屾暣 15 鏉″湪 [`references/viz_pitfalls.md`](references/viz_pitfalls.md)銆?
- **P1**锛歯<10/缁勭殑鍧囧€兼煴鎺╃洊鍒嗗竷 鈫?鏀圭绾?+ stripplot
- **P2**锛氬弻 Y 杞寸殑"鐩稿叧"鏄綔鍥捐€呮崗閫犵殑 鈫?鎷嗗瓙鍥炬垨鏍囧噯鍖?- **P3**锛氶ゼ鍥句笌 3D 鍥?鈫?妯悜鏌辩姸
- **P4**锛歒 杞翠笉褰撴埅鏂?鈫?浠?0 璧锋垨鏂鏄庣ず
- **P6**锛歺 鏄垎绫荤敤鎶樼嚎杩炲潎鍊?鈫?鏁ｇ偣 / 鏌辩姸
- **P14**锛歳ainbow / jet 鑹插浘 鈫?viridis / RdBu_r
- **P12**锛氫竴鍥惧璁虹偣 鈫?鎷嗗浘锛屼竴鍥句竴缁撹
- **P16**锛氫腑鏂?璐熷彿鍙樻柟妗?鈫?setup_style 閰?CJK + 鍏?unicode_minus锛屽鍑哄墠 visual_qa 鎷︽埅
- **P18**锛氬瓙鍥?a/b/c 涔辨斁 鈫?add_panel_labels 缁熶竴瀵归綈

### 瀹夎

```
璇峰府鎴戝畨瑁呰繖涓?Skill锛歨ttps://github.com/Haojae/scipilot-figure-skill.git
```

鎴栨墜鍔細

```bash
git clone https://github.com/Haojae/scipilot-figure-skill.git \
          ~/.claude/skills/scipilot-figure-skill
pip install -r ~/.claude/skills/scipilot-figure-skill/requirements.txt
```

`SciencePlots` / `pypdf` / `kaleido` 鏄彲閫夊寮猴紝缂哄け鏃朵笉褰卞搷杩愯銆?
### 涓枃鏀寔

`setup_style(lang='zh')` 鎸変紭鍏堢骇鏌ユ壘锛?
```
Noto Sans CJK SC > Source Han Sans SC > SimHei > Microsoft YaHei
```

鎵句笉鍒颁换浣?CJK 瀛椾綋鏃舵姏鍑烘竻鏅扮殑瀹夎鎻愮ず銆備腑鏂囨湡鍒?瀹嬩綋 + Times New Roman 鏁板瓧"娣锋帓锛氫紶 `serif_for_zh=True`銆?
### 浣跨敤绀轰緥锛? 涓紝**鑷冲皯 2 涓綋鐜?鎬濊€?**锛?
**渚?1锛氱敤鎴峰彧涓竴涓?CSV**

```
鎴戞湁杩欎唤 results.csv锛屽府鎴戠敾鎴愯鏂囧浘銆?```

鈫?Skill 涓嶄細鐩存帴鐢汇€備細鍏堬細
1. 闂?浣犺繖浠芥暟鎹富瑕佹兂璇存湇璇昏€呯浉淇′粈涔堬紵"
2. 璺?`profile_data.py` 杈撳嚭鍓栨瀽鎶ュ憡
3. 缁欏嚭鎺ㄨ崘鍥惧瀷 + 鐞嗙敱 + 澶囬€?4. 鐢ㄦ埛纭鍚庢墠杩涘叆缁樺埗娴佺▼

**渚?2锛氱敤鎴锋寚瀹氱殑鍥惧瀷涓嶅悎閫?*

```
甯垜鐢?3 缁勫悇 5 涓牱鏈殑鍧囧€兼煴鐘跺浘銆?```

鈫?Skill 涓诲姩鎷︽埅锛?
> n=5 澶皬锛屽潎鍊兼煴鎺╃洊鍒嗗竷鈥斺€斿绋夸汉寰堝彲鑳借姹?show individual points"銆?> 鎴戝缓璁敼鎴?**绠辩嚎 + stripplot 鍙犲姞姣忎釜鐐?*锛? 涓偣鐩存帴鍙銆傝鎸夊師鏂规鐢伙紝杩樻槸鏀癸紵

**渚?3锛氬闈㈡澘缁勫悎**

```
缁欐垜鐢?Figure 1锛? panel锛屽垎鍒槸 PCA銆乴oss銆佹贩娣嗙煩闃点€佺敓瀛樻洸绾裤€?Nature 鍙屾爮銆?```

鈫?鍚?panel 瀛楀彿閰嶈壊缁熶竴锛屽瓙鍥炬爣绛?a/b/c/d 鍔犵矖宸︿笂锛屽鍑?PDF + 鐏板害棰勮銆?
**渚?4锛氬甫鏄捐憲鎬ф爣娉?*

```
3 缁勬暟鎹敾绠辩嚎 + 鏄捐憲鎬с€?```

鈫?鍏堢‘璁?n銆佹楠屾柟娉曘€佹槸鍚﹀閲嶆牎姝ｏ紱鍥炬敞蹇呴』鍐欐竻缁熻鍐呭銆?
### 鍛戒护琛岀洿鎺ヨ皟鑴氭湰

```bash
# 鏁版嵁鍓栨瀽锛堟€濊€冪殑璧风偣锛?python scripts/profile_data.py results.csv --group group --group condition

# 鍒楀彲鐢?CJK 瀛椾綋
python scripts/setup_style.py --list-fonts

# 婕旂ず瀵煎嚭
python scripts/export_figure.py demo --out ./test_demo

# 鍚堣鑷
python scripts/check_figure.py figs/*.pdf --min-dpi 300 --strict
```

### SciPilot Skills 瀹舵棌

| Skill | 鐘舵€?| 鍔熻兘 |
|---|---|---|
| scipilot-cite-skill | [v1.0.0](https://github.com/Haojae/scipilot-cite-skill) | 鏂囩尞妫€绱笌寮曠敤鎻掑叆 |
| **scipilot-figure-skill** | **v2.1.0 (鏈粨搴?** | **鍙鍖栭【闂?+ 缁樺埗 + 瑙嗚鑷闂幆** |
| scipilot-polish-skill | 瑙勫垝涓?| 瀛︽湳璁烘枃娑﹁壊 |
| scipilot-review-skill | 瑙勫垝涓?| AI 妯℃嫙瀹＄ |
| scipilot-submit-skill | 瑙勫垝涓?| 鎶曠鏍煎紡閫傞厤 |
| scipilot-read-skill | 瑙勫垝涓?| 璁烘枃闃呰涓庣炕璇?|

### 璁稿彲璇?
[MIT](LICENSE) 漏 2026 Haojae

---

## English

### Overview

The hardest part of scientific plotting is rarely "I don't know matplotlib" 鈥?it's "I have data, I don't know which chart conveys my conclusion." `scipilot-figure-skill` is the second member of the SciPilot Skills family, built around this insight: **think first, plot second**.

### Why this isn't just a plotting tool

```
Generic plotter            scipilot-figure-skill
鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€             鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
"plot a bar chart"  鈫?   Profiles data first: types, n, distribution, outliers
plt.bar()                Asks: "What argument do you want this figure to make?"
                         Decides chart type from data shape + intent
                         Refuses bad choices (n=5 mean bar 鈫?stripplot instead)
                         Suggests splitting figures when dimensions exceed 12
                         Only then renders 鈫?spec 鈫?audit 鈫?export
```

### 8-step core workflow

```
0. Understand   鈥?what does this figure argue? where is the data?
   鈫?1. Profile      鈥?profile_data.py: types / n / distribution / outliers / corr
   鈫?2. Select       鈥?chart_selection.md: decision framework by shape + intent
   鈫?(active interception 鈫?viz_pitfalls.md)
3. Spec         鈥?journal_specs.md: column width / font / DPI
   鈫?4. Style        鈥?setup_style.py: journal preset + CJK font config
   鈫?5. Plot         鈥?plot_recipes.md: 9 recipe families
   鈫?6. Self-check   鈥?visual_qa (program) + AI reads the PNG (visual_review.md): glyphs/clipping/overlap/alignment
   鈫?7. Export       鈥?export_figure.py: multi-format + final size + grayscale
```

### New in v2.1: a post-render visual self-check loop

Generic plotters stop at "saved" 鈥?nobody looks at the result, so CJK tofu boxes, clipped labels, legends covering data, and misaligned panel letters all survive to submission. v2.1 closes the loop **after rendering**:

```
plot 鈫?render PNG 鈫?program audit (glyphs/clipping/overlap) + AI reads image (occlusion/panel alignment/grayscale)
                              鈫?issues found
       go back, fix, re-render, re-read 鈥?until clean
```

- **Program catches deterministic issues**: `visual_qa.audit_layout()` traps missing-glyph warnings (both warnings and logging channels), text clipped off-canvas, and overlapping tick labels.
- **AI catches perceptual issues**: after rasterizing to PNG, the skill reads the image to check whether the legend covers data, whether panel letters a/b/c line up, and whether colors stay distinct in grayscale.
- **One-call panel alignment**: `layout_tools.add_panel_labels(fig)` places a/b/c/d in unified figure coordinates so they align both ways.
- **Font safety net**: `setup_style` fixes the minus-sign box in all modes and auto-configures CJK fonts.

See [`references/visual_review.md`](references/visual_review.md).

### Five hard rules

1. **Render at final size, never rescale** 鈥?set `figsize=(3.5, 2.625)` directly
2. **Vectors first** 鈥?PDF / SVG / EPS for data figures; **never JPEG**
3. **Colorblind-safe palette** 鈥?Okabe-Ito default + redundant encoding
4. **Readable type at final size** 鈥?7-9 pt body, 6 pt minimum
5. **Errors must be explained** 鈥?captions state SD/SEM/CI + n + test type

### Actively intercepted mistakes

Full 15 in [`references/viz_pitfalls.md`](references/viz_pitfalls.md).

- **P1**: mean-only bar charts with n<10 hide distributions 鈫?use box + stripplot
- **P2**: dual-Y axis fabricates correlations 鈫?split panels or standardize
- **P3**: pie charts and 3D bars 鈫?horizontal bar
- **P14**: rainbow / jet colormaps 鈫?viridis / RdBu_r
- **P12**: one figure with five points 鈫?split, one figure per claim
- **P16**: CJK / minus-sign tofu boxes 鈫?setup_style configures CJK + disables unicode_minus; visual_qa blocks leftover missing glyphs
- **P18**: scattered panel letters 鈫?add_panel_labels aligns a/b/c in one call

### Installation

```
Please install this Skill for me: https://github.com/Haojae/scipilot-figure-skill.git
```

Manual:

```bash
git clone https://github.com/Haojae/scipilot-figure-skill.git \
          ~/.claude/skills/scipilot-figure-skill
pip install -r ~/.claude/skills/scipilot-figure-skill/requirements.txt
```

### Usage examples

**Example 1: bare CSV**

```
I have results.csv. Plot it for my paper.
```

The skill will: profile the data, ask what argument the figure should make, recommend a chart with rationale + alternatives, and only then plot.

**Example 2: bad request, gentle refusal**

```
Plot a bar chart of group means: 3 groups, 5 samples each.
```

The skill will reply:

> With n=5 per group a mean bar chart hides the distribution and reviewers
> typically ask for individual data points. I recommend **box plot +
> stripplot overlay** 鈥?all five points are visible and the distribution
> is clear. Stick with bars, or switch?

**Example 3: multi-panel composite**

```
Figure 1, 4 panels: PCA, loss curves, confusion matrix, survival.
Nature double column.
```

**Example 4: statistical comparison**

```
3 groups, box plot with significance.
```

### SciPilot Skills family

| Skill | Status | Purpose |
|---|---|---|
| scipilot-cite-skill | [v1.0.0](https://github.com/Haojae/scipilot-cite-skill) | Reference discovery & insertion |
| **scipilot-figure-skill** | **v2.1.0 (this repo)** | **Advisor + renderer + visual self-check loop** |
| scipilot-polish-skill | Planned | Academic prose polishing |
| scipilot-review-skill | Planned | AI peer-review simulation |
| scipilot-submit-skill | Planned | Submission formatting |
| scipilot-read-skill | Planned | Paper reading & translation |

### License

[MIT](LICENSE) 漏 2026 Haojae

### Dependencies / 渚濊禆

```
matplotlib>=3.7
seaborn>=0.13
plotly>=5.18
pandas>=2.0
numpy>=1.24
scipy>=1.10
Pillow>=10.0
SciencePlots>=2.1   # optional
pypdf>=4.0          # optional
kaleido>=0.2.1      # optional
PyMuPDF>=1.23       # optional; only for visual_qa.render_preview() of saved PDFs
```

Python 3.9+ recommended.
