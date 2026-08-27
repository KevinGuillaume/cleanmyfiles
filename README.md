# Clean My Files
A simple script to clean your directories and organize them.

It scans a source folder, sorts files into subfolders by type (Images, Documents, Audio, Videos, Archives, Other), and flags any duplicate files it finds by content (not just filename) along the way. Duplicate detection and file organizing both run concurrently using Python's `threading`.

## How to Install

No external dependencies, so everything used is in the Python standard library. Just make sure you have Python 3.10+ installed, then clone/download this repo.

## How to Run

```
python3 main.py [source] [--dest DEST] [--move]
```

- `source` (optional) — the directory to organize. Defaults to `test_files/incoming/` if omitted.
- `--dest DEST` (optional) — where organized files go. Defaults to `test_files/organized/`.
- `--move` (optional) — move files instead of copying them (see below).

Examples:

```
python3 main.py                                   # organize the built-in sandbox folder
python3 main.py ~/Downloads                       # organize ~/Downloads into test_files/organized/
python3 main.py ~/Downloads --dest ~/Desktop/Sorted   # organize into a custom destination
python3 main.py ~/Downloads --dest ~/Desktop/Sorted --move   # move instead of copy
```

By default, files are copied into the destination, leaving originals untouched. Any duplicate file groups (identical content, different names) are printed before organizing starts.

Copying is the default and recommended mode — it's non-destructive, so a bug or an interrupted run can't lose files. Only use `--move` once you've confirmed a run without the flag organizes things the way you expect.

## Customization

- **Categories** — edit the `CATEGORIES` dict at the top of `main.py` to add extensions or change which folder name a given extension maps to. Anything not listed falls into `Other`.
- **Worker count** — `organize_all_files(..., num_workers=4)` controls how many threads process files concurrently; `find_duplicates` uses a fixed pool of 8 for hashing. Adjust either if you're working with a very large or very small number of files.
