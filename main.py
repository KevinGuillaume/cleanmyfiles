import shutil
from pathlib import Path

CATEGORIES = {
    ".jpg": "Images", 
    ".jpeg": "Images", 
    ".png": "Images", 
    ".gif": "Images",
    ".pdf": "Documents", 
    ".docx": "Documents", 
    ".txt": "Documents",
    ".mp3": "Audio",
    ".wav": "Audio",
    ".mp4": "Videos", 
    ".mov": "Videos",
    ".zip": "Archives",
    ".tar": "Archives",
}


def scan_directory(source: Path) -> list[Path]:
    """Return every file (not subdirectory) directly inside `source`."""
    files = []
    for file in source.iterdir():
        if file.is_file():
            files.append(file)

    return files


def categorize(file_path: Path) -> str:
    """Map a file's extension to a category name, defaulting to 'Other'."""
    suffix = file_path.suffix
    category = CATEGORIES.get(suffix, "Other")

    return category


def organize_file(file_path: Path, dest_root: Path) -> None:
    """Copy file_path into dest_root/<category>/, creating the folder if needed."""
    folder = categorize(file_path=file_path)
    dest_folder = dest_root / folder
    dest_folder.mkdir(parents=True, exist_ok= True)
    shutil.copy2(file_path,dest_folder)

    return


def main():
    source = Path("test_files/incoming")
    dest = Path("test_files/organized")

    files = scan_directory(source)
    for f in files:
        organize_file(f, dest)

    print(f"Organized {len(files)} files into {dest}")


if __name__ == "__main__":
    main()
