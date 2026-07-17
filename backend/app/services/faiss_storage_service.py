"""
Supabase Storage service for per-user FAISS indices.

FAISS indices are stored per authenticated user under::

    FAISS/<user_uid>/
        index.faiss
        index.pkl

Uploads use upsert=True so a new upload replaces the previous index.
"""

import logging
import shutil
import tempfile
from pathlib import Path

from supabase import create_client

from app.core.config import settings

logger = logging.getLogger(__name__)


class FaissStorageService:
    """Manages per-user FAISS indices in the Supabase FAISS bucket."""

    FAISS_FILES = ["index.faiss", "index.pkl"]

    def __init__(self) -> None:
        self._client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY,
        )
        self._bucket = settings.SUPABASE_FAISS_BUCKET
        logger.debug("FaissStorageService initialized: bucket=%s", self._bucket)

    # ------------------------------------------------------------------
    # Remote path helpers
    # ------------------------------------------------------------------

    def _remote_path(self, user_uid: str, filename: str) -> str:
        """Return the full storage path for a user's FAISS file."""
        return f"{user_uid}/{filename}"

    # ------------------------------------------------------------------
    # Upload / Download / Delete / Exists
    # ------------------------------------------------------------------

    def upload_user_index(self, user_uid: str, local_dir: str | Path) -> None:
        """
        Upload a user's FAISS index files from a local directory to Supabase Storage.

        Only files that exist locally are uploaded. Missing files are logged
        as warnings and skipped.

        Args:
            user_uid: The Supabase user UUID.
            local_dir: Path to a directory containing index.faiss and index.pkl.

        Raises:
            Exception: If any upload fails.
        """
        local_dir = Path(local_dir)
        for filename in self.FAISS_FILES:
            local_file = local_dir / filename
            if not local_file.exists():
                logger.warning(
                    "FAISS file not found for upload (skipping): bucket=%s, path=%s, local=%s",
                    self._bucket,
                    self._remote_path(user_uid, filename),
                    local_file,
                )
                continue

            remote = self._remote_path(user_uid, filename)
            logger.info(
                "Uploading FAISS file: bucket=%s, remote=%s, local=%s",
                self._bucket,
                remote,
                local_file,
            )

            with open(local_file, "rb") as f:
                self._client.storage.from_(self._bucket).upload(
                    path=remote,
                    file=f.read(),
                    file_options={"upsert": "true"},
                )

            logger.info(
                "FAISS file uploaded: bucket=%s, remote=%s, size=%d",
                self._bucket,
                remote,
                local_file.stat().st_size,
            )

    def download_user_index(self, user_uid: str, local_dir: str | Path) -> None:
        """
        Download a user's FAISS index files from Supabase Storage to a local directory.

        Args:
            user_uid: The Supabase user UUID.
            local_dir: Path to a directory where files will be written.

        Raises:
            FileNotFoundError: If any required FAISS file does not exist remotely.
            Exception: If any download fails.
        """
        local_dir = Path(local_dir)
        local_dir.mkdir(parents=True, exist_ok=True)

        for filename in self.FAISS_FILES:
            remote = self._remote_path(user_uid, filename)
            local_file = local_dir / filename

            try:
                logger.info(
                    "Downloading FAISS file: bucket=%s, remote=%s, local=%s",
                    self._bucket,
                    remote,
                    local_file,
                )
                data = self._client.storage.from_(self._bucket).download(remote)

                with open(local_file, "wb") as f:
                    f.write(data)

                logger.info(
                    "FAISS file downloaded: bucket=%s, remote=%s, size=%d",
                    self._bucket,
                    remote,
                    len(data),
                )
            except Exception as e:
                logger.error(
                    "Failed to download FAISS file: bucket=%s, remote=%s, error=%s",
                    self._bucket,
                    remote,
                    e,
                )
                raise FileNotFoundError(
                    f"FAISS file not found in storage: {self._bucket}/{remote}"
                ) from e

    def delete_user_index(self, user_uid: str) -> None:
        """
        Delete a user's entire FAISS index from Supabase Storage.

        Errors are logged but not raised, making this safe for non-critical
        cleanup operations.

        Args:
            user_uid: The Supabase user UUID.
        """
        paths = [self._remote_path(user_uid, f) for f in self.FAISS_FILES]
        try:
            self._client.storage.from_(self._bucket).remove(paths)
            logger.info(
                "Deleted FAISS index for user: bucket=%s, user=%s",
                self._bucket,
                user_uid,
            )
        except Exception as e:
            logger.warning(
                "Failed to delete FAISS index for user %s: %s",
                user_uid,
                e,
            )

    def index_exists(self, user_uid: str) -> bool:
        """
        Check whether a user has a FAISS index in Supabase Storage.

        Uses storage.info() on the index.faiss file. Returns False for any
        error (file not found, network issue, etc.) rather than raising.

        Args:
            user_uid: The Supabase user UUID.

        Returns:
            True if index.faiss exists for this user, False otherwise.
        """
        remote = self._remote_path(user_uid, "index.faiss")
        try:
            self._client.storage.from_(self._bucket).info(remote)
            logger.debug("FAISS index exists: bucket=%s, path=%s", self._bucket, remote)
            return True
        except Exception as e:
            logger.debug(
                "FAISS index not found: bucket=%s, path=%s, error=%s",
                self._bucket,
                remote,
                e,
            )
            return False

    # ------------------------------------------------------------------
    # Temporary directory helpers
    # ------------------------------------------------------------------

    @staticmethod
    def create_temp_dir() -> Path:
        """Create and return a temporary directory for FAISS operations."""
        temp_dir = Path(tempfile.mkdtemp(prefix="faiss_"))
        logger.debug("Created temp directory: %s", temp_dir)
        return temp_dir

    @staticmethod
    def cleanup_temp_dir(temp_dir: str | Path) -> None:
        """
        Remove a temporary directory and all of its contents.

        Failures are logged as warnings but do not raise, so callers can
        safely use this in a finally block without masking prior exceptions.
        """
        try:
            shutil.rmtree(temp_dir)
            logger.debug("Cleaned up temp directory: %s", temp_dir)
        except Exception as e:
            logger.warning(
                "Failed to clean up temp directory %s: %s",
                temp_dir,
                e,
            )
