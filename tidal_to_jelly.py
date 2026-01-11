import argparse
import shutil
import re
import os
import tempfile
from pathlib import Path


def organize_zip(zip_path_str):
    # Convert string path to Path object
    zip_path = Path(zip_path_str).resolve()

    if not zip_path.exists():
        print(f"Error: File not found at {zip_path}")
        return

    # The directory where the zip is located (destination for the new folders)
    output_base_dir = zip_path.parent

    # Regex to parse the filenames based on your provided format:
    # "Artist - Album - Disc-Track Title.ext"
    # Example: "John Medeski - The Curse (...) - 01-01 Fake Tears (...).flac"
    filename_pattern = re.compile(
        r"^(?P<artist>.+?) - (?P<album>.+?) - \d+-(?P<track>\d+) (?P<title>.+)(?P<ext>\.[^.]+)$"
    )

    print(f"Processing: {zip_path.name}")

    # Create a temporary directory for extraction so we don't clutter the downloads folder
    with tempfile.TemporaryDirectory() as temp_dir:
        print("Extracting archive...")
        try:
            shutil.unpack_archive(zip_path, temp_dir)
        except shutil.ReadError:
            print("Error: The file is not a valid zip archive.")
            return

        print("Restructuring files...")

        # Walk through the extracted files (handles cases where zip contains a root folder or not)
        files_moved = 0
        for root, _, files in os.walk(temp_dir):
            for filename in files:
                # Skip hidden files (like .DS_Store)
                if filename.startswith("."):
                    continue

                match = filename_pattern.match(filename)

                if match:
                    # Extract metadata from regex groups
                    artist = match.group("artist").strip()
                    album = match.group("album").strip()
                    track_num = match.group("track")  # Keeps leading zero (e.g., "01")
                    title = match.group("title").strip()
                    ext = match.group("ext")

                    # 1. Create target Directory: Artist/Album
                    target_dir = output_base_dir / artist / album
                    target_dir.mkdir(parents=True, exist_ok=True)

                    # 2. Define new filename: "01 Song Title.ext"
                    new_filename = f"{track_num} {title}{ext}"
                    target_file = target_dir / new_filename

                    # 3. Move the file
                    source_file = Path(root) / filename
                    shutil.move(source_file, target_file)

                    print(f"Saved: {artist}/{album}/{new_filename}")
                    files_moved += 1
                else:
                    # Optional: Handle non-matching files (like cover.jpg or nfo)
                    # For now, we leave them in temp (they get deleted) or you can move them to root
                    pass

        print(f"\nDone! Organized {files_moved} files into: {output_base_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract and organize music zip files."
    )
    parser.add_argument("zipfile", help="Path to the zip file")

    args = parser.parse_args()
    organize_zip(args.zipfile)
