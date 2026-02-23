I have a dictionary image generator program that creates visual dictionary entries. I need you to create a properly formatted entry for the word **[WORD]**.

### Required Format Specifications:

**File Structure:**
```
WORD: [word]
PRONUNCIATION: [IPA pronunciation]

DEFINITION: [definition text]
PART_OF_SPEECH: [noun/verb/adjective/adverb/etc.]
USAGE: [example sentence]

DEFINITION: [second definition if applicable]
PART_OF_SPEECH: [part of speech]
USAGE: [example sentence]

SYNONYMS: [comma-separated list]

ETYMOLOGY: [primary etymology paragraph]

ADDITIONAL_ETYMOLOGY: [detailed etymology with multiple paragraphs if needed]
```

**Important Requirements:**

1. **Pronunciation**: Use IPA (International Phonetic Alphabet) format
2. **Multiple Definitions**: Include 1-3 definitions if the word has multiple meanings
3. **Part of Speech**: Label each definition (noun, verb, adjective, adverb, etc.)
4. **Usage Examples**: Provide realistic, natural example sentences for each definition
5. **Synonyms**: Include 3-5 relevant synonyms as a comma-separated list
6. **Etymology**: 
   - Primary etymology paragraph explaining the word's origin
   - Additional etymology with deeper historical context, development over time, and interesting linguistic details
   - **IMPORTANT**: Mention origin languages explicitly (e.g., "from Latin", "Greek origin", "Old French") as the program automatically detects these and creates colored language badges

7. **Language Origin Badges**: The program will automatically detect and display colored badges for languages mentioned in the etymology, including:
   - Latin, Greek, Old English, Middle English, French, German, Sanskrit, Arabic, Hebrew, Italian, Spanish, Dutch, Norse, Celtic, Persian, Portuguese, and more

8. **No Antonyms**: Do not include an ANTONYMS field (this feature has been removed)

**Additional Context:**
- The output will be rendered as a professional two-column image
- Left column shows: word, pronunciation, language badges, definitions, and synonyms
- Right column shows: detailed etymology
- Use paragraph breaks in ADDITIONAL_ETYMOLOGY (double line breaks) for better readability

Please format the entry for **[WORD]** following these specifications exactly.

---

## Quick Reference Template

For your reference, here's the basic structure:

```
WORD: example
PRONUNCIATION: ɪɡˈzæmpəl

DEFINITION: A thing characteristic of its kind or illustrating a general rule
PART_OF_SPEECH: noun
USAGE: This painting is a perfect example of the Impressionist style.

SYNONYMS: instance, case, illustration, specimen, sample

ETYMOLOGY: From Old French "example," from Latin "exemplum" meaning "a sample"

ADDITIONAL_ETYMOLOGY: The Latin "exemplum" derives from "eximere" (to take out, remove), from "ex-" (out) + "emere" (to take). The word entered English in the late 14th century with the meaning "an instance serving for illustration." The verb form developed in the 15th century.
```

---

## Tips for Best Results

1. **Be Specific About Language Origins**: Instead of just "from Latin," try "from Latin 'word' meaning 'translation'" - this provides richer context
2. **Include Historical Development**: Show how the word's meaning evolved over time
3. **Add Interesting Facts**: Etymology trivia makes the entries more engaging
4. **Use Multiple Paragraphs**: Break up long etymology sections for readability
5. **Verify IPA**: Double-check pronunciation symbols for accuracy
