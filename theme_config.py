"""
Enhanced theme configuration with random theme generator using OKLAB color space.
"""

import random
import math
import re
from dataclasses import dataclass
from typing import Tuple


@dataclass
class ColorScheme:
    """Color scheme configuration."""
    bg_color: str
    text_color: str
    accent_color: str
    secondary_color: str
    divider_color: str
    tertiary_color: str = ""


@dataclass
class LayoutConfig:
    """Layout configuration."""
    margin: float = 40
    line_spacing: float = 1.2
    section_spacing: float = 20


def oklab_to_linear_srgb(L: float, a: float, b: float) -> Tuple[float, float, float]:
    """Convert OKLAB to linear sRGB."""
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    
    l = l_ * l_ * l_
    m = m_ * m_ * m_
    s = s_ * s_ * s_
    
    r = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    b_lin = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    
    return (r, g, b_lin)


def linear_to_srgb(c: float) -> float:
    """Convert linear RGB component to sRGB."""
    if c <= 0.0031308:
        return 12.92 * c
    return 1.055 * (c ** (1/2.4)) - 0.055


def oklab_to_hex(L: float, a: float, b: float) -> str:
    """Convert OKLAB to hex color."""
    r_lin, g_lin, b_lin = oklab_to_linear_srgb(L, a, b)
    
    r = max(0, min(1, linear_to_srgb(r_lin)))
    g = max(0, min(1, linear_to_srgb(g_lin)))
    b_val = max(0, min(1, linear_to_srgb(b_lin)))
    
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b_val*255):02x}"


def generate_random_theme(seed: int = None, dark_mode: bool = True) -> ColorScheme:
    """
    Generate a random color scheme using OKLAB color space.
    
    Args:
        seed: Random seed for reproducibility
        dark_mode: Whether to generate a dark or light theme
    
    Returns:
        ColorScheme with perceptually uniform colors
    """
    if seed is not None:
        random.seed(seed)
    
    # Generate base hue angle (0-360 degrees)
    base_hue = random.uniform(0, 360)
    
    # Convert to OKLAB a, b components (chroma and hue in OKLAB space)
    # Using moderate chroma for pleasant colors
    chroma = random.uniform(0.08, 0.15)
    
    def hue_to_ab(hue_deg: float, chroma_val: float) -> Tuple[float, float]:
        """Convert hue angle and chroma to OKLAB a, b components."""
        hue_rad = math.radians(hue_deg)
        return chroma_val * math.cos(hue_rad), chroma_val * math.sin(hue_rad)
    
    if dark_mode:
        # Dark theme: dark background, light text
        bg_L = random.uniform(0.15, 0.25)
        text_L = random.uniform(0.85, 0.95)
        accent_L = random.uniform(0.60, 0.75)
        secondary_L = random.uniform(0.50, 0.60)
        divider_L = random.uniform(0.25, 0.35)
        
        # Background: desaturated
        bg_a, bg_b = hue_to_ab(base_hue, chroma * 0.3)
        bg_color = oklab_to_hex(bg_L, bg_a, bg_b)
        
        # Text: nearly achromatic
        text_color = oklab_to_hex(text_L, 0, 0)
        
        # Accent: vibrant complementary or analogous color
        accent_hue = base_hue + random.choice([0, 30, 60, 180, 210])
        accent_a, accent_b = hue_to_ab(accent_hue, chroma * 1.5)
        accent_color = oklab_to_hex(accent_L, accent_a, accent_b)
        
        # Secondary: muted
        secondary_a, secondary_b = hue_to_ab(base_hue + 15, chroma * 0.5)
        secondary_color = oklab_to_hex(secondary_L, secondary_a, secondary_b)
        
        # Divider: slightly lighter than background
        div_a, div_b = hue_to_ab(base_hue, chroma * 0.3)
        divider_color = oklab_to_hex(divider_L, div_a, div_b)
        
    else:
        # Light theme: light background, dark text
        bg_L = random.uniform(0.92, 0.98)
        text_L = random.uniform(0.20, 0.30)
        accent_L = random.uniform(0.45, 0.60)
        secondary_L = random.uniform(0.40, 0.50)
        divider_L = random.uniform(0.80, 0.88)
        
        # Background: nearly white with hint of color
        bg_a, bg_b = hue_to_ab(base_hue, chroma * 0.2)
        bg_color = oklab_to_hex(bg_L, bg_a, bg_b)
        
        # Text: nearly black
        text_color = oklab_to_hex(text_L, 0, 0)
        
        # Accent: saturated
        accent_hue = base_hue + random.choice([0, 30, 60, 180, 210])
        accent_a, accent_b = hue_to_ab(accent_hue, chroma * 1.5)
        accent_color = oklab_to_hex(accent_L, accent_a, accent_b)
        
        # Secondary: muted
        secondary_a, secondary_b = hue_to_ab(base_hue + 15, chroma * 0.6)
        secondary_color = oklab_to_hex(secondary_L, secondary_a, secondary_b)
        
        # Divider: light gray with tint
        div_a, div_b = hue_to_ab(base_hue, chroma * 0.2)
        divider_color = oklab_to_hex(divider_L, div_a, div_b)
    
    return ColorScheme(
        bg_color=bg_color,
        text_color=text_color,
        accent_color=accent_color,
        secondary_color=secondary_color,
        divider_color=divider_color
    )


# ---------------------------------------------------------------------------
# Palette-driven themes
#
# An AI (or the user) supplies a PRIMARY colour, optionally SECONDARY and
# TERTIARY colours, and a colour-harmony mode. This code turns that into the
# five colour slots the renderer uses, in OKLCH, and nudges lightness so text
# and accents always stay readable against the background.
# ---------------------------------------------------------------------------

# Hue offsets (degrees from the primary hue) for the secondary and tertiary colours.
HARMONY_OFFSETS: dict[str, tuple[float, float]] = {
    "monochromatic":       (0, 0),
    "analogous":           (30, -30),
    "complementary":       (180, 0),
    "split-complementary": (150, 210),
    "triadic":             (120, 240),
    "tetradic":            (60, 180),
}

_HARMONY_ALIASES: dict[str, str] = {
    "mono": "monochromatic", "monochrome": "monochromatic",
    "analogue": "analogous",
    "complement": "complementary",
    "split": "split-complementary", "splitcomplementary": "split-complementary",
    "triad": "triadic",
    "rectangle": "tetradic", "square": "tetradic", "double-complementary": "tetradic",
}


def normalize_harmony(name: str | None) -> str | None:
    """Return a canonical harmony name, or None if it is not recognised."""
    if not name:
        return None
    key = re.sub(r"[\s_]+", "-", name.strip().lower())
    key = _HARMONY_ALIASES.get(key, key)
    return key if key in HARMONY_OFFSETS else None


def normalize_hex(value: str | None) -> str | None:
    """Return '#rrggbb' from '#abc', 'abc', '#aabbcc', or text containing '#aabbcc'; else None."""
    if not value:
        return None
    value = value.strip()
    m = re.fullmatch(r"#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})", value)
    if not m:
        m = re.search(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b", value)
    if not m:
        return None
    h = m.group(1).lower()
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return "#" + h


def _srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_to_oklch(hex_color: str) -> Tuple[float, float, float]:
    """Convert '#rrggbb' to OKLCH (L 0-1, C ~0-0.4, h in degrees)."""
    h = hex_color.lstrip("#")
    r, g, b = (_srgb_to_linear(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = l ** (1 / 3), m ** (1 / 3), s ** (1 / 3)
    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    bb = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return L, math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360


def oklch_to_hex(L: float, C: float, h_deg: float) -> str:
    """OKLCH to hex. If the colour is outside sRGB, chroma is reduced (hue is kept)."""
    L = max(0.0, min(1.0, L))
    rad = math.radians(h_deg)
    cos_h, sin_h = math.cos(rad), math.sin(rad)

    def in_gamut(c: float) -> bool:
        return all(-1e-4 <= v <= 1 + 1e-4
                   for v in oklab_to_linear_srgb(L, c * cos_h, c * sin_h))

    if not in_gamut(C):
        lo, hi = 0.0, C
        for _ in range(24):
            mid = (lo + hi) / 2
            if in_gamut(mid):
                lo = mid
            else:
                hi = mid
        C = lo
    return oklab_to_hex(L, C * cos_h, C * sin_h)


def contrast_ratio(hex_a: str, hex_b: str) -> float:
    """WCAG contrast ratio between two '#rrggbb' colours (1.0 - 21.0)."""
    def lum(hx: str) -> float:
        hx = hx.lstrip("#")
        r, g, b = (_srgb_to_linear(int(hx[i:i + 2], 16) / 255) for i in (0, 2, 4))
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    la, lb = lum(hex_a), lum(hex_b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def _fit_contrast(L: float, C: float, h: float, bg_hex: str,
                  min_ratio: float, lighten: bool) -> str:
    """Move lightness (keeping hue/chroma) until the colour reaches *min_ratio* against *bg_hex*."""
    step = 0.01 if lighten else -0.01
    candidate = oklch_to_hex(L, C, h)
    for _ in range(100):
        candidate = oklch_to_hex(L, C, h)
        if contrast_ratio(candidate, bg_hex) >= min_ratio:
            break
        L += step
        if L < 0 or L > 1:
            break
    return candidate


@dataclass
class PaletteSpec:
    """A palette request: primary colour, optional secondary/tertiary, and a harmony mode."""
    primary: str
    harmony: str = "analogous"
    secondary: str | None = None
    tertiary: str | None = None

    @classmethod
    def from_fields(cls, primary: str | None, harmony: str | None = None,
                    secondary: str | None = None, tertiary: str | None = None
                    ) -> "PaletteSpec | None":
        """Validate raw strings (from a TXT file or the CLI). Returns None if there is no usable palette."""
        if not any([primary, harmony, secondary, tertiary]):
            return None

        p = normalize_hex(primary)
        if p is None:
            print("[theme] WARNING: palette ignored - PALETTE_PRIMARY is missing or not a valid hex colour")
            return None

        h = normalize_harmony(harmony)
        if harmony and h is None:
            print(f"[theme] WARNING: unknown harmony '{harmony}' - using 'analogous'. "
                  f"Valid: {', '.join(HARMONY_OFFSETS)}")
        s = normalize_hex(secondary)
        if secondary and s is None:
            print("[theme] WARNING: PALETTE_SECONDARY is not a valid hex colour - deriving it from the harmony")
        t = normalize_hex(tertiary)
        if tertiary and t is None:
            print("[theme] WARNING: PALETTE_TERTIARY is not a valid hex colour - deriving it from the harmony")

        return cls(primary=p, harmony=h or "analogous", secondary=s, tertiary=t)


def generate_palette_theme(spec: PaletteSpec, dark_mode: bool = True) -> ColorScheme:
    """
    Build a ColorScheme from a PaletteSpec.

    primary   -> accent colour (title, headings)
    secondary -> secondary colour (pronunciation, part-of-speech, muted text)
    tertiary  -> tints the divider lines (also returned as tertiary_color)

    The background and body text take the primary's hue at very low chroma so
    everything feels cohesive. Lightness is adjusted (never hue) so accent and
    secondary text reach WCAG contrast 4.5:1 against the background.
    """
    pL, pC, pH = hex_to_oklch(spec.primary)
    off_s, off_t = HARMONY_OFFSETS[spec.harmony]

    def resolve(explicit: str | None, offset: float) -> Tuple[float, float]:
        """Return (chroma, hue) from the explicit colour, or from the harmony offset."""
        if explicit:
            _, c, h = hex_to_oklch(explicit)
            return c, h
        return pC * 0.6, (pH + offset) % 360

    sec_c, sec_h = resolve(spec.secondary, off_s)
    ter_c, ter_h = resolve(spec.tertiary, off_t)

    accent_c = max(0.05, min(pC, 0.22))
    sec_c = max(0.03, min(sec_c, 0.12))
    div_c = max(0.015, min(ter_c * 0.5, 0.06))
    ter_vis_c = max(0.05, min(ter_c, 0.16))

    if dark_mode:
        bg = oklch_to_hex(0.20, min(pC * 0.30, 0.045), pH)
        text = oklch_to_hex(0.92, 0.012, pH)
        accent = _fit_contrast(min(max(pL, 0.60), 0.85), accent_c, pH, bg, 4.5, True)
        secondary = _fit_contrast(0.70, sec_c, sec_h, bg, 4.5, True)
        divider = _fit_contrast(0.33, div_c, ter_h, bg, 1.5, True)
        tertiary = _fit_contrast(0.72, ter_vis_c, ter_h, bg, 3.0, True)
    else:
        bg = oklch_to_hex(0.97, min(pC * 0.12, 0.02), pH)
        text = oklch_to_hex(0.25, 0.015, pH)
        accent = _fit_contrast(max(min(pL, 0.50), 0.30), accent_c, pH, bg, 4.5, False)
        secondary = _fit_contrast(0.46, sec_c, sec_h, bg, 4.5, False)
        divider = _fit_contrast(0.86, div_c, ter_h, bg, 1.2, False)
        tertiary = _fit_contrast(0.50, ter_vis_c, ter_h, bg, 3.0, False)

    return ColorScheme(
        bg_color=bg,
        text_color=text,
        accent_color=accent,
        secondary_color=secondary,
        divider_color=divider,
        tertiary_color=tertiary,
    )


class ThemeConfig:
    """Theme configuration manager with random theme generation."""
    
    DARK_THEME: ColorScheme = ColorScheme(
        bg_color="#1a1a1a",
        text_color="#e0e0e0",
        accent_color="#00ff00",
        secondary_color="#888888",
        divider_color="#333333"
    )
    
    LIGHT_THEME: ColorScheme = ColorScheme(
        bg_color="#ffffff",
        text_color="#333333",
        accent_color="#2c5aa0",
        secondary_color="#666666",
        divider_color="#dddddd"
    )
    
    @classmethod
    def get_theme(cls, dark_mode: bool = True, random_theme: bool = False, seed: int = None,
                  palette: "PaletteSpec | None" = None) -> ColorScheme:
        """
        Get color scheme based on mode.
        
        Priority: palette (primary/secondary/tertiary + harmony) > random theme > default theme.
        
        Args:
            dark_mode: Whether to use dark mode
            random_theme: Whether to generate a random theme
            seed: Random seed for reproducible random themes
            palette: Palette request (e.g. supplied by the AI in the TXT file)
        
        Returns:
            ColorScheme object
        """
        if palette is not None:
            return generate_palette_theme(palette, dark_mode=dark_mode)
        if random_theme:
            return generate_random_theme(seed=seed, dark_mode=dark_mode)
        return cls.DARK_THEME if dark_mode else cls.LIGHT_THEME
    
    @classmethod
    def get_layout(cls) -> LayoutConfig:
        """Get default layout configuration."""
        return LayoutConfig()


# Example usage
if __name__ == "__main__":
    print("Random Dark Theme:")
    dark_theme = generate_random_theme(dark_mode=True)
    print(f"  Background: {dark_theme.bg_color}")
    print(f"  Text: {dark_theme.text_color}")
    print(f"  Accent: {dark_theme.accent_color}")
    print(f"  Secondary: {dark_theme.secondary_color}")
    print(f"  Divider: {dark_theme.divider_color}")
    
    print("\nRandom Light Theme:")
    light_theme = generate_random_theme(dark_mode=False)
    print(f"  Background: {light_theme.bg_color}")
    print(f"  Text: {light_theme.text_color}")
    print(f"  Accent: {light_theme.accent_color}")
    print(f"  Secondary: {light_theme.secondary_color}")
    print(f"  Divider: {light_theme.divider_color}")
    
    print("\nWith seed for reproducibility:")
    seeded_theme = generate_random_theme(seed=42, dark_mode=True)
    print(f"  Background: {seeded_theme.bg_color}")
    print(f"  Text: {seeded_theme.text_color}")
    print(f"  Accent: {seeded_theme.accent_color}")