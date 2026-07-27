# Enterprise Integration Platform Guide (`resume-parser-v2`)

> Phase 16 Extensibility Layer providing Public APIs, Plugin SDK & Lifecycle Management, Topic Event Bus, Webhooks Framework, University ERP & LMS Connectors, Identity/SSO Adapters, AI Provider Abstractions, Import/Export Engine, and Plugin Marketplace Foundation.

---

## 🏛️ Integration Platform Architecture

```
               FacultyIQ Core Platform (Phases 1–15)
                              │
                              ▼
               [Enterprise Integration Platform]
                              │
  ┌───────────────────────────┼───────────────────────────┐
  ▼                           ▼                           ▼
[Plugin SDK & Lifecycle]     [Event Bus & Webhooks]     [University Connectors]
(Sandbox, Install, Enable)   (Pub/Sub, HMAC Sign)       (SAP, Canvas, Azure AD)
  │                           │                           │
  ├───────────────────────────┼───────────────────────────┤
  ▼                           ▼                           ▼
[AI Provider Adapters]       [Import / Export Engine]   [Marketplace Directory]
(Ollama, OpenAI, Gemini)     (JSON / CSV Batch Data)     (Plugin Registry & Sigs)
```

---

## 🔌 REST API Endpoints

### 1. `GET /api/v1/plugins`
Returns all installed, enabled, and disabled plugins.

### 2. `POST /api/v1/plugins/install`
Installs a new plugin instance after verifying version compatibility.

### 3. `POST /api/v1/webhooks`
Registers a target webhook endpoint to receive HMAC-signed event payloads.

### 4. `GET /api/v1/connectors`
Lists all active ERP, LMS, Identity, and Notification connector configurations.

### 5. `POST /api/v1/import`
Executes batch import of candidates, jobs, departments, users, or configs.

### 6. `POST /api/v1/export`
Triggers batch export of analytics reports, interview results, or audit logs in JSON/CSV format.

### 7. `GET /api/v1/marketplace`
Searches available plugin listings in the FacultyIQ marketplace directory.

---

## 🧩 Plugin SDK Example

```python
from app.integration.sdk.plugin_sdk import BaseFacultyIQPlugin
from app.integration.schemas.integration_models import PluginMetadata, PluginCategory

class CustomPublicationScorerPlugin(BaseFacultyIQPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="custom_pub_scorer",
            name="Custom Publication Scorer",
            category=PluginCategory.EVALUATION,
            author="University Team",
        )

    def initialize(self, config: dict) -> bool:
        return True

    def execute(self, payload: dict) -> dict:
        return {"bonus_points": 15, "reason": "High impact factor publications"}
```
