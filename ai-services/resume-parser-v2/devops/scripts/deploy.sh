#!/usr/bin/env bash
# =========================================================
# FacultyIQ Production Zero-Downtime Deployment Script
# =========================================================

set -euo pipefail

NAMESPACE="facultyiq-prod"
CHART_PATH="devops/helm/facultyiq"
VALUES_FILE="devops/helm/facultyiq/values-prod.yaml"

echo "[INFO] Starting zero-downtime deployment for FacultyIQ..."

# 1. Apply Kubernetes manifests
kubectl apply -f devops/kubernetes/namespace.yaml
kubectl apply -f devops/kubernetes/configmap.yaml
kubectl apply -f devops/kubernetes/secrets.yaml

# 2. Upgrade via Helm
helm upgrade --install facultyiq "${CHART_PATH}" -f "${VALUES_FILE}" --namespace "${NAMESPACE}"

# 3. Wait for Deployment Rollout
echo "[INFO] Waiting for deployment rollout to complete..."
kubectl rollout status deployment/facultyiq-ai-services -n "${NAMESPACE}" --timeout=180s

# 4. Smoke Test Health Check
echo "[INFO] Running post-deployment health check..."
curl -f http://localhost:8000/api/v1/health || (echo "[ERROR] Health check failed!" && exit 1)

echo "[SUCCESS] FacultyIQ successfully deployed to production!"
