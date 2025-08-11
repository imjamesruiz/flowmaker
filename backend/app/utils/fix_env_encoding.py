import os
import shutil
import tempfile
import time
from typing import Optional


def _resolve_env_path(explicit_path: Optional[str] = None) -> str:
    if explicit_path:
        return os.path.abspath(explicit_path)

    # 1) Try CWD
    cwd_path = os.path.abspath(os.path.join(os.getcwd(), ".env"))
    if os.path.exists(cwd_path):
        return cwd_path

    # 2) Try backend root (parent of this file's directory's parent: app/ -> backend/)
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    backend_env = os.path.join(backend_root, ".env")
    if os.path.exists(backend_env):
        return backend_env

    # Default fallback (CWD)
    return cwd_path


def _read_with_best_effort(raw_bytes: bytes) -> str:
    # Try common encodings, including BOM-handling variants
    candidate_encodings = (
        "utf-8",       # strict UTF-8
        "utf-8-sig",   # UTF-8 with BOM
        "utf-16",      # UTF-16 with BOM autodetect
        "utf-16-le",
        "utf-16-be",
        "utf-32",
    )

    last_error: Optional[Exception] = None
    for enc in candidate_encodings:
        try:
            return raw_bytes.decode(enc)
        except Exception as exc:  # keep trying
            last_error = exc

    # If everything failed, re-raise the last error
    if last_error:
        raise last_error

    # Fallback (should never reach)
    return raw_bytes.decode("utf-8")


def fix_env_file_encoding(env_path: Optional[str] = None) -> str:
    """
    Reads the .env file even if it has a BOM or is UTF-16, and rewrites it
    as UTF-8 without BOM. Writes to a temp file, creates a .env.bak backup,
    then swaps in place with retries to mitigate file-lock issues on Windows.

    Returns the absolute path of the .env file that was fixed.
    """
    path = _resolve_env_path(env_path)

    if not os.path.exists(path):
        # Nothing to fix
        return path

    # Backup first
    backup_path = f"{path}.bak"
    shutil.copyfile(path, backup_path)

    # Read raw bytes and decode with best effort
    with open(path, "rb") as f:
        raw = f.read()

    text = _read_with_best_effort(raw)

    # Write to a temp file in the same directory to allow atomic replace
    directory = os.path.dirname(path)
    fd, temp_path = tempfile.mkstemp(prefix=".env_", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as tmp:
            tmp.write(text)

        # Try replacing the original file with retries (handles transient locks)
        max_attempts = 10
        for attempt in range(1, max_attempts + 1):
            try:
                os.replace(temp_path, path)  # atomic on Windows and POSIX
                print("✅ .env file encoding fixed and saved as UTF-8 without BOM.")
                break
            except PermissionError:
                if attempt == max_attempts:
                    raise
                time.sleep(0.5)
    finally:
        # If replacement succeeded, temp_path no longer exists.
        # If it failed with an exception other than PermissionError retries, cleanup.
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

    return path


