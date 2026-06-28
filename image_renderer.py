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

    def draw_word_form_chips(self, draw: Any, word_forms: list[dict[str, str]],
                             x: float, y: float, max_width: float) -> float:
        """
        Draw related word-form chips (e.g. snobby (adj.), snobbery (n.)).

        Visually these are deliberately *not* colour-filled like the
        language-origin badges — they use an outlined/neutral style so the
        two badge types are easy to tell apart at a glance.
        """
        if not word_forms:
            return y

        padding_x = 10
        padding_y = 4
        chip_spacing = 8
        current_x = x
        current_y = y

        font = self.generator.font_small
        sample_bbox = font.getbbox("Ag")
        font_height = sample_bbox[3] - sample_bbox[1]
        chip_height = font_height + (padding_y * 2)

        for entry in word_forms:
            form = entry.get("form", "")
            label = entry.get("label", "")
            if not form:
                continue
            chip_text = f"{form} ({label})" if label else form

            text_bbox = font.getbbox(chip_text)
            text_width = text_bbox[2] - text_bbox[0]
            chip_width = text_width + (2 * padding_x)

            if current_x + chip_width > x + max_width and current_x > x:
                current_x = x
                current_y += chip_height + chip_spacing

            draw.rounded_rectangle(
                [(current_x, current_y),
                 (current_x + chip_width, current_y + chip_height)],
                radius=4,
                outline=self.generator.secondary_color,
                width=1,
            )

            text_x = current_x + padding_x - text_bbox[0]
            text_y = current_y + padding_y - text_bbox[1]
            draw.text((text_x, text_y), chip_text,
                      font=font, fill=self.generator.secondary_color)

            current_x += chip_width + chip_spacing

        return current_y + chip_height + (chip_spacing * 2)

    # ------------------------------------------------------------------
    # Etymology flow helpers (used for multi-column overflow)
    # ------------------------------------------------------------------

    def _etymology_flow_items(self, data: DictionaryData,
                              col_width: float) -> list[tuple[str, float, bool]]:
        """
        Pre-compute the etymology block as a flat list of drawable lines.

        Returns a list of (line_text, height, is_heading) tuples, in draw
        order, already wrapped for *col_width*. "is_heading" marks the
        "Etymology & Additional Etymology:" label line. Paragraph-break
        spacing is folded in as a preceding blank entry with empty text
        and the gap as its height — callers should still draw nothing for
        empty text, just advance y by its height.
        """
        items: list[tuple[str, float, bool]] = []
        combined_etymology = data.get_combined_etymology()
        if not combined_etymology:
            return items

        lh_small = self.line_height(self.generator.font_small)
        lh_main = self.line_height(self.generator.font_main)
        ss = self.generator.section_spacing

        label = "Etymology & Additional Etymology:"
        items.append((label, lh_small, True))

        paragraphs = (combined_etymology.split('\n\n')
                      if '\n\n' in combined_etymology
                      else combined_etymology.split('\n'))
        # Filter blank paragraphs up front so spacing logic matches draw_text_block
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        for i, paragraph in enumerate(paragraphs):
            for line in self.wrap_text(paragraph, self.generator.font_main, col_width - 20):
                items.append((line, lh_main, False))
            if i < len(paragraphs) - 1:
                items.append(("", ss * 0.5, False))

        return items

    def _flow_into_columns(self, items: list[tuple[str, float, bool]],
                           target_height: float) -> list[list[tuple[str, float, bool]]]:
        """
        Greedily distribute pre-measured flow *items* into as many columns
        as needed so that no column exceeds *target_height*.

        A heading line is never left stranded alone at the bottom of a
        column — if a heading wouldn't be followed by at least one more
        line in the same column, it's pushed to the next column instead.
        """
        columns: list[list[tuple[str, float, bool]]] = [[]]
        current_height = 0.0

        for idx, (text, height, is_heading) in enumerate(items):
            # Don't start a new column with a paragraph-break spacer.
            if not text and current_height == 0.0:
                continue

            # Avoid stranding a heading as the last line of a column.
            if is_heading and current_height + height >= target_height and current_height > 0:
                columns.append([])
                current_height = 0.0

            if current_height + height > target_height and current_height > 0:
                columns.append([])
                current_height = 0.0
                if not text:
                    continue

            columns[-1].append((text, height, is_heading))
            current_height += height

        return columns

    def _measure_flow_height(self, items: list[tuple[str, float, bool]]) -> float:
        return sum(h for _, h, _ in items)

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

        if data.word_forms:
            left_height += lh_small
            sample_bbox = self.generator.font_small.getbbox("Ag")
            chip_h = (sample_bbox[3] - sample_bbox[1]) + 8
            chip_spacing = 8
            # Rough estimate: assume ~2 chips per row at this column width.
            estimated_rows = max(1, (len(data.word_forms) + 1) // 2)
            left_height += estimated_rows * (chip_h + chip_spacing)
            left_height += ss * 0.3

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

        # Word forms (related grammatical forms, e.g. snobby (adj.))
        if data.word_forms:
            bb = self.generator.font_small.getbbox("Word Forms:")
            draw.text((x, current_y - bb[1]), "Word Forms:",
                      font=self.generator.font_small,
                      fill=self.generator.accent_color)
            current_y += self.line_height(self.generator.font_small)

            current_y = self.draw_word_form_chips(draw, data.word_forms,
                                                   x, current_y, col_width)

            current_y += self.generator.section_spacing * 0.3

        return current_y

    def render_etymology_column(self, draw: Any, column_items: list[tuple[str, float, bool]],
                                x: float, y: float) -> float:
        """Draw one column's worth of pre-flowed etymology lines."""
        current_y = y
        for text, height, is_heading in column_items:
            if not text:
                current_y += height
                continue
            if is_heading:
                bb = self.generator.font_small.getbbox(text)
                draw.text((x, current_y - bb[1]), text,
                          font=self.generator.font_small,
                          fill=self.generator.accent_color)
            else:
                bb = self.generator.font_main.getbbox(strip_tags(text) or "A")
                self._draw_span_text(draw, x, current_y - bb[1], text,
                                     self.generator.font_main, self.generator.text_color)
            current_y += height
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
                     output_path: str = "dictionary_definition.png",
                     max_height_give: float = 0.35,
                     max_etymology_columns: int = 4) -> Image.Image:
        """
        Render the dictionary entry.

        The image height is capped to roughly the left column's height
        (plus *max_height_give* as a fraction of that height, so a column
        can finish a paragraph without being forced to split awkwardly).
        If the etymology text would overflow that height in a single
        right-hand column, it is reflowed across additional columns of
        the same width — growing the image *wider* instead of taller —
        up to *max_etymology_columns*.
        """
        col_gap: float = 50
        margin = self.generator.margin

        left_col_width: float = (width - (2 * margin) - col_gap) * 0.45
        etym_col_width: float = (width - (2 * margin) - col_gap) * 0.55

        left_height, _ = self.calculate_column_heights(data, left_col_width, etym_col_width)

        # Target height for the whole image: left column's natural height,
        # with some give so a column doesn't cut a paragraph off mid-thought.
        target_height = left_height * (1 + max_height_give)

        # Flow the etymology text at the standard column width and see how
        # many columns (at that width) are needed to fit inside target_height.
        etym_items = self._etymology_flow_items(data, etym_col_width)

        num_etym_cols = 1
        columns: list[list[tuple[str, float, bool]]] = [etym_items]
        if etym_items:
            total_etym_height = self._measure_flow_height(etym_items)
            # Greedy packing at target_height tells us the minimum column
            # count needed; cap it at max_etymology_columns.
            greedy_columns = self._flow_into_columns(etym_items, target_height)
            num_etym_cols = min(max(len(greedy_columns), 1), max_etymology_columns)

            # Re-balance evenly across exactly num_etym_cols columns so the
            # last column isn't left mostly empty — pack each column to
            # total_height / num_etym_cols rather than the looser
            # give-adjusted target used just to pick the count.
            balanced_target = max(total_etym_height / num_etym_cols, 1.0)
            columns = self._flow_into_columns(etym_items, balanced_target)

            # Rounding in the balance pass can occasionally produce one
            # extra column — if so, merge the overflow into the last
            # allowed column rather than exceeding the cap.
            if len(columns) > num_etym_cols:
                merged = columns[:num_etym_cols - 1]
                tail: list[tuple[str, float, bool]] = []
                for col in columns[num_etym_cols - 1:]:
                    tail.extend(col)
                merged.append(tail)
                columns = merged

        # Actual right-hand block height = tallest etymology column.
        right_height = max((self._measure_flow_height(c) for c in columns), default=0.0)

        total_height = max(left_height, right_height) + (2 * margin) + 20

        # Total width grows with extra etymology columns.
        total_width = (
            margin + left_col_width + col_gap
            + (num_etym_cols * etym_col_width)
            + ((num_etym_cols - 1) * col_gap)
            + margin
        )
        total_width = max(total_width, width)

        image = Image.new("RGB", (int(total_width), int(total_height)), self.generator.bg_color)
        draw = ImageDraw.Draw(image)

        left_x = margin
        start_y = margin

        self.render_left_column(draw, data, left_x, start_y, left_col_width)

        # Render each etymology column, with a divider before each one
        # (including the one separating it from the left column).
        col_x = left_x + left_col_width + col_gap
        for column_items in columns:
            divider_x = int(col_x - (col_gap / 2))
            draw.line(
                [(divider_x, start_y), (divider_x, int(total_height - margin))],
                fill=self.generator.divider_color, width=2)

            self.render_etymology_column(draw, column_items, col_x, start_y)
            col_x += etym_col_width + col_gap

        # If there was no etymology at all, still draw the single divider
        # between left column and the (empty) right space.
        if not columns or not etym_items:
            divider_x = int(left_x + left_col_width + (col_gap / 2))
            draw.line(
                [(divider_x, start_y), (divider_x, int(total_height - margin))],
                fill=self.generator.divider_color, width=2)

        image.save(output_path, "PNG", quality=95)
        print(f"Dictionary definition image saved as: {output_path}")
        print(f"[layout] left_height={left_height:.0f} target_height={target_height:.0f} "
              f"etym_columns={num_etym_cols} final_size={int(total_width)}x{int(total_height)}")
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
