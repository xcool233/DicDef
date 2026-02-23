from pathlib import Path
from typing import Any, TypeAlias

from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont, ImageFont as ImageFontType

font_types: TypeAlias = FreeTypeFont | ImageFontType


def load_default() -> font_types:
    return ImageFont.load_default()


def _try_load(path: str | None, size: int) -> font_types | None:
    """Return a FreeTypeFont if the file exists and Pillow can open it."""
    if path and Path(path).expanduser().exists():
        try:
            return ImageFont.truetype(str(path), size)
        except Exception:          # pragma: no cover – defensive
            pass
    return None


def _fallback_main(size: int) -> font_types:
    """Try a handful of common system fonts, finally fall back to PIL default."""
    candidates: list[str] = [
        "/System/Library/Fonts/Arial.ttf",                    # macOS
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",    # Linux
        "C:\\Windows\\Fonts\\arial.ttf",                      # Windows
        "arial.ttf",                                          # generic
    ]

    for cand in candidates:
        font: font_types | None = _try_load(cand, size)
        if font:
            print(f"[fonts] Loaded fallback main font: {cand}")
            return font

    # Last resort – PIL’s built‑in bitmap font
    print("[fonts] Using Pillow default font for main text")
    return load_default()


def _fallback_ipa(size: int, main_font_path: str | None) -> font_types:
    """IPA font fall-backs - try dedicated IPA fonts, then the main font."""
    candidates: list[str | None] = [
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",  # Noto (good IPA coverage)
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",      # DejaVu
        "/System/Library/Fonts/Arial Unicode MS.ttf",           # macOS Unicode
        "C:\\Windows\\Fonts\\Arial.ttf",                        # Windows
        main_font_path,                                         # reuse main font if all else fails
    ]

    for cand in candidates:
        font: font_types | None = _try_load(cand, size)
        if font:
            print(f"[fonts] Loaded fallback IPA font: {cand}")
            return font

    # As a safety net, just reuse the main font (it will render something)
    print("[fonts] Re-using main font for IPA text")
    return _try_load(main_font_path, size) or ImageFont.load_default()


def load_fonts(generator: Any, font_path: str | None = None, ipa_font_path: str | None = None) -> None:
    default_main = "/usr/share/fonts/opentype/atkinson-hyperlegible/AtkinsonHyperlegible-Regular.otf"
    main_candidate: str = font_path or default_main

    _ = _try_load(main_candidate, generator.font_size)
    if _ is not None:
        main_font: font_types = _
    else:
        main_font: font_types = _fallback_main(generator.font_size)

    # Store the three size variants – they share the same underlying file
    generator.font_main = main_font
    generator.font_large = (
        ImageFont.truetype(main_font.path, generator.font_size + 8)
        if hasattr(main_font, "path")
        else main_font
    )
    generator.font_small = (
        ImageFont.truetype(main_font.path, max(generator.font_size - 4, 8))
        if hasattr(main_font, "path")
        else main_font
    )
    print("[fonts] Main fonts loaded (large/small derived)")

    default_ipa = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
    ipa_candidate: str = ipa_font_path or default_ipa

    ipa_font: font_types | None = _try_load(ipa_candidate, generator.font_size - 2)
    if ipa_font is None:
        # Pass the path of the *actual* main font we ended up using
        main_path: Any | None = getattr(main_font, "path", None)
        ipa_font: FreeTypeFont = _fallback_ipa(generator.font_size - 2, main_path)

    generator.font_ipa = ipa_font
    print("[fonts] IPA font loaded")
