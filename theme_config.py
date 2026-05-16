"""
Enhanced theme configuration with random theme generator using OKLAB color space.
"""

import random
import math
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
    def get_theme(cls, dark_mode: bool = True, random_theme: bool = False, seed: int = None) -> ColorScheme:
        """
        Get color scheme based on mode.
        
        Args:
            dark_mode: Whether to use dark mode
            random_theme: Whether to generate a random theme
            seed: Random seed for reproducible random themes
        
        Returns:
            ColorScheme object
        """
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