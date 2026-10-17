I have a dictionary image generator program that creates visual dictionary entries. I need you to create a properly formatted entry for the word **Sinister**, including a colour palette that suits the word's mood.

### Required Format Specifications:

**File Structure:**
```
WORD: [word]
PRONUNCIATION: [IPA pronunciation]

PALETTE_HARMONY: [monochromatic | analogous | complementary | split-complementary | triadic | tetradic]
PALETTE_PRIMARY: [hex colour, e.g. #8b1a1a]
PALETTE_SECONDARY: [hex colour — optional]
PALETTE_TERTIARY: [hex colour — optional]

DEFINITION: [definition text]
PART_OF_SPEECH: [noun/verb/adjective/adverb/etc.]
USAGE: [example sentence — plain text, no quotes; the renderer adds them automatically]

DEFINITION: [second definition if applicable]
PART_OF_SPEECH: [part of speech]
USAGE: [example sentence]

SYNONYMS: [comma-separated list]

WORD_FORMS: [comma-separated list, each optionally tagged with part of speech in parentheses]

ETYMOLOGY: [primary etymology paragraph]

ADDITIONAL_ETYMOLOGY: [detailed etymology with multiple paragraphs if needed]
```

**Important Requirements:**

1. **Pronunciation**: Use IPA (International Phonetic Alphabet) format
2. **Multiple Definitions**: Include 1–3 definitions if the word has multiple meanings
3. **Part of Speech**: Label each definition (noun, verb, adjective, adverb, etc.)
4. **Usage Examples**: Provide realistic, natural example sentences for each definition. Write them as plain text — **do not wrap them in quotation marks**; the renderer wraps them automatically.
5. **Synonyms**: Include 3–5 relevant synonyms as a comma-separated list
6. **Word Forms** *(optional)*: Include 2–6 related grammatical forms of the word — other parts of speech derived from the same root (e.g. for "magnanimous": "magnanimously (adv.)", "magnanimity (n.)"). Each item is `form (label)`, comma-separated; the parenthetical label is optional. These render as small outlined chips below Synonyms, visually distinct from the coloured language-origin badges. Omit the field entirely if the word has no notable related forms.
7. **Etymology**:
   - Primary etymology paragraph explaining the word's origin
   - Additional etymology with deeper historical context, development over time, and interesting linguistic details
   - **IMPORTANT**: Mention origin languages explicitly (e.g., "from Latin", "Greek origin", "Old French") as the program automatically detects these and creates coloured language badges

8. **Language Origin Badges**: The program automatically detects and displays coloured badge pills (white text on a coloured background) for languages mentioned in the etymology, including:
   - Latin, Greek, Old English, Middle English, French, German, Sanskrit, Arabic, Hebrew, Italian, Spanish, Dutch, Norse, Celtic, Persian, Portuguese, and more

9. **No Antonyms**: Do not include an ANTONYMS field (this feature has been removed)

10. **Colour Palette**: Choose a palette that reflects the word's mood, using the rules in the **Colour Palette** section below.

**Additional Context — Layout:**
- The output is rendered as a professional **two-column image**:
  - **Left column (45% width)**: word title (accent colour), IPA pronunciation, language badges, definitions with part-of-speech labels, and synonyms
  - **Right column (55% width)**: etymology section, labelled `"Etymology & Additional Etymology:"`
- A vertical divider line separates the two columns

**Paragraph breaks in ADDITIONAL_ETYMOLOGY**: Use **double line breaks** (`\n\n`) between paragraphs — the renderer treats these as separate paragraph blocks with extra spacing. Single line breaks within a paragraph are also fine.

---

### Colour Palette

The program builds the whole colour theme (background, text, headings, secondary text, divider lines) from a small palette that **you** choose. You pick the *mood* — the program does the colour maths, so the result is cohesive and always readable.

**What to supply**

| Field | Required? | What it does |
|---|---|---|
| `PALETTE_HARMONY` | Yes | The colour-harmony rule used to relate the colours (see table below) |
| `PALETTE_PRIMARY` | Yes | The word's signature colour as a hex code. Drives the background tint, the title, and the headings |
| `PALETTE_SECONDARY` | Optional | Supporting colour for pronunciation, part-of-speech labels, and example sentences |
| `PALETTE_TERTIARY` | Optional | Subtle accent; tints the divider lines |

If you leave out `PALETTE_SECONDARY` and/or `PALETTE_TERTIARY`, the program **derives them from the harmony mode automatically**. This is the safest option and is recommended unless you have a specific reason to choose them yourself.

**Harmony modes** — pick the one that best matches the word's feel:

| Mode | Relationship to primary hue | Feel / best for |
|---|---|---|
| `monochromatic` | Same hue, varied tone | Calm, focused, austere, melancholic words |
| `analogous` | Neighbours (about ±30°) | Harmonious, natural, soothing; safe default |
| `complementary` | Opposite (180°) | High tension and contrast; dramatic, conflicting words |
| `split-complementary` | About 150° and 210° | Contrast with less harshness; lively but balanced |
| `triadic` | Evenly spaced (120° / 240°) | Vibrant, playful, energetic words |
| `tetradic` | 60° and 180° | Rich, complex, varied; use sparingly |

**How to choose the primary colour**

1. Decide the word's dominant mood (e.g. sinister → menace and dread; serene → calm; effervescent → bright and lively).
2. Pick **one** clear, saturated base colour for that mood. Think "what colour *is* this word?" — for example:
   - sinister, wrath, visceral → deep or blood red (`#8b1a1a`)
   - serene, tranquil, ethereal → soft blue or teal (`#3b7ea1`)
   - verdant, tenacious, pastoral → green (`#2e7d4f`)
   - lugubrious, melancholy, twilight → indigo or slate violet (`#4b4a8f`)
   - effervescent, jubilant, sanguine → warm amber or gold (`#d98e04`)
   - ephemeral, whimsical, saccharine → rose or pink (`#c2557f`)
3. Choose the harmony mode from the table above that supports that mood.
4. Don't worry about making the primary light or dark enough to read — the program automatically adjusts **lightness only** (never the hue) so text and headings stay clearly legible in both dark and light modes.

**Rules**
- Always use **6-digit hex codes** with a leading `#` (e.g. `#8b1a1a`).
- Use the harmony names **exactly** as listed (lowercase, hyphenated).
- If you supply `PALETTE_SECONDARY` / `PALETTE_TERTIARY`, they should actually follow the chosen harmony (e.g. for `analogous`, hues about 30° either side of the primary; for `complementary`, the secondary on the opposite side of the colour wheel). If you aren't certain, omit them.
- If `PALETTE_PRIMARY` is missing or invalid, the entire palette is ignored with a warning and the default or random theme is used instead.
- Place the four `PALETTE_` lines directly after `PRONUNCIATION`, as in the template.

**Example for "Sinister"**
```
PALETTE_HARMONY: analogous
PALETTE_PRIMARY: #8b1a1a
```
(A deep blood-red primary with analogous neighbours gives a dark maroon background with red and rust accents. Secondary and tertiary are derived automatically.)

---

### Text Styling Tags

The renderer supports inline tags for styling text. Tags can be **nested and combined**, and every opening tag needs a matching closing tag.

| Tag | Effect | Typical use |
|---|---|---|
| `<i>…</i>` | *Italic* | Foreign-language words, cited terms, titles, the word being discussed |
| `<b>…</b>` | **Bold** | Key terms, emphasis (use sparingly) |
| `<u>…</u>` | Underline | Rarely needed; strong emphasis only |
| `<s>…</s>` | ~~Strikethrough~~ | Obsolete or rejected forms |
| `<noto>…</noto>` | Switches to the Noto Sans font | Non-Latin scripts (see below) |

Combine by nesting: `<b><i>bold italic</i></b>`, `<i><u>underlined italic</u></i>`, `<noto><i>ἀριστερός</i></noto>`.

**Where tags work:** definitions, usage examples, synonyms, and the etymology fields. They do **not** apply to `WORD_FORMS`, `PART_OF_SPEECH`, `PRONUNCIATION`, or the palette fields — keep those as plain text.

**Rules:**
- Close every tag **within the same paragraph**. A tag left open does not carry over a blank line into the next paragraph.
- Use tags **only** around the words that need styling, not around whole sentences.
- Don't use Markdown (`*italic*`, `**bold**`) — the renderer doesn't understand it and will print the asterisks literally.
- In the etymology, italicise foreign-language words and the words being glossed, e.g. `From Latin <i>exemplum</i>, meaning "a sample"`. The quotation marks around meanings stay as plain text.
- Language names themselves (Latin, Old French…) stay plain, so the origin badges are detected correctly.

---

### Non-Latin Characters — `<noto>` Tag

If the etymology references words in a non-Latin script (Greek, Arabic, Hebrew, Cyrillic, Devanagari, CJK, etc.), wrap those characters in `<noto>` tags so the renderer switches to a Unicode-capable fallback font for that span:

```
ETYMOLOGY: From Greek <noto>μεγαλόψυχος</noto> (megalopsychos), meaning "great-souled"
```

Plain Latin text — including romanised transliterations — does **not** need tags. Only use `<noto>` for the actual non-Latin script characters. To italicise a non-Latin word, nest the tags: `<noto><i>μεγαλόψυχος</i></noto>`.

---

## Quick Reference Template

```
WORD: Example
PRONUNCIATION: ɪɡˈzæmpəl

PALETTE_HARMONY: analogous
PALETTE_PRIMARY: #3b7ea1

DEFINITION: A thing characteristic of its kind or illustrating a general rule
PART_OF_SPEECH: Noun
USAGE: This painting is a perfect example of the Impressionist style.

SYNONYMS: instance, case, illustration, specimen, sample

WORD_FORMS: exemplify (v.), exemplary (adj.), exemplification (n.)

ETYMOLOGY: From Old French <i>example</i>, from Latin <i>exemplum</i>, meaning "a sample"

ADDITIONAL_ETYMOLOGY: The Latin <i>exemplum</i> derives from <i>eximere</i> (to take out, remove), from <i>ex-</i> (out) + <i>emere</i> (to take). The word entered English in the late 14th century with the meaning "an instance serving for illustration."

The verb form developed in the 15th century and fell out of common use, though it survives in the phrase <i>to example someone</i>.
```

---

## Running the Program from the Terminal

**Please give me the finished entry in a single code block, then tell me the command to run it** — for example: save the block as `DicDef.txt`, then run `python3 main.py --input DicDef.txt`.

### Requirements
- Python 3.10 or newer
- The Pillow library: `pip install pillow`
- A TrueType font. The default is Atkinson Hyperlegible; if it isn't found, the program falls back to Noto Sans, DejaVu Sans, Liberation Sans or Arial, or you can point to one with `--font`.

### Basic usage
```
python3 main.py --input DicDef.txt
```
The image is saved in the current folder, named after the word with a capital first letter (e.g. `Sinister.png`). Use `--output` to choose a different name.

### Command-line options

| Option | Short | Description | Default |
|---|---|---|---|
| `--input FILE` | `-i` | Input TXT file (required unless using `--sample`) | — |
| `--output FILE` | `-o` | Output image path | Word from the file + `.png` |
| `--dark` | `-d` | Dark mode | On |
| `--light` | `-l` | Light mode instead of dark | Off |
| `--random-theme` | `-r` | Random OKLAB colour theme (only used when no palette applies) | Off |
| `--seed N` | | Seed for a reproducible random theme | Random |
| `--primary HEX` | | Primary colour; overrides `PALETTE_PRIMARY` in the file | From file |
| `--secondary HEX` | | Secondary colour; overrides `PALETTE_SECONDARY` | From file / derived |
| `--tertiary HEX` | | Tertiary colour; overrides `PALETTE_TERTIARY` | From file / derived |
| `--harmony MODE` | | `monochromatic`, `analogous`, `complementary`, `split-complementary`, `triadic`, `tetradic` | `analogous` |
| `--ignore-palette` | | Ignore all `PALETTE_` fields in the file | Off |
| `--font FILE` | `-f` | Custom font file for main text | Atkinson Hyperlegible |
| `--ipa-font FILE` | | Custom font file for IPA pronunciation | Noto Sans |
| `--font-size N` | `-s` | Base font size in pixels | 24 |
| `--width N` | `-w` | Image width in pixels (the image grows wider if the etymology needs extra columns) | 1400 |
| `--sample` | | Create `sample_word.txt` and exit | — |

### Which colours win?
Highest priority first:
1. Command-line colour flags (`--primary`, `--secondary`, `--tertiary`, `--harmony`)
2. `PALETTE_` fields in the TXT file
3. `--random-theme`
4. The default dark or light theme

So `--random-theme` is a safe fallback: if the file has a palette, the palette is used; if not, a random theme is generated. Add `--ignore-palette --random-theme` to force a random theme anyway. `--light` and `--dark` still apply to palettes — the same palette renders as either a dark or a light design.

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

# Create a sample input file to see the format
python3 main.py --sample
```

When a palette is used, the program prints the harmony and the final background, text, accent, secondary and divider colours so you can see exactly what was applied.

### Troubleshooting
- **`Error: File '…' not found`** — check the `--input` path and run the command from the program's folder.
- **`WARNING: palette ignored`** — `PALETTE_PRIMARY` is missing or not a valid hex colour.
- **`unknown harmony`** — the harmony name is misspelled; the program falls back to `analogous`.
- **Tiny or missing text** — no TrueType font was found; pass one with `--font /path/to/font.ttf`.
- **Greek, Arabic or other scripts show as boxes** — wrap them in `<noto>…</noto>` tags in the TXT file.

---

## Tips for Best Results

1. **Be Specific About Language Origins**: Instead of just "from Latin," write "from Latin <i>exemplum</i> meaning 'a sample'" — richer context makes the entry more engaging
2. **Include Historical Development**: Show how the word's meaning evolved over time
3. **Add Interesting Facts**: Etymology trivia makes the entries more engaging
4. **Use Multiple Paragraphs**: Break up long etymology sections with double line breaks for readability — each paragraph gets its own visual block in the right column
5. **Verify IPA**: Double-check pronunciation symbols for accuracy
6. **Style Foreign Words**: Put `<i>…</i>` around foreign-language words and glossed terms in the etymology; use `<b>` and `<u>` sparingly, and always close every tag in the same paragraph
7. **Non-Latin Script**: Use `<noto>…</noto>` tags around Greek, Arabic, Hebrew, Cyrillic, and similar characters so they render with the correct Unicode font; transliterated text in plain Latin letters does not need tags
8. **Don't Add Quotes Around Usage**: The renderer automatically wraps usage examples in `"…"` — if you add them yourself, they will be double-quoted in the output
9. **Word Forms Are Optional**: Only include `WORD_FORMS` when the word has genuinely useful derived forms worth showing; skip the field for words without notable variants rather than padding it out
10. **Let the Mood Drive the Colour**: Choose the primary colour from the word's emotional tone, not just its literal meaning, and prefer deriving secondary and tertiary colours from the harmony rather than inventing them
11. **One Saturated Primary Is Enough**: A single clear base colour plus a harmony mode produces a more cohesive result than several hand-picked hex codes
