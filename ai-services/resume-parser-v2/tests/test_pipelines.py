"""
Tests for pipeline registration and execution framework.
"""

import pytest
from app.pipelines.base import IPipelineStep, PipelineContext
from app.pipelines.registry import pipeline_registry


class MockPipelineStep(IPipelineStep):
    @property
    def name(self) -> str:
        return "mock_step"

    async def execute(self, context: PipelineContext) -> PipelineContext:
        context.data["processed_by"] = "mock_step"
        return context


@pytest.mark.anyio
async def test_pipeline_registration_and_execution():
    step = MockPipelineStep()
    pipeline_registry.register("test_pipeline", [step])

    pipeline = pipeline_registry.get("test_pipeline")
    ctx = PipelineContext(document_id="doc_123")

    result = await pipeline.run(ctx)
    assert result.success is True
    assert result.completed_steps == ["mock_step"]
    assert result.context.data["processed_by"] == "mock_step"
