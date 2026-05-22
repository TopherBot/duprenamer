# dupRenamer

**Zero‑dependency, single‑file Python CLI** that **detects duplicate files** in a directory and **auto‑renames** them with a numeric suffix.

---

## Features (tiny & quick)
- 📂 Scan a folder recursively.
- 🧬 Detect duplicates using SHA‑256 hash (fast & collision‑resistant).
- ✏️ Auto‑rename duplicates to `original (1).ext`, `original (2).ext`, …
- 🚀 One‑line install via `pipx` or `python -m pip install .`
- ✅ Full test suite (pytest) and linting (ruff) run on **GitHub Actions**.
- 🔐 Security scan (Trivy) and dependency review baked into CI.

---

## Installation
```bash
# Using pipx (recommended – isolates the CLI)
pipx install git+https://github.com/your‑org/duprenamer.git

# Or regular pip install for a virtualenv / global install
python -m pip install git+https://github.com/your‑org/duprenamer.git
```

---

## Usage
```bash
# Scan the current directory
duprenamer .

# Scan a specific path, quiet mode (only prints renames)
duprenamer /path/to/files --quiet
```

### Options
| Flag | Description |
|------|-------------|
| `-h`, `--help` | Show help message |
| `-q`, `--quiet` | Suppress the summary table |
| `-d`, `--dry-run` | Show what would be renamed **without** touching the filesystem |
| `-v`, `--verbose` | Show each file processed |

---

## How it works (in a nutshell)
1. Walk the directory tree (`os.scandir`).
2. Compute a SHA‑256 hash for every file (read in 64 KB chunks).  
3. Store `hash → [paths]` mapping.
4. When more than one path shares a hash, generate a new unique name for the later entries and rename them via `os.replace` (atomic on the same filesystem).
5. Print a concise table of actions taken.

---

## Development
```bash
# Clone & create a venv
git clone https://github.com/your‑org/duprenamer.git
cd duprenamer
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]

# Run tests & lint locally
pytest -q
ruff check duprenamer.py
```

---

## CI/CD (GitHub Actions) – tiny but complete
The repository ships a **single workflow** that:
1. **Checks out** the code.
2. **Sets up Python** (3.11).
3. **Installs** the package in editable mode with dev extras.
4. **Runs ruff** linting.
5. **Runs pytest** (requires ≥80 % coverage).
6. **Runs Trivy** to scan the source tree for known CVEs.
7. **Posts a summary** badge to the PR.

The workflow is pinned to full commit SHAs for maximum security.

---

## License
MIT – see `LICENSE`.

---

*Feel free to fork, open an issue, or submit a PR. The CI will automatically enforce lint, test, and security standards.*