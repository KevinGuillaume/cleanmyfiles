# Clean My Files
A simple script to clean your directories and organize them.

It scans a source folder, sorts files into subfolders by type (Images, Documents, Audio, Videos, Archives, Other), and flags any duplicate files it finds by content (not just filename) along the way. Duplicate detection and file organizing both run concurrently using Python's `threading`.

## How to Install

Requires Python 3.10+. Uses one small dependency ([questionary](https://github.com/tmbo/questionary)) for the interactive copy/move prompt, so set up a virtual environment first:

```
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

## How to Run

```
./venv/bin/python3 main.py [source] [--dest DEST] [--move | --copy]
```

- `source` (optional) — the directory to organize. Defaults to `test_files/incoming/` if omitted.
- `--dest DEST` (optional) — where organized files go. Defaults to `test_files/organized/`.
- `--move` / `--copy` (optional, mutually exclusive) — pick a mode without being prompted. If you pass neither, you'll get an interactive arrow-key menu to choose Copy or Move at runtime.

Examples:

```
./venv/bin/python3 main.py                                          # interactive prompt, sandbox folder
./venv/bin/python3 main.py ~/Downloads                               # interactive prompt, real folder
./venv/bin/python3 main.py ~/Downloads --dest ~/Desktop/Sorted --copy   # non-interactive, for scripts/automation
./venv/bin/python3 main.py ~/Downloads --dest ~/Desktop/Sorted --move   # non-interactive, moves instead of copies
```

By default, files are copied into the destination, leaving originals untouched. Any duplicate file groups (identical content, different names) are printed before organizing starts.

Copying is the safer mode — non-destructive, so a bug or an interrupted run can't lose files. Only choose Move once you've confirmed a Copy run organizes things the way you expect. `--copy` and `--move` are there specifically so this can still run non-interactively (e.g. from a script or cron job) without hanging on the prompt.

## Customization

- **Categories** — edit the `CATEGORIES` dict at the top of `main.py` to add extensions or change which folder name a given extension maps to. Anything not listed falls into `Other`.
- **Worker count** — `organize_all_files(..., num_workers=4)` controls how many threads process files concurrently; `find_duplicates` uses a fixed pool of 8 for hashing. Adjust either if you're working with a very large or very small number of files.
