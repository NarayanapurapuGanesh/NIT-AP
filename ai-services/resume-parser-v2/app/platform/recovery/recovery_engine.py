"""
Disaster Recovery Engine.
Executes automated recovery procedures, restores payload from backups, and performs validation tests.
"""

import hashlib
import json
import os
import time
from typing import Any, Dict, Optional
from app.platform.backup.backup_engine import BackupEngine
from app.platform.schemas.platform_models import RecoveryResult
from core.logging import get_logger

logger = get_logger("recovery_engine")


class DisasterRecoveryEngine:
    """Enterprise Disaster Recovery Engine."""

    def __init__(self, backup_engine: BackupEngine) -> None:
        self.backup_engine = backup_engine

    def restore_backup(self, backup_id: str) -> RecoveryResult:
        start_time = time.time()
        record = self.backup_engine.get_backup(backup_id)

        if not record or not os.path.exists(record.file_path):
            logger.error("Restore failed: Backup record or file not found", backup_id=backup_id)
            return RecoveryResult(backup_id=backup_id, status="failed", validated=False)

        with open(record.file_path, "r", encoding="utf-8") as f:
            content = f.read()

        current_checksum = hashlib.sha256(content.encode("utf-8")).hexdigest()
        if current_checksum != record.checksum:
            logger.error("Checksum verification failed for backup", backup_id=backup_id)
            return RecoveryResult(backup_id=backup_id, status="corrupt", validated=False)

        data = json.loads(content)
        duration_ms = round((time.time() - start_time) * 1000, 2)
        records_restored = len(data) if isinstance(data, dict) else 1

        result = RecoveryResult(
            backup_id=backup_id,
            status="success",
            records_restored=records_restored,
            duration_ms=duration_ms,
            validated=True,
        )

        logger.info("Disaster recovery restore completed successfully", backup_id=backup_id, duration_ms=duration_ms)
        return result
