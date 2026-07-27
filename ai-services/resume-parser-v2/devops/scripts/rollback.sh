#!/usr/bin/env bash
# =========================================================
# FacultyIQ Emergency Rollback Script
# =========================================================

set -euo pipefail

NAMESPACE="facultyiq-prod"

echo "[WARNING] Initiating emergency deployment rollback..."

# 1. Rollback Helm Release
helm rollback facultyiq --namespace "${NAMESPACE}"

# 2. Rollback Kubernetes Deployment
kubectl rollout undo deployment/facultyiq-ai-services -n "${NAMESPACE}"

# 3. Verify Rollback Status
kubectl rollout status deployment/facultyiq-ai-services -n "${NAMESPACE}" --timeout=120s

echo "[SUCCESS] Rollback completed successfully!"
