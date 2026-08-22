import hashlib
import shutil
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor

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

stats = {}
stats_lock = threading.Lock()

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


def hash_file(file_path: Path) -> str:
    """Return the sha256 hex digest of a file's contents."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def find_duplicates(files: list[Path]) -> dict[str, list[Path]]:
    """Hash all files concurrently, group by hash, return only groups with 2+ files."""
    with ThreadPoolExecutor(max_workers=8) as executor:
        hashes = executor.map(hash_file, files)
        pairs = zip(files,hashes)
        res = {}
        # Pair[0] = path
        # Pair[1] = hash
        for pair in pairs:
            res.setdefault(pair[1], []).append(pair[0])

        dupe_dict = {}
        for hash,items in res.items():
            if len(items) > 1:
                dupe_dict[hash] = items
        return dupe_dict


def organize_file(file_path: Path, dest_root: Path) -> None:
    """Copy file_path into dest_root/<category>/, creating the folder if needed."""
    folder = categorize(file_path=file_path)

    with stats_lock:
        if folder in stats:
            stats[folder] += 1
        else:
            stats[folder] = 1


    dest_folder = dest_root / folder
    dest_folder.mkdir(parents=True, exist_ok= True)
    shutil.copy2(file_path,dest_folder)

    return


def main():
    source = Path("test_files/incoming")
    dest = Path("test_files/organized")

    files = scan_directory(source)

    dupes = find_duplicates(files)
    for d,v in dupes.items():
        print(v)

    threads = [threading.Thread(target=organize_file, args=(f,dest)) for f in files]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"Organized {len(files)} files into {dest}")
    for category, count in sorted(stats.items()):
        print(f"  {category}: {count}")


if __name__ == "__main__":
    main()
