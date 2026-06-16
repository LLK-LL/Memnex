"""
scipilot-figure-skill :: profile_data.py
========================================
Exploratory data analysis for figure planning.

鏈剼鏈槸 scipilot-figure-skill"鎬濊€?缁樺埗"宸ヤ綔娴佺殑绗?1 姝ャ€?璇诲叆 CSV / Excel / DataFrame锛岃緭鍑烘帰绱㈡€у垎鏋愭姤鍛娾€斺€旀瘡鍒楃被鍨嬨€佺己澶辩巼銆?鏍锋湰閲忋€佸垎甯冨舰鎬併€佸紓甯稿€笺€佺浉鍏虫€р€斺€斿苟鍩轰簬杩欎簺浜嬪疄缁欏嚭"寤鸿鍥惧瀷"鎻愮ず銆?
宸ヤ綔娴佷綅缃?
    鐢ㄦ埛缁欐暟鎹?        鈫?profile_data.py      鈫?浣犲湪杩欓噷
        鈫?chart_selection.md   鎸夋暟鎹舰鎬佹煡鍥惧瀷
        鈫?setup_style.py
        鈫?plot
        鈫?check_figure.py

Usage
-----
    from profile_data import profile_data, render_report

    info = profile_data("results.csv", group_cols=["group", "condition"])
    print(render_report(info))

CLI:
    python profile_data.py results.csv
    python profile_data.py results.csv --group group --group condition
    python profile_data.py results.csv --json > profile.json
"""
from __future__ import annotations

import argparse
import io
import json
import math
import os
import sys
import warnings
from typing import Any

import numpy as np
import pandas as pd

# Windows GBK 缁堢榛樿鏃犳硶鎵?unicode 绠ご/鏂瑰ご鎷彿 鈥斺€?寮哄埗璧?UTF-8
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    except Exception:
        pass


# 鏁版嵁绫诲瀷甯搁噺
TYPE_CONTINUOUS = "continuous"
TYPE_CATEGORICAL = "categorical"
TYPE_ORDINAL = "ordinal"
TYPE_DATETIME = "datetime"
TYPE_BOOLEAN = "boolean"
TYPE_TEXT = "text"
TYPE_UNKNOWN = "unknown"


def _detect_column_type(s: pd.Series) -> str:
    """璇嗗埆涓€鍒楃殑鏁版嵁绫诲瀷銆傝鍒欐寜鍙潬鎬ч€掗檷鎺掑簭銆?""
    if pd.api.types.is_datetime64_any_dtype(s):
        return TYPE_DATETIME
    if pd.api.types.is_bool_dtype(s):
        return TYPE_BOOLEAN
    if pd.api.types.is_numeric_dtype(s):
        non_null = s.dropna()
        # 鍏ㄦ槸 0/1 鈬?褰撴垚 boolean
        if non_null.isin({0, 1}).all() and non_null.nunique() <= 2:
            return TYPE_BOOLEAN
        # 鍞竴鍊煎緢灏戜笖閮芥槸鏁存暟 鈬?鍙兘鏄湁搴忓垎绫伙紙濡?Likert 1-5锛?        if non_null.nunique() <= 7 and (non_null % 1 == 0).all():
            return TYPE_ORDINAL
        return TYPE_CONTINUOUS
    if isinstance(s.dtype, pd.CategoricalDtype):
        if s.cat.ordered:
            return TYPE_ORDINAL
        return TYPE_CATEGORICAL
    if pd.api.types.is_object_dtype(s):
        # 灏濊瘯瑙ｆ瀽涓烘椂闂达紙鍓?10 涓潪绌哄€硷級锛屽け璐ヤ篃鏃犳墍璋?        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                pd.to_datetime(s.dropna().iloc[:10], errors="raise")
            return TYPE_DATETIME
        except Exception:
            pass
        non_null = s.dropna()
        nunique = non_null.nunique()
        if nunique == 0:
            return TYPE_UNKNOWN
        # 涓嶅悓鍊兼暟閲忕浉瀵规牱鏈噺寰堝皯 鈬?鍒嗙被
        ratio = nunique / max(len(non_null), 1)
        if nunique <= 30 and ratio < 0.5:
            return TYPE_CATEGORICAL
        return TYPE_TEXT
    return TYPE_UNKNOWN


def _iqr_outliers(s: pd.Series) -> tuple[int, float, float]:
    """鐢?IQR 娉曡繑鍥?(寮傚父鍊兼暟, 涓嬬晫, 涓婄晫)銆?""
    s = s.dropna()
    if len(s) < 4:
        return 0, float("nan"), float("nan")
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return int(((s < lo) | (s > hi)).sum()), float(lo), float(hi)


def _skewness(s: pd.Series) -> float:
    """Fisher鈥揚earson 鍋忓害绯绘暟锛涚┖鎴栧父鏁板垪杩斿洖 nan銆?""
    arr = s.dropna().to_numpy(dtype=float)
    if len(arr) < 3:
        return float("nan")
    mean = arr.mean()
    sd = arr.std(ddof=1)
    if sd == 0:
        return 0.0
    return float(np.mean(((arr - mean) / sd) ** 3))


def _profile_continuous(s: pd.Series) -> dict:
    s = s.dropna()
    if len(s) == 0:
        return {"n": 0}
    out_n, out_lo, out_hi = _iqr_outliers(s)
    skew = _skewness(s)
    return {
        "n": int(len(s)),
        "mean": float(s.mean()),
        "median": float(s.median()),
        "sd": float(s.std(ddof=1)) if len(s) > 1 else 0.0,
        "min": float(s.min()),
        "max": float(s.max()),
        "skewness": skew,
        "skew_label": _label_skew(skew),
        "n_outliers_iqr": out_n,
        "outlier_lo": out_lo,
        "outlier_hi": out_hi,
        "needs_log_axis": _suggest_log_axis(s),
    }


def _label_skew(skew: float) -> str:
    if math.isnan(skew):
        return "unknown"
    a = abs(skew)
    if a < 0.5:
        return "approximately symmetric"
    if a < 1.0:
        return "moderately skewed"
    return "highly skewed"


def _suggest_log_axis(s: pd.Series) -> bool:
    """鑼冨洿璺ㄦ暟涓噺绾?+ 鍏ㄦ 鈬?寤鸿瀵规暟杞淬€?""
    s = s.dropna()
    if (s <= 0).any() or len(s) < 5:
        return False
    return s.max() / max(s.min(), 1e-300) > 100


def _profile_categorical(s: pd.Series) -> dict:
    counts = s.dropna().value_counts()
    return {
        "n": int(s.dropna().shape[0]),
        "n_unique": int(counts.shape[0]),
        "categories": [(str(k), int(v)) for k, v in counts.items()],
        "min_group_n": int(counts.min()) if len(counts) > 0 else 0,
        "max_group_n": int(counts.max()) if len(counts) > 0 else 0,
        "small_groups_flag": bool(len(counts) > 0 and counts.min() < 10),
    }


def _correlation_matrix(df: pd.DataFrame, cont_cols: list[str]) -> dict | None:
    """杩炵画鍒椾箣闂寸殑 Pearson 鐩稿叧锛涗笉瓒充袱鍒楄繑鍥?None銆?""
    if len(cont_cols) < 2:
        return None
    sub = df[cont_cols].dropna()
    if sub.shape[0] < 5:
        return None
    corr = sub.corr(method="pearson")
    pairs: list[dict] = []
    cols = corr.columns.tolist()
    for i, a in enumerate(cols):
        for b in cols[i + 1:]:
            r = float(corr.loc[a, b])
            pairs.append({"a": a, "b": b, "r": r,
                          "magnitude": _label_r(r)})
    pairs.sort(key=lambda x: -abs(x["r"]))
    return {"columns": cols, "matrix": corr.round(3).to_dict(),
            "pairs_sorted": pairs}


def _label_r(r: float) -> str:
    a = abs(r)
    if a < 0.1:
        return "negligible"
    if a < 0.3:
        return "weak"
    if a < 0.5:
        return "moderate"
    if a < 0.7:
        return "strong"
    return "very strong"


def _group_summary(df: pd.DataFrame, group_cols: list[str]) -> dict | None:
    """璁＄畻鍒嗙粍鏍锋湰閲忓垎甯冿紱宓屽/浜ゅ弶鍒嗙粍閮芥敮鎸併€?""
    if not group_cols:
        return None
    gs = df.groupby(group_cols, dropna=False).size()
    return {
        "by": group_cols,
        "n_groups": int(gs.shape[0]),
        "min_n_per_group": int(gs.min()),
        "max_n_per_group": int(gs.max()),
        "median_n_per_group": int(gs.median()),
        "small_groups_flag": bool(gs.min() < 10),
        "tiny_groups_flag": bool(gs.min() < 3),
        "per_group_counts": [(str(idx), int(n)) for idx, n in gs.items()][:20],
    }


def _suggest_charts(info: dict) -> list[str]:
    """鎶婃暟鎹壒寰佺炕璇戞垚"寤鸿鍥惧瀷"鎻愮ず銆傜矖绮掑害鈥斺€旂簿缁嗗喅绛栦粛瑕佹煡 chart_selection.md銆?""
    cols = info["columns"]
    cont = [c for c, m in cols.items() if m["type"] == TYPE_CONTINUOUS]
    cats = [c for c, m in cols.items()
            if m["type"] in (TYPE_CATEGORICAL, TYPE_BOOLEAN, TYPE_ORDINAL)]
    dt = [c for c, m in cols.items() if m["type"] == TYPE_DATETIME]
    group = info.get("group_summary")
    suggestions: list[str] = []

    # 鏃堕棿搴忓垪
    if dt and cont:
        suggestions.append(
            f"鏃堕棿搴忓垪瀛樺湪锛氱敤鎶樼嚎鍥?({dt[0]} 浣?x 杞达紝"
            f"{cont[0]}{'/' + cont[1] if len(cont) > 1 else ''} 浣?y 杞? + 璇樊甯?)

    # 1 涓垎绫?+ 1 涓繛缁細缁忓吀瀵规瘮鍦烘櫙
    if cats and cont:
        if group and group.get("small_groups_flag"):
            suggestions.append(
                f"鍒嗙被 vs 杩炵画锛屽皬鏍锋湰锛堟瘡缁?n<10锛夆啋 "
                "**绠辩嚎鍥?灏忔彁鐞村浘 + stripplot 鍙犲姞鍘熷鐐?*锛?
                "**閬垮厤**鍙敾鍧囧€兼煴鐘跺浘锛屼細鎺╃洊鍒嗗竷銆?)
        else:
            suggestions.append(
                f"鍒嗙被 vs 杩炵画锛屾牱鏈噺鍏呰冻 鈫?绠辩嚎鍥?/ 灏忔彁鐞村浘锛?
                "鎴栧甫璇樊妫掔殑鏌辩姸鍥撅紙璇樊妫掕鏄?SD/SEM/CI锛?)

    # 涓や釜鎴栨洿澶氳繛缁?鈫?鏁ｇ偣鎴栨暎鐐圭煩闃?    if len(cont) >= 2:
        if len(cont) == 2:
            suggestions.append(
                f"涓よ繛缁彉閲?{cont[0]} vs {cont[1]} 鈫?鏁ｇ偣鍥撅紙鍚洖褰掓嫙鍚?+ r 鍊硷級")
        else:
            suggestions.append(
                f"鈮? 涓繛缁彉閲?鈫?鐩稿叧鎬х儹鍔涘浘锛坽cont[:5]}锛夋垨 pairplot 鏁ｇ偣鐭╅樀")

    # 鍗曚釜杩炵画 鈫?鍒嗗竷
    if len(cont) >= 1 and not cats and not dt:
        suggestions.append(
            f"鍗曚釜杩炵画鍙橀噺 {cont[0]} 鈫?鐩存柟鍥?/ KDE / 绠辩嚎鍥剧湅鍒嗗竷")

    # 缁村害杩囪浇 鈫?寤鸿鎷嗗浘
    if len(cats) >= 2 and len(cont) >= 1:
        n_combo = 1
        for cat in cats:
            n_combo *= max(cols[cat].get("n_unique", 1), 1)
        if n_combo > 12:
            suggestions.append(
                f"鍒嗙被缁村害缁勫悎鏁?= {n_combo}锛坽', '.join(cats)} 鍏ㄤ氦鍙夛級锛?
                "**涓€寮犲浘濉炰笉涓?*鈥斺€斿缓璁寜鏌愪竴缁存媶鎴愬闈㈡澘锛屾垨閫夋嫨瀛愰泦銆?)

    # 鍋忓害澶?鈫?鎻愮ず瀵规暟杞?    for c in cont:
        m = cols[c]
        if m.get("needs_log_axis"):
            suggestions.append(
                f"{c} 璺ㄦ暟涓噺绾э紙{m['min']:.3g} ~ {m['max']:.3g}锛夆啋 鐢ㄥ鏁?y 杞?)
        elif m.get("skew_label") == "highly skewed":
            suggestions.append(
                f"{c} 楂樺害鍋忔€侊紙skew={m['skewness']:.2f}锛夆啋 "
                "鑰冭檻瀵规暟鍙樻崲鎴栧皬鎻愮惔鍥句唬鏇垮潎鍊兼煴鍥?)

    if not suggestions:
        suggestions.append("鏁版嵁鐗瑰緛涓嶈冻浠ョ粰鍑虹壒瀹氬缓璁紱鏌?chart_selection.md 鐨勫喅绛栨鏋躲€?)
    return suggestions


def profile_data(source, group_cols: list[str] | None = None) -> dict:
    """
    涓诲叆鍙ｃ€傝鍏ユ暟鎹苟杩斿洖缁撴瀯鍖栫殑鍒嗘瀽鎶ュ憡锛坉ict锛夈€?
    Args:
        source: 鏂囦欢璺緞锛坈sv/xlsx锛夈€乸d.DataFrame銆佹垨瀛楃涓插唴瀹广€?        group_cols: 鍒嗙粍鍒楀悕鍒楄〃锛堝祵濂?浜ゅ弶锛夛紝鐢ㄤ簬鍒嗙粍鏍锋湰閲忕粺璁°€?    Returns:
        dict 鍖呭惈 keys: n_rows / n_cols / columns / correlation /
        group_summary / suggestions / warnings
    """
    if isinstance(source, pd.DataFrame):
        df = source.copy()
        path_label = "<DataFrame>"
    elif isinstance(source, str) and os.path.exists(source):
        ext = os.path.splitext(source)[1].lower()
        if ext in (".xlsx", ".xls"):
            df = pd.read_excel(source)
        elif ext in (".tsv",):
            df = pd.read_csv(source, sep="\t")
        else:
            df = pd.read_csv(source)
        path_label = source
    else:
        raise ValueError(f"Cannot read data from {source!r}")

    group_cols = group_cols or []
    for g in group_cols:
        if g not in df.columns:
            raise ValueError(f"group column {g!r} not in data; "
                             f"available: {df.columns.tolist()}")

    cols_info: dict[str, dict] = {}
    warnings: list[str] = []
    for c in df.columns:
        s = df[c]
        ctype = _detect_column_type(s)
        n_total = len(s)
        n_null = int(s.isnull().sum())
        entry = {
            "type": ctype,
            "n_total": n_total,
            "n_null": n_null,
            "missing_rate": n_null / n_total if n_total else 0.0,
        }
        if entry["missing_rate"] > 0.20:
            warnings.append(
                f"鍒?{c!r} 缂哄け鐜?{entry['missing_rate']:.0%} 鈥?鐢诲浘鍓嶈€冭檻鏄惁濉ˉ銆佸墧闄ゃ€?
                "鎴栧湪鍥炬敞涓氦浠ｃ€?)
        if ctype == TYPE_CONTINUOUS:
            entry.update(_profile_continuous(s))
        elif ctype in (TYPE_CATEGORICAL, TYPE_BOOLEAN, TYPE_ORDINAL):
            entry.update(_profile_categorical(s))
            if entry.get("small_groups_flag"):
                warnings.append(
                    f"鍒?{c!r} 鑷冲皯鏈変竴涓被鍒?n<10 鈥?灏忔牱鏈繀椤诲睍绀哄師濮嬫暟鎹偣锛?
                    "涓嶈鍙敾鍧囧€兼煴鐘跺浘銆?)
        elif ctype == TYPE_DATETIME:
            non_null = pd.to_datetime(s, errors="coerce").dropna()
            if len(non_null) > 0:
                entry["min"] = str(non_null.min())
                entry["max"] = str(non_null.max())
        cols_info[c] = entry

    cont_cols = [c for c, m in cols_info.items() if m["type"] == TYPE_CONTINUOUS]
    correlation = _correlation_matrix(df, cont_cols)

    info = {
        "source": path_label,
        "n_rows": int(df.shape[0]),
        "n_cols": int(df.shape[1]),
        "columns": cols_info,
        "correlation": correlation,
        "group_summary": _group_summary(df, group_cols),
        "warnings": warnings,
    }
    info["suggestions"] = _suggest_charts(info)
    return info


def render_report(info: dict) -> str:
    """鎶?profile_data() 鐨勮緭鍑烘覆鏌撴垚 markdown 椋庢牸鐨勪汉绫诲彲璇绘姤鍛娿€?""
    lines: list[str] = []
    lines.append(f"# Data profile: {info['source']}")
    lines.append(f"")
    lines.append(f"**Shape:** {info['n_rows']} rows 脳 {info['n_cols']} cols")
    lines.append("")

    # 姣忓垪
    lines.append("## Columns")
    lines.append("")
    lines.append("| Column | Type | n | missing | summary |")
    lines.append("|---|---|---|---|---|")
    for c, m in info["columns"].items():
        summary = ""
        if m["type"] == TYPE_CONTINUOUS:
            summary = (f"mean={m.get('mean', 0):.3g}, sd={m.get('sd', 0):.3g}, "
                       f"range=[{m.get('min', 0):.3g}, {m.get('max', 0):.3g}], "
                       f"skew={m.get('skewness', 0):.2f} ({m.get('skew_label')})")
            if m.get("n_outliers_iqr", 0):
                summary += f"; outliers={m['n_outliers_iqr']} (IQR)"
            if m.get("needs_log_axis"):
                summary += "; -> log axis"
        elif m["type"] in (TYPE_CATEGORICAL, TYPE_BOOLEAN, TYPE_ORDINAL):
            cats = m.get("categories", [])[:5]
            cats_str = ", ".join(f"{k}({v})" for k, v in cats)
            more = f" +{m['n_unique']-len(cats)} more" if m["n_unique"] > len(cats) else ""
            summary = f"{m['n_unique']} levels: {cats_str}{more}; min_group_n={m['min_group_n']}"
        elif m["type"] == TYPE_DATETIME:
            summary = f"{m.get('min', '?')} 鈫?{m.get('max', '?')}"
        miss = f"{m['n_null']} ({m['missing_rate']:.0%})" if m["missing_rate"] > 0 else "0"
        lines.append(f"| `{c}` | {m['type']} | {m['n_total']-m['n_null']} | {miss} | {summary} |")
    lines.append("")

    # 鍒嗙粍
    if info.get("group_summary"):
        gs = info["group_summary"]
        lines.append("## Group structure")
        lines.append(f"- Grouped by: `{'`, `'.join(gs['by'])}`")
        lines.append(f"- Number of groups: {gs['n_groups']}")
        lines.append(f"- Group size: min={gs['min_n_per_group']}, "
                     f"median={gs['median_n_per_group']}, max={gs['max_n_per_group']}")
        if gs["tiny_groups_flag"]:
            lines.append("- **WARN**: at least one group has n<3 鈥?statistics unreliable; "
                         "must show all raw points.")
        elif gs["small_groups_flag"]:
            lines.append("- **WARN**: at least one group has n<10 鈥?use box/violin + stripplot "
                         "rather than mean-only bar chart.")
        lines.append("")

    # 鐩稿叧鎬?    if info.get("correlation"):
        corr = info["correlation"]
        lines.append("## Correlations (Pearson, sorted by |r|)")
        for p in corr["pairs_sorted"][:10]:
            lines.append(f"- `{p['a']}` 鈫?`{p['b']}` : r = {p['r']:.3f} ({p['magnitude']})")
        if len(corr["pairs_sorted"]) > 10:
            lines.append(f"- ... +{len(corr['pairs_sorted']) - 10} more pairs")
        lines.append("")

    # 璀﹀憡
    if info["warnings"]:
        lines.append("## Warnings")
        for w in info["warnings"]:
            lines.append(f"- {w}")
        lines.append("")

    # 鍥惧瀷寤鸿
    lines.append("## Chart suggestions (preliminary)")
    for s in info["suggestions"]:
        lines.append(f"- {s}")
    lines.append("")
    lines.append("> 杩欐槸鍩轰簬鏁版嵁褰㈡€佺殑**鍒濇寤鸿**銆傛渶缁堝浘鍨嬮€夋嫨蹇呴』缁撳悎"
                 "**璁鸿瘉鐩爣**锛堜綘鎯宠浠€涔堬級鈥斺€?璇﹁ `references/chart_selection.md`銆?)
    return "\n".join(lines)


def _cli() -> int:
    p = argparse.ArgumentParser(description="scipilot-figure-skill data profiler")
    p.add_argument("source", help="CSV / Excel / TSV file path")
    p.add_argument("--group", action="append", default=[],
                   help="鍒嗙粍鍒楀悕锛堝彲澶氭鎸囧畾褰㈡垚宓屽/浜ゅ弶鍒嗙粍锛?)
    p.add_argument("--json", action="store_true",
                   help="杈撳嚭 JSON 鑰岄潪 markdown 鎶ュ憡")
    args = p.parse_args()

    info = profile_data(args.source, group_cols=args.group)
    if args.json:
        # numpy / pandas 鐨勭被鍨嬪湪 json.dump 閲岃杞?native
        def _default(o):
            if isinstance(o, (np.integer,)):
                return int(o)
            if isinstance(o, (np.floating,)):
                return float(o)
            if isinstance(o, (np.ndarray, pd.Series)):
                return o.tolist()
            return str(o)
        json.dump(info, sys.stdout, ensure_ascii=False, indent=2, default=_default)
        sys.stdout.write("\n")
    else:
        print(render_report(info))
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
