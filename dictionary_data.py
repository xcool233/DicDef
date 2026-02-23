"""
Dictionary data structures and parsing functionality.
"""

from typing import Any


class DictionaryData:
    """Container for dictionary entry data."""
    
    def __init__(self) -> None:
        self.word: str = ""
        self.pronunciation: str = ""
        self.definitions: list[dict[str, str]] = []
        self.synonyms: list[str] = []
        self.etymology: str = ""
        self.additional_etymology: str = ""
        self.origin_languages: list[str] = []  # New: detected origin languages
    
    def get_combined_etymology(self) -> str:
        """Combine etymology and additional etymology into one field."""
        parts = []
        if self.etymology:
            parts.append(self.etymology)
        if self.additional_etymology:
            parts.append(self.additional_etymology)
        return "\n\n".join(parts)
    
    def detect_origin_languages(self) -> None:
        """Detect origin languages from etymology text."""
        combined_text = self.get_combined_etymology().lower()
        
        # Language patterns to detect
        language_patterns = {
            "Latin": ["latin", "from latin"],
            "Greek": ["greek", "from greek"],
            "Old English": ["old english", "anglo-saxon"],
            "Middle English": ["middle english"],
            "French": ["french", "old french", "middle french"],
            "German": ["german", "germanic"],
            "Sanskrit": ["sanskrit"],
            "Arabic": ["arabic"],
            "Hebrew": ["hebrew"],
            "Italian": ["italian"],
            "Spanish": ["spanish"],
            "Dutch": ["dutch"],
            "Norse": ["norse", "old norse", "scandinavian"],
            "Celtic": ["celtic", "gaelic"],
            "Persian": ["persian"],
            "Portuguese": ["portuguese"],
        }
        
        detected = []
        for language, patterns in language_patterns.items():
            if any(pattern in combined_text for pattern in patterns):
                detected.append(language)
        
        self.origin_languages = detected
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format for compatibility."""
        return {
            "word": self.word,
            "pronunciation": self.pronunciation,
            "definitions": self.definitions,
            "synonyms": self.synonyms,
            "etymology": self.get_combined_etymology(),
            "origin_languages": self.origin_languages
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'DictionaryData':
        """Create instance from dictionary data."""
        instance = cls()
        instance.word = data.get("word", "")
        instance.pronunciation = data.get("pronunciation", "")
        instance.definitions = data.get("definitions", [])
        instance.synonyms = data.get("synonyms", [])
        instance.origin_languages = data.get("origin_languages", [])
        # Handle combined etymology or separate fields
        if "etymology" in data and isinstance(data["etymology"], str):
            instance.etymology = data["etymology"]
        else:
            instance.etymology = data.get("etymology", "")
            instance.additional_etymology = data.get("additional_etymology", "")
        return instance


def parse_txt_file(file_path: str) -> DictionaryData:
    """Parse a specially formatted TXT file into dictionary data."""
    data: DictionaryData = DictionaryData()
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content: str = file.read().strip()
    
    lines: list[str] = content.split('\n')
    current_definition = None
    current_field = None
    field_content = []
    
    for line in lines:
        # Check if this is a field header
        if line.startswith("WORD:"):
            if current_field == "ADDITIONAL_ETYMOLOGY":
                data.additional_etymology = '\n'.join(field_content).strip()
                field_content = []
            data.word = line[5:].strip()
            current_field = None
        elif line.startswith("PRONUNCIATION:"):
            if current_field == "ADDITIONAL_ETYMOLOGY":
                data.additional_etymology = '\n'.join(field_content).strip()
                field_content = []
            data.pronunciation = line[14:].strip()
            current_field = None
        elif line.startswith("DEFINITION:"):
            if current_field == "ADDITIONAL_ETYMOLOGY":
                data.additional_etymology = '\n'.join(field_content).strip()
                field_content = []
            if current_definition is not None:
                data.definitions.append(current_definition)
            current_definition = {
                "part_of_speech": "",
                "definition": line[11:].strip(),
                "usage": ""
            }
            current_field = None
        elif line.startswith("PART_OF_SPEECH:"):
            if current_field == "ADDITIONAL_ETYMOLOGY":
                data.additional_etymology = '\n'.join(field_content).strip()
                field_content = []
            if current_definition is not None:
                current_definition["part_of_speech"] = line[16:].strip()
            current_field = None
        elif line.startswith("USAGE:"):
            if current_field == "ADDITIONAL_ETYMOLOGY":
                data.additional_etymology = '\n'.join(field_content).strip()
                field_content = []
            if current_definition is not None:
                current_definition["usage"] = line[6:].strip()
            current_field = None
        elif line.startswith("SYNONYMS:"):
            if current_field == "ADDITIONAL_ETYMOLOGY":
                data.additional_etymology = '\n'.join(field_content).strip()
                field_content = []
            synonyms_text: str = line[9:].strip()
            if synonyms_text:
                data.synonyms = [s.strip() for s in synonyms_text.split(',') if s.strip()]
            current_field = None
        elif line.startswith("ETYMOLOGY:"):
            if current_field == "ADDITIONAL_ETYMOLOGY":
                data.additional_etymology = '\n'.join(field_content).strip()
                field_content = []
            data.etymology = line[10:].strip()
            current_field = None
        elif line.startswith("ADDITIONAL_ETYMOLOGY:"):
            # Start collecting multi-line content
            current_field = "ADDITIONAL_ETYMOLOGY"
            field_content = [line[21:].strip()] if line[21:].strip() else []
        elif line.startswith("NOTE:") or line.startswith("HISTORICAL_USAGE:"):
            if current_field == "ADDITIONAL_ETYMOLOGY":
                data.additional_etymology = '\n'.join(field_content).strip()
                field_content = []
            current_field = None
        else:
            # This is a continuation line
            if current_field == "ADDITIONAL_ETYMOLOGY":
                field_content.append(line)
    
    # Handle any remaining content
    if current_field == "ADDITIONAL_ETYMOLOGY":
        data.additional_etymology = '\n'.join(field_content).strip()
    
    # Add the last definition
    if current_definition is not None:
        data.definitions.append(current_definition)
    
    # Detect origin languages from etymology
    data.detect_origin_languages()
    
    return data