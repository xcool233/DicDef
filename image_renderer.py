"""
Image rendering functionality for dictionary definitions with two-column layout.
"""

from typing import Any, Protocol, runtime_checkable

from PIL import Image, ImageDraw
from dictionary_data import DictionaryData


@runtime_checkable
class GeneratorProtocol(Protocol):
    """Protocol defining the interface expected by ImageRenderer."""
    
    # Colors
    bg_color: str
    text_color: str
    accent_color: str
    secondary_color: str
    divider_color: str
    
    # Layout
    margin: float
    line_spacing: float
    section_spacing: float
    
    # Fonts
    font_main: Any
    font_large: Any
    font_small: Any
    font_ipa: Any


class ImageRenderer:
    """Handles the actual image generation and drawing operations."""
    
    # Language badge colors (background colors for badges)
    LANGUAGE_COLORS = {
        "Latin": "#8B4513",
        "Greek": "#4169E1",
        "Old English": "#2F4F4F",
        "Middle English": "#556B2F",
        "French": "#4B0082",
        "German": "#B8860B",
        "Sanskrit": "#FF8C00",
        "Arabic": "#8B008B",
        "Hebrew": "#006400",
        "Italian": "#DC143C",
        "Spanish": "#FF6347",
        "Dutch": "#FF8C00",
        "Norse": "#4682B4",
        "Celtic": "#228B22",
        "Persian": "#9932CC",
        "Portuguese": "#CD853F",
    }
    
    def __init__(self, generator: GeneratorProtocol) -> None:
        self.generator: GeneratorProtocol = generator
    
    def wrap_text(self, text: str, font: Any, max_width: float) -> list[str]:
        """Wrap text to fit within specified width."""
        words: list[str] = text.split()
        lines: list[Any] = []
        current_line: list[str] = []
        
        for word in words:
            test_line: str = " ".join(current_line + [word])
            bbox: Any = font.getbbox(test_line)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line: list[str] = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(" ".join(current_line))
        
        return lines
    
    def draw_language_badges(self, draw: Any, languages: list[str], 
                            x: float, y: float, max_width: float) -> float:
        """Draw language origin badges and return the new y position."""
        if not languages:
            return y
        
        badge_height = 24
        badge_spacing = 8
        padding_x = 10
        padding_y = 5
        current_x = x
        current_y = y
        
        for language in languages:
            # Get badge color
            bg_color = self.LANGUAGE_COLORS.get(language, "#666666")
            
            # Measure text
            text_bbox = self.generator.font_small.getbbox(language)
            text_width = text_bbox[2] - text_bbox[0]
            badge_width = text_width + (2 * padding_x)
            
            # Check if we need to wrap to next line
            if current_x + badge_width > x + max_width and current_x > x:
                current_x = x
                current_y += badge_height + badge_spacing
            
            # Draw rounded rectangle background
            draw.rounded_rectangle(
                [(current_x, current_y), 
                 (current_x + badge_width, current_y + badge_height)],
                radius=4,
                fill=bg_color
            )
            
            # Draw text centered in badge
            text_x = current_x + padding_x
            text_y = current_y + padding_y
            draw.text((text_x, text_y), language, 
                     font=self.generator.font_small, fill="#FFFFFF")
            
            current_x += badge_width + badge_spacing
        
        return current_y + badge_height + (badge_spacing * 2)
    
    def draw_text_block(self, draw: Any, text: str, font: Any, color: str, 
                        x: float, y: float, max_width: float) -> float:
        """Draw a block of text with wrapping and paragraph support, return the new y position."""
        current_y: float = y
        
        # Split text into paragraphs on double newlines or single newlines
        paragraphs = text.split('\n\n') if '\n\n' in text else text.split('\n')
        
        for i, paragraph in enumerate(paragraphs):
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            lines: list[str] = self.wrap_text(paragraph, font, max_width)
            
            for line in lines:
                draw.text((x, current_y), line, font=font, fill=color)
                bbox: Any = font.getbbox(line)
                line_height: Any = bbox[3] - bbox[1]
                current_y += line_height * self.generator.line_spacing
            
            # Add extra spacing between paragraphs (except after the last one)
            if i < len(paragraphs) - 1:
                current_y += self.generator.section_spacing * 0.5
        
        return current_y
    
    def calculate_column_heights(self, data: DictionaryData, left_col_width: float, right_col_width: float) -> tuple[float, float]:
        """Calculate heights for left and right columns."""
        # Left column: word, pronunciation, language badges, definitions, synonyms
        left_height: float = 0
        
        # Word and pronunciation
        left_height += int(self.generator.font_large.getbbox("A")[3] * self.generator.line_spacing)
        if data.pronunciation:
            left_height += int(self.generator.font_ipa.getbbox("A")[3] * self.generator.line_spacing)
        
        # Language badges
        if data.origin_languages:
            # Estimate badge height (may wrap to multiple lines)
            num_badges = len(data.origin_languages)
            estimated_rows = (num_badges + 2) // 3  # Rough estimate
            left_height += estimated_rows * 32  # badge height + spacing
            left_height += self.generator.section_spacing * 0.3
        
        left_height += self.generator.section_spacing
        
        # Definitions
        for definition in data.definitions:
            left_height += int(self.generator.font_small.getbbox("A")[3] * self.generator.line_spacing)
            def_lines = self.wrap_text(definition["definition"], self.generator.font_main, left_col_width - 10)
            left_height += len(def_lines) * int(self.generator.font_main.getbbox("A")[3] * self.generator.line_spacing)
            if definition.get("usage"):
                # Add extra vertical spacing before usage example
                left_height += self.generator.section_spacing * 0.3
                usage_lines = self.wrap_text(f'"{definition["usage"]}"', self.generator.font_small, left_col_width - 30)
                left_height += len(usage_lines) * int(self.generator.font_small.getbbox("A")[3] * self.generator.line_spacing)
            left_height += self.generator.section_spacing
        
        # Synonyms
        if data.synonyms:
            left_height += int(self.generator.font_small.getbbox("A")[3] * self.generator.line_spacing)
            syn_text = ", ".join(data.synonyms)
            syn_lines = self.wrap_text(syn_text, self.generator.font_main, left_col_width - 10)
            left_height += len(syn_lines) * int(self.generator.font_main.getbbox("A")[3] * self.generator.line_spacing)
            left_height += self.generator.section_spacing
        
        # Right column: etymology & additional etymology
        right_height: float = 0
        combined_etymology = data.get_combined_etymology()
        if combined_etymology:
            right_height += int(self.generator.font_small.getbbox("A")[3] * self.generator.line_spacing)
            
            # Handle paragraphs for height calculation
            paragraphs = combined_etymology.split('\n\n') if '\n\n' in combined_etymology else combined_etymology.split('\n')
            for i, paragraph in enumerate(paragraphs):
                paragraph = paragraph.strip()
                if not paragraph:
                    continue
                etym_lines = self.wrap_text(paragraph, self.generator.font_main, right_col_width - 20)
                right_height += len(etym_lines) * int(self.generator.font_main.getbbox("A")[3] * self.generator.line_spacing)
                # Add paragraph spacing
                if i < len(paragraphs) - 1:
                    right_height += self.generator.section_spacing * 0.5
            
            right_height += self.generator.section_spacing
        
        return left_height, right_height
    
    def render_left_column(self, draw: Any, data: DictionaryData, 
                          x: float, y: float, col_width: float) -> float:
        """Render the left column (word, definitions, synonyms)."""
        current_y: float = y
        
        # Word title
        draw.text((x, current_y), data.word, 
                    font=self.generator.font_large, fill=self.generator.accent_color)
        current_y += int(self.generator.font_large.getbbox(data.word)[3] * self.generator.line_spacing)
        
        # Pronunciation
        if data.pronunciation:
            pronunciation: str = f"/{data.pronunciation}/"
            draw.text((x, current_y), pronunciation, 
                        font=self.generator.font_ipa, fill=self.generator.secondary_color)
            current_y += int(self.generator.font_ipa.getbbox(pronunciation)[3] * self.generator.line_spacing)
        
        # Language origin badges
        if data.origin_languages:
            current_y += self.generator.section_spacing * 0.3
            current_y = self.draw_language_badges(draw, data.origin_languages, 
                                                  x, current_y, col_width)
        
        current_y += self.generator.section_spacing
        
        # Definitions
        for i, definition in enumerate(data.definitions):
            part_of_speech: str = definition.get("part_of_speech", "")
            if part_of_speech:
                # Use part of speech as label instead of "Definition 1"
                draw.text((x, current_y), f"- {part_of_speech}", 
                        font=self.generator.font_small, fill=self.generator.accent_color)
                current_y += int(self.generator.font_small.getbbox(part_of_speech)[3] * self.generator.line_spacing)
            
            def_text: str = definition.get("definition", "")
            current_y = self.draw_text_block(draw, def_text, self.generator.font_main, 
                                            self.generator.text_color, x + 10, 
                                            current_y, col_width - 10)
            
            if definition.get("usage"):
                # Add extra vertical spacing before usage example
                current_y += self.generator.section_spacing * 0.3
                usage_text: str = f'"{definition["usage"]}"'
                current_y = self.draw_text_block(draw, usage_text, self.generator.font_small, 
                                                self.generator.secondary_color, x + 30, 
                                                current_y, col_width - 30)
            
            current_y += self.generator.section_spacing
        
        # Synonyms
        if data.synonyms:
            draw.text((x, current_y), "Synonyms:", 
                        font=self.generator.font_small, fill=self.generator.accent_color)
            current_y += int(self.generator.font_small.getbbox("Synonyms:")[3] * self.generator.line_spacing)
            
            text = ", ".join(data.synonyms)
            current_y = self.draw_text_block(draw, text, self.generator.font_main, 
                                            self.generator.text_color, x + 10, 
                                            current_y, col_width - 10)
            
            current_y += self.generator.section_spacing
        
        return current_y
    
    def render_right_column(self, draw: Any, data: DictionaryData, 
                           x: float, y: float, col_width: float) -> float:
        """Render the right column (etymology)."""
        current_y: float = y
        
        combined_etymology = data.get_combined_etymology()
        if combined_etymology:
            # Debug: print the full etymology text
            print(f"[DEBUG] Combined etymology length: {len(combined_etymology)}")
            print(f"[DEBUG] Number of paragraphs: {len(combined_etymology.split(chr(10)+chr(10)))}")
            
            draw.text((x, current_y), "Etymology & Additional Etymology:", 
                        font=self.generator.font_small, fill=self.generator.accent_color)
            current_y += int(self.generator.font_small.getbbox("Etymology")[3] * self.generator.line_spacing)
            
            current_y = self.draw_text_block(draw, combined_etymology, self.generator.font_main, 
                                            self.generator.text_color, x + 20, 
                                            current_y, col_width - 20)
            
            current_y += self.generator.section_spacing
        
        return current_y
    
    def create_image(self, data: DictionaryData, width: int = 1400, 
                    output_path: str = "dictionary_definition.png") -> Image.Image:
        """Create and render the complete dictionary definition image with two-column layout."""
        # Calculate column widths - more balanced split (45/55)
        col_gap: float = 50  # Space between columns
        left_col_width: float = (width - (2 * self.generator.margin) - col_gap) * 0.45
        right_col_width: float = (width - (2 * self.generator.margin) - col_gap) * 0.55
        
        # Calculate heights for both columns
        left_height, right_height = self.calculate_column_heights(data, left_col_width, right_col_width)
        
        # Total height is the maximum of the two columns plus margins
        # Add some extra padding to be safe
        total_height: float = max(left_height, right_height) + (2 * self.generator.margin) + 20
        
        # Create image
        image = Image.new("RGB", (width, int(total_height)), self.generator.bg_color)
        draw = ImageDraw.Draw(image)
        
        # Column positions
        left_x: float = self.generator.margin
        right_x: float = self.generator.margin + left_col_width + col_gap
        start_y: float = self.generator.margin
        
        # Render columns
        self.render_left_column(draw, data, left_x, start_y, left_col_width)
        self.render_right_column(draw, data, right_x, start_y, right_col_width)
        
        # Draw vertical divider between columns
        divider_x: int = int(left_x + left_col_width + (col_gap / 2))
        draw.line([(divider_x, start_y), (divider_x, int(total_height - self.generator.margin))], 
                 fill=self.generator.divider_color, width=2)
        
        # Save image
        image.save(output_path, "PNG", quality=95)
        print(f"Dictionary definition image saved as: {output_path}")
        
        return image