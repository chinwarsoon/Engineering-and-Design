"""
Streaming File Hash Utility — common.library.utility.file_hash.

Provides content-based file hashing with configurable algorithm and buffer
size. Designed as the SSOT (Single Source of Truth) for all hash computations
across eks, dcc, and code_tracer projects.

Revision: 0.1
Date: 2026-07-19
Author: CodeBuddy
Summary: Initial extraction from eks.engine.core.file_property_parser._compute_hash()
         (T1.99.147 — I187). Replaces 3 separate hash implementations with one
         canonical source.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional

__all__ = ["compute_file_hash", "FileHasher"]


def compute_file_hash(
    file_path: str | Path,
    algorithm: str = "sha256",
    buffer_size: int = 65536,
) -> str:
    """
    Compute the content hash of a file using streaming reads.

    Args:
        file_path: Path to the file to hash.
        algorithm: Hash algorithm name (e.g. "sha256", "md5", "sha512").
        buffer_size: Read chunk size in bytes (default 64 KB).

    Returns:
        Hex-encoded digest string.

    Raises:
        FileNotFoundError: If file_path does not exist.
        ValueError: If algorithm is not supported by hashlib.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    try:
        h = hashlib.new(algorithm)
    except ValueError as exc:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}") from exc

    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(buffer_size)
            if not chunk:
                break
            h.update(chunk)

    return h.hexdigest()


class FileHasher:
    """
    Configurable file-content hasher with algorithm selection and verification.

    Encapsulates ``compute_file_hash`` for repeated use with the same settings.
    Provides ``verify()`` to check an expected hash against actual file content.

    Example::

        hasher = FileHasher(algorithm="sha256")
        digest = hasher.hash_file("/data/doc.pdf")
        assert hasher.verify("/data/doc.pdf", digest)
    """

    def __init__(self, algorithm: str = "sha256", buffer_size: int = 65536):
        """
        Args:
            algorithm: Default hash algorithm (e.g. "sha256", "md5").
            buffer_size: Read chunk size in bytes.
        """
        self.algorithm = algorithm
        self.buffer_size = buffer_size

    def hash_file(self, file_path: str | Path) -> str:
        """Compute the content hash for *file_path* using the configured algorithm."""
        return compute_file_hash(file_path, algorithm=self.algorithm, buffer_size=self.buffer_size)

    def hash_bytes(self, data: bytes) -> str:
        """Compute the content hash for a raw bytes buffer."""
        h = hashlib.new(self.algorithm)
        h.update(data)
        return h.hexdigest()

    def verify(self, file_path: str | Path, expected_hash: str) -> bool:
        """
        Return ``True`` if the actual file hash matches *expected_hash*.

        Uses a constant-time comparison to avoid timing attacks on hash strings.
        """
        actual = self.hash_file(file_path)
        return _constant_time_compare(actual, expected_hash)


def _constant_time_compare(a: str, b: str) -> bool:
    """Constant-time string comparison for hash verification."""
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a, b):
        result |= ord(x) ^ ord(y)
    return result == 0
