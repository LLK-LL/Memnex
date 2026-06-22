"""
scipilot-figure-skill :: setup_style.py
=======================================
Publication-grade matplotlib / seaborn style configuration.

搴旂敤鍑虹増绾ф牱寮忛璁俱€傛敮鎸?nature / ieee / science / general 鍥涚鏈熷垔棰勮锛?鏀寔涓嫳鏂囷紙lang='zh'/'en'锛夛紝涓枃妯″紡鎸変紭鍏堢骇鑷姩鏌ユ壘
Noto Sans CJK SC > Source Han Sans SC > SimHei > Microsoft YaHei
骞朵慨姝ｈ礋鍙锋覆鏌撱€係ciencePlots 鍙€夆€斺€旇浜嗗氨鐢紝娌¤鍥為€€鍒板唴缃瓑鏁堥璁俱€?
Usage
-----
    from setup_style import setup_style

    # Nature 鍗曟爮鑻辨枃鍥?    setup_style(journal='nature', lang='en')

    # 涓枃鏈熷垔閫氱敤
    setup_style(journal='general', lang='zh')

    # 鍏抽棴 SciencePlots 寮哄埗鐢ㄥ唴缃璁?    setup_style(journal='ieee', use_sciplots=False)

CLI: ``python setup_style.py --list-fonts`` 鍒楀嚭鍙敤 CJK 瀛椾綋銆?"""
from __future__ import annotations

import argparse
import sys
import warnings

import matplotlib
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt


# 鏈熷垔棰勮锛歠igsize 鍗曚綅涓鸿嫳瀵革紝瀵瑰簲璇ユ湡鍒婂崟鏍忔爣绉板搴?# Nature: 89mm = 3.5 in  鍙屾爮: 183mm = 7.2 in
# Science: 涓?Nature 鎺ヨ繎
# IEEE: 鍗曟爮 3.5 in, 鍙屾爮 7.16 in
JOURNAL_PRESETS = {
    "nature": {
        "figure.figsize": (3.5, 2.625),  # 4:3 ratio @ 89mm
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 7,
        "axes.labelsize": 8,
        "axes.titlesize": 8,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "legend.fontsize": 7,
        "lines.linewidth": 1.0,
        "lines.markersize": 4,
        "axes.linewidth": 0.6,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.minor.width": 0.4,
        "ytick.minor.width": 0.4,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    },
    "science": {
        "figure.figsize": (3.5, 2.625),
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 7,
        "axes.labelsize": 7,
        "axes.titlesize": 8,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "legend.fontsize": 6,
        "lines.linewidth": 1.0,
        "lines.markersize": 4,
        "axes.linewidth": 0.6,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    },
    "ieee": {
        "figure.figsize": (3.5, 2.5),
        "figure.dpi": 150,
        "savefig.dpi": 600,
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
        "font.size": 8,
        "axes.labelsize": 8,
        "axes.titlesize": 9,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "legend.fontsize": 7,
        "lines.linewidth": 1.0,
        "lines.markersize": 4,
        "axes.linewidth": 0.7,
        "axes.grid": False,
        "axes.spines.top": True,
        "axes.spines.right": True,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    },
    "general": {
        "figure.figsize": (5.0, 3.5),
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 9,
        "axes.labelsize": 10,
        "axes.titlesize": 11,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "lines.linewidth": 1.2,
        "lines.markersize": 5,
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    },
}

# 涓枃瀛椾綋浼樺厛绾у垪琛紙鎸夊彲鐢ㄦ€?+ 鏈熷垔鎺ュ彈搴︽帓搴忥級
CJK_FONT_PRIORITY = [
    "Noto Sans CJK SC",
    "Noto Sans SC",
    "Source Han Sans SC",
    "Source Han Sans CN",
    "SimHei",
    "Microsoft YaHei",
    "PingFang SC",
    "Heiti SC",
    "WenQuanYi Zen Hei",
    "Arial Unicode MS",
]

CJK_SERIF_PRIORITY = [
    "Noto Serif CJK SC",
    "Noto Serif SC",
    "Source Han Serif SC",
    "Source Han Serif CN",
    "SimSun",
    "STSong",
    "Songti SC",
]

CJK_INSTALL_HINT = """\
鎵句笉鍒颁换浣曚腑鏂囧瓧浣撱€傝瀹夎 Noto CJK 瀛椾綋涔嬩竴锛?
  Linux:    sudo apt install fonts-noto-cjk    # Debian/Ubuntu
            sudo dnf install google-noto-sans-cjk-fonts  # Fedora/RHEL
  macOS:    brew install --cask font-noto-sans-cjk-sc
            鎴栦笅杞? https://github.com/notofonts/noto-cjk/releases
  Windows:  涓嬭浇 https://github.com/notofonts/noto-cjk/releases
            瑙ｅ帇鍚庡彸閿?.ttf/.otf 鏂囦欢 -> "涓烘墍鏈夌敤鎴峰畨瑁?

鎴栬€呭垪鍑哄綋鍓嶅凡瀹夎鐨勪腑鏂囧瓧浣擄細
  python setup_style.py --list-fonts
"""


def _available_fonts() -> set[str]:
    """杩斿洖 matplotlib 宸茬储寮曠殑鍏ㄩ儴瀛椾綋鍚嶉泦鍚堛€?""
    return {f.name for f in fm.fontManager.ttflist}


def list_cjk_fonts() -> list[str]:
    """杩斿洖绯荤粺涓婂彲鐢ㄧ殑 CJK 瀛椾綋锛堟寜浼樺厛绾ф帓搴忥級銆?""
    available = _available_fonts()
    hits = []
    for f in CJK_FONT_PRIORITY + CJK_SERIF_PRIORITY:
        if f in available and f not in hits:
            hits.append(f)
    # 棰濆鍋氫竴娆″寘鍚腑鏂囧叧閿瘝鐨勬壂鎻忥紝鎹曡幏闈炴爣鍑嗗懡鍚嶇殑涓枃瀛椾綋
    for f in available:
        lower = f.lower()
        if any(k in lower for k in ("cjk", "han", "songti", "yahei", "simhei", "simsun")):
            if f not in hits:
                hits.append(f)
    return hits


def configure_chinese_fonts(serif_for_zh: bool = False) -> str:
    """
    鑷姩妫€娴嬪苟閰嶇疆涓枃瀛椾綋锛涘悓鏃朵慨姝ｈ礋鍙锋覆鏌撱€?
    Args:
        serif_for_zh: True 鏃朵紭鍏堥€夌敤琛嚎涓枃瀛椾綋锛堝畫浣撶被锛夛紝鐢ㄤ簬涓枃鏈熷垔
            "瀹嬩綋姝ｆ枃 + Times New Roman 鏁板瓧" 鐨勬贩鎺掔害瀹氥€?    Returns:
        瀹為檯閫夌敤鐨勪腑鏂囧瓧浣撳悕銆?    Raises:
        RuntimeError: 绯荤粺鏈畨瑁呬换浣曡瘑鍒埌鐨勪腑鏂囧瓧浣撱€?    """
    available = _available_fonts()
    priority = CJK_SERIF_PRIORITY + CJK_FONT_PRIORITY if serif_for_zh else CJK_FONT_PRIORITY

    chosen = None
    for f in priority:
        if f in available:
            chosen = f
            break

    if chosen is None:
        # 鍏滃簳锛氭壂鍖呭惈 cjk/han 绛夊叧閿瓧鐨勫瓧浣?        for f in available:
            lower = f.lower()
            if any(k in lower for k in ("cjk", "han", "song", "hei", "yahei", "kaiti")):
                chosen = f
                break

    if chosen is None:
        raise RuntimeError(CJK_INSTALL_HINT)

    # 涓枃鏈熷垔甯歌姹備腑鏂?+ Times New Roman 娣锋帓锛氫腑鏂囪蛋涓枃瀛椾綋锛岃タ鏂囪蛋 Times
    plt.rcParams["font.family"] = ["sans-serif"] if not serif_for_zh else ["serif"]
    if serif_for_zh:
        plt.rcParams["font.serif"] = [chosen, "Times New Roman", "Times", "DejaVu Serif"]
    else:
        plt.rcParams["font.sans-serif"] = [chosen, "Arial", "Helvetica", "DejaVu Sans"]
    # 淇璐熷彿 unicode minus 鍦ㄦ煇浜涗腑鏂囧瓧浣撻噷娓叉煋鎴愭柟妗嗙殑闂
    plt.rcParams["axes.unicode_minus"] = False
    return chosen


def _try_sciencplots(journal: str) -> bool:
    """If SciencePlots is installed, apply its style stack; otherwise return False."""
    try:
        import scienceplots  # noqa: F401
    except ImportError:
        return False

    # SciencePlots 椋庢牸鏍堬細鍩虹 + 鏈熷垔鍙樹綋
    stack = ["science"]
    if journal == "nature":
        stack.append("nature")
    elif journal == "ieee":
        stack.append("ieee")
    # 鍏虫帀 LaTeX 娓叉煋閬垮厤鐜缂?LaTeX 鏃跺穿婧冿紱涓枃妯″紡蹇呴』鍏?    stack.append("no-latex")
    try:
        plt.style.use(stack)
        return True
    except OSError as e:
        warnings.warn(f"SciencePlots style stack failed: {e}; fallback to builtin.")
        return False


def setup_style(
    journal: str = "general",
    lang: str = "en",
    use_sciplots: bool = True,
    serif_for_zh: bool = False,
    constrained_layout: bool = True,
) -> dict:
    """
    搴旂敤鍑虹増绾ф牱寮忛璁俱€?
    Args:
        journal: 'nature' | 'science' | 'ieee' | 'general'
        lang: 'en' | 'zh' 鈥?涓枃妯″紡鑷姩閰嶇疆涓枃瀛椾綋骞朵慨姝ｈ礋鍙?        use_sciplots: 浼樺厛灏濊瘯 SciencePlots锛涗笉鍙敤鍒欏洖閫€鍒板唴缃璁?        serif_for_zh: 涓枃妯″紡涓嬩娇鐢ㄥ畫浣撶被琛嚎瀛椾綋锛堜腑鏂囨湡鍒婂父绾﹀畾锛?        constrained_layout: 榛樿 True鈥斺€斿叏灞€寮€鍚?constrained_layout 鑷€傚簲鎺掔増锛?            浠庢簮澶村噺灏戞爣棰?杞存爣绛捐瑁併€佸浘渚嬪帇鏁版嵁銆佸瓙鍥句簰鐩搁噸鍙犮€傞渶瑕佹墜鍔?            subplots_adjust 鎴栨煇浜?colorbar 鍐欐硶鏃跺彲浼?False 鍏抽棴銆?    Returns:
        dict 鍖呭惈 keys: journal / lang / sciplots_used / cjk_font / constrained_layout
    """
    if journal not in JOURNAL_PRESETS:
        raise ValueError(f"Unknown journal preset: {journal}. "
                         f"Choose from {sorted(JOURNAL_PRESETS)}")

    sciplots_used = False
    if use_sciplots:
        sciplots_used = _try_sciencplots(journal)

    # 鍐呯疆棰勮濮嬬粓鍦?SciencePlots 涔嬩笂瑕嗙洊涓€閬嶏紝纭繚鍏抽敭鍙傛暟锛坒onttype銆佸瓧鍙凤級钀藉疄
    plt.rcParams.update(JOURNAL_PRESETS[journal])

    # 榛樿寮€鍚嚜閫傚簲鎺掔増锛氫粠婧愬ご鍑忓皯鏂囧瓧閬洊 / 瑁佸垏 / 瀛愬浘閲嶅彔
    plt.rcParams["figure.constrained_layout.use"] = constrained_layout

    # 鍏ㄦā寮忛粯璁や慨姝ｈ礋鍙凤細閬垮厤鎵€閫夊瓧浣撶己 U+2212 鏃惰礋鍙锋覆鏌撴垚鏂规锛堜竴绉嶄贡鐮侊級銆?    # 鐢?ASCII hyphen-minus 浠ｆ浛鐪熷噺鍙凤紝鍑犱箮鎵€鏈夊瓧浣撻兘鍚紝鏈€绋冲Ε銆?    plt.rcParams["axes.unicode_minus"] = False

    cjk_font = None
    if lang == "zh":
        cjk_font = configure_chinese_fonts(serif_for_zh=serif_for_zh)
    elif lang != "en":
        raise ValueError(f"lang must be 'en' or 'zh', got {lang!r}")

    return {
        "journal": journal,
        "lang": lang,
        "sciplots_used": sciplots_used,
        "cjk_font": cjk_font,
        "constrained_layout": constrained_layout,
    }


def _cli() -> int:
    p = argparse.ArgumentParser(description="scipilot-figure-skill style setup")
    p.add_argument("--list-fonts", action="store_true",
                   help="鍒楀嚭褰撳墠绯荤粺涓婂彲鐢ㄧ殑 CJK 瀛椾綋")
    p.add_argument("--test", action="store_true",
                   help="搴旂敤棰勮骞舵墦鍗?rcParams 鍏抽敭鍊?)
    p.add_argument("--journal", default="general",
                   choices=list(JOURNAL_PRESETS))
    p.add_argument("--lang", default="en", choices=["en", "zh"])
    p.add_argument("--no-sciplots", action="store_true")
    p.add_argument("--serif-zh", action="store_true")
    args = p.parse_args()

    if args.list_fonts:
        fonts = list_cjk_fonts()
        if fonts:
            print("宸叉娴嬪埌鐨?CJK 瀛椾綋锛堟寜浼樺厛绾ф帓搴忥級锛?)
            for f in fonts:
                print(f"  - {f}")
        else:
            print("鏈娴嬪埌浠讳綍 CJK 瀛椾綋銆?)
            print(CJK_INSTALL_HINT)
        return 0

    if args.test:
        info = setup_style(journal=args.journal, lang=args.lang,
                           use_sciplots=not args.no_sciplots,
                           serif_for_zh=args.serif_zh)
        print(f"applied: {info}")
        for k in ("figure.figsize", "font.family", "font.size",
                  "axes.labelsize", "pdf.fonttype", "axes.unicode_minus"):
            print(f"  {k} = {plt.rcParams[k]!r}")
        return 0

    p.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
