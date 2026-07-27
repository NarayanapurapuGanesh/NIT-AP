#!/usr/bin/env bash
# =========================================================
# FacultyIQ Database & Configuration Automated Backup Script
# =========================================================

set -euo pipefail

BACKUP_DIR="./devops/backups/snapshots"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "${BACKUP_DIR}"

echo "[INFO] Creating database backup snapshot: ${TIMESTAMP}..."

# Execute PG dump inside postgres container
docker exec facultyiq-postgres pg_dump -U facultyiq_admin facultyiq > "${BACKUP_DIR}/db_backup_${TIMESTAMP}.sql"

# SHA256 checksum verification
sha256sum "${BACKUP_DIR}/db_backup_${TIMESTAMP}.sql" > "${BACKUP_DIR}/db_backup_${TIMESTAMP}.sql.sha256"

echo "[SUCCESS] Backup created at ${BACKUP_DIR}/db_backup_${TIMESTAMP}.sql"
