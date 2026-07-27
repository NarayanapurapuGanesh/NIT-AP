"""
Canonical Pydantic v2 Models for Enterprise Integration Platform.
Plugins, Webhooks, Events, ERP/LMS/Identity/Notification Connectors,
AI Provider Adapters, Import/Export, Marketplace & API Gateway.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field


# --- Enums ---

class PluginCategory(str, Enum):
    RECRUITMENT = "recruitment"
    EVALUATION = "evaluation"
    INTERVIEW = "interview"
    ANALYTICS = "analytics"
    WORKFLOW = "workflow"
    NOTIFICATION = "notification"
    AI_PROVIDER = "ai_provider"
    DOCUMENT_PARSER = "document_parser"


class PluginStatus(str, Enum):
    INSTALLED = "installed"
    ENABLED = "enabled"
    DISABLED = "disabled"
    FAILED = "failed"


class EventType(str, Enum):
    CANDIDATE_CREATED = "CandidateCreated"
    RESUME_PARSED = "ResumeParsed"
    MATCHING_COMPLETED = "MatchingCompleted"
    DECISION_GENERATED = "DecisionGenerated"
    INTERVIEW_SCHEDULED = "InterviewScheduled"
    INTERVIEW_COMPLETED = "InterviewCompleted"
    OFFER_ACCEPTED = "OfferAccepted"
    WORKFLOW_COMPLETED = "WorkflowCompleted"
    PLUGIN_INSTALLED = "PluginInstalled"


class AIProviderType(str, Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    ANTHROPIC = "anthropic"
    GOOGLE_GEMINI = "google_gemini"
    CUSTOM = "custom"


# --- Plugin & Marketplace Models ---

class PluginMetadata(BaseModel):
    plugin_id: str
    name: str
    version: str = "1.0.0"
    category: PluginCategory
    author: str
    description: str = ""
    min_system_version: str = "2.0.0"
    dependencies: List[str] = Field(default_factory=list)
    permissions_required: List[str] = Field(default_factory=list)


class PluginInstance(BaseModel):
    instance_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    metadata: PluginMetadata
    status: PluginStatus = PluginStatus.INSTALLED
    installed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    config: Dict[str, Any] = Field(default_factory=dict)


class MarketplaceListing(BaseModel):
    listing_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    metadata: PluginMetadata
    downloads: int = 0
    rating: float = 5.0
    digital_signature: str = ""


# --- Event Bus & Webhook Models ---

class EventEnvelope(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    tenant_id: str = "default_university"
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WebhookSubscription(BaseModel):
    subscription_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = "default_university"
    target_url: str
    secret: str
    subscribed_events: List[EventType] = Field(default_factory=list)
    is_active: bool = True


class WebhookDeliveryLog(BaseModel):
    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    subscription_id: str
    event_id: str
    target_url: str
    status_code: int = 200
    success: bool = True
    attempt_number: int = 1
    delivered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# --- Connectors & Adapters Models ---

class ERPConnectorConfig(BaseModel):
    system_type: str  # SAP, Banner, Oracle_HRMS, Peoplesoft
    endpoint_url: str
    auth_token: Optional[str] = None
    enabled: bool = True


class LMSConnectorConfig(BaseModel):
    system_type: str  # Canvas, Moodle, Blackboard
    api_key: str
    base_url: str
    enabled: bool = True


class IdentityConnectorConfig(BaseModel):
    provider_type: str  # AzureAD, GoogleWorkspace, LDAP, SAML, OIDC
    client_id: str
    tenant_domain: str
    enabled: bool = True


class NotificationConnectorConfig(BaseModel):
    provider_type: str  # SMTP, MS365, Twilio, Firebase, WhatsApp
    api_key_or_secret: str
    sender_id: str
    enabled: bool = True


class AIAdapterConfig(BaseModel):
    provider_type: AIProviderType
    api_base: str
    model_name: str
    api_key: Optional[str] = None
    temperature: float = 0.2


# --- Import / Export & API Gateway Models ---

class ImportRequest(BaseModel):
    entity_type: str  # candidates, jobs, departments, users, configs
    data_format: str = "json"  # json, csv
    payload: List[Dict[str, Any]] = Field(default_factory=list)


class ImportResult(BaseModel):
    imported_count: int
    failed_count: int
    errors: List[str] = Field(default_factory=list)


class ExportRequest(BaseModel):
    entity_type: str
    format: str = "json"


class ExportResult(BaseModel):
    export_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: str
    format: str
    record_count: int
    file_content: str


class APIKeyRecord(BaseModel):
    key_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    api_key: str
    tenant_id: str
    name: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
