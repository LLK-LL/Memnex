"""
scipilot-figure-skill :: layout_tools.py
========================================
鎺掔増瀹夊叏缃?+ 澶氶潰鏉垮瓙鍥剧紪鍙峰榻愩€?
瑙ｅ喅涓ょ被楂橀鎴愬浘闂锛?
1. **瀛愬浘 a/b/c 缂栧彿涔辨斁銆佹í绔栦笉瀵归綈** 鈥斺€?`add_panel_labels()`
   鎶婃瘡涓爣绛鹃敋瀹氬湪鍚勫瓙鍥剧殑 ``axes fraction (0,1)``锛堝乏涓婅锛夛紝鍐嶇粺涓€鏂藉姞
   **鍚屼竴涓?points 鍋忕Щ**銆傜敱浜庡悓涓€鍒楀瓙鍥剧殑宸﹁竟缂?figure-x 鐩稿悓銆佸悓涓€琛屽瓙鍥?   鐨勪笂杈圭紭 figure-y 鐩稿悓锛岀粺涓€鍋忕Щ鍚庢墍鏈夋爣绛?*妯湅涓€鏉＄嚎銆佺珫鐪嬩竴鏉＄嚎**锛?   涓嶄細鍥犱负鍚勫瓙鍥?y 杞村埢搴﹀搴︿笉鍚岃€岄敊浣嶃€?
2. **鏍囬/杞存爣绛捐瑁併€佸浘渚嬪帇鏁版嵁銆佸瓙鍥句簰鐩搁噸鍙?* 鈥斺€?`finalize_figure()`
   鍑哄浘鍓嶅厹搴曞惎鐢?constrained_layout锛堝け璐ュ洖閫€ tight_layout锛夛紝缁熶竴杈硅窛銆?
涓よ€呴兘鏄?浜嬪悗鍏滃簳"宸ュ叿锛氬嵆浣跨粯鍒堕樁娈垫病娉ㄦ剰甯冨眬锛岃窇涓€閬嶄篃鑳芥妸鐗堥潰鏁戝洖鏉ャ€?
Usage
-----
    from layout_tools import add_panel_labels, finalize_figure
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.4))
    # ... 鍦?4 涓瓙鍥句笂鍚勮嚜浣滃浘 ...
    finalize_figure(fig)                 # 鍏堟妸鐗堥潰鐞嗛『
    add_panel_labels(fig, style="nature")  # a b c d锛岃嚜鍔ㄥ榻?
CLI: ``python layout_tools.py demo --out ./panel_demo`` 鐢讳竴寮?2x2 楠岃瘉瀵归綈銆?"""
from __future__ import annotations

import argparse
import string
import sys

import matplotlib.pyplot as plt


# Windows GBK 缁堢涓嬬洿鎺?print 涓枃浼?UnicodeEncodeError銆傜敤 reconfigure 鑰岄潪鏇挎崲
# sys.stdout锛氬箓绛夈€佷笉鍒涘缓鏂板璞★紝澶氫釜鑴氭湰涓€璧?import 鏃朵篃涓嶄細鍏抽棴搴曞眰娴併€?if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


# 瀛愬浘缂栧彿鐨勫嚑绉嶆湡鍒婃儻渚?PANEL_STYLES = {
    "nature": lambda s: s,                    # a  b  c   锛堝皬鍐欏姞绮楋紝Nature/Cell 绯伙級
    "science": lambda s: s,                   # a  b  c
    "ieee": lambda s: f"({s})",               # (a)(b)(c) 锛圛EEE/Elsevier 绯伙級
    "paren": lambda s: f"({s})",              # (a)(b)(c)
    "upper": lambda s: s.upper(),             # A  B  C
    "upper_paren": lambda s: f"({s.upper()})",  # (A)(B)(C)
}


def _letter_sequence(n: int) -> list[str]:
    """鐢熸垚 a, b, ..., z, aa, ab, ... 鐨勬爣绛惧簭鍒椼€?""
    letters = string.ascii_lowercase
    out: list[str] = []
    for i in range(n):
        if i < 26:
            out.append(letters[i])
        else:
            # 绗?27 涓捣鐢?aa, ab... 鍏滃簳锛堣秴杩?26 涓?panel 宸叉瀬缃曡锛?            out.append(letters[i // 26 - 1] + letters[i % 26])
    return out


def _data_axes(fig) -> list:
    """鍙彇鐪熸鐨勭綉鏍煎瓙鍥撅紝鎺掗櫎 colorbar / inset锛堝畠浠病鏈?subplotspec锛夈€?""
    return [ax for ax in fig.axes if ax.get_subplotspec() is not None]


def add_panel_labels(
    fig,
    axes=None,
    labels=None,
    style: str = "nature",
    fontsize=None,
    fontweight: str = "bold",
    x_offset_pt: float = -20.0,
    y_offset_pt: float = 2.0,
    ha: str = "right",
    va: str = "bottom",
    color: str = "black",
):
    """
    缁欏闈㈡澘鍥剧殑姣忎釜瀛愬浘鎵撶粺涓€瀵归綈鐨?a/b/c 缂栧彿銆?
    瀵归綈鍘熺悊锛氭爣绛鹃敋鐐瑰浐瀹氫负鍚勫瓙鍥剧殑 ``axes fraction (0, 1)``锛堝乏涓婅锛夛紝
    鍐嶅姞 **缁熶竴鐨?(x_offset_pt, y_offset_pt) points 鍋忕Щ**銆傚悓鍒楀瓙鍥惧乏杈圭紭
    figure-x 鐩稿悓銆佸悓琛屽瓙鍥句笂杈圭紭 figure-y 鐩稿悓 鈫?鍋忕Щ涓€鑷?鈫?妯珫閮藉榻愩€?    鐢ㄧ墿鐞?points 鍋忕Щ鑰岄潪 axes 姣斾緥鍋忕Щ锛屼繚璇佷笉鍚屽昂瀵稿瓙鍥剧殑鏍囩闂磋窛涓€鑷淬€?
    Args:
        fig: matplotlib Figure銆?        axes: 瑕佹爣娉ㄧ殑 axes 鍒楄〃锛涢粯璁よ嚜鍔ㄥ彇鎵€鏈夌綉鏍煎瓙鍥撅紙鎸夐槄璇婚『搴?            涓娾啋涓嬨€佸乏鈫掑彸鎺掑簭锛夛紝骞舵帓闄?colorbar / inset銆?        labels: 鑷畾涔夋爣绛惧垪琛紱榛樿鎸?style 鐢熸垚 a/b/c...銆?        style: 'nature'|'science'(a b c) | 'ieee'|'paren'((a)(b)(c)) |
            'upper'(A B C) | 'upper_paren'((A)(B)(C))銆?        fontsize: 鏍囩瀛楀彿锛涢粯璁ゅ彇 rcParams['axes.labelsize']銆?        fontweight: 榛樿 'bold'锛堟湡鍒婃儻渚嬪瓙鍥炬爣绛惧姞绮楋級銆?        x_offset_pt: 姘村钩鍋忕Щ(points)锛岃礋鍊?绉诲埌瀛愬浘宸︿晶锛堥粯璁?-20锛?            绾﹁鏍囩钀藉湪 y 杞存爣绛惧渚т笂鏂癸級銆?        y_offset_pt: 鍨傜洿鍋忕Щ(points)锛屾鍊?涓婄Щ锛堥粯璁?+2锛夈€?        ha, va: 鏍囩瀵归綈鏂瑰紡锛涢粯璁ゅ彸涓嬭瀵归綈鍒板亸绉荤偣銆?        color: 鏍囩棰滆壊銆?
    Returns:
        鏀剧疆鐨?Text/Annotation 瀵硅薄鍒楄〃锛堜究浜庤皟鐢ㄦ柟鍐嶅井璋冧綅缃級銆?    """
    if axes is None:
        axes = _data_axes(fig)
        # 鎸夐槄璇婚『搴忔帓搴忥細y1 瓒婂ぇ瓒婇潬涓婃帓鍦ㄥ墠锛屽悓鎺掓寜 x0 浠庡乏鍒板彸
        axes = sorted(
            axes,
            key=lambda ax: (-round(ax.get_position().y1, 3),
                            round(ax.get_position().x0, 3)),
        )
    axes = list(axes)
    n = len(axes)
    if n == 0:
        return []

    if labels is None:
        fmt = PANEL_STYLES.get(style)
        if fmt is None:
            raise ValueError(
                f"Unknown panel style: {style!r}. "
                f"Choose from {sorted(PANEL_STYLES)}"
            )
        labels = [fmt(s) for s in _letter_sequence(n)]
    elif len(labels) < n:
        raise ValueError(
            f"鎻愪緵浜?{len(labels)} 涓?labels 浣嗘湁 {n} 涓瓙鍥鹃渶瑕佹爣娉ㄣ€?
        )

    if fontsize is None:
        fontsize = plt.rcParams.get("axes.labelsize", 9)

    placed = []
    for ax, lab in zip(axes, labels):
        t = ax.annotate(
            lab,
            xy=(0, 1), xycoords="axes fraction",
            xytext=(x_offset_pt, y_offset_pt), textcoords="offset points",
            fontsize=fontsize, fontweight=fontweight, color=color,
            ha=ha, va=va,
            annotation_clip=False,   # 鍏抽敭锛氬厑璁告爣绛剧敾鍦?axes 杈圭晫涔嬪涓嶈瑁?        )
        placed.append(t)
    return placed


def finalize_figure(fig, prefer: str = "constrained", verbose: bool = False) -> str:
    """
    鍑哄浘鍓嶅厹搴曠悊椤虹増闈細鍑忓皯鏍囬/杞存爣绛捐瑁併€佸浘渚嬪帇鏁版嵁銆佸瓙鍥句簰鐩搁噸鍙犮€?
    浼樺厛鐢?constrained_layout锛坢atplotlib 鑷€傚簲鎺掔増寮曟搸锛夛紝澶辫触鍐嶅洖閫€
    tight_layout锛岄兘澶辫触鍒欎笉鍔ㄣ€?*寤鸿鍏堣皟鏈嚱鏁板啀 add_panel_labels**鈥斺€?    鐗堥潰瀹氫笅鏉ュ悗瀛愬浘浣嶇疆鎵嶇ǔ瀹氥€?
    Args:
        fig: matplotlib Figure銆?        prefer: 'constrained'锛堥粯璁わ級| 'tight'銆?        verbose: True 鏃舵墦鍗板疄闄呴噰鐢ㄧ殑绛栫暐銆?
    Returns:
        瀹為檯閲囩敤鐨勭瓥鐣ワ細'constrained' | 'tight' | 'none'銆?    """
    used = "none"
    if prefer == "constrained":
        try:
            fig.set_layout_engine("constrained")
            fig.canvas.draw()   # 瑙﹀彂涓€娆″竷灞€璁＄畻锛岃瀛愬浘浣嶇疆钀藉畾
            used = "constrained"
        except Exception:
            used = "none"
    if used == "none":
        try:
            with _suppress_tight_warnings():
                fig.tight_layout()
            used = "tight"
        except Exception:
            used = "none"
    if verbose:
        print(f"[layout_tools] finalize_figure -> {used}")
    return used


class _suppress_tight_warnings:
    """tight_layout 鍦ㄦ煇浜涚粍鍚堜笅浼氬彂 UserWarning锛涢潤榛樹箣锛屼笉褰卞搷缁撴灉銆?""

    def __enter__(self):
        import warnings
        self._cm = warnings.catch_warnings()
        self._cm.__enter__()
        warnings.simplefilter("ignore")
        return self

    def __exit__(self, *exc):
        return self._cm.__exit__(*exc)


def _demo(out_basename: str) -> None:
    """鐢讳竴寮?2x2 婕旂ず鍥撅細鍒绘剰璁╁悇瀛愬浘 y 杞撮噺绾т笉鍚岋紝楠岃瘉鏍囩浠嶆í绔栧榻愩€?""
    import numpy as np
    rng = np.random.default_rng(0)

    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.4))
    # 宸︿笂锛氭櫘閫氶噺绾?    axes[0, 0].plot(np.arange(10), rng.normal(0, 1, 10), marker="o")
    axes[0, 0].set_ylabel("score")
    # 鍙充笂锛氳秴澶ч噺绾э紙y 杞村埢搴︽暟瀛楀緢瀹斤紝鏈€鑰冮獙瀵归綈锛?    axes[0, 1].plot(np.arange(10), rng.normal(0, 1, 10) * 1e6, marker="s")
    axes[0, 1].set_ylabel("count")
    # 宸︿笅锛氳礋鍊?+ 闀挎爣绛?    axes[1, 0].bar(np.arange(5), rng.normal(0, 1, 5))
    axes[1, 0].set_ylabel("螖 expression (a.u.)")
    axes[1, 0].set_xlabel("condition")
    # 鍙充笅锛氬皬鏁?    axes[1, 1].scatter(rng.random(20), rng.random(20))
    axes[1, 1].set_ylabel("p")
    axes[1, 1].set_xlabel("x")

    used = finalize_figure(fig, verbose=True)
    labels = add_panel_labels(fig, style="nature")

    png = f"{out_basename}.png"
    fig.savefig(png, dpi=150, bbox_inches="tight")
    print(f"[layout_tools] layout={used}, labels={[t.get_text() for t in labels]}")
    print(f"[layout_tools] wrote {png}")
    print("鑲夌溂/AI 澶嶆牳锛歛/b 椤堕儴搴旂瓑楂橈紝a/c 宸︾紭搴旂瓑瀹解€斺€斿嵆妯珫瀵归綈銆?)


def _cli() -> int:
    p = argparse.ArgumentParser(description="scipilot-figure-skill layout tools")
    p.add_argument("cmd", choices=["demo"],
                   help="`demo`: 鐢讳竴寮?2x2 楠岃瘉瀛愬浘鏍囩瀵归綈")
    p.add_argument("--out", default="./panel_demo", help="杈撳嚭 basename")
    args = p.parse_args()
    if args.cmd == "demo":
        _demo(args.out)
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
