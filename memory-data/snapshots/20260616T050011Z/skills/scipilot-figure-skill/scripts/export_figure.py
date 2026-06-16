"""
scipilot-figure-skill :: export_figure.py
=========================================
Unified figure export to multiple formats at exact final size.

- Vector preferred: PDF / SVG / EPS for line/bar/scatter (lossless, journal-friendly).
- Raster for photos / micrographs: PNG / TIFF at >= 300 DPI; never JPEG for data figures.
- Embeds TrueType fonts (fonttype 42) so journals don't reject Type-3 PDFs.
- Optional grayscale preview to sanity-check colorblind safety.

Usage
-----
    from export_figure import export_figure
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.plot([0,1,2],[3,1,4])

    paths = export_figure(
        fig,
        basename="figs/fig1_main",
        formats=["pdf", "svg", "png"],
        size_inches=(3.5, 2.625),   # 寮哄埗鎴?Nature 鍗曟爮灏哄
        dpi=600,
        grayscale_preview=True,
    )
    # -> ['figs/fig1_main.pdf', 'figs/fig1_main.svg',
    #     'figs/fig1_main.png', 'figs/fig1_main_grayscale.png']

CLI: ``python export_figure.py demo`` 鐢熸垚涓€寮犳紨绀哄浘骞跺鏍煎紡瀵煎嚭銆?"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Iterable

import matplotlib.pyplot as plt


VECTOR_FORMATS = {"pdf", "svg", "eps"}
RASTER_FORMATS = {"png", "tiff", "tif", "jpg", "jpeg"}
SUPPORTED_FORMATS = VECTOR_FORMATS | RASTER_FORMATS


def _ensure_parent(path: str) -> None:
    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)


def export_figure(
    fig,
    basename: str,
    formats: Iterable[str] | None = None,
    dpi: int = 300,
    size_inches: tuple[float, float] | None = None,
    grayscale_preview: bool = False,
    tight: bool = True,
    pad_inches: float = 0.05,
    transparent: bool = False,
) -> list[str]:
    """
    Export a matplotlib Figure to one or more formats at exact final size.

    Args:
        fig: matplotlib Figure object.
        basename: 杈撳嚭璺緞鍓嶇紑锛堜笉鍚墿灞曞悕锛夛紱鍙寘鍚瓙鐩綍锛岃嚜鍔ㄥ垱寤恒€?        formats: list/tuple of extensions, e.g. ['pdf', 'svg', 'png'].
            Default: ['pdf', 'svg', 'png'].
        dpi: raster 鏍煎紡鍒嗚鲸鐜囷紱寤鸿 300锛堟櫘閫氾級/ 600锛圛EEE 绛夛級銆?        size_inches: (width, height) 鑻卞锛涙寚瀹氬悗浼?fig.set_size_inches() 寮哄埗
            鏈€缁堝昂瀵搞€傚己鐑堝缓璁紶鍏モ€斺€斾繚璇佸鍑哄悗涓嶅繀鍦?Word/LaTeX 閲屼簩娆＄缉鏀俱€?        grayscale_preview: 棰濆鐢熸垚涓€寮?_grayscale.png 渚涜壊鐩插畨鍏ㄦ鏌ャ€?        tight: 鏄惁璧?bbox_inches='tight'锛堣鎺夌暀鐧斤級銆?        pad_inches: tight 妯″紡涓嬩繚鐣欑殑杈硅窛锛堣嫳瀵革級銆?        transparent: 閫忔槑鑳屾櫙锛圥PT/娴锋姤鍙兘闇€瑕侊級銆?
    Returns:
        瀹為檯鍐欏嚭鐨勬枃浠惰矾寰勫垪琛ㄣ€?    """
    if formats is None:
        formats = ("pdf", "svg", "png")
    formats = [f.lower().lstrip(".") for f in formats]
    unknown = [f for f in formats if f not in SUPPORTED_FORMATS]
    if unknown:
        raise ValueError(f"Unsupported formats: {unknown}. "
                         f"Supported: {sorted(SUPPORTED_FORMATS)}")

    if size_inches is not None:
        if len(size_inches) != 2:
            raise ValueError("size_inches must be (width, height)")
        fig.set_size_inches(*size_inches)

    # 寮哄埗宓屽叆 TrueType 瀛椾綋锛坒onttype 42锛夛紱澶氬鏈熷垔鏄庣‘鎷掔粷 Type-3 PDF銆?    plt.rcParams["pdf.fonttype"] = 42
    plt.rcParams["ps.fonttype"] = 42
    plt.rcParams["svg.fonttype"] = "none"  # 鏂囨湰浠嶅彲缂栬緫锛屾湡鍒婇€氬父鏇存杩?
    saved: list[str] = []
    for fmt in formats:
        if fmt in {"jpg", "jpeg"}:
            print(f"[scipilot-figure-skill] WARNING: skipping {fmt} 鈥?"
                  "JPEG is lossy and unsuitable for line/text figures.",
                  file=sys.stderr)
            continue
        path = f"{basename}.{fmt}"
        _ensure_parent(path)
        kwargs: dict = {
            "bbox_inches": "tight" if tight else None,
            "pad_inches": pad_inches,
            "transparent": transparent,
        }
        if fmt in RASTER_FORMATS:
            kwargs["dpi"] = dpi
        fig.savefig(path, **kwargs)
        saved.append(path)
        print(f"[scipilot-figure-skill] wrote {path}")

    if grayscale_preview:
        gray_path = _grayscale_from(fig, basename, dpi=dpi)
        if gray_path:
            saved.append(gray_path)
    return saved


def _grayscale_from(fig, basename: str, dpi: int) -> str | None:
    """
    瀵煎嚭鐏板害棰勮鐗堢敤浜庤壊鐩插畨鍏ㄦ鏌ャ€?    浼樺厛鐢?PIL 杞伆搴︼紱鎵句笉鍒?PIL 鏃堕€€鍖栦负閲嶆柊鐢诲浘锛堝叧闂鑹诧級銆?    """
    try:
        from PIL import Image
    except ImportError:
        print("[scipilot-figure-skill] Pillow not available; "
              "grayscale preview skipped.", file=sys.stderr)
        return None

    png_path = f"{basename}.png"
    _ensure_parent(png_path)
    fig.savefig(png_path, dpi=dpi, bbox_inches="tight")

    gray_path = f"{basename}_grayscale.png"
    Image.open(png_path).convert("L").save(gray_path)
    print(f"[scipilot-figure-skill] wrote {gray_path} (grayscale preview)")
    return gray_path


def _demo(out_basename: str) -> None:
    """Generate a small demo figure for quick smoke testing."""
    import numpy as np
    rng = np.random.default_rng(7)
    x = np.linspace(0, 10, 50)
    y1 = np.sin(x) + rng.normal(0, 0.1, x.size)
    y2 = np.cos(x) + rng.normal(0, 0.1, x.size)

    fig, ax = plt.subplots(figsize=(3.5, 2.625))
    ax.plot(x, y1, label="sin", marker="o", markersize=3)
    ax.plot(x, y2, label="cos", marker="s", markersize=3, linestyle="--")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend(frameon=False)

    paths = export_figure(
        fig, out_basename,
        formats=["pdf", "svg", "png"],
        size_inches=(3.5, 2.625),
        dpi=300,
        grayscale_preview=True,
    )
    print("\nDemo done. Files:")
    for p in paths:
        print(f"  {p}")


def _cli() -> int:
    p = argparse.ArgumentParser(description="scipilot-figure-skill figure exporter")
    p.add_argument("cmd", choices=["demo"], help="`demo`: 璺戜竴寮犳紨绀哄浘瀵煎嚭 4 绉嶆牸寮?)
    p.add_argument("--out", default="./scipilot_demo",
                   help="杈撳嚭 basename (榛樿 ./scipilot_demo)")
    args = p.parse_args()
    if args.cmd == "demo":
        _demo(args.out)
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
