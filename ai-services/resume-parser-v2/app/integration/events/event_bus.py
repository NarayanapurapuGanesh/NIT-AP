"""
Event Bus Engine.
Provides topic-based asynchronous Event Publisher and Subscriber model.
Publishes CandidateCreated, ResumeParsed, MatchingCompleted, DecisionGenerated,
InterviewScheduled, InterviewCompleted, OfferAccepted, WorkflowCompleted, PluginInstalled.
"""

from typing import Any, Callable, Dict, List, Optional
from app.integration.schemas.integration_models import EventEnvelope, EventType
from core.logging import get_logger

logger = get_logger("event_bus")

SubscriberCallback = Callable[[EventEnvelope], None]


class EventBusEngine:
    """Enterprise Topic Event Bus Engine."""

    def __init__(self) -> None:
        self._subscribers: Dict[EventType, List[SubscriberCallback]] = {}
        self._event_history: List[EventEnvelope] = []

    def subscribe(self, event_type: EventType, callback: SubscriberCallback) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.info("Subscribed to event topic", event_type=event_type.value)

    def publish(self, event_type: EventType, payload: Dict[str, Any], tenant_id: str = "default_university") -> EventEnvelope:
        event = EventEnvelope(event_type=event_type, payload=payload, tenant_id=tenant_id)
        self._event_history.append(event)

        callbacks = self._subscribers.get(event_type, [])
        for cb in callbacks:
            try:
                cb(event)
            except Exception as e:
                logger.error("Subscriber callback failed", event_type=event_type.value, error=str(e))

        logger.info("Published event to event bus", event_id=event.event_id, event_type=event_type.value, subscriber_count=len(callbacks))
        return event

    def get_event_history(self, limit: int = 50, event_type: Optional[EventType] = None) -> List[EventEnvelope]:
        events = self._event_history
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return events[-limit:]
