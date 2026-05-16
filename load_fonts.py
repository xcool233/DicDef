from pathlib import Path
from typing import Any, TypeAlias
import subprocess

from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont, ImageFont as ImageFontType

font_types: TypeAlias = FreeTypeFont | ImageFontType

# Noto Sans candidates (broad Unicode / IPA coverage)
_NOTO_CANDIDATES: list[str] = [
    "/usr/share/fonts/google-noto/NotoSans-Regular.ttf",             # Fedora / Bazzite
    "/usr/share/fonts/opentype/noto/NotoSans-Regular.otf",           # Fedora alt
    "/usr/share/fonts/noto/NotoSans-Regular.ttf",                    # Fedora alt
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",           # Debian / Ubuntu
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",               # universal fallback
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "C:\\Windows\\Fonts\\arial.ttf",                                  # Windows
]


def _fc_match(family: str) -> str | None:
    """Use fc-match to find a font file by family name (Linux only)."""
    try:
        result = subprocess.run(
            ["fc-match", "--format=%{file}", family],
            capture_output=True, text=True, timeout=2
        )
        path = result.stdout.strip()
        if path and Path(path).exists():
            return path
    except Exception:
        pass
    return None


def _try_load(path: str | None, size: int) -> font_types | None:
    """Return a FreeTypeFont if the file exists and Pillow can open it."""
    if path and Path(path).expanduser().exists():
        try:
            return ImageFont.truetype(str(path), size)
        except Exception:
            pass
    return None


def _fallback_main(size: int) -> font_types:
    """Try common system fonts, then fc-match, finally PIL bitmap default."""
    candidates: list[str] = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/google-noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/opentype/noto/NotoSans-Regular.otf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "arial.ttf",
    ]
    for cand in candidates:
        font = _try_load(cand, size)
        if font:
            print(f"[fonts] Loaded fallback main font: {cand}")
            return font

    for family in ("sans-serif", "DejaVu Sans", "Liberation Sans"):
        path = _fc_match(family)
        if path:
            font = _try_load(path, size)
            if font:
                print(f"[fonts] Loaded fc-match font ({family}): {path}")
                return font

    print("[fonts] WARNING: No TrueType font found — text will render as tiny bitmaps.")
    print("[fonts]   Fix: sudo dnf install dejavu-sans-fonts  OR pass --font /path/to/font.ttf")
    return ImageFont.load_default()


def _fallback_ipa(size: int, main_font_path: str | None) -> font_types:
    """IPA font fall-backs (prefer fonts with broad Unicode / IPA coverage)."""
    candidates: list[str | None] = [
        "/usr/share/fonts/google-noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/opentype/noto/NotoSans-Regular.otf",
        "/usr/share/fonts/noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "C:\\Windows\\Fonts\\Arial.ttf",
        main_font_path,
    ]
    for cand in candidates:
        font = _try_load(cand, size)
        if font:
            print(f"[fonts] Loaded fallback IPA font: {cand}")
            return font
    print("[fonts] Re-using main font for IPA text")
    return _try_load(main_font_path, size) or ImageFont.load_default()


def _load_noto(size: int) -> font_types | None:
    """Load Noto Sans at the given size for use as a Unicode fallback font."""
    for cand in _NOTO_CANDIDATES:
        font = _try_load(cand, size)
        if font:
            print(f"[fonts] Loaded Noto fallback font ({size}px): {cand}")
            return font
    path = _fc_match("Noto Sans")
    if path:
        font = _try_load(path, size)
        if font:
            print(f"[fonts] Loaded Noto via fc-match ({size}px): {path}")
            return font
    print("[fonts] WARNING: Could not load Noto fallback font – non-Latin glyphs may not render")
    return None


def load_fonts(generator: Any, font_path: str | None = None, ipa_font_path: str | None = None) -> None:
    # ── Primary (Atkinson) ────────────────────────────────────────────────────
    default_main = "/usr/local/share/fonts/a/AtkinsonHyperlegible_Regular.ttf"
    main_candidate: str = font_path or default_main

    loaded = _try_load(main_candidate, generator.font_size)
    main_font: font_types = loaded if loaded is not None else _fallback_main(generator.font_size)

    generator.font_main = main_font
    generator.font_large = (
        ImageFont.truetype(main_font.path, generator.font_size + 8)
        if hasattr(main_font, "path") else main_font
    )
    generator.font_small = (
        ImageFont.truetype(main_font.path, max(generator.font_size - 4, 8))
        if hasattr(main_font, "path") else main_font
    )
    print("[fonts] Main fonts loaded (large/small derived)")

    # ── IPA font ──────────────────────────────────────────────────────────────
    default_ipa = "/usr/share/fonts/google-noto/NotoSans-Regular.ttf"
    ipa_candidate: str = ipa_font_path or default_ipa
    ipa_font: font_types | None = _try_load(ipa_candidate, generator.font_size - 2)
    if ipa_font is None:
        main_path: Any | None = getattr(main_font, "path", None)
        ipa_font = _fallback_ipa(generator.font_size - 2, main_path)
    # Safety net: PIL bitmap default has no getbbox — fall back to main font
    if not hasattr(ipa_font, "getbbox"):
        ipa_font = main_font
    generator.font_ipa = ipa_font
    print("[fonts] IPA font loaded")

    # ── Noto fallback fonts (one per size variant) ────────────────────────────
    generator.font_fallback_main  = _load_noto(generator.font_size)
    generator.font_fallback_large = _load_noto(generator.font_size + 8)
    generator.font_fallback_small = _load_noto(max(generator.font_size - 4, 8))
    print("[fonts] Noto fallback fonts loaded")