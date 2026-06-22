# 涓冪被鍥鹃厤鏂?
姣忎竴鑺傜粰涓€浠?*鍙洿鎺ヨ繍琛岀殑 Python 浠ｇ爜**鈥斺€旂洿鎺ュ鍒舵敼鏁版嵁灏辫兘鍑哄浘銆傛墍鏈変唬鐮佸亣璁惧凡缁忚皟杩?`setup_style()`銆?
## 鐩綍

- [閫氱敤鍓嶇疆](#閫氱敤鍓嶇疆)
- [1. 鎶樼嚎鍥撅紙鍚宸槾褰憋級](#1-鎶樼嚎鍥惧惈璇樊闃村奖)
- [2. 鏌辩姸鍥撅紙鍒嗙粍 + 璇樊妫掞級](#2-鏌辩姸鍥惧垎缁?-璇樊妫?
- [3. 鏁ｇ偣鍥撅紙澶氳涔夋槧灏?+ 鍥炲綊绾匡級](#3-鏁ｇ偣鍥惧璇箟鏄犲皠--鍥炲綊绾?
- [4. 绠辩嚎鍥?/ 灏忔彁鐞村浘锛堝彔 stripplot锛塢(#4-绠辩嚎鍥?-灏忔彁鐞村浘鍙?stripplot)
- [5. 鐑姏鍥撅紙鎰熺煡鍧囧寑鑹插浘锛塢(#5-鐑姏鍥炬劅鐭ュ潎鍖€鑹插浘)
- [6. 璇樊妫掑浘](#6-璇樊妫掑浘)
- [7. 鍒嗗竷鍥撅紙鐩存柟鍥?/ KDE锛塢(#7-鍒嗗竷鍥剧洿鏂瑰浘--kde)
- [8. 鐩稿叧鎬х煩闃?/ 鏁ｇ偣鐭╅樀](#8-鐩稿叧鎬х煩闃?-鏁ｇ偣鐭╅樀)
- [9. 澶氶潰鏉跨粍鍚堝浘](#9-澶氶潰鏉跨粍鍚堝浘)
- [10. Plotly 浜や簰鍥綸(#10-plotly-浜や簰鍥?

---

## 閫氱敤鍓嶇疆

```python
import sys, os
sys.path.insert(0, '../scripts')   # 鍋囪浠?references/ 璋?from setup_style import setup_style
from export_figure import export_figure

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 涓€娆℃€ц濂芥牱寮?setup_style(journal='nature', lang='en')

# Okabe-Ito 8 鑹诧紙鑹茬洸瀹夊叏锛?OKABE = ['#000000', '#E69F00', '#56B4E9', '#009E73',
         '#F0E442', '#0072B2', '#D55E00', '#CC79A7']
# 涔熷彲鐩存帴鐢?seaborn 鐨?colorblind
PAL = sns.color_palette('colorblind')
```

---

## 1. 鎶樼嚎鍥撅紙鍚宸槾褰憋級

**浣曟椂鐢?*锛氭椂闂村簭鍒椼€亁 鏄繛缁彉閲忋€侀渶瑕佸睍绀哄潎鍊悸辫宸€?
```python
def lineplot_with_band(ax, x, y_mean, y_err, label, color, ls='-'):
    """y_err 鍙互鏄?SD/SEM/95%CI锛屽浘娉ㄩ噷鍔″繀浜や唬銆?""
    ax.plot(x, y_mean, color=color, linewidth=1.0, linestyle=ls, label=label)
    ax.fill_between(x, y_mean - y_err, y_mean + y_err,
                    color=color, alpha=0.2, linewidth=0)

# --- 绀轰緥 ---
rng = np.random.default_rng(42)
x = np.linspace(0, 10, 100)
# 鍋囪 n=12 鍙皬榧狅紝瀵规瘡涓?x 绠?mean 卤 SEM
n = 12
y1_samples = np.sin(x)[:, None] + rng.normal(0, 0.3, (100, n))
y2_samples = np.cos(x)[:, None] + rng.normal(0, 0.3, (100, n))
y1_mean, y1_sem = y1_samples.mean(1), y1_samples.std(1, ddof=1) / np.sqrt(n)
y2_mean, y2_sem = y2_samples.mean(1), y2_samples.std(1, ddof=1) / np.sqrt(n)

fig, ax = plt.subplots(figsize=(3.5, 2.625))
lineplot_with_band(ax, x, y1_mean, y1_sem, 'Condition A',
                   color=OKABE[2], ls='-')
lineplot_with_band(ax, x, y2_mean, y2_sem, 'Condition B',
                   color=OKABE[6], ls='--')   # 绗簩鏉＄敤铏氱嚎 -> 榛戠櫧鍙
ax.set_xlabel('Time (s)')
ax.set_ylabel('Response (a.u.)')
ax.legend(frameon=False, loc='lower right')

# 鍥炬敞蹇呴』鍐? shaded band = SEM, n = 12 mice per group.
export_figure(fig, 'figs/01_line', formats=['pdf', 'svg', 'png'],
              size_inches=(3.5, 2.625), dpi=300, grayscale_preview=True)
```

**鍧?*锛?- `fill_between` 蹇呴』鏄惧紡 `linewidth=0`锛屽惁鍒?PDF 閲岄槾褰辫竟缂樹細鏈夌粏绾?- 涓嶅悓鏇茬嚎**蹇呴』**鏈夐櫎棰滆壊涔嬪鐨勫尯鍒嗭紙绾垮瀷 / marker锛夛紝鍚﹀垯鐏板害涓嬩笉鍙

---

## 2. 鏌辩姸鍥撅紙鍒嗙粍 + 璇樊妫掞級

**浣曟椂鐢?*锛氬垎绫诲彉閲忕殑鍧囧€煎姣斻€佺粍闂存瘮杈冦€?
```python
# 鏁版嵁锛? 缁?脳 2 鏉′欢 脳 n=10 閲嶅
rng = np.random.default_rng(0)
groups = ['Control', 'Drug A', 'Drug B']
conditions = ['Before', 'After']
data = pd.DataFrame({
    'group': np.repeat(groups, 2 * 10),
    'condition': np.tile(np.repeat(conditions, 10), 3),
    'value': np.concatenate([
        rng.normal(loc, 1.0, 10)
        for loc in [1, 2, 3, 4, 2, 3]   # 6 缁勫悎
    ]),
})

# 鐢?seaborn barplot鈥斺€旈粯璁ゅ氨鏄?mean + 95%CI锛坆ootstrap锛?# 鎯宠 SD/SEM 鏀?errorbar 鍙傛暟
fig, ax = plt.subplots(figsize=(3.5, 2.625))
sns.barplot(
    data=data, x='group', y='value', hue='condition',
    palette=[OKABE[2], OKABE[6]],
    errorbar='se',          # 'sd' | 'se' | ('ci', 95) | None
    capsize=0.15,
    err_kws={'linewidth': 0.8},
    ax=ax,
)
# 鍙犲姞鍘熷鐐规樉绀烘暟鎹垎甯冣€斺€斿绋夸汉鍠滄鐪嬪垎甯冭€岄潪鍙湅鍧囧€?sns.stripplot(
    data=data, x='group', y='value', hue='condition',
    palette=[OKABE[2], OKABE[6]],
    dodge=True, size=2, alpha=0.6, edgecolor='black', linewidth=0.3,
    ax=ax, legend=False,
)
ax.set_xlabel(''); ax.set_ylabel('Score (a.u.)')
ax.legend(title='', frameon=False, loc='upper left')

# 鍥炬敞: bars = mean 卤 SEM; dots = individual replicates; n = 10 per group.
export_figure(fig, 'figs/02_bar', formats=['pdf', 'svg', 'png'],
              size_inches=(3.5, 2.625), dpi=300)
```

**鍧?*锛?- 鏌辩姸鍥?*涓嶈**鐢ㄦ病鏈夎宸鐨勭函鏌扁€斺€斿绋夸汉浼氭€€鐤戞病鍋氶噸澶?- 澶氱粍姣旇緝鏃堕厤鑹蹭繚鎸佺被鍒竴鑷达紙鍚屼竴涓潯浠跺湪涓嶅悓鍥鹃噷鍚岃壊锛?- `barplot` 榛樿 95% CI 鏄?bootstrap锛?*閫熷害鎱?*锛屾槑纭啓 `errorbar='se'` 鎴?`'sd'` 鏇村揩涔熸洿鏄庣‘

---

## 3. 鏁ｇ偣鍥撅紙澶氳涔夋槧灏?+ 鍥炲綊绾匡級

**浣曟椂鐢?*锛氱浉鍏虫€с€佸弻鍙橀噺鍏崇郴锛涘彲浠ュ悓鏃舵槧灏?hue锛堥鑹诧級+ style锛坢arker锛? size銆?
```python
# 妯℃嫙鏁版嵁锛歂 涓牱鏈紝x 鍜?y 鏈夌浉鍏虫€э紝鍒嗕袱缁?rng = np.random.default_rng(1)
N = 80
df = pd.DataFrame({
    'x': rng.normal(0, 1, N),
    'group': rng.choice(['A', 'B'], N),
})
df['y'] = 0.6 * df['x'] + np.where(df['group']=='B', 0.5, 0) + rng.normal(0, 0.5, N)

fig, ax = plt.subplots(figsize=(3.5, 3.0))
sns.scatterplot(
    data=df, x='x', y='y',
    hue='group', style='group',     # 棰滆壊 + marker 褰㈢姸鍙岄噸缂栫爜
    palette=[OKABE[2], OKABE[6]],
    s=25, alpha=0.85, edgecolor='black', linewidth=0.3,
    ax=ax,
)
# 鍒嗙粍鍥炲綊绾?+ 95% CI
sns.regplot(data=df[df.group=='A'], x='x', y='y',
            scatter=False, color=OKABE[2], line_kws={'lw': 1.0}, ax=ax)
sns.regplot(data=df[df.group=='B'], x='x', y='y',
            scatter=False, color=OKABE[6], line_kws={'lw': 1.0}, ax=ax)

# 鍦ㄥ浘閲屾爣 Pearson r 鍜?p
from scipy.stats import pearsonr
for g, c in zip(['A', 'B'], [OKABE[2], OKABE[6]]):
    sub = df[df.group == g]
    r, p = pearsonr(sub.x, sub.y)
    ax.text(0.05 if g=='A' else 0.05, 0.95 if g=='A' else 0.88,
            f'{g}: r={r:.2f}, p={p:.1e}',
            transform=ax.transAxes, fontsize=6, color=c, va='top')

ax.set_xlabel('Predictor x'); ax.set_ylabel('Response y')
ax.legend(title='Group', frameon=False, loc='lower right')

export_figure(fig, 'figs/03_scatter', formats=['pdf', 'svg', 'png'],
              size_inches=(3.5, 3.0), dpi=300)
```

**鍧?*锛?- 鏁ｇ偣鍥炬牱鏈噺寰堝ぇ锛?1000锛夋椂锛宎lpha 璋冨埌 0.2-0.3 闃叉 over-plotting锛屾垨鐢?`sns.jointplot` 鍔犺竟缂樺瘑搴?- 鎶?r 鍜?p 鏍囧湪鍥鹃噷**寰堢渷瀹＄浜烘椂闂?*锛屽姞鍒嗛」
- regplot 鐨?`scatter=False` 蹇呴』锛屽惁鍒欐暎鐐逛細琚敾涓ら亶

---

## 4. 绠辩嚎鍥?/ 灏忔彁鐞村浘锛堝彔 stripplot锛?
**浣曟椂鐢?*锛氱粍闂村垎甯冨姣旓紱绠辩嚎鍥剧湅鍥涘垎浣嶏紝灏忔彁鐞村浘鐪嬪瘑搴︺€?*鏈€浣冲疄璺?*锛氱绾垮浘/灏忔彁鐞村浘 + stripplot 鍙犲姞鏄剧ず鍘熷鐐广€?
```python
# 鍚屼换鍔?2 鐨勬暟鎹?fig, ax = plt.subplots(figsize=(3.5, 2.625))
sns.boxplot(
    data=data, x='group', y='value', hue='condition',
    palette=[OKABE[2], OKABE[6]],
    showfliers=False,        # 涓嶇敾寮傚父鐐癸紝鐢?stripplot 鏄剧ず鍏ㄩ儴鐐?    width=0.6,
    linewidth=0.8,
    ax=ax,
)
sns.stripplot(
    data=data, x='group', y='value', hue='condition',
    palette=[OKABE[2], OKABE[6]],
    dodge=True, size=2.5, alpha=0.6,
    edgecolor='black', linewidth=0.3,
    ax=ax, legend=False,
)
ax.set_xlabel(''); ax.set_ylabel('Score (a.u.)')
ax.legend(title='', frameon=False)

# 鎯崇敤灏忔彁鐞村浘鎶?boxplot 鎹?violinplot 鍗冲彲:
# sns.violinplot(..., inner=None, cut=0)
# inner=None 鍏虫帀鍐呴儴灏忔潯锛沜ut=0 璁╁皬鎻愮惔涓嶈秴鍑烘暟鎹寖鍥?
export_figure(fig, 'figs/04_box', formats=['pdf', 'svg', 'png'],
              size_inches=(3.5, 2.625), dpi=300)
```

**鏄捐憲鎬ф爣娉?*锛堝闇€锛夛細

```python
from matplotlib.lines import Line2D
def sig_bracket(ax, x1, x2, y, h, text, fontsize=6):
    """鍦?(x1, x2) 涔嬮棿鐢讳竴閬撳甫鏂囧瓧鐨勬ˉ銆?""
    ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y],
            color='black', linewidth=0.6)
    ax.text((x1+x2)/2, y+h, text, ha='center', va='bottom', fontsize=fontsize)

# 渚? 鍦?Control vs Drug A 涓婃柟鍔?'**'
# x1=0-0.15, x2=0-0.15 瀵瑰簲 dodge 鍚庡疄闄呬綅缃紱璋冧竴涓嬪亸绉?# sig_bracket(ax, -0.2, 0.2, y=5.5, h=0.1, text='**')
```

**鍧?*锛?- 灏忔彁鐞村浘姣旂绾垮浘**鏇村鏄撹瀵?*鈥斺€攏<10 鏃跺瘑搴︿及璁′笉鍙潬锛屽缓璁洿鎺ョ敤绠辩嚎
- 鏄捐憲鎬ф爣娉ㄥ繀椤诲湪鍥炬敞閲岃鏄庯細what test锛屾槸鍚︽牎姝ｅ閲嶆瘮杈冿紙Bonferroni / FDR锛?- `* p<0.05, ** p<0.01, *** p<0.001` 杩欑缂╁啓闇€鍦ㄥ浘娉ㄦ垨鏂囩珷涓畾涔?
---

## 5. 鐑姏鍥撅紙鎰熺煡鍧囧寑鑹插浘锛?
**浣曟椂鐢?*锛氱煩闃垫暟鎹€佺浉鍏虫€х煩闃点€佹贩娣嗙煩闃点€佸熀鍥犺〃杈剧煩闃点€?
```python
# 妯℃嫙涓€涓?8脳8 鐩稿叧鐭╅樀
rng = np.random.default_rng(2)
mat = rng.uniform(-1, 1, (8, 8))
mat = (mat + mat.T) / 2     # 瀵圭О
np.fill_diagonal(mat, 1.0)
labels = [f'f{i+1}' for i in range(8)]

fig, ax = plt.subplots(figsize=(3.5, 3.0))
hm = sns.heatmap(
    mat, ax=ax,
    cmap='RdBu_r',          # 鍙屽悜鏁版嵁鐢ㄥ彂鏁ｈ壊鍥撅紱鍗曞悜鏁版嵁鐢?'viridis' / 'magma'
    vmin=-1, vmax=1,        # 鏄惧紡閿佸畾鑼冨洿 -> 澶氫釜鍥惧彲姣旇緝
    center=0,
    annot=True, fmt='.2f',
    annot_kws={'fontsize': 5},
    cbar_kws={'label': "Pearson's r", 'shrink': 0.8},
    linewidths=0.5, linecolor='white',
    xticklabels=labels, yticklabels=labels,
    square=True,
)
ax.tick_params(labelsize=6)
hm.collections[0].colorbar.ax.tick_params(labelsize=6)

export_figure(fig, 'figs/05_heatmap', formats=['pdf', 'svg', 'png'],
              size_inches=(3.5, 3.0), dpi=300)
```

**鍧?*锛?- **涓嶈鐢?* rainbow / jet / hsv鈥斺€旀劅鐭ヤ笉鍧囧寑锛屼細"閫犲嘲閫犺胺"銆?*姘歌繙鐢?* viridis / magma / inferno / cividis / RdBu_r
- 鍙屽悜鏁版嵁锛堟璐熸湁鎰忎箟锛夊繀椤诲彂鏁ｈ壊鍥撅紙`RdBu_r`銆乣PiYG`锛? `center=0`
- 鏁板€?annot 澶ч噺鏁版嵁鏃跺叧鎺夛紙`annot=False`锛夛紝涓嶇劧绯婃垚涓€鐗?- `square=True` 璁╂瘡涓牸瀛愭鏂瑰舰锛屾洿涓撲笟

---

## 6. 璇樊妫掑浘

**浣曟椂鐢?*锛氬皯閲忕偣浣嶇殑鍧囧€?卤 璇樊瀵规瘮锛涘吀鍨嬪涓嶅悓鍓傞噺銆佷笉鍚屾椂闂寸偣銆?
```python
doses = np.array([0, 1, 3, 10, 30, 100])
n = 8
rng = np.random.default_rng(3)
responses = (np.log10(doses + 1) * 2 + rng.normal(0, 0.5, (n, doses.size)))
mean = responses.mean(0)
sem = responses.std(0, ddof=1) / np.sqrt(n)

fig, ax = plt.subplots(figsize=(3.5, 2.625))
ax.errorbar(
    doses, mean, yerr=sem,
    fmt='o',                  # marker
    color=OKABE[2], ecolor=OKABE[2],
    elinewidth=0.8, capsize=2, capthick=0.8,
    markersize=5, markeredgecolor='black', markeredgewidth=0.4,
    label='Compound X',
)
ax.set_xscale('symlog', linthresh=1)   # 0 鍓傞噺淇濈暀鍦ㄨ酱涓?ax.set_xlabel('Dose (渭M)')
ax.set_ylabel('Response (a.u.)')
ax.legend(frameon=False, loc='lower right')

# 鍥炬敞: data = mean 卤 SEM, n = 8 wells per dose.
export_figure(fig, 'figs/06_errbar', formats=['pdf', 'svg', 'png'],
              size_inches=(3.5, 2.625), dpi=300)
```

**鍧?*锛?- `capsize=2`锛堥粯璁?0 鏃舵病鏈?cap锛夛紝鏈?cap 鏇存槗璇?- `symlog` 姣?`log` 鏇撮€傚悎鍖呭惈 0 鐨勫墏閲忚酱锛堥伩鍏?log(0) 鎶ラ敊锛?- 璇樊妫掑彲浠ユ槸涓嶅绉扮殑锛堜紶 `yerr=[lower_err, upper_err]`锛夛紝琛ㄨ揪闈為珮鏂垎甯?
---

## 7. 鍒嗗竷鍥撅紙鐩存柟鍥?/ KDE锛?
**浣曟椂鐢?*锛氱湅鍗曚釜杩炵画鍙橀噺鐨勫垎甯冨舰鎬佲€斺€旀槸鍚﹀绉般€佹槸鍚﹀弻宄般€佹槸鍚﹀亸鎬併€佹槸鍚︽湁 outlier銆?
```python
rng = np.random.default_rng(7)
# 妯℃嫙鍙屽嘲鍒嗗竷
data1 = np.concatenate([rng.normal(0, 1, 200), rng.normal(4, 1, 200)])
# 妯℃嫙鍋忔€佸垎甯?data2 = rng.lognormal(0, 0.5, 400)

fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.8), constrained_layout=True)

# === 鐩存柟鍥?+ KDE 鍙犲姞 ===
ax = axes[0]
ax.hist(data1, bins=30, density=True, alpha=0.55,
        color=OKABE[2], edgecolor='black', linewidth=0.4,
        label='Histogram')
# KDE 鐢?seaborn 鐩存帴鐢诲湪鍚屼竴 ax
sns.kdeplot(data1, ax=ax, color=OKABE[6], linewidth=1.2, label='KDE')
# 鍦ㄥ簳閮ㄥ姞 rug 鏄剧ず姣忎釜鍘熷鐐?sns.rugplot(data1, ax=ax, color='black', height=0.04, alpha=0.4)
ax.set_xlabel('Value'); ax.set_ylabel('Density')
ax.set_title('Bimodal distribution')
ax.legend(frameon=False, fontsize=6)

# === 鍋忔€佸垎甯?+ 涓綅鏁?vs 鍧囧€?===
ax = axes[1]
ax.hist(data2, bins=30, density=True, alpha=0.55,
        color=OKABE[3], edgecolor='black', linewidth=0.4)
sns.kdeplot(data2, ax=ax, color=OKABE[6], linewidth=1.2)
ax.axvline(data2.mean(), color='red', linestyle='--', linewidth=0.8,
           label=f'mean={data2.mean():.2f}')
ax.axvline(np.median(data2), color='black', linestyle=':', linewidth=0.8,
           label=f'median={np.median(data2):.2f}')
ax.set_xlabel('Value (log-normal)'); ax.set_ylabel('Density')
ax.set_title('Right-skewed: mean vs median')
ax.legend(frameon=False, fontsize=6)

export_figure(fig, 'figs/07_distribution', formats=['pdf', 'svg', 'png'],
              size_inches=(7.0, 2.8), dpi=300)
```

**鍧?*锛?- `bins` 澶 鈫?鍣煶锛涘お灏?鈫?骞虫粦杩囧害銆俙bins='auto'` 鏄笉閿欑殑璧风偣
- KDE 鍦ㄦ暟鎹█灏戯紙n<30锛夋椂**涓嶅彲闈?*鈥斺€旂洿鏂瑰浘鏇磋瘹瀹?- 澶氱粍鍙犲姞鍒嗗竷 鈫?鐢?`alpha=0.4` 閫忔槑鑹插潡锛涙洿寤鸿鐢?small multiples 鍒嗛潰鐢?- 鍋忔€佸己鐑?鈫?鍚屾椂鏄剧ず鍧囧€硷紙绾㈣櫄锛夊拰涓綅鏁帮紙榛戠偣锛夎瀹＄浜虹湅鍑哄樊寮?- 鐪嬪埌鍙屽嘲绔嬪埢璀﹁锛氭槸鍚﹀垎缁勭粨鏋勬病鎷嗭紵

---

## 8. 鐩稿叧鎬х煩闃?/ 鏁ｇ偣鐭╅樀

**浣曟椂鐢?*锛氬涓繛缁彉閲忥紙3-20+锛夋兂鐪嬩袱涓ゅ叧绯汇€?*鍙橀噺 鈮?8 鐢?pairplot锛? 8 鐢?heatmap**銆?
### 8a. 鐩稿叧鎬х儹鍔涘浘

```python
# 妯℃嫙 6 鍒楁暟鎹?rng = np.random.default_rng(8)
n = 200
base = rng.normal(0, 1, n)
df = pd.DataFrame({
    'feature_A': base + rng.normal(0, 0.5, n),
    'feature_B': base + rng.normal(0, 0.3, n),
    'feature_C': -base + rng.normal(0, 0.4, n),
    'feature_D': rng.normal(0, 1, n),
    'feature_E': rng.normal(0, 1, n),
    'feature_F': base * 0.5 + rng.normal(0, 0.6, n),
})
corr = df.corr(method='pearson')

# 鍗婄煩闃垫洿鏄撹锛堝绉帮紝鐢讳竴鍗婂氨澶燂級
mask = np.triu(np.ones_like(corr, dtype=bool), k=1)

fig, ax = plt.subplots(figsize=(4.0, 3.5))
sns.heatmap(
    corr, mask=mask,
    cmap='RdBu_r', vmin=-1, vmax=1, center=0,
    annot=True, fmt='.2f', annot_kws={'fontsize': 6},
    cbar_kws={'label': "Pearson's r", 'shrink': 0.7},
    linewidths=0.5, linecolor='white',
    square=True, ax=ax,
)
ax.tick_params(labelsize=6)
ax.set_title('Feature correlations', fontsize=8)

export_figure(fig, 'figs/08a_corr_heatmap', formats=['pdf', 'svg', 'png'],
              size_inches=(4.0, 3.5), dpi=300)
```

### 8b. 鏁ｇ偣鐭╅樀 (pairplot)

```python
# pairplot 閫傚悎 鈮?8 鍒楋紱瓒呰繃灏辩硦
import seaborn as sns
df_sub = df[['feature_A', 'feature_B', 'feature_C', 'feature_D']].copy()
df_sub['group'] = rng.choice(['Ctrl', 'Treat'], n)

g = sns.pairplot(
    df_sub, hue='group',
    palette={'Ctrl': OKABE[2], 'Treat': OKABE[6]},
    plot_kws=dict(s=10, alpha=0.6, edgecolor='black', linewidth=0.2),
    diag_kws=dict(linewidth=0.8),
    height=1.4,           # 姣忎釜瀛愬浘鑻卞鏁帮紱鎬诲昂瀵?鈮?height 脳 n_cols
    aspect=1.0,
)
g.fig.set_size_inches(6.0, 6.0)
for ax in g.axes.flat:
    if ax is not None:
        ax.tick_params(labelsize=6)
        ax.set_xlabel(ax.get_xlabel(), fontsize=7)
        ax.set_ylabel(ax.get_ylabel(), fontsize=7)

export_figure(g.fig, 'figs/08b_pairplot', formats=['pdf', 'svg', 'png'],
              size_inches=(6.0, 6.0), dpi=300)
```

**鍧?*锛?- pairplot 鍙橀噺鏁?> 8 鈫?瀛愬浘灏忎簬 1 in锛岃倝鐪间笉鍙
- 閰?`hue` 鍖哄垎缁勮鏈夋剰涔夛紝鍚﹀垯鎶婂瑙掑垎甯冪湅绯?- 涓婁笁瑙掑拰涓嬩笁瑙掗兘鐢荤浉鍏冲浘 = 淇℃伅鍐椾綑锛涚敤 `mask` 鍙敾涓€鍗?
---

## 9. 澶氶潰鏉跨粍鍚堝浘

**浣曟椂鐢?*锛氫竴绡囪鏂囦竴寮?Figure 閫氬父 2-6 涓瓙鍥撅紱瑕佷繚璇佸瓙鍥惧瓧鍙枫€侀厤鑹层€佸潗鏍囧昂搴︿竴鑷淬€?
```python
fig, axes = plt.subplots(
    2, 2,
    figsize=(7.2, 5.4),                # Nature 鍙屾爮 7.2 in
    constrained_layout=True,           # 姣?tight_layout 鏅鸿兘
)

# === 瀛愬浘 a锛氭姌绾?===
ax = axes[0, 0]
x = np.linspace(0, 10, 50)
ax.plot(x, np.sin(x), color=OKABE[2], label='A')
ax.plot(x, np.cos(x), color=OKABE[6], linestyle='--', label='B')
ax.set_xlabel('Time (s)'); ax.set_ylabel('Signal')
ax.legend(frameon=False, fontsize=6)

# === 瀛愬浘 b锛氭暎鐐?===
ax = axes[0, 1]
ax.scatter(rng.normal(0,1,50), rng.normal(0,1,50),
           c=OKABE[3], s=12, edgecolor='black', linewidth=0.3)
ax.set_xlabel('PC1'); ax.set_ylabel('PC2')

# === 瀛愬浘 c锛氭煴鐘?===
ax = axes[1, 0]
vals = [3.2, 4.5, 2.8]; errs = [0.3, 0.2, 0.4]
ax.bar(['G1','G2','G3'], vals, yerr=errs, capsize=2,
       color=[OKABE[2], OKABE[6], OKABE[3]], edgecolor='black', linewidth=0.5)
ax.set_ylabel('Score')

# === 瀛愬浘 d锛氱绾?===
ax = axes[1, 1]
data_box = [rng.normal(loc, 1, 30) for loc in [0, 0.7, 1.4]]
ax.boxplot(data_box, tick_labels=['G1','G2','G3'],
           patch_artist=True, widths=0.5,
           boxprops=dict(facecolor=OKABE[2], alpha=0.6, linewidth=0.6),
           medianprops=dict(color='black', linewidth=1.0),
           flierprops=dict(marker='o', markersize=2))
ax.set_ylabel('Value')

# 瀛愬浘鏍囩锛歛, b, c, d (Nature 椋庢牸)
for ax, label in zip(axes.flat, ['a', 'b', 'c', 'd']):
    ax.text(-0.20, 1.05, label, transform=ax.transAxes,
            fontsize=9, fontweight='bold', va='top', ha='right')

export_figure(fig, 'figs/09_panels', formats=['pdf', 'svg', 'png'],
              size_inches=(7.2, 5.4), dpi=300, grayscale_preview=True)
```

**鍧?*锛?- 瀛愬浘鏍囩浣嶇疆 `(-0.20, 1.05)` 瑙嗗潗鏍囪酱鏍囩瀹藉害璋冩暣锛涘乏瀵归綈灞呭渚ф晥鏋滄渶绋?- **缁熶竴閰嶈壊**锛氬悓涓€鍙橀噺鍦ㄤ笉鍚屽瓙鍥鹃噷鍚岃壊锛?Condition A 姘歌繙钃濊壊"锛?- **缁熶竴灏哄害**锛氬彲姣旂殑瀛愬浘鍏辩敤 ylim/xlim锛岃瀵规瘮鐩磋
- `constrained_layout=True` 浼樺厛锛涘畠浼氳嚜鍔ㄥ崗璋冨瓙鍥鹃棿璺濆拰澶栭儴 colorbar/legend

---

## 10. Plotly 浜や簰鍥?
**浣曟椂鐢?*锛氳ˉ鍏呮潗鏂欍€佸崥瀹€侀渶瑕?hover 鏁版嵁鐨?web 绔睍绀恒€?*姝ｅ紡鎶曠 PDF 涓嶇敤 plotly**鈥斺€旀姇绋跨郴缁熶笉鎺ュ彈 HTML銆?
```python
import plotly.express as px
import plotly.io as pio

# 涓枃鏀寔
pio.templates.default = 'plotly_white'
common_layout = dict(
    font=dict(family='Noto Sans CJK SC, Source Han Sans, SimHei, Arial',
              size=12),
    title_font_size=14,
)

df = pd.DataFrame({
    'dose': np.repeat([0, 1, 3, 10, 30, 100], 8),
    'response': np.tile(np.arange(8), 6) + np.random.randn(48),
    'group': np.tile(['A', 'B'] * 4, 6),
})
fig = px.scatter(
    df, x='dose', y='response', color='group', symbol='group',
    log_x=True,
    color_discrete_sequence=['#56B4E9', '#D55E00'],     # Okabe-Ito
    template='plotly_white',
    title='鍓傞噺鍝嶅簲鏇茬嚎锛堜氦浜掔増锛?,
)
fig.update_layout(**common_layout)
fig.write_html('figs/10_interactive.html')
fig.write_image('figs/10_interactive.pdf', width=500, height=350)  # 闇€ pip install kaleido
```

**鍧?*锛?- 浜や簰鍥句繚瀛?PDF / SVG 闇€瑕?`kaleido` 鍖咃紙`pip install -U kaleido`锛?- plotly 榛樿鑳屾櫙鐏帮紝鍔?`template='plotly_white'`
- 涓枃瀛椾綋鍦?plotly 閲岄€氳繃 `layout.font.family` 閰嶇疆锛屼笌 matplotlib 鐙珛
