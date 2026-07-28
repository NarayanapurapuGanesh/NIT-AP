from app.services.full_evaluation_service import FullEvaluationService
from app.services.video_pipeline_service import VideoPipelineService
from app.services.visual_pipeline_service import VisualPipelineService

# Singleton instances
_pipeline_service_instance: VideoPipelineService | None = None
_visual_pipeline_service_instance: VisualPipelineService | None = None
_full_evaluation_service_instance: FullEvaluationService | None = None


def get_pipeline_service() -> VideoPipelineService:
    """Dependency provider returning singleton VideoPipelineService instance."""
    global _pipeline_service_instance
    if _pipeline_service_instance is None:
        _pipeline_service_instance = VideoPipelineService()
    return _pipeline_service_instance


def get_visual_pipeline_service() -> VisualPipelineService:
    """Dependency provider returning singleton VisualPipelineService instance."""
    global _visual_pipeline_service_instance
    if _visual_pipeline_service_instance is None:
        _visual_pipeline_service_instance = VisualPipelineService()
    return _visual_pipeline_service_instance


def get_full_evaluation_service() -> FullEvaluationService:
    """Dependency provider returning singleton FullEvaluationService instance."""
    global _full_evaluation_service_instance
    if _full_evaluation_service_instance is None:
        _full_evaluation_service_instance = FullEvaluationService()
    return _full_evaluation_service_instance
