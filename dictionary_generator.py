"""
Main dictionary image generator class with random theme support.
"""

from typing import Any, TypeAlias

from PIL import Image
from load_fonts import load_fonts
from theme_config import ThemeConfig, ColorScheme, LayoutConfig
from image_renderer import ImageRenderer
from dictionary_data import DictionaryData, parse_txt_file


class DictionaryImageGenerator:
    """Main class for generating dictionary definition images."""
    
    def __init__(self, dark_mode: bool = True, random_theme: bool = False, 
                theme_seed: int | None = None, font_path: str | None = None, 
                ipa_font_path: str | None = None, font_size: int = 24) -> None:
        """
        Initialize dictionary image generator.
        
        Args:
            dark_mode: Use dark mode theme (default: True)
            random_theme: Generate random color scheme using OKLAB (default: False)
            theme_seed: Random seed for reproducible random themes (default: None)
            font_path: Custom font file path for main text (default: None)
            ipa_font_path: Custom font file path for IPA pronunciation (default: None)
            font_size: Base font size in pixels (default: 24)
        """
        self.dark_mode: bool = dark_mode
        self.random_theme: bool = random_theme
        self.theme_seed: int | None = theme_seed
        self.font_size: int = font_size
        
        # Apply theme (regular or random)
        color_scheme: ColorScheme = ThemeConfig.get_theme(
            dark_mode=dark_mode,
            random_theme=random_theme,
            seed=theme_seed
        )
        self.bg_color: str = color_scheme.bg_color
        self.text_color: str = color_scheme.text_color
        self.accent_color: str = color_scheme.accent_color
        self.secondary_color: str = color_scheme.secondary_color
        self.divider_color: str = color_scheme.divider_color
        
        # Apply layout
        layout: LayoutConfig = ThemeConfig.get_layout()
        self.margin: float = layout.margin
        self.line_spacing: float = layout.line_spacing
        self.section_spacing: float = layout.section_spacing
        
        # Load fonts
        load_fonts(self, font_path=font_path, ipa_font_path=ipa_font_path)
        
        # Initialize renderer
        self.renderer: ImageRenderer = ImageRenderer(self)
    
    def generate_image_from_data(self, data: DictionaryData, width: int = 1400, 
                                output_path: str = "dictionary_definition.png") -> Image.Image:
        """Generate image from DictionaryData object."""
        return self.renderer.create_image(data, width, output_path)
    
    def generate_image(self, data: dict[str, Any] | DictionaryData, width: int = 1400,
                        output_path: str = "dictionary_definition.png") -> Image.Image:
        """Generate dictionary definition image from data dict or DictionaryData object."""
        if isinstance(data, dict):
            dictionary_data: DictionaryData = DictionaryData.from_dict(data)
        else:
            dictionary_data: DictionaryData = data
            
        return self.generate_image_from_data(dictionary_data, width, output_path)
    
    def generate_from_file(self, file_path: str, width: int = 1400,
                            output_path: str = "dictionary_definition.png") -> Image.Image:
        """Generate image directly from a text file."""
        data: DictionaryData = parse_txt_file(file_path)
        return self.generate_image_from_data(data, width, output_path)

DIG: TypeAlias = DictionaryImageGenerator