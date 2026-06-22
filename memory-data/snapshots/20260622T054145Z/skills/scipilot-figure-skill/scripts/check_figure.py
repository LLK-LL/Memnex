"""
scipilot-figure-skill :: check_figure.py
========================================
Pre-submission figure compliance audit.

閫愭枃浠舵鏌ワ細鏍煎紡锛堢煝閲?vs 浣嶅浘 vs 涓嶅厑璁哥殑 JPEG锛夈€佸儚绱犲昂瀵?DPI銆?鐭㈤噺 PDF 鐨勫瓧浣撳祵鍏ョ被鍨嬶紙蹇呴』 TrueType/Type 42锛夛紝杈撳嚭闂娓呭崟銆?闈炵牬鍧忔€р€斺€斿彧璇汇€佷笉淇敼鍘熷浘銆?
Usage
-----
    from check_figure import check_figure, print_report
    issues, info = check_figure("figs/fig1.pdf", min_dpi=300, target_inches=(3.5, 2.625))
    print_report("figs/fig1.pdf", issues, info)

CLI:
    python check_figure.py figs/fig1.pdf figs/fig2.png --min-dpi 300
    python check_figure.py figs/*.pdf --strict   # 浠绘剰 FAIL 鍗?exit 2
"""
from __future__ import annotations

import argparse
import glob
import os
import sys
from typing import Any

JPEG_FORMATS = {"jpg", "jpeg"}
VECTOR_FORMATS = {"pdf", "svg", "eps"}
RASTER_OK_FORMATS = {"png", "tiff", "tif"}

# Severity 搴忓彿瓒婇珮瓒婁弗閲?SEVERITY = {"INFO": 0, "WARN": 1, "FAIL": 2}


def _ext(path: str) -> str:
    return os.path.splitext(path)[1].lower().lstrip(".")


def _check_raster(path: str, ext: str, min_dpi: int,
                  target_inches: tuple[float, float] | None) -> tuple[list, dict]:
    """浣嶅浘锛圥NG/TIFF/JPEG锛夊悎瑙勬€ф鏌ャ€?""
    issues: list[tuple[str, str]] = []
    info: dict[str, Any] = {"category": "raster", "ext": ext}

    if ext in JPEG_FORMATS:
        issues.append(("FAIL",
                       "JPEG 涓嶉€傚悎绾挎潯/鏂囧瓧绫绘暟鎹浘锛堟湁鎹熷帇缂╋級銆?
                       "鏀圭敤 PDF/SVG锛堢煝閲忥級鎴?PNG/TIFF锛堜綅鍥撅級銆?))

    try:
        from PIL import Image
    except ImportError:
        issues.append(("INFO",
                       "Pillow 鏈畨瑁咃紝璺宠繃鍍忕礌/DPI 妫€鏌ワ細"
                       "pip install Pillow 鍚庡彲鍚敤銆?))
        return issues, info

    try:
        img = Image.open(path)
        info["size_px"] = img.size  # (w, h)
        dpi = img.info.get("dpi")
        info["dpi"] = dpi
    except Exception as e:
        issues.append(("FAIL", f"鏃犳硶璇诲彇鍥惧儚锛歿e}"))
        return issues, info

    if dpi is None:
        issues.append(("WARN",
                       "鏂囦欢鏈祵鍏?DPI 鍏冩暟鎹€傛湡鍒婂線寰€鎸?DPI 鎶樼畻鏈€缁堝昂瀵革紝"
                       "璇风敤 fig.savefig(dpi=300) 鏄惧紡鎸囧畾銆?))
    else:
        dx = dpi[0] if isinstance(dpi, tuple) else dpi
        # PIL roundtrips DPI as float and may give 299.9994 for a value saved
        # at 300; round before compare to absorb that.
        dx_rounded = round(float(dx))
        if dx_rounded < min_dpi:
            issues.append(("FAIL",
                           f"DPI = {dx_rounded} 浣庝簬瑕佹眰鐨?{min_dpi}銆?
                           "閲嶆柊 savefig(dpi=...) 涓€娆°€?))
        if target_inches is not None:
            tw, th = target_inches
            actual_w_in = info["size_px"][0] / float(dx)
            actual_h_in = info["size_px"][1] / float(dx)
            tol = 0.1  # 鑻卞瀹瑰樊
            if abs(actual_w_in - tw) > tol or abs(actual_h_in - th) > tol:
                issues.append((
                    "WARN",
                    f"瀹為檯灏哄 鈮?{actual_w_in:.2f}脳{actual_h_in:.2f} in锛?
                    f"鐩爣 {tw}脳{th} in銆傝鍦ㄧ敾鍥炬椂鐩存帴璁?figsize=({tw}, {th})锛?
                    "涓嶈鍦?Word/LaTeX 閲屼簩娆＄缉鏀俱€?
                ))
    return issues, info


def _check_pdf_fonts(path: str) -> list[tuple[str, str]]:
    """妫€鏌?PDF 鐨勫瓧浣撳祵鍏ョ被鍨嬧€斺€斿瀹舵湡鍒婃嫆鏀?Type 3 (CFF outlines)銆?""
    issues: list[tuple[str, str]] = []
    try:
        from pypdf import PdfReader
    except ImportError:
        try:
            from PyPDF2 import PdfReader  # noqa: F401
        except ImportError:
            issues.append(("INFO",
                           "pypdf / PyPDF2 鏈畨瑁咃紝璺宠繃瀛椾綋宓屽叆绫诲瀷妫€鏌ャ€?
                           "pip install pypdf 鍚庡彲鍚敤銆?))
            return issues

    try:
        reader = PdfReader(path)
    except Exception as e:
        issues.append(("WARN", f"PDF 鏃犳硶瑙ｆ瀽浠ユ鏌ュ瓧浣擄細{e}"))
        return issues

    bad_fonts: list[str] = []
    not_embedded: list[str] = []
    for page in reader.pages:
        try:
            resources = page.get("/Resources")
            if not resources:
                continue
            fonts = resources.get("/Font")
            if not fonts:
                continue
            for fname, fobj in fonts.items():
                font = fobj.get_object()
                subtype = str(font.get("/Subtype", ""))
                base = str(font.get("/BaseFont", "?"))
                descriptor = font.get("/FontDescriptor")
                if descriptor:
                    descriptor = descriptor.get_object()
                    embedded = any(k in descriptor for k in
                                   ("/FontFile", "/FontFile2", "/FontFile3"))
                else:
                    embedded = False
                if "Type3" in subtype:
                    bad_fonts.append(f"{base} ({subtype})")
                elif not embedded and "Type1" not in subtype:
                    not_embedded.append(base)
        except Exception:
            continue
    if bad_fonts:
        issues.append((
            "FAIL",
            f"PDF 涓惈 Type 3 瀛椾綋: {', '.join(set(bad_fonts))[:200]}. "
            "Type 3 瀛椾綋鏀惧ぇ鍚庝細绯婏紝澶氬鏈熷垔鎷掓敹銆?
            "鍦?matplotlib 涓 rcParams['pdf.fonttype'] = 42 閲嶅嚭鍥俱€?
        ))
    if not_embedded:
        issues.append((
            "WARN",
            f"PDF 涓互涓嬪瓧浣撳彲鑳芥湭宓屽叆: {', '.join(set(not_embedded))[:200]}. "
            "瀵艰嚧浠栦汉鐢佃剳鎵撳紑鍙樻垚鏇夸唬瀛椾綋銆?
        ))
    return issues


def _check_svg(path: str) -> list[tuple[str, str]]:
    """SVG 绠€妫€锛氳鍛?base64 宓屽叆鐨勪綅鍥撅紙鐮村潖鐭㈤噺浼樺娍锛夈€?""
    issues: list[tuple[str, str]] = []
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            head = f.read(50000)
    except Exception as e:
        issues.append(("WARN", f"SVG 璇诲け璐? {e}"))
        return issues
    if "data:image/png;base64" in head or "data:image/jpeg;base64" in head:
        issues.append(("WARN",
                       "SVG 涓寘鍚?base64 宓屽叆鐨勪綅鍥锯€斺€斾細涓㈠け鐭㈤噺浼樺娍銆?
                       "妫€鏌ユ槸鍚﹀湪 plot 涓鐢ㄤ簡 imshow 鎴栧浘鍍忚创鍥俱€?))
    return issues


def check_figure(path: str, min_dpi: int = 300,
                 target_inches: tuple[float, float] | None = None
                 ) -> tuple[list[tuple[str, str]], dict]:
    """
    瀹¤涓€寮犲浘銆傝繑鍥?(issues, info)銆?    issues: [(severity, message), ...]; severity 鈭?{INFO, WARN, FAIL}
    info: 鍏冩暟鎹瓧鍏革紙鏍煎紡銆佸儚绱犮€丏PI 绛夛級
    """
    issues: list[tuple[str, str]] = []
    info: dict[str, Any] = {"path": path}

    if not os.path.exists(path):
        return [("FAIL", f"鏂囦欢涓嶅瓨鍦? {path}")], info

    ext = _ext(path)
    info["ext"] = ext
    info["size_bytes"] = os.path.getsize(path)

    if ext in VECTOR_FORMATS:
        info["category"] = "vector"
        if ext == "pdf":
            issues.extend(_check_pdf_fonts(path))
        elif ext == "svg":
            issues.extend(_check_svg(path))
    elif ext in RASTER_OK_FORMATS or ext in JPEG_FORMATS:
        sub_issues, sub_info = _check_raster(path, ext, min_dpi, target_inches)
        issues.extend(sub_issues)
        info.update(sub_info)
    else:
        issues.append(("WARN", f"鏈瘑鍒殑鎵╁睍鍚? .{ext}"))

    return issues, info


def print_report(path: str, issues: list, info: dict) -> str:
    """浠ュ彲璇绘牸寮忔墦鍗颁竴寮犲浘鐨勫璁＄粨鏋滐紝杩斿洖 overall verdict 瀛楃涓层€?""
    print(f"\n--- {path} ---")
    if "category" in info:
        print(f"  category: {info['category']}  ext: {info['ext']}  "
              f"size: {info.get('size_bytes', '?')} B")
    if info.get("size_px"):
        print(f"  pixels: {info['size_px'][0]}x{info['size_px'][1]}  "
              f"dpi: {info.get('dpi')}")

    if not issues:
        print("  [PASS] 鏃犻棶棰樸€?)
        return "PASS"

    max_sev = max(SEVERITY[s] for s, _ in issues)
    verdict = {2: "FAIL", 1: "WARN", 0: "INFO"}[max_sev]
    for severity, msg in sorted(issues, key=lambda x: -SEVERITY[x[0]]):
        print(f"  [{severity}] {msg}")
    print(f"  >>> verdict: {verdict}")
    return verdict


def _cli() -> int:
    p = argparse.ArgumentParser(description="scipilot-figure-skill compliance checker")
    p.add_argument("paths", nargs="+", help="鍥炬枃浠惰矾寰勶紝鍙敤 glob")
    p.add_argument("--min-dpi", type=int, default=300)
    p.add_argument("--width-in", type=float, help="鐩爣瀹藉害(鑻卞)")
    p.add_argument("--height-in", type=float, help="鐩爣楂樺害(鑻卞)")
    p.add_argument("--strict", action="store_true",
                   help="浠绘剰 FAIL 鍗?exit code 2")
    args = p.parse_args()

    target = None
    if args.width_in and args.height_in:
        target = (args.width_in, args.height_in)

    expanded: list[str] = []
    for pat in args.paths:
        m = glob.glob(pat)
        expanded.extend(m if m else [pat])

    any_fail = False
    for path in expanded:
        issues, info = check_figure(path, min_dpi=args.min_dpi, target_inches=target)
        verdict = print_report(path, issues, info)
        if verdict == "FAIL":
            any_fail = True

    print()
    if args.strict and any_fail:
        print("[scipilot-figure-skill] strict mode: at least one FAIL 鈥?exit 2")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
