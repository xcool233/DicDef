# Dictionary Image Generator

Turns a plain-text dictionary entry into a clean, two-column image: the word, pronunciation, definitions and synonyms on the left, and the etymology on the right. Each entry gets its own colour palette, chosen to match the mood of the word, and the program works out the rest of the theme so the text is always readable.

![Sinister](Sinister.png)

## Contents

- [Features](#features)
- [Requirements](#requirements)
- [Quick start](#quick-start)
- [Input file format](#input-file-format)
- [Text styling tags](#text-styling-tags)
- [Colour palettes](#colour-palettes)
- [Command-line options](#command-line-options)
- [Fonts](#fonts)
- [Using it from Python](#using-it-from-python)
- [Project layout](#project-layout)
- [Troubleshooting](#troubleshooting)

## Features

- **Two-column layout**: word, IPA, definitions and synonyms on the left (45%), etymology on the right (55%), separated by a vertical divider.
- **Palette-driven themes**: give a primary colour and a harmony rule; the program builds the background, text, heading, secondary and divider colours, and adjusts lightness so contrast stays readable in dark and light modes.
- **Language origin badges**: languages mentioned in the etymology (Latin, Greek, Old English, and more) are detected automatically and shown as coloured pills.
- **Word-form chips**: related forms such as *sinisterly (adv.)* appear as outlined chips, visually distinct from the origin badges.
- **Inline text styling**: bold, italic, underline and strikethrough via simple tags, plus a `<noto>` tag for non-Latin scripts.
- **Long etymologies flow sideways**: instead of growing very tall, the etymology spills into extra columns (up to 4) and the image grows wider.
- **Dark or light mode** for any palette, plus a random OKLAB theme generator.

## Requirements

- Python 3.10 or newer
- [Pillow](https://pypi.org/project/pillow/) 9.1 or newer: `pip install pillow`
- A TrueType font. [Atkinson Hyperlegible](https://brailleinstitute.org/freefont) is the default; see [Fonts](#fonts) for fallbacks.
- Optional but recommended: Noto Sans, which is used for IPA pronunciation and non-Latin scripts.

## Quick start

1. Write or generate an entry (see [Input file format](#input-file-format)) and save it as `DicDef.txt`.
2. Run:

   ```
   python3 main.py --input DicDef.txt
   ```

3. The image is saved in the current folder, named after the word with a capital first letter (for example `Sinister.png`).

To see the format with a ready-made example, run `python3 main.py --sample`. This writes `sample_word.txt` and exits.

## Input file format

Entries are plain UTF-8 text files made of `FIELD: value` lines.

```
WORD: Sinister
PRONUNCIATION: ˈsɪnɪstər

PALETTE_HARMONY: analogous
PALETTE_PRIMARY: #8b1a1a
PALETTE_SECONDARY: #...        (optional)
PALETTE_TERTIARY: #...         (optional)

DEFINITION: Giving the impression that something harmful or evil is about to happen
PART_OF_SPEECH: Adjective
USAGE: A sinister silence settled over the house.

DEFINITION: Pertaining to the left side
PART_OF_SPEECH: Adjective
USAGE: The lion stood on the sinister side of the shield.

SYNONYMS: menacing, ominous, malevolent, threatening, baleful

WORD_FORMS: sinisterly (adv.), sinisterness (n.), sinistral (adj.)

ETYMOLOGY: From Old French <i>sinistre</i>, from Latin <i>sinister</i>, meaning "left."

ADDITIONAL_ETYMOLOGY: The Latin <i>sinister</i> originally meant simply "left"...

A second paragraph, separated by a blank line.
```

### Fields

| Field | Required | Notes |
|---|---|---|
| `WORD` | Yes | Also used for the output filename. |
| `PRONUNCIATION` | No | IPA, written **without** slashes; the renderer adds `/…/` itself. |
| `DEFINITION` | Yes | Repeat the `DEFINITION` / `PART_OF_SPEECH` / `USAGE` group for each meaning. Each `DEFINITION` line starts a new definition. |
| `PART_OF_SPEECH` | No | Shown as a small label above its definition. |
| `USAGE` | No | Plain-text example sentence. **Don't add quotation marks**; the renderer adds them. |
| `SYNONYMS` | No | Comma-separated list. |
| `WORD_FORMS` | No | Comma-separated; each item may end with a part-of-speech label in parentheses, such as `sinistral (adj.)`. Omit the field if there are no notable forms. |
| `ETYMOLOGY` | No | One line. Shown first in the etymology column. |
| `ADDITIONAL_ETYMOLOGY` | No | May run over several lines and paragraphs. Use a **blank line** between paragraphs. It ends at the next field name. |
| `PALETTE_*` | No | See [Colour palettes](#colour-palettes). |

Other notes:

- Only `ADDITIONAL_ETYMOLOGY` can span multiple lines. Every other field must fit on one line.
- Lines starting with `NOTE:` or `HISTORICAL_USAGE:` are ignored.
- The etymology column is labelled "Etymology & Additional Etymology:"; the two fields are joined into one block.
- There is no `ANTONYMS` field.

### Language badges

The program scans the etymology text for language names and adds a badge for each one it finds: Latin, Greek, Old English, Middle English, French, German, Sanskrit, Arabic, Hebrew, Italian, Spanish, Dutch, Norse, Celtic, Persian and Portuguese.

Detection is a simple text match, so a language name anywhere in the etymology adds its badge, even in a passing mention. Write language names in plain text, with no styling tags around them. Variants count too: "Old French" gives French, "Germanic" gives German, and "Old Norse" or "Scandinavian" gives Norse.

## Text styling tags

Wrap text in tags to style it. Tags can be nested and combined, and each opening tag needs a closing tag.

| Tag | Effect |
|---|---|
| `<i>…</i>` | *Italic* |
| `<b>…</b>` | **Bold** |
| `<u>…</u>` | Underline |
| `<s>…</s>` | ~~Strikethrough~~ |
| `<noto>…</noto>` | Render with Noto Sans (for scripts the main font lacks) |

`<em>`, `<strong>`, `<strike>` and `<del>` work as aliases for `<i>`, `<b>` and `<s>`.

```
From Latin <i>sinister</i>, meaning "left"
The word was <b><i>never</i></b> common
The Greek word <noto><i>ἀριστερός</i></noto> (aristeros)
```

**Where tags work:** definitions, usage examples, synonyms, the etymology fields and the word title. They don't apply to `PRONUNCIATION`, `PART_OF_SPEECH`, `WORD_FORMS` or the palette fields.

**Things to know:**

- Close every tag within the same paragraph. An open tag does not carry across a blank line.
- Markdown (`*italic*`, `**bold**`) is **not** supported and would print the asterisks literally.
- Bold and italic use the real font files when they sit next to your regular font (for example `AtkinsonHyperlegible-Bold.ttf` and `…-Italic.ttf`). If none are found, a synthetic bold or slant is applied and a `[fonts] No real italic file found…` message is printed. It looks fine, just less crisp.
- Underline and strikethrough run continuously across spaces and wrapped lines.

### Non-Latin scripts

Greek, Arabic, Hebrew, Cyrillic, Devanagari, CJK and similar scripts need `<noto>` tags so they render in a font that has the glyphs; otherwise they appear as empty boxes. Romanised transliterations in plain Latin letters don't need tags.

```
ETYMOLOGY: From Greek <noto>μεγαλόψυχος</noto> (megalopsychos), meaning "great-souled"
```

## Colour palettes

You choose the mood and the program does the colour maths. The palette fields in the TXT file are:

| Field | Required | What it does |
|---|---|---|
| `PALETTE_HARMONY` | Yes (defaults to `analogous` if only other fields are given) | The harmony rule relating the colours. |
| `PALETTE_PRIMARY` | **Yes** | The word's signature colour. Drives the title and headings (accent colour) and the tint of the background and body text. |
| `PALETTE_SECONDARY` | No | Pronunciation, usage examples and word-form chips. |
| `PALETTE_TERTIARY` | No | Tints the divider lines. |

If secondary or tertiary are left out, they are derived from the harmony, which is the recommended approach. Colours are written as 6-digit hex codes such as `#8b1a1a`. Short codes like `#abc` and codes without the `#` are also accepted.

### Harmony modes

| Mode | Hue offsets from primary | Feel |
|---|---|---|
| `monochromatic` | 0°, 0° | Calm, austere, melancholic |
| `analogous` | +30°, −30° | Harmonious and soothing; a safe default |
| `complementary` | 180°, 0° | High tension and drama |
| `split-complementary` | 150°, 210° | Contrast with less harshness |
| `triadic` | 120°, 240° | Vibrant, playful, energetic |
| `tetradic` | 60°, 180° | Rich and complex; use sparingly |

Common spellings are accepted too, such as `mono`, `complement`, `split` and `triad`. An unrecognised name falls back to `analogous` with a warning.

### Example primaries

| Mood | Colour |
|---|---|
| Menace, wrath | `#8b1a1a` (deep red) |
| Serene, tranquil | `#3b7ea1` (soft blue) |
| Verdant, pastoral | `#2e7d4f` (green) |
| Melancholy, twilight | `#4b4a8f` (indigo) |
| Jubilant, effervescent | `#d98e04` (amber) |
| Whimsical, ephemeral | `#c2557f` (rose) |

### How readability is kept

The program only ever changes the **lightness** of your colours, never the hue. It nudges lightness until the accent and secondary colours reach a 4.5:1 contrast ratio against the background, so any saturated primary works in both dark and light mode.

### Which colours win

From highest priority to lowest:

1. Command-line colour flags (`--primary`, `--secondary`, `--tertiary`, `--harmony`)
2. `PALETTE_*` fields in the TXT file
3. `--random-theme`
4. The default dark or light theme

If `PALETTE_PRIMARY` is missing or invalid, the whole palette is ignored with a warning, and the next option in the list applies. When a palette is used, the program prints the harmony and the final colours it chose.

## Command-line options

```
python3 main.py --input FILE [options]
```

| Option | Short | Description | Default |
|---|---|---|---|
| `--input FILE` | `-i` | Input TXT file (required unless using `--sample`) | none |
| `--output FILE` | `-o` | Output image path | Word from the file + `.png` |
| `--dark` | `-d` | Dark mode | On |
| `--light` | `-l` | Light mode instead of dark | Off |
| `--random-theme` | `-r` | Random OKLAB theme (only used when no palette applies) | Off |
| `--seed N` | | Seed for a reproducible random theme | Random |
| `--primary HEX` | | Primary colour; overrides `PALETTE_PRIMARY` | From file |
| `--secondary HEX` | | Secondary colour; overrides `PALETTE_SECONDARY` | From file / derived |
| `--tertiary HEX` | | Tertiary colour; overrides `PALETTE_TERTIARY` | From file / derived |
| `--harmony MODE` | | One of the six harmony modes | `analogous` |
| `--ignore-palette` | | Ignore all `PALETTE_` fields in the file | Off |
| `--font FILE` | `-f` | Font file for main text | Atkinson Hyperlegible |
| `--ipa-font FILE` | | Font file for IPA pronunciation | Noto Sans |
| `--font-size N` | `-s` | Base font size in pixels | 24 |
| `--width N` | `-w` | Image width in pixels (grows wider if the etymology needs extra columns) | 1400 |
| `--sample` | | Create `sample_word.txt` and exit | none |

### Examples

```
# Standard render using the palette in the file
python3 main.py -i DicDef.txt

# Light version of the same palette
python3 main.py -i DicDef.txt --light

# Custom output name and width
python3 main.py -i DicDef.txt -o sinister_card.png --width 1000

# Try a different harmony without editing the file
python3 main.py -i DicDef.txt --harmony complementary

# Override the colour completely from the command line
python3 main.py -i DicDef.txt --primary "#8b1a1a" --harmony split-complementary

# Ignore the file's palette and use a reproducible random theme
python3 main.py -i DicDef.txt --ignore-palette --random-theme --seed 42

# Larger text on a narrower image
python3 main.py -i DicDef.txt --font-size 28 --width 1200
```

## Fonts

| Use | Default | Falls back to |
|---|---|---|
| Main text | Atkinson Hyperlegible (`/usr/local/share/fonts/a/AtkinsonHyperlegible_Regular.ttf`) | DejaVu Sans, Liberation Sans, Noto Sans, Arial, then `fc-match` |
| IPA pronunciation | Noto Sans (`/usr/share/fonts/google-noto/NotoSans-Regular.ttf`) | Noto Sans in other common locations, DejaVu Sans, Liberation Sans, Arial, then the main font |
| `<noto>` spans | Noto Sans, searched for in common Linux and Windows locations, then `fc-match` | Main font |

The default paths are set in `load_fonts.py`. If Atkinson lives somewhere else on your system, either pass `--font /path/to/AtkinsonHyperlegible-Regular.ttf` or change `default_main` in that file. Because the main font is passed in as a path, bold and italic files named like the regular one (`…-Bold.ttf`, `…-Italic.ttf`, `…-BoldItalic.ttf`) are found automatically.

For good IPA and non-Latin rendering, install Noto Sans. On Fedora, for example, install the `google-noto-sans-fonts` package.

## Using it from Python

`main.py` is a thin wrapper, so you can drive the generator directly:

```python
from dictionary_data import parse_txt_file
from dictionary_generator import DictionaryImageGenerator
from theme_config import PaletteSpec

data = parse_txt_file("DicDef.txt")

palette = PaletteSpec.from_fields(
    primary=data.palette_primary,
    harmony=data.palette_harmony,
    secondary=data.palette_secondary or None,
    tertiary=data.palette_tertiary or None,
)

generator = DictionaryImageGenerator(dark_mode=True, palette=palette)
generator.generate_image_from_data(data, width=1400, output_path="Sinister.png")
```

The palette is passed to the generator's constructor, so build it from the parsed data as above (this is what `main.py` does). You can also build a `DictionaryData` yourself or pass a plain dictionary to `generator.generate_image(...)`.

## Project layout

| File | Purpose |
|---|---|
| `main.py` | Command-line interface; resolves palette priority and the output filename |
| `dictionary_data.py` | `DictionaryData` container, the TXT parser, language-origin detection |
| `dictionary_generator.py` | `DictionaryImageGenerator`, which wires together the theme, fonts and renderer |
| `image_renderer.py` | Layout and drawing: columns, word wrapping, badges, chips, styled text, etymology flow |
| `theme_config.py` | Default, random and palette-driven colour themes (OKLAB / OKLCH maths, contrast fitting) |
| `load_fonts.py` | Font discovery, IPA font, Noto fallback fonts |

## Troubleshooting

| Problem | Cause and fix |
|---|---|
| `Error: File '…' not found` | Check the `--input` path, and run the command from the program's folder. |
| `WARNING: palette ignored` | `PALETTE_PRIMARY` is missing or not a valid hex colour. Check it is a hex code such as `#8b1a1a`. |
| `unknown harmony` | The harmony name is misspelled. The program falls back to `analogous`. |
| Tiny or blocky text | No TrueType font was found. Pass one with `--font /path/to/font.ttf`. |
| Greek, Arabic or other scripts show as boxes | Wrap them in `<noto>…</noto>` in the TXT file, and make sure Noto Sans is installed. |
| Tags like `<i>` appear literally | Check you are using the updated `image_renderer.py`, and that the tag is spelled correctly with a matching closing tag. Markdown asterisks are never converted. |
| Italic or bold looks slightly rough | No real bold or italic font file was found beside your main font, so a synthetic style is used. Put the family's Bold and Italic files in the same folder as the Regular file. |
| Text is quoted twice | You added quotation marks to a `USAGE` line. Remove them; the renderer adds them. |
| Pronunciation shows `//word//` | You included slashes in `PRONUNCIATION`. Remove them. |
| A badge appears for a language you didn't intend | Language detection is a text match anywhere in the etymology. Reword the passing mention, or accept the badge. |
| Image is much wider than `--width` | Long etymologies are split into extra columns (up to 4) to keep the image from becoming very tall. Shorten the etymology or reduce `--font-size`. |
