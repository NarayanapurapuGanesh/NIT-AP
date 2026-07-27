"""
API v1 Router aggregation.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    admin,
    agent,
    analytics,
    classify,
    explainability,
    extract,
    health,
    ingest,
    integration,
    intelligence,
    interview,
    job,
    matching,
    platform,
    quality,
    readiness,
    recruitment,
    structure,
    version,
    workflow,
)

api_v1_router = APIRouter()

api_v1_router.include_router(health.router, tags=["System"])
api_v1_router.include_router(version.router, tags=["System"])
api_v1_router.include_router(readiness.router, tags=["System"])
api_v1_router.include_router(classify.router, tags=["Classification Engine"])
api_v1_router.include_router(ingest.router, tags=["Document Ingestion & Extraction Engine"])
api_v1_router.include_router(structure.router, tags=["Resume Structure Engine"])
api_v1_router.include_router(extract.router, tags=["Information Extraction Engine"])
api_v1_router.include_router(intelligence.router, tags=["Resume Intelligence & Validation Engine"])
api_v1_router.include_router(agent.router, tags=["Resume Intelligence Agent"])
api_v1_router.include_router(job.router, tags=["Job Description Intelligence Engine"])
api_v1_router.include_router(matching.router, tags=["Candidate-Job Matching Engine"])
api_v1_router.include_router(recruitment.router, tags=["Recruitment Decision Agent"])
api_v1_router.include_router(explainability.router, tags=["Explainability, Audit & Evidence Engine"])
api_v1_router.include_router(interview.router, tags=["Interview Intelligence & Assessment System"])
api_v1_router.include_router(workflow.router, tags=["Recruitment Workflow Orchestrator"])
api_v1_router.include_router(analytics.router, tags=["Analytics & Executive Dashboard"])
api_v1_router.include_router(admin.router, tags=["Enterprise Administration Platform"])
api_v1_router.include_router(platform.router, tags=["Enterprise Platform Operations"])
api_v1_router.include_router(integration.router, tags=["Enterprise Integration Platform"])
api_v1_router.include_router(quality.router, tags=["Enterprise Production Certification"])
