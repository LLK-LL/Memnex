"""
scipilot-figure-skill :: visual_qa.py
=====================================
鍑哄浘鍚庣殑銆岀▼搴忚嚜妫€銆?銆屾覆鏌撻瑙堛€嶁€斺€旇嚜妫€闂幆鐨勬満鍣ㄩ偅涓€灞傘€?
璁捐鍒嗗伐锛?- **绋嬪簭锛堟湰鑴氭湰锛?* 鎶?*纭畾鎬?*闂锛氱己瀛椾贡鐮併€佹枃瀛楄秺鐣岃鍒囥€佸埢搴︽爣绛鹃噸鍙犮€?- **AI 璇诲浘**锛堣 references/visual_review.md锛夋姄**鎰熺煡鎬?*闂锛氬浘渚嬪帇鏁版嵁銆?  瀛愬浘鏍囩鏄惁瀵归綈銆侀厤鑹茬伆搴﹀彲鍒嗐€佹暣浣撹鎰熴€?
涓ゅ眰涓茶捣鏉ユ墠鏄畬鏁寸殑銆屽嚭鍥?鈫?娓?PNG 鈫?绋嬪簭鑷 + AI 璇诲浘 鈫?鍥炴敼 鈫?鍐嶇湅銆嶉棴鐜€?
鏍稿績鑳藉姏
--------
- ``render_preview(fig_or_path, out_png, dpi)`` 鈥斺€?娓蹭竴寮犱腑鍒嗚鲸鐜?PNG锛?  渚?AI 鐢?Read 宸ュ叿璇诲浘澶嶆牳锛堢煝閲?PDF 娌℃硶鐩存帴"鐪嬪儚绱犻噸鍙?锛屽繀椤诲厛鏍呮牸鍖栵級銆?- ``audit_layout(fig)`` 鈥斺€?杩斿洖 ``[(severity, msg), ...]``锛?  * **缂哄瓧**锛團AIL锛夛細娓叉煋鏃跺悓鏃舵嫤鎴?matplotlib 鐨?warnings 涓?logging 涓ゆ潯
    鍛婅閫氶亾锛屼换涓€鎶?"missing from font" 鍗冲垽瀹氭垚鍥句細鍑烘柟妗?涔辩爜銆?  * **鏂囧瓧瓒婄晫瑁佸垏**锛圵ARN锛夛細Text 鐨?window_extent 瓒呭嚭鐢诲竷杈圭晫銆?  * **鍒诲害鏍囩閲嶅彔**锛圵ARN锛夛細鐩搁偦 tick label 鐨勫寘鍥寸洅姘村钩/鍨傜洿鐩镐氦銆?
severity 绾﹀畾涓?check_figure.py 淇濇寔涓€鑷达細INFO < WARN < FAIL銆?
Usage
-----
    from visual_qa import render_preview, audit_layout, print_report

    fig, ax = plt.subplots()
    ...
    png = render_preview(fig, "figs/_preview.png", dpi=150)  # 缁?AI 璇诲浘
    issues = audit_layout(fig)
    print_report(issues)

CLI:
    python visual_qa.py demo                       # 璺戜竴閬嶈嚜妫€婕旂ず
    python visual_qa.py figs/fig1.png --preview out.png
"""
from __future__ import annotations

import argparse
import io
import logging
import os
import sys
import warnings

import matplotlib.pyplot as plt
import matplotlib.text as mtext


# Windows GBK 缁堢涓?print 涓枃浼?UnicodeEncodeError銆傜敤 reconfigure 鑰岄潪鏇挎崲
# sys.stdout锛氬箓绛夈€佷笉鍒涘缓鏂板璞★紝澶氫釜鑴氭湰涓€璧?import 鏃朵篃涓嶄細鍏抽棴搴曞眰娴併€?if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

SEVERITY = {"INFO": 0, "WARN": 1, "FAIL": 2}
_GLYPH_MARKERS = ("missing from", "Glyph", "findfont")


def _ensure_parent(path: str) -> None:
    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)


class _GlyphLogHandler(logging.Handler):
    """鎷︽埅 matplotlib logger 閲屽叧浜庣己瀛?/ 鎵句笉鍒板瓧浣撶殑璁板綍銆?""

    def __init__(self):
        super().__init__()
        self.messages: list[str] = []

    def emit(self, record):
        msg = record.getMessage()
        if any(m in msg for m in _GLYPH_MARKERS):
            self.messages.append(msg)


def _draw_and_collect_glyph_warnings(fig) -> list[str]:
    """
    娓叉煋涓€娆?figure锛屽悓鏃朵粠 warnings 鍜?logging 涓ゆ潯閫氶亾鏀堕泦缂哄瓧鍛婅銆?
    matplotlib 涓嶅悓鐗堟湰瀵圭己瀛楃殑涓婃姤鏂瑰紡涓嶄竴锛氳€佺増鏈蛋 warnings.warn锛?    鏂扮増鏈蛋 logging銆備袱杈归兘鎸備笂鎵嶄笉浼氭紡銆傛覆鏌撻『渚胯 renderer 灏辩华锛?    渚涘悗缁?window_extent 娴嬮噺浣跨敤銆?    """
    handler = _GlyphLogHandler()
    mpl_logger = logging.getLogger("matplotlib")
    prev_level = mpl_logger.level
    mpl_logger.setLevel(logging.WARNING)
    mpl_logger.addHandler(handler)

    collected: list[str] = []
    try:
        with warnings.catch_warnings(record=True) as wlist:
            warnings.simplefilter("always")
            # 鐢诲埌鍐呭瓨鍗冲彲锛屼笉钀界洏锛沝raw 涔熶細瑙﹀彂缂哄瓧鍛婅
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=100)
            buf.close()
        for w in wlist:
            s = str(w.message)
            if any(m in s for m in _GLYPH_MARKERS):
                collected.append(s)
    finally:
        mpl_logger.removeHandler(handler)
        mpl_logger.setLevel(prev_level)

    collected.extend(handler.messages)
    # 鍘婚噸骞朵繚鎸侀『搴?    seen, uniq = set(), []
    for m in collected:
        if m not in seen:
            seen.add(m)
            uniq.append(m)
    return uniq


def _visible_texts(fig) -> list:
    out = []
    for t in fig.findobj(mtext.Text):
        try:
            if t.get_visible() and t.get_text().strip():
                out.append(t)
        except Exception:
            continue
    return out


def audit_layout(fig, clip_tol_px: float = 2.0, overlap_tol_px: float = 1.0
                 ) -> list[tuple[str, str]]:
    """
    瀵逛竴寮?matplotlib Figure 鍋氱増闈㈣嚜妫€銆傝繑鍥?[(severity, msg), ...]銆?
    妫€娴嬮」锛?        1. 缂哄瓧涔辩爜锛團AIL锛夆€斺€?涓枃/鐗规畩绗﹀彿瀛椾綋鏈懡涓€?        2. 鏂囧瓧瓒婄晫瑁佸垏锛圵ARN锛夆€斺€?鏍囬/杞存爣绛?鏍囨敞瓒呭嚭鐢诲竷銆?        3. 鍒诲害鏍囩閲嶅彔锛圵ARN锛夆€斺€?x/y 杞寸浉閭诲埢搴﹀寘鍥寸洅鐩镐氦銆?
    闈炵牬鍧忔€э細鍙覆鏌撴祴閲忥紝涓嶄慨鏀?fig 鍐呭銆?    """
    issues: list[tuple[str, str]] = []

    # ---- 1. 缂哄瓧锛堝悓鏃惰Е鍙戜竴娆℃覆鏌擄紝璁?renderer 灏辩华锛?---
    glyph_msgs = _draw_and_collect_glyph_warnings(fig)
    if glyph_msgs:
        sample = " | ".join(glyph_msgs[:3])
        issues.append((
            "FAIL",
            f"妫€娴嬪埌缂哄瓧锛屾垚鍥句細鍑虹幇鏂规/涔辩爜锛歿sample[:240]}銆?
            "涓枃鍥捐鍏?setup_style(lang='zh') 閰嶇疆 CJK 瀛椾綋锛?
            "鑻ユ槸璐熷彿鏂规锛岀‘璁?axes.unicode_minus=False銆?
        ))

    try:
        renderer = fig.canvas.get_renderer()
    except Exception:
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()

    W = float(fig.bbox.width)
    H = float(fig.bbox.height)

    # ---- 2. 鏂囧瓧瓒婄晫瑁佸垏 ----
    # 鍒诲害鏍囩鐨勮秺鐣岀敱 constrained_layout / bbox_inches='tight' 鑷姩澶勭悊锛屼笖鍙︽湁
    # 鍒诲害閲嶅彔妫€娴嬭鐩栤€斺€旇繖閲岃烦杩囧畠浠紝鍙洴 title / 杞存爣绛?/ 鏍囨敞杩欑被鐢ㄦ埛鏂囧瓧锛?    # 閬垮厤 constrained_layout 涓嬪埢搴﹁创杈归€犳垚鐨勮鎶ャ€?    tick_ids = set()
    for ax in fig.axes:
        for tl in (*ax.get_xticklabels(), *ax.get_xticklabels(minor=True),
                   *ax.get_yticklabels(), *ax.get_yticklabels(minor=True)):
            tick_ids.add(id(tl))

    clipped: list[str] = []
    for t in _visible_texts(fig):
        if id(t) in tick_ids:
            continue
        try:
            bb = t.get_window_extent(renderer)
        except Exception:
            continue
        if (bb.x0 < -clip_tol_px or bb.y0 < -clip_tol_px
                or bb.x1 > W + clip_tol_px or bb.y1 > H + clip_tol_px):
            txt = t.get_text().strip().replace("\n", " ")
            if txt:
                clipped.append(txt[:24])
    if clipped:
        uniq = list(dict.fromkeys(clipped))[:6]
        issues.append((
            "WARN",
            f"浠ヤ笅鏂囧瓧鍙兘瓒呭嚭鐢诲竷琚鍒囷細{uniq}銆?
            "璺?finalize_figure(fig) 鎴栧鍑烘椂 bbox_inches='tight' 鍏滃簳锛?
            "鏍囬/鏍囩杩囬暱鍙崲琛屾垨缂╃煭銆?
        ))

    # ---- 3. 鍒诲害鏍囩閲嶅彔 ----
    overlap_axes = 0
    for ax in fig.axes:
        if ax.get_subplotspec() is None:
            continue
        if _ticklabels_overlap(ax.get_xticklabels(), renderer,
                               axis="x", tol=overlap_tol_px):
            overlap_axes += 1
            continue
        if _ticklabels_overlap(ax.get_yticklabels(), renderer,
                               axis="y", tol=overlap_tol_px):
            overlap_axes += 1
    if overlap_axes:
        issues.append((
            "WARN",
            f"{overlap_axes} 涓瓙鍥惧瓨鍦ㄥ埢搴︽爣绛鹃噸鍙犮€?
            "x 杞达細ax.tick_params(axis='x', rotation=30) 鎴栧噺灏戝埢搴?缂╃煭鏍囩锛?
            "y 杞达細澧炲ぇ瀛愬浘楂樺害鎴栧噺灏戝埢搴︽暟銆?
        ))

    return issues


def _ticklabels_overlap(labels, renderer, axis: str, tol: float) -> bool:
    """鐩搁偦鍒诲害鏍囩鍖呭洿鐩掓槸鍚︾浉浜ゃ€俛xis='x' 鐪嬫按骞炽€?y' 鐪嬪瀭鐩淬€?""
    boxes = []
    for l in labels:
        try:
            if l.get_visible() and l.get_text().strip():
                boxes.append(l.get_window_extent(renderer))
        except Exception:
            continue
    if len(boxes) < 2:
        return False
    if axis == "x":
        boxes.sort(key=lambda b: b.x0)
        return any(a.x1 - b.x0 > tol for a, b in zip(boxes, boxes[1:]))
    else:
        boxes.sort(key=lambda b: b.y0)
        return any(a.y1 - b.y0 > tol for a, b in zip(boxes, boxes[1:]))


def render_preview(fig_or_path, out_png: str = "_preview.png",
                   dpi: int = 150) -> str:
    """
    娓蹭竴寮?PNG 棰勮渚?AI 璇诲浘銆?
    Args:
        fig_or_path: matplotlib Figure 瀵硅薄锛堣嚜妫€闂幆涓昏矾寰勶級锛屾垨涓€涓凡钀界洏
            鐨勫浘鐗囪矾寰勶紙浣嶅浘鐩存帴杩斿洖锛汸DF 闇€鍙€夌殑 PyMuPDF锛夈€?        out_png: 杈撳嚭 PNG 璺緞銆?        dpi: 棰勮鍒嗚鲸鐜囷紝榛樿 150锛堝 AI 鐪嬫竻鏂囧瓧/閲嶅彔锛屽張涓嶈嚦浜庡お澶э級銆?
    Returns:
        鍙緵 Read 璇诲彇鐨?PNG 璺緞锛堜綅鍥炬潵婧愭椂杩斿洖鍘熻矾寰勶級銆?    """
    if hasattr(fig_or_path, "savefig"):
        _ensure_parent(out_png)
        fig_or_path.savefig(out_png, dpi=dpi, bbox_inches="tight")
        return out_png

    path = str(fig_or_path)
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    if ext in {"png", "tif", "tiff", "jpg", "jpeg", "bmp"}:
        return path
    if ext == "pdf":
        try:
            import fitz  # PyMuPDF, 鍙€?        except ImportError as e:
            raise RuntimeError(
                "鎶?PDF 娓叉垚棰勮闇€瑕?PyMuPDF锛坧ip install pymupdf锛夈€?
                "鑷闂幆鏇存帹鑽愮洿鎺ユ妸 matplotlib Figure 瀵硅薄浼犵粰 render_preview锛?
                "鍦ㄥ鍑哄墠灏卞畬鎴愯鍥惧鏍搞€?
            ) from e
        doc = fitz.open(path)
        pix = doc[0].get_pixmap(dpi=dpi)
        _ensure_parent(out_png)
        pix.save(out_png)
        doc.close()
        return out_png
    raise RuntimeError(f"涓嶆敮鎸佷粠 .{ext} 鐢熸垚棰勮锛涜浼?Figure 瀵硅薄鎴栦綅鍥俱€?)


def print_report(issues: list[tuple[str, str]]) -> str:
    """鎵撳嵃 audit_layout 鐨勭粨鏋滐紝杩斿洖 verdict锛圥ASS/WARN/FAIL锛夈€?""
    if not issues:
        print("  [PASS] 绋嬪簭鑷鏈彂鐜扮己瀛?/ 瑁佸垏 / 鍒诲害閲嶅彔銆?)
        print("  >>> 浠嶉渶 AI 璇诲浘澶嶆牳鎰熺煡鎬ч棶棰橈紙瑙?visual_review.md锛夈€?)
        return "PASS"
    max_sev = max(SEVERITY[s] for s, _ in issues)
    verdict = {2: "FAIL", 1: "WARN", 0: "INFO"}[max_sev]
    for sev, msg in sorted(issues, key=lambda x: -SEVERITY[x[0]]):
        print(f"  [{sev}] {msg}")
    print(f"  >>> verdict: {verdict}锛堜慨瀹屽啀娓蹭竴娆?PNG 璁?AI 璇诲浘澶嶆牳锛?)
    return verdict


def _demo() -> int:
    """鏋勯€犱竴寮犳湁鐗堥潰闂鐨勫浘锛屾紨绀?audit_layout 鑳芥姄鍑烘潵銆?""
    import numpy as np
    rng = np.random.default_rng(1)

    fig, ax = plt.subplots(figsize=(3.0, 2.2))
    cats = [f"very_long_condition_name_{i}" for i in range(12)]
    ax.bar(range(12), rng.random(12))
    ax.set_xticks(range(12))
    ax.set_xticklabels(cats)  # 鏁呮剰涓嶆棆杞?-> x 杞村埢搴﹀繀鐒堕噸鍙?    ax.set_title("An intentionally overlong title that runs off the canvas edge")
    ax.set_ylabel("value")

    print("=== visual_qa demo锛氬涓€寮犲埢鎰忓仛鍧忕増闈㈢殑鍥捐嚜妫€ ===")
    issues = audit_layout(fig)
    print_report(issues)
    out = render_preview(fig, "./visual_qa_demo.png", dpi=120)
    print(f"\n棰勮宸插啓鍑猴細{out}锛堝彲鐢?Read 宸ュ叿璇诲浘澶嶆牳锛?)
    print("娉細缂哄瓧妫€娴嬪彧鍦ㄤ腑鏂囨湭閰嶅瓧浣撶瓑鎯呭喌涓嬫墠浼?FAIL锛涙湰 demo 涓昏灞曠ず瑁佸垏+閲嶅彔銆?)
    return 0


def _cli() -> int:
    p = argparse.ArgumentParser(description="scipilot-figure-skill visual QA")
    p.add_argument("target", nargs="?", help="鍥剧墖璺緞锛涙垨 'demo'")
    p.add_argument("--preview", metavar="OUT.png",
                   help="鎶?target 娓叉垚 PNG 棰勮鍒版璺緞")
    p.add_argument("--dpi", type=int, default=150)
    args = p.parse_args()

    if args.target == "demo" or args.target is None:
        return _demo()

    if args.preview:
        out = render_preview(args.target, args.preview, dpi=args.dpi)
        print(f"[visual_qa] 棰勮锛歿out}")
    else:
        # 瀵瑰凡钀界洏鏂囦欢锛宎udit_layout 闇€瑕?Figure 瀵硅薄锛岃繖閲屽彧鑳芥彁绀?        print("[visual_qa] 瀵瑰凡钀界洏鍥剧墖鍙敮鎸?--preview 娓插浘锛?
              "鐗堥潰鑷 audit_layout 璇峰湪鐢诲浘鑴氭湰閲屽 Figure 瀵硅薄璋冪敤銆?)
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
