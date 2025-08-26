#!/usr/bin/env python3
import os, sys, csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
MASTERS = ASSETS / "masters"
OUT = ASSETS / "icons"
CSV_PATH = ROOT / "strategy_icon_variant_matrix.csv"

TOKENS = {
    "paper": "#FFFFFF",
    "slate_950": "#060607",
    "brand_orange": "#FF6A00",
    "ink": "#000000",
    "copper": "#B87333",
    "burnt_orange": "#CC5500",
    "matte": "#333333",
    "embossed": "#F5F5F5"
}

FINISH_COLORS = {
    "flat-orange": TOKENS["brand_orange"],
    "matte-carbon": TOKENS["matte"],
    "satin-black": TOKENS["ink"],
    "burnt-orange": TOKENS["burnt_orange"],
    "copper-foil": TOKENS["copper"],
    "embossed-paper": TOKENS["embossed"]
}

def pick_master(size_px: int) -> Path:
    return MASTERS / ("strategy_icon_micro.svg" if size_px <= 32 else "strategy_icon_standard.svg")

def bake_svg(master_svg: str, mode: str, finish: str) -> str:
    bg = TOKENS["paper"] if mode == "light" else TOKENS["slate_950"]
    fg = FINISH_COLORS.get(finish, TOKENS["brand_orange"])
    svg = master_svg.replace("#FF6A00", bg)   # replace background rect
    svg = svg.replace("#FFFFFF", fg)          # replace icon shapes
    return svg

def maybe_export_png(svg_bytes: bytes, out_png: Path, size_px: int):
    try:
        import cairosvg
        out_png.parent.mkdir(parents=True, exist_ok=True)
        cairosvg.svg2png(bytestring=svg_bytes, write_to=str(out_png), output_width=size_px, output_height=size_px)
        return True
    except Exception as e:
        return False

def main():
    if not CSV_PATH.exists():
        print(f"[error] Missing CSV matrix at {CSV_PATH}")
        sys.exit(1)

    import csv
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    generated = 0
    png_count = 0
    for r in rows:
        mode = r["Mode"]
        finish = r["Finish"]
        size = int(r["Size (px)"])
        context = r["Context"]
        filename = r.get("Filename") or f"strategy_icon-{mode}-{finish}-{size}px.png"

        master_path = pick_master(size)
        if not master_path.exists():
            print(f"[warn] Master not found: {master_path}")
            continue

        master_svg = master_path.read_text(encoding="utf-8")
        baked_svg = bake_svg(master_svg, mode, finish)

        folder = OUT / mode / finish / f"{size}px" / context
        folder.mkdir(parents=True, exist_ok=True)

        svg_path = folder / (Path(filename).stem + ".svg")
        svg_path.write_text(baked_svg, encoding="utf-8")

        png_ok = maybe_export_png(baked_svg.encode("utf-8"), folder / Path(filename).name, size)
        if png_ok:
            png_count += 1

        generated += 1

    print(f"[done] Generated {generated} SVG variants. PNG exports: {png_count} (requires cairosvg).")

if __name__ == "__main__":
    main()
