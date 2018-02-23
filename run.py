"""Runs generator to create character image dataset.

This script assumes that the fonts have already been obtained using scraper.
"""

import argparse
import colorama

from src.generator import CharImageGenerator


def main():
    # Initialize colored output
    colorama.init()

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--charset',
        help="Path to a file containing characters to be turned into images, separated by newlines."
    )

    parser.add_argument(
        '--font-dir',
        help="Path to a directory containing font files (obtained by scraper), separated by newlines."
    )

    parser.add_argument(
        '-p', '--prefix',
        help="If provided, generated directory will be prefixed with the value of `prefix`."
    )

    args = parser.parse_args()

    gen = CharImageGenerator.load(charset_path=args.charset, fonts_path=args.font_dir, out_dir=args.prefix)

    print(f"{colorama.Fore.YELLOW}Creating sprite sheets ...")
    gen.create_sprites()  # Generates sprite sheets as a preview of fonts - no augmentation performed
    print(f"{colorama.Fore.GREEN}Sprite sheets have been created successfully.")

    print(f"{colorama.Fore.YELLOW}Generating character images ...")
    gen.create_and_save_charsets(test_train_split=True)  # Also creates default charset dir if not existent
    print(f"{colorama.Fore.GREEN}Image generation completed successfully.")


if __name__ == '__main__':
    main()
