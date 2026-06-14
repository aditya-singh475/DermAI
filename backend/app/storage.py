"""Local image storage — no cloud services."""

import os
import uuid
from pathlib import Path

from .config import get_settings


def get_upload_dir() -> Path:
    settings = get_settings()
    path = Path(settings.UPLOAD_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_user_image(username: str, image_bytes: bytes, original_filename: str) -> str:
    """Save uploaded image locally. Returns relative path from upload dir."""
    ext = _safe_extension(original_filename)
    user_dir = get_upload_dir() / _safe_username(username)
    user_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}{ext}"
    full_path = user_dir / filename
    full_path.write_bytes(image_bytes)

    return str(Path(_safe_username(username)) / filename)


def resolve_image_path(relative_path: str) -> Path | None:
    """Resolve stored relative path to absolute path if it exists."""
    if not relative_path:
        return None
    full = get_upload_dir() / relative_path
    if full.is_file():
        return full
    return None


def _safe_username(username: str) -> str:
    safe = "".join(c for c in username if c.isalnum() or c in "-_")
    return safe or "user"


def _safe_extension(filename: str) -> str:
    name = (filename or "").lower()
    if name.endswith(".png"):
        return ".png"
    if name.endswith(".jpeg"):
        return ".jpeg"
    return ".jpg"
