"""
Pytest integration & unit tests for Phase 12 Enterprise Recruitment Workflow Orchestrator.
"""

import pytest
from httpx import AsyncClient
from app.workflow.pipeline.workflow_pipeline import WorkflowPipeline
from app.workflow.schemas.workflow_models import WorkflowActionRequest, WorkflowStartRequest


@pytest.fixture
def workflow_pipeline():
    return WorkflowPipeline()


@pytest.mark.anyio
async def test_workflow_pipeline_execution(workflow_pipeline: WorkflowPipeline):
    start_req = WorkflowStartRequest(job_uuid="job_wf_101", candidate_uuid="cand_wf_101")
    report = await workflow_pipeline.start_recruitment_workflow(start_req)

    assert report.job_uuid == "job_wf_101"
    assert report.current_state == "Applications Open"
    assert len(report.history) > 0
    assert len(report.notifications) > 0

    # Advance state
    act_req = WorkflowActionRequest(
        workflow_id=report.workflow_id,
        action="Approve",
        actor_id="dean_academic",
    )
    updated_report = await workflow_pipeline.execute_workflow_action(act_req)

    assert updated_report.current_state == "Screening"
    assert len(updated_report.approvals) == 1
    assert updated_report.approvals[0].actor_id == "dean_academic"


@pytest.mark.anyio
async def test_workflow_api_endpoints(async_client: AsyncClient):
    # 1. Start Workflow
    start_req = WorkflowStartRequest(job_uuid="job_api_202", candidate_uuid="cand_api_202")
    res1 = await async_client.post("/api/v1/workflow/start", json=start_req.model_dump(mode="json"))
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["success"] is True
    wf_id = data1["data"]["workflow_id"]

    # 2. Execute Action
    act_req = WorkflowActionRequest(workflow_id=wf_id, action="Override", override_decision="Recommended")
    res2 = await async_client.post("/api/v1/workflow/action", json=act_req.model_dump(mode="json"))
    assert res2.status_code == 200
    assert res2.json()["success"] is True

    # 3. Query Workflow Status
    res3 = await async_client.get(f"/api/v1/workflow/{wf_id}")
    assert res3.status_code == 200
    assert res3.json()["success"] is True
    assert res3.json()["data"]["workflow_id"] == wf_id

    # 4. Query Workflow History
    res4 = await async_client.get(f"/api/v1/workflow/history/{wf_id}")
    assert res4.status_code == 200
    assert res4.json()["success"] is True
    assert len(res4.json()["data"]) >= 2
