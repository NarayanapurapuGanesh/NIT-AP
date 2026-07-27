# SRE & Operational Incident Response Runbook (`FacultyIQ`)

> Standard Operating Procedures (SOP) for Site Reliability Engineers and DevOps personnel managing FacultyIQ in production.

---

## 🚨 Incident Response Matrix

### 1. High API Latency (>250ms P95)
- **Symptom**: Prometheus alert `High API Latency` fired.
- **Action**:
  1. Inspect pod CPU/Memory metrics: `kubectl top pods -n facultyiq-prod`.
  2. Scale deployment replicas: `kubectl scale deployment facultyiq-ai-services --replicas=10 -n facultyiq-prod`.
  3. Verify Redis cache hit ratio via `GET /api/v1/platform/cache/stats`.

### 2. Service Failure / Pod CrashLoopBackOff
- **Symptom**: Readiness probe failing or pod status `CrashLoopBackOff`.
- **Action**:
  1. Inspect logs: `kubectl logs -l app=facultyiq-ai-services -n facultyiq-prod --tail=200`.
  2. Initiate rollback if caused by new release: `./devops/scripts/rollback.sh`.

### 3. Database Outage / Connection Loss
- **Symptom**: Database health probe returning `UNHEALTHY`.
- **Action**:
  1. Check PostgreSQL pod status: `kubectl get statefulset postgres -n facultyiq-prod`.
  2. Execute restore from backup if data corruption detected.

---

## 💾 Backup & Disaster Recovery Procedures

### Manual Backup Trigger
```bash
./devops/scripts/backup.sh
```

### Database Restore Procedure
```bash
docker exec -i facultyiq-postgres psql -U facultyiq_admin facultyiq < devops/backups/snapshots/db_backup_TIMESTAMP.sql
```
