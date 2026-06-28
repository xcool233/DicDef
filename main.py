"""
Command-line interface for the dictionary image generator with random theme support.
"""

import argparse
from argparse import ArgumentParser, Namespace
from dictionary_generator import DictionaryImageGenerator
from dictionary_data import parse_txt_file


def create_sample_file(output_path: str = "sample_word.txt") -> None:
    """Create a sample TXT file for testing."""
    sample_content = """WORD: serendipity
PRONUNCIATION: ˌsɛrənˈdɪpɪti

DEFINITION: The occurrence and development of events by chance in a happy or beneficial way
PART_OF_SPEECH: noun
USAGE: A fortunate stroke of serendipity brought the old friends together after decades apart

DEFINITION: A pleasant surprise; an instance of finding something good or useful while not specifically searching for it
PART_OF_SPEECH: noun
USAGE: The discovery of penicillin was a famous example of serendipity in science

SYNONYMS: chance, fortune, luck, providence, fate

ETYMOLOGY: Coined by Horace Walpole in 1754, from the Persian fairy tale "The Three Princes of Serendip"

ADDITIONAL_ETYMOLOGY: The princes in the tale were always making discoveries by accidents and sagacity of things they were not in quest of

HISTORICAL_USAGE: The term has been increasingly used in scientific contexts since the mid-20th century to describe accidental discoveries
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        _ = f.write(sample_content.strip())
    
    print(f"Sample file created: {output_path}")


def main() -> None:
    parser: ArgumentParser = argparse.ArgumentParser(
        description="Generate dictionary definition images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i word.txt
  %(prog)s -i word.txt -o custom_name.png
  %(prog)s -i word.txt --light --width 1000
  %(prog)s -i word.txt --random-theme
  %(prog)s -i word.txt --random-theme --seed 42
  %(prog)s --sample  # Create sample input file
        """
    )
    
    _ = parser.add_argument("--input", "-i", help="Input TXT file path")
    _ = parser.add_argument("--output", "-o", default=None, 
                        help="Output image path (default: word from file + .png)")
    _ = parser.add_argument("--dark", "-d", action="store_true", default=True, 
                        help="Use dark mode (default)")
    _ = parser.add_argument("--light", "-l", action="store_true", 
                        help="Use light mode instead of dark mode")
    _ = parser.add_argument("--random-theme", "-r", action="store_true",
                        help="Generate a random color theme using OKLAB color space")
    _ = parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducible random themes")
    _ = parser.add_argument("--font", "-f", help="Custom font file path for main text")
    _ = parser.add_argument("--ipa-font", help="Custom font file path for IPA pronunciation")
    _ = parser.add_argument("--font-size", "-s", type=int, default=24, 
                        help="Font size (default: 24)")
    _ = parser.add_argument("--width", "-w", type=int, default=1400, 
                        help="Image width (default: 800)")
    _ = parser.add_argument("--sample", action="store_true", 
                        help="Create sample TXT file and exit")

    args: Namespace = parser.parse_args()

    # Handle sample file creation
    if args.sample:
        create_sample_file()
        return

    # Validate input
    if not args.input:
        parser.error("Please provide an input file with --input or create a sample with --sample")

    try:
        # Parse the file first to get the word
        data = parse_txt_file(args.input)
        
        # Determine output filename
        if args.output:
            output_path = args.output
        else:
            # Use the word as the filename, capitalize first letter
            word = data.word.strip()
            if word:
                # Capitalize first letter and make safe for filename
                output_path = word[0].upper() + word[1:] + ".png"
            else:
                output_path = "dictionary_definition.png"
        
        # Create generator
        generator: DictionaryImageGenerator = DictionaryImageGenerator(
            dark_mode=not args.light,  # Dark mode unless --light is specified
            random_theme=args.random_theme,
            theme_seed=args.seed,
            font_path=args.font,
            ipa_font_path=args.ipa_font,
            font_size=args.font_size
        )

        # Generate image from parsed data
        _ = generator.generate_image_from_data(
            data=data,
            width=args.width,
            output_path=output_path
        )
        
        if args.random_theme:
            seed_info = f" (seed: {args.seed})" if args.seed else " (random seed)"
            print(f"Generated with random theme{seed_info}")

    except FileNotFoundError:
        print(f"Error: File '{args.input}' not found")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()