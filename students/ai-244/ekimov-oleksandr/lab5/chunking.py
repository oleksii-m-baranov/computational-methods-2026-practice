"""Завантаження документів та розбиття їх на чанки для лабораторної роботи № 5."""

from pathlib import Path
from typing import Any
import re

try:
    import config
except ImportError:
    config = None


def _cfg(name: str, default: Any) -> Any:
    if config is not None and hasattr(config, name):
        return getattr(config, name)
    return default


def load_documents(doc_dirs: list[str] | tuple[str, ...] | None = None) -> list[dict[str, Any]]:
    """Завантажує текстові документи з указаних каталогів (по замовчуванню config.DOC_DIRS)."""
    dirs = doc_dirs if doc_dirs is not None else _cfg("DOC_DIRS", ["data/corpus", "data/docs"])
    documents: list[dict[str, Any]] = []
    seen_paths: set[Path] = set()

    for raw_dir in dirs:
        base_path = Path(raw_dir)
        if not base_path.exists() or not base_path.is_dir():
            continue

        for file_path in sorted(base_path.rglob("*.txt")):
            resolved = file_path.resolve()
            if resolved in seen_paths or not file_path.is_file():
                continue
            seen_paths.add(resolved)

            raw_text = file_path.read_text(encoding="utf-8")
            normalized = raw_text.replace("\r\n", "\n").replace("\r", "\n").strip()
            if not normalized:
                continue

            lines = normalized.split("\n")
            title = lines[0].strip() if lines else file_path.stem

            body_start = 1
            while body_start < len(lines) and not lines[body_start].strip():
                body_start += 1
            body = "\n".join(lines[body_start:]).strip() if body_start < len(lines) else normalized

            documents.append(
                {
                    "id": file_path.stem,
                    "path": str(file_path),
                    "title": title,
                    "text": body if body else normalized,
                    "raw_text": normalized,
                }
            )

    return documents


def split_fixed(text: str, size: int, overlap: int = 0) -> list[str]:
    """Розбиває текст на чанки фіксованого розміру з перекриттям."""
    step = max(1, int(size) - max(0, int(overlap)))
    chunk_len = max(1, int(size))
    parts: list[str] = []

    for start in range(0, len(text), step):
        piece = text[start : start + chunk_len]
        if piece:
            parts.append(piece)
        if start + chunk_len >= len(text):
            break

    return parts


def split_paragraphs(text: str, size: int) -> list[str]:
    """Групує абзаци у чанки не довше вказаного розміру в символах."""
    limit = max(1, int(size))
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", text.strip()) if p.strip()]
    parts: list[str] = []
    current = ""

    for para in paragraphs:
        if not current:
            if len(para) <= limit:
                current = para
            else:
                parts.extend(split_fixed(para, limit, 0))
        else:
            if len(current) + 2 + len(para) <= limit:
                current = f"{current}\n\n{para}"
            else:
                parts.append(current)
                if len(para) <= limit:
                    current = para
                else:
                    parts.extend(split_fixed(para, limit, 0))
                    current = ""

    if current:
        parts.append(current)

    return parts


def _split_paragraphs(text: str) -> list[str]:
    """Розбиває текст на непорожні абзаци."""
    parts = re.split(r"\n\s*\n+", text.strip())
    paragraphs = [re.sub(r"[ \t]+", " ", p).strip() for p in parts if p and p.strip()]
    return paragraphs


def _split_fixed(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Розбиває текст на чанки фіксованого розміру з перекриттям."""
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []

    size = max(1, int(chunk_size))
    step = max(1, size - max(0, int(overlap)))
    chunks: list[str] = []

    for start in range(0, len(cleaned), step):
        piece = cleaned[start : start + size].strip()
        if piece:
            chunks.append(piece)
        if start + size >= len(cleaned):
            break

    return chunks


def _pack_paragraphs(paragraphs: list[str], max_chars: int) -> list[str]:
    """Групує послідовні абзаци в чанки до межі max_chars символів."""
    limit = max(1, int(max_chars))
    packed: list[str] = []
    current: list[str] = []
    current_len = 0

    for para in paragraphs:
        para_len = len(para)
        if para_len > limit:
            if current:
                packed.append("\n\n".join(current))
                current = []
                current_len = 0
            packed.extend(_split_fixed(para, limit, 0))
            continue

        sep_len = 2 if current else 0
        if current_len + sep_len + para_len <= limit:
            current.append(para)
            current_len += sep_len + para_len
        else:
            packed.append("\n\n".join(current))
            current = [para]
            current_len = para_len

    if current:
        packed.append("\n\n".join(current))

    return packed


def chunk_document(
    doc: dict[str, Any],
    method: str | None = None,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
    with_title: bool | None = None,
) -> list[dict[str, Any]]:
    """Розбиває один документ на чанки з метаданими."""
    chunk_method = (method if method is not None else _cfg("CHUNK_METHOD", "paragraphs")).lower()
    max_chars = chunk_size if chunk_size is not None else _cfg("CHUNK_SIZE", 800)
    overlap = chunk_overlap if chunk_overlap is not None else _cfg("CHUNK_OVERLAP", 0)
    add_title = with_title if with_title is not None else _cfg("WITH_TITLE", False)

    title = doc.get("title", doc.get("id", "document"))
    doc_id = doc.get("id", title)
    source_path = doc.get("path", "")
    text = doc.get("text") or doc.get("raw_text") or ""

    if chunk_method == "fixed":
        raw_chunks = _split_fixed(text, max_chars, overlap)
    else:
        paragraphs = _split_paragraphs(text)
        raw_chunks = _pack_paragraphs(paragraphs, max_chars)

    result: list[dict[str, Any]] = []
    for idx, content in enumerate(raw_chunks):
        final_text = f"{title}\n\n{content}" if add_title and title else content
        result.append(
            {
                "chunk_id": f"{doc_id}_c{idx:02d}",
                "doc_id": doc_id,
                "title": title,
                "path": source_path,
                "chunk_index": idx,
                "text": final_text,
            }
        )

    return result


def chunk_documents(
    documents: list[dict[str, Any]] | None = None,
    method: str | None = None,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
    with_title: bool | None = None,
) -> list[dict[str, Any]]:
    """Розбиває список документів на загальний список чанків."""
    docs = documents if documents is not None else load_documents()
    all_chunks: list[dict[str, Any]] = []
    for doc in docs:
        all_chunks.extend(
            chunk_document(
                doc,
                method=method,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                with_title=with_title,
            )
        )
    return all_chunks