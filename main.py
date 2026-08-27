import argparse
import hashlib
import shutil
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor
import queue

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
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
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


def organize_file(file_path: Path, dest_root: Path, move: bool = False) -> None:
    """Copy (or move, if move=True) file_path into dest_root/<category>/, creating the folder if needed."""
    folder = categorize(file_path=file_path)

    with stats_lock:
        if folder in stats:
            stats[folder] += 1
        else:
            stats[folder] = 1


    dest_folder = dest_root / folder
    dest_folder.mkdir(parents=True, exist_ok= True)
    if move:
        shutil.move(file_path,dest_folder)
    else:
        shutil.copy2(file_path,dest_folder)
    return

def worker(q: queue.Queue, dest_root: Path, move: bool = False) -> None:
    while True:
        file_path = q.get()
        if file_path is None:
            q.task_done()
            break
        organize_file(file_path, dest_root,move)
        q.task_done()

def organize_all_files(files: list[Path], dest_root: Path, move: bool = False, num_workers=4):
    q = queue.Queue()
    for f in files:
        q.put(f)
    workers = [threading.Thread(target=worker,args=(q,dest_root,move)) for _ in range(num_workers)]
    for w in workers:
        w.start()

    q.join()

    for _ in range(num_workers):
        q.put(None)

    for w in workers:
        w.join()


def main():
    parser = argparse.ArgumentParser(description="Organize files by type.")
    parser.add_argument("source", nargs="?", default="test_files/incoming",
                         help="Directory to organize (default: test_files/incoming)")
    parser.add_argument("--dest", default="test_files/organized",
                         help="Directory to organize files into (default: test_files/organized)")
    parser.add_argument("--move", action="store_true", help="Move files instead of copying (default: copy)")
    args = parser.parse_args()

    source = Path(args.source)
    dest = Path(args.dest)

    if not source.is_dir():
        print(f"Error: source directory does not exist: {source}")
        return

    files = scan_directory(source)

    dupes = find_duplicates(files)
    for d,v in dupes.items():
        print(v)

    organize_all_files(files, dest, move=args.move)

    action = "Moved" if args.move else "Organized"
    print(f"{action} {len(files)} files into {dest}")
    for category, count in sorted(stats.items()):
        print(f"  {category}: {count}")


if __name__ == "__main__":
    main()
