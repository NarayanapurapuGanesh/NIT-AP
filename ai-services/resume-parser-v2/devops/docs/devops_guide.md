# Enterprise DevOps & Infrastructure Architecture Guide (`FacultyIQ`)

> Phase 17 DevOps & Platform Engineering documentation covering Docker multi-stage builds, Kubernetes production manifests, Helm v3 charts, Terraform IaC, GitHub Actions CI/CD pipelines, Zero-downtime deployment, and Alerting.

---

## 🏛️ CI/CD & Deployment Pipeline Architecture

```
                               Developer Push / PR
                                        │
                                        ▼
                             [GitHub Actions CI]
                       (Ruff, Pytest, Security Scans)
                                        │
                                        ▼
                          [Container Image Build]
                      (Docker Multi-Stage + Cosign)
                                        │
                                        ▼
                          [Helm Release Deployment]
                     (EKS / Kubernetes Rolling Update)
                                        │
                                        ▼
                         [Health Check & Smoke Test]
                     (Zero-Downtime / Auto-Rollback)
```

---

## 🐋 Docker Environments

| Environment | Command | Purpose |
|-------------|---------|---------|
| **Production** | `docker compose -f devops/docker/docker-compose.yml up -d` | Full production containerized stack |
| **Development** | `docker compose -f devops/docker/docker-compose.dev.yml up -d` | Live reload local environment |

---

## ☸️ Kubernetes & Helm Commands

### Deploy Helm Chart
```bash
helm upgrade --install facultyiq devops/helm/facultyiq -f devops/helm/facultyiq/values-prod.yaml --namespace facultyiq-prod --create-namespace
```

### Emergency Rollback
```bash
./devops/scripts/rollback.sh
```

---

## 🛡️ Infrastructure as Code (Terraform)

```bash
cd devops/terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```
