"""
Image rendering functionality for dictionary definitions with two-column layout.

Font strategy
-------------
Atkinson Hyperlegible is used for all text by default.
Wrap any text in <noto>...</noto> tags to render it with Noto Sans instead —
useful for characters Atkinson doesn't support (Greek, Arabic, CJK, etc.).

The IPA pronunciation line always uses the dedicated IPA font (Noto Sans).
"""

from __future__ import annotations

import re
from typing import Any, Protocol, runtime_checkable

from PIL import Image, ImageDraw
from dictionary_data import DictionaryData


# ---------------------------------------------------------------------------
# Tag parsing  –  <noto>text</noto>  →  list of (text, use_noto) spans
# ---------------------------------------------------------------------------

# A "span" is (text: str, noto: bool)
Span = tuple[str, bool]

_NOTO_TAG = re.compile(r'<noto>(.*?)</noto>', re.DOTALL)


def parse_spans(text: str) -> list[Span]:
    """
    Split *text* into a list of (segment, use_noto) spans.

    Plain text → (segment, False)  →  rendered with primary font (Atkinson)
    <noto>…</noto> → (segment, True) →  rendered with Noto fallback font
    """
    spans: list[Span] = []
    last = 0
    for m in _NOTO_TAG.finditer(text):
        if m.start() > last:
            spans.append((text[last:m.start()], False))
        spans.append((m.group(1), True))
        last = m.end()
    if last < len(text):
        spans.append((text[last:], False))
    return spans or [(text, False)]


def strip_tags(text: str) -> str:
    """Remove all <noto>…</noto> tags, returning plain text (for width measurement)."""
    return _NOTO_TAG.sub(r'\1', text)


# ---------------------------------------------------------------------------
# GeneratorProtocol
# ---------------------------------------------------------------------------

@runtime_checkable
class GeneratorProtocol(Protocol):
    """Protocol defining the interface expected by ImageRenderer."""

    bg_color: str
    text_color: str
    accent_color: str
    secondary_color: str
    divider_color: str

    margin: float
    line_spacing: float
    section_spacing: float

    font_main: Any
    font_large: Any
    font_small: Any
    font_ipa: Any

    # Noto fallback fonts – one per size variant (may be None)
    font_fallback_main: Any
    font_fallback_large: Any
    font_fallback_small: Any


# ---------------------------------------------------------------------------
# ImageRenderer
# ---------------------------------------------------------------------------

class ImageRenderer:
    """Handles the actual image generation and drawing operations."""

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
        self.generator = generator

    # ------------------------------------------------------------------
    # Font resolution helpers
    # ------------------------------------------------------------------

    def _primary_for(self, font: Any) -> Any:
        """Return *font* unchanged – it is always the Atkinson variant."""
        return font

    def _fallback_for(self, font: Any) -> Any:
        """Return the Noto variant that matches the size of *font*."""
        g = self.generator
        if font is g.font_large:
            return getattr(g, "font_fallback_large", None) or font
        if font is g.font_small:
            return getattr(g, "font_fallback_small", None) or font
        # font_main or anything else
        return getattr(g, "font_fallback_main", None) or font

    def _font_for_span(self, font: Any, noto: bool) -> Any:
        """Return the correct PIL font for a span."""
        return self._fallback_for(font) if noto else font

    # ------------------------------------------------------------------
    # Measurement helpers (tag-aware)
    # ------------------------------------------------------------------

    def _measure_text(self, text: str, font: Any) -> float:
        """
        Return the pixel width of *text*, which may contain <noto> tags.
        Each span is measured with its actual rendering font.
        """
        total = 0.0
        for segment, noto in parse_spans(text):
            f = self._font_for_span(font, noto)
            bb = f.getbbox(segment)
            total += bb[2] - bb[0]
        return total

    def line_height(self, font: Any) -> float:
        """Stable line height using a tall reference string."""
        bbox = font.getbbox("Ágjy")
        return (bbox[3] - bbox[1]) * self.generator.line_spacing

    # ------------------------------------------------------------------
    # Word-wrap  (tag-aware)
    # ------------------------------------------------------------------

    def wrap_text(self, text: str, font: Any, max_width: float) -> list[str]:
        """
        Wrap *text* (which may contain <noto> tags) to fit within *max_width*.

        Tags are preserved in the returned lines so the renderer can honour them.
        Width measurement uses the correct font for each tagged span.
        """
        # We wrap on word boundaries in the *plain* text, then reconstruct
        # the tagged version for each line.
        #
        # Strategy: tokenise into words that carry their tag state, then
        # greedily pack words onto lines exactly as before.

        # Build a flat list of (word_with_tags, plain_word) pairs.
        # We re-assemble tagged words by walking spans and splitting on spaces.
        tagged_words: list[str] = _split_into_tagged_words(text)

        lines: list[str] = []
        current: list[str] = []

        for word in tagged_words:
            candidate = " ".join(current + [word])
            if self._measure_text(candidate, font) <= max_width:
                current.append(word)
            else:
                if current:
                    lines.append(" ".join(current))
                    current = [word]
                else:
                    lines.append(word)

        if current:
            lines.append(" ".join(current))
        return lines

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def _draw_span_text(self, draw: Any, x: float, y: float,
                        text: str, font: Any, fill: str) -> float:
        """
        Draw *text* (possibly containing <noto> tags) starting at (x, y).
        *y* is the visual top of the line (bbox[1] already cancelled by caller).
        Returns the new x position after drawing.
        """
        for segment, noto in parse_spans(text):
            f = self._font_for_span(font, noto)
            bb = f.getbbox(segment)
            # Cancel internal top bearing so glyphs from different fonts
            # sit on the same visual baseline.
            draw.text((x, y - bb[1]), segment, font=f, fill=fill)
            x += bb[2] - bb[0]
        return x

    def draw_text_block(self, draw: Any, text: str, font: Any, color: str,
                        x: float, y: float, max_width: float) -> float:
        """Draw a (possibly tagged) block of text with wrapping and paragraph breaks."""
        current_y = y
        lh = self.line_height(font)

        paragraphs = text.split('\n\n') if '\n\n' in text else text.split('\n')

        for i, paragraph in enumerate(paragraphs):
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            for line in self.wrap_text(paragraph, font, max_width):
                bb = font.getbbox(strip_tags(line) or "A")
                self._draw_span_text(draw, x, current_y - bb[1], line, font, color)
                current_y += lh

            if i < len(paragraphs) - 1:
                current_y += self.generator.section_spacing * 0.5

        return current_y

    def draw_language_badges(self, draw: Any, languages: list[str],
                             x: float, y: float, max_width: float) -> float:
        """Draw language origin badges and return the new y position."""
        if not languages:
            return y

        padding_x = 10
        padding_y = 4
        badge_spacing = 8
        current_x = x
        current_y = y

        sample_bbox = self.generator.font_small.getbbox("Ag")
        font_height = sample_bbox[3] - sample_bbox[1]
        badge_height = font_height + (padding_y * 2)

        for language in languages:
            bg_color = self.LANGUAGE_COLORS.get(language, "#666666")

            text_bbox = self.generator.font_small.getbbox(language)
            text_width = text_bbox[2] - text_bbox[0]
            badge_width = text_width + (2 * padding_x)

            if current_x + badge_width > x + max_width and current_x > x:
                current_x = x
                current_y += badge_height + badge_spacing

            draw.rounded_rectangle(
                [(current_x, current_y),
                 (current_x + badge_width, current_y + badge_height)],
                radius=4,
                fill=bg_color,
            )

            text_x = current_x + padding_x - text_bbox[0]
            text_y = current_y + padding_y - text_bbox[1]
            draw.text((text_x, text_y), language,
                      font=self.generator.font_small, fill="#FFFFFF")

            current_x += badge_width + badge_spacing

        return current_y + badge_height + (badge_spacing * 2)

    # ------------------------------------------------------------------
    # Column height estimation
    # ------------------------------------------------------------------

    def calculate_column_heights(self, data: DictionaryData,
                                  left_col_width: float,
                                  right_col_width: float) -> tuple[float, float]:
        lh_main  = self.line_height(self.generator.font_main)
        lh_large = self.line_height(self.generator.font_large)
        lh_small = self.line_height(self.generator.font_small)
        lh_ipa   = self.line_height(self.generator.font_ipa)
        ss = self.generator.section_spacing

        # ── Left column ──────────────────────────────────────────────
        left_height: float = 0

        left_height += lh_large
        if data.pronunciation:
            left_height += lh_ipa

        if data.origin_languages:
            sample_bbox = self.generator.font_small.getbbox("Ag")
            badge_h = (sample_bbox[3] - sample_bbox[1]) + 8
            badge_spacing = 8
            estimated_rows = max(1, (len(data.origin_languages) + 2) // 3)
            left_height += estimated_rows * (badge_h + badge_spacing)
            left_height += ss * 0.3

        left_height += ss

        for definition in data.definitions:
            left_height += lh_small
            def_lines = self.wrap_text(definition["definition"],
                                       self.generator.font_main, left_col_width - 10)
            left_height += len(def_lines) * lh_main
            if definition.get("usage"):
                left_height += ss * 0.3
                usage_lines = self.wrap_text(f'"{definition["usage"]}"',
                                             self.generator.font_small, left_col_width - 30)
                left_height += len(usage_lines) * lh_small
            left_height += ss

        if data.synonyms:
            left_height += lh_small
            syn_lines = self.wrap_text(", ".join(data.synonyms),
                                       self.generator.font_main, left_col_width - 10)
            left_height += len(syn_lines) * lh_main
            left_height += ss

        # ── Right column ─────────────────────────────────────────────
        right_height: float = 0
        combined_etymology = data.get_combined_etymology()
        if combined_etymology:
            right_height += lh_small

            paragraphs = (combined_etymology.split('\n\n')
                          if '\n\n' in combined_etymology
                          else combined_etymology.split('\n'))
            for i, paragraph in enumerate(paragraphs):
                paragraph = paragraph.strip()
                if not paragraph:
                    continue
                etym_lines = self.wrap_text(paragraph, self.generator.font_main,
                                            right_col_width - 20)
                right_height += len(etym_lines) * lh_main
                if i < len(paragraphs) - 1:
                    right_height += ss * 0.5

            right_height += ss

        return left_height, right_height

    # ------------------------------------------------------------------
    # Column rendering
    # ------------------------------------------------------------------

    def render_left_column(self, draw: Any, data: DictionaryData,
                           x: float, y: float, col_width: float) -> float:
        current_y = y

        # Word title
        bb = self.generator.font_large.getbbox(strip_tags(data.word) or "A")
        self._draw_span_text(draw, x, current_y - bb[1],
                             data.word, self.generator.font_large,
                             self.generator.accent_color)
        current_y += self.line_height(self.generator.font_large)

        # Pronunciation  (always IPA font – Noto, already has full coverage)
        if data.pronunciation:
            pronunciation = f"/{data.pronunciation}/"
            bb = self.generator.font_ipa.getbbox(pronunciation)
            draw.text((x, current_y - bb[1]), pronunciation,
                      font=self.generator.font_ipa,
                      fill=self.generator.secondary_color)
            current_y += self.line_height(self.generator.font_ipa)

        # Language badges
        if data.origin_languages:
            current_y += self.generator.section_spacing * 0.3
            current_y = self.draw_language_badges(draw, data.origin_languages,
                                                  x, current_y, col_width)

        current_y += self.generator.section_spacing

        # Definitions
        for definition in data.definitions:
            part_of_speech = definition.get("part_of_speech", "")
            if part_of_speech:
                label = f"- {part_of_speech}"
                bb = self.generator.font_small.getbbox(label)
                draw.text((x, current_y - bb[1]), label,
                          font=self.generator.font_small,
                          fill=self.generator.accent_color)
                current_y += self.line_height(self.generator.font_small)

            current_y = self.draw_text_block(
                draw, definition.get("definition", ""),
                self.generator.font_main, self.generator.text_color,
                x + 10, current_y, col_width - 10)

            if definition.get("usage"):
                current_y += self.generator.section_spacing * 0.3
                current_y = self.draw_text_block(
                    draw, f'"{definition["usage"]}"',
                    self.generator.font_small, self.generator.secondary_color,
                    x + 30, current_y, col_width - 30)

            current_y += self.generator.section_spacing

        # Synonyms
        if data.synonyms:
            bb = self.generator.font_small.getbbox("Synonyms:")
            draw.text((x, current_y - bb[1]), "Synonyms:",
                      font=self.generator.font_small,
                      fill=self.generator.accent_color)
            current_y += self.line_height(self.generator.font_small)

            current_y = self.draw_text_block(
                draw, ", ".join(data.synonyms),
                self.generator.font_main, self.generator.text_color,
                x + 10, current_y, col_width - 10)

            current_y += self.generator.section_spacing

        return current_y

    def render_right_column(self, draw: Any, data: DictionaryData,
                            x: float, y: float, col_width: float) -> float:
        current_y = y

        combined_etymology = data.get_combined_etymology()
        if combined_etymology:
            label = "Etymology & Additional Etymology:"
            bb = self.generator.font_small.getbbox(label)
            draw.text((x, current_y - bb[1]), label,
                      font=self.generator.font_small,
                      fill=self.generator.accent_color)
            current_y += self.line_height(self.generator.font_small)

            current_y = self.draw_text_block(
                draw, combined_etymology,
                self.generator.font_main, self.generator.text_color,
                x + 20, current_y, col_width - 20)

            current_y += self.generator.section_spacing

        return current_y

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def create_image(self, data: DictionaryData, width: int = 1400,
                     output_path: str = "dictionary_definition.png") -> Image.Image:
        col_gap: float         = 50
        left_col_width: float  = (width - (2 * self.generator.margin) - col_gap) * 0.45
        right_col_width: float = (width - (2 * self.generator.margin) - col_gap) * 0.55

        left_height, right_height = self.calculate_column_heights(
            data, left_col_width, right_col_width)

        total_height = max(left_height, right_height) + (2 * self.generator.margin) + 20

        image = Image.new("RGB", (width, int(total_height)), self.generator.bg_color)
        draw  = ImageDraw.Draw(image)

        left_x  = self.generator.margin
        right_x = self.generator.margin + left_col_width + col_gap
        start_y = self.generator.margin

        self.render_left_column(draw,  data, left_x,  start_y, left_col_width)
        self.render_right_column(draw, data, right_x, start_y, right_col_width)

        divider_x = int(left_x + left_col_width + (col_gap / 2))
        draw.line(
            [(divider_x, start_y), (divider_x, int(total_height - self.generator.margin))],
            fill=self.generator.divider_color, width=2)

        image.save(output_path, "PNG", quality=95)
        print(f"Dictionary definition image saved as: {output_path}")
        return image


# ---------------------------------------------------------------------------
# Internal helper – tokenise a tagged string into word-level tokens
# ---------------------------------------------------------------------------

def _split_into_tagged_words(text: str) -> list[str]:
    """
    Split *text* into a list of whitespace-delimited tokens while preserving
    <noto>…</noto> tags around each word's content.

    e.g. 'hello <noto>μεγαλόψυχος</noto> world'
         → ['hello', '<noto>μεγαλόψυχος</noto>', 'world']

    Spans that contain spaces (unusual but possible) are kept as single tokens.
    """
    # Build a flat sequence of (char, noto_flag) then reassemble into words.
    chars: list[tuple[str, bool]] = []
    for segment, noto in parse_spans(text):
        for ch in segment:
            chars.append((ch, noto))

    if not chars:
        return []

    words: list[str] = []
    current_chars: list[tuple[str, bool]] = []

    def flush() -> None:
        if not current_chars:
            return
        # Re-encode back into a tagged string
        result = ""
        in_noto = False
        for ch, noto in current_chars:
            if noto and not in_noto:
                result += "<noto>"
                in_noto = True
            elif not noto and in_noto:
                result += "</noto>"
                in_noto = False
            result += ch
        if in_noto:
            result += "</noto>"
        words.append(result)
        current_chars.clear()

    for ch, noto in chars:
        if ch == ' ':
            flush()
        else:
            current_chars.append((ch, noto))
    flush()

    return words
