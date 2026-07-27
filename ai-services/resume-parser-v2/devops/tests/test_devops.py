"""
Pytest validation tests for Phase 17 Enterprise DevOps Platform.
Validates existence and structure of Dockerfiles, Docker Compose, Kubernetes manifests,
Helm charts, Terraform IaC, GitHub Workflows, Shell scripts, and Observability configs.
"""

import os
import pytest


@pytest.fixture
def devops_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def test_dockerfiles_exist(devops_dir):
    docker_dir = os.path.join(devops_dir, "docker")
    assert os.path.exists(os.path.join(docker_dir, "Dockerfile.ai-services"))
    assert os.path.exists(os.path.join(docker_dir, "Dockerfile.backend"))
    assert os.path.exists(os.path.join(docker_dir, "Dockerfile.frontend"))
    assert os.path.exists(os.path.join(docker_dir, "nginx.conf"))
    assert os.path.exists(os.path.join(docker_dir, "docker-compose.yml"))


def test_kubernetes_manifests_exist(devops_dir):
    k8s_dir = os.path.join(devops_dir, "kubernetes")
    manifests = [
        "namespace.yaml", "configmap.yaml", "secrets.yaml",
        "ai-services-deployment.yaml", "backend-deployment.yaml", "frontend-deployment.yaml",
        "postgres-statefulset.yaml", "redis-statefulset.yaml", "ollama-deployment.yaml",
        "ingress.yaml", "hpa.yaml", "pdb.yaml", "cronjobs.yaml"
    ]
    for m in manifests:
        assert os.path.exists(os.path.join(k8s_dir, m)), f"Missing k8s manifest: {m}"


def test_helm_chart_structure(devops_dir):
    helm_dir = os.path.join(devops_dir, "helm", "facultyiq")
    assert os.path.exists(os.path.join(helm_dir, "Chart.yaml"))
    assert os.path.exists(os.path.join(helm_dir, "values.yaml"))
    assert os.path.exists(os.path.join(helm_dir, "values-prod.yaml"))
    assert os.path.exists(os.path.join(helm_dir, "templates", "deployment.yaml"))


def test_terraform_iac_modules(devops_dir):
    tf_dir = os.path.join(devops_dir, "terraform")
    files = ["main.tf", "variables.tf", "vpc.tf", "eks.tf", "rds.tf", "s3.tf", "outputs.tf"]
    for f in files:
        assert os.path.exists(os.path.join(tf_dir, f)), f"Missing Terraform file: {f}"


def test_github_workflows_exist(devops_dir):
    gh_dir = os.path.join(devops_dir, "github", "workflows")
    assert os.path.exists(os.path.join(gh_dir, "ci.yml"))
    assert os.path.exists(os.path.join(gh_dir, "cd.yml"))
    assert os.path.exists(os.path.join(gh_dir, "security-scan.yml"))


def test_automation_scripts_exist(devops_dir):
    scripts_dir = os.path.join(devops_dir, "scripts")
    assert os.path.exists(os.path.join(scripts_dir, "deploy.sh"))
    assert os.path.exists(os.path.join(scripts_dir, "rollback.sh"))
    assert os.path.exists(os.path.join(scripts_dir, "backup.sh"))


def test_monitoring_configs_exist(devops_dir):
    mon_dir = os.path.join(devops_dir, "monitoring")
    assert os.path.exists(os.path.join(mon_dir, "prometheus.yml"))
    assert os.path.exists(os.path.join(mon_dir, "grafana-dashboard.json"))
