# Technical Deep Dive

This document provides a comprehensive technical breakdown of the MCP Gateway (ContextForge) codebase—covering architecture, module internals, execution flow, UI design, and end-to-end feature walkthroughs.

---

## 1. High-Level Design (HLD)

### 1.1 Overall Architecture

MCP Gateway is a **FastAPI-based gateway, proxy, and registry** for Model Context Protocol (MCP) servers and Agent-to-Agent (A2A) agents. It federates local and remote MCP services into a unified, protocol-compliant interface.

```
┌──────────────────────────────────────────────────────────────────┐
│                        MCP Clients                               │
│   (Claude Desktop, Continue, Zed, OpenWebUI, LangChain, etc.)   │
└───────────┬──────────────┬──────────────┬────────────────────────┘
            │ SSE          │ WebSocket    │ Streamable HTTP / stdio
            ▼              ▼              ▼
┌──────────────────────────────────────────────────────────────────┐
│                     MCP Gateway (FastAPI)                         │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────────┐  │
│  │ Middleware  │ │  Routers   │ │  Services  │ │   Plugins    │  │
│  │  Pipeline   │ │ (17+ APIs) │ │ (46 svcs)  │ │ (50+ hooks)  │  │
│  └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └──────┬───────┘  │
│        │              │              │               │           │
│  ┌─────┴──────────────┴──────────────┴───────────────┴────────┐  │
│  │                     Data Layer                              │  │
│  │  SQLAlchemy ORM  │  Redis Cache  │  Alembic Migrations     │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────────────────┘
                       │ Federation / Peer Discovery
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│              Remote MCP Servers & Peer Gateways                  │
│   (SSE / WebSocket / stdio / HTTP backends)                      │
└──────────────────────────────────────────────────────────────────┘
```

### 1.2 Major Modules and Responsibilities

| Module | Directory | Responsibility |
|--------|-----------|----------------|
| **Application Core** | `mcpgateway/main.py` | FastAPI app creation, lifespan, middleware/router wiring |
| **Configuration** | `mcpgateway/config.py` | Pydantic Settings for all environment variables |
| **Data Models** | `mcpgateway/models.py` | SQLAlchemy ORM definitions (55+ tables) |
| **Schemas** | `mcpgateway/schemas.py` | Pydantic request/response validation (50+ schemas) |
| **Database** | `mcpgateway/db.py` | Engine creation, session management, connection pooling |
| **Authentication** | `mcpgateway/auth.py` | JWT verification, API token lookup, user resolution |
| **Services** | `mcpgateway/services/` | Business logic (46 service files) |
| **Routers** | `mcpgateway/routers/` | FastAPI endpoint definitions (17 routers) |
| **Middleware** | `mcpgateway/middleware/` | Request pipeline processing (12 middleware) |
| **Transports** | `mcpgateway/transports/` | SSE, WebSocket, stdio, streamable HTTP |
| **Plugins** | `mcpgateway/plugins/` | Plugin framework, loader, executor, registry |
| **Federation** | `mcpgateway/federation/` | Peer discovery, health checks, request forwarding |
| **Cache** | `mcpgateway/cache/` | Redis + in-memory caching layer |
| **Admin UI** | `mcpgateway/admin.py`, `templates/`, `static/` | HTMX-based admin dashboard |
| **Utilities** | `mcpgateway/utils/` | JWT helpers, Redis client, SSL, pagination, etc. |
| **Validation** | `mcpgateway/validation/` | JSON-RPC protocol and tag validation |
| **Instrumentation** | `mcpgateway/instrumentation/` | OpenTelemetry SQLAlchemy query tracing |

### 1.3 Key System Interactions

1. **Client → Gateway** — Clients connect via SSE, WebSocket, or streamable HTTP. The middleware pipeline authenticates, validates, and routes requests.
2. **Gateway → Services** — Routers delegate to service classes that encapsulate all business logic.
3. **Services → Database** — Services use SQLAlchemy sessions injected via FastAPI dependency injection.
4. **Services → Plugins** — Tool/resource/prompt operations invoke plugin hooks (pre/post) for filtering, transformation, and policy enforcement.
5. **Gateway → Federated Peers** — The gateway service discovers and routes requests to remote MCP servers via SSE/HTTP.
6. **Admin UI → Backend** — The HTMX-based UI fetches HTML partials from admin endpoints, with Alpine.js managing client state.

### 1.4 Technology Stack and Design Rationale

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Web Framework | FastAPI | Async-native, automatic OpenAPI docs, Pydantic integration |
| Validation | Pydantic 2.12+ | Runtime type checking, schema generation, settings management |
| ORM | SQLAlchemy 2.0 | Multi-database support, async-ready, mature migration tooling |
| Migrations | Alembic | Versioned schema changes with upgrade/downgrade |
| Serialization | orjson | 2–3x faster JSON than stdlib |
| Cache | Redis + in-memory | Distributed caching with local fallback |
| UI Framework | HTMX + Alpine.js + Tailwind CSS | Server-driven UI with minimal JavaScript |
| Auth | PyJWT + argon2 | Industry-standard token auth and password hashing |
| Deployment | Uvicorn / Gunicorn / Granian | ASGI servers for development and production |
| Observability | Prometheus + OpenTelemetry | Metrics collection and distributed tracing |

---

## 2. Low-Level Design (LLD)

### 2.1 Application Core (`main.py`)

The FastAPI application is created via the `create_app()` pattern with a lifespan context manager.

**App initialization:**

```python
app = FastAPI(
    title="MCP Gateway",
    default_response_class=ORJSONResponse,  # orjson for fast serialization
    lifespan=lifespan,                       # async context manager
)
```

**Lifespan startup sequence:**

1. Initialize logging service
2. Create Redis client pool
3. Set up observability (Phoenix tracing, if enabled)
4. Validate security configuration (JWT secret, auth settings)
5. Initialize plugin manager (load YAML config → instantiate plugins → register hooks)
6. Initialize 8+ core services: `ToolService`, `ResourceService`, `PromptService`, `GatewayService`, `RootService`, `CompletionService`, `SamplingService`, `ExportService`
7. Initialize caches: `ResourceCache`, `SessionRegistry`
8. Start conditional services: metrics buffer, log aggregation, SSO bootstrap
9. Refresh slugs across all entities

**Lifespan shutdown sequence (reverse):**

1. Cancel background tasks (aggregation loops)
2. Shutdown plugin manager
3. Flush metrics buffer
4. Shutdown core services
5. Close Redis connection pool

### 2.2 Configuration (`config.py`)

A single `Settings(BaseSettings)` class using Pydantic v2 manages all configuration:

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    # Core
    host: str = "0.0.0.0"
    port: int = 4444
    database_url: str = "sqlite:///./mcp.db"

    # Auth
    jwt_secret_key: str = "change-me"
    auth_required: bool = True

    # Features (100+ settings)
    mcpgateway_ui_enabled: bool = True
    mcpgateway_a2a_enabled: bool = False
    plugins_enabled: bool = False
    ...
```

Settings are accessed via `get_settings()`, which returns a cached singleton. A `LazySettingsWrapper` defers instantiation until first access.

### 2.3 Database Layer (`db.py`, `models.py`)

**Engine creation** (`build_engine()`):

- Backend detection: PostgreSQL, SQLite, or MySQL/MariaDB
- PostgreSQL: TCP keep-alive, prepared statements, pool size 200
- SQLite: `StaticPool` with `check_same_thread=False`, 50 connection cap
- Connection pooling with `pool_pre_ping=True` for stale connection recovery

**Session management:**

- `SessionLocal` — scoped session factory
- `ResilientSession` — custom session class with automatic error recovery
- `get_db()` — FastAPI dependency that yields a session, commits on success, rolls back on error

**ORM models** (55+ tables organized by domain):

| Domain | Models |
|--------|--------|
| Core entities | `Tool`, `Resource`, `Prompt`, `Server`, `Gateway`, `A2AAgent` |
| Auth/RBAC | `EmailUser`, `Role`, `UserRole`, `EmailApiToken`, `TokenRevocation` |
| OAuth/SSO | `OAuthToken`, `OAuthState`, `SSOProvider`, `SSOAuthSession` |
| Teams | `EmailTeam`, `EmailTeamMember`, `EmailTeamInvitation` |
| Metrics | `ToolMetric`, `ResourceMetric`, `ServerMetric`, `PromptMetric`, `A2AAgentMetric` |
| Aggregated metrics | `ToolMetricsHourly`, `ResourceMetricsHourly`, `ServerMetricsHourly`, etc. |
| Observability | `ObservabilityTrace`, `ObservabilitySpan`, `ObservabilityEvent` |
| Sessions | `SessionRecord`, `SessionMessageRecord` |
| Config | `GlobalConfig`, `LLMProvider`, `LLMModel` |
| Audit | `AuditTrail`, `SecurityEvent`, `StructuredLogEntry` |

### 2.4 Authentication (`auth.py`)

**Authentication flow:**

```
Request with Bearer token
    │
    ├─ JWT token? → verify_jwt_token() → check claims (exp, aud, iss)
    │                                   → check_token_revoked(jti)
    │                                   → resolve user + team
    │
    └─ API token? → SHA-256 hash lookup → verify expiration
                                        → check revocation
                                        → update last_used timestamp
```

**FastAPI dependency chain:**

```python
security = HTTPBearer(auto_error=False)

async def get_current_user(credentials = Depends(security), db = Depends(get_db)):
    # Verify token, resolve user, return auth context
```

### 2.5 Middleware Pipeline

Middleware executes in **reverse registration order** (last registered = first executed):

```
Request → CompressMiddleware
        → CORSMiddleware
        → SecurityHeadersMiddleware
        → ValidationMiddleware
        → MCPProtocolVersionMiddleware
        → MCPPathRewriteMiddleware
        → HttpAuthMiddleware
        → DocsAuthMiddleware
        → RequestLoggingMiddleware
        → ProxyHeadersMiddleware
        → [Conditional: CorrelationID, AuthContext, Observability, TokenScoping]
        → Router → Handler → Response (back through pipeline)
```

| Middleware | Purpose |
|-----------|---------|
| `ProxyHeadersMiddleware` | Trust X-Forwarded-* headers from reverse proxies |
| `RequestLoggingMiddleware` | Log request/response at gateway boundary |
| `DocsAuthMiddleware` | Protect /docs, /redoc, /openapi.json |
| `MCPProtocolVersionMiddleware` | Validate MCP-Protocol-Version header |
| `SecurityHeadersMiddleware` | Add X-Content-Type-Options, X-Frame-Options, etc. |
| `ValidationMiddleware` | Input sanitization and payload validation |
| `MCPPathRewriteMiddleware` | Rewrite `/servers/<id>/mcp` → `/mcp` |
| `HttpAuthMiddleware` | Plugin-based authentication hooks |
| `CORSMiddleware` | Cross-Origin Resource Sharing configuration |
| `CompressMiddleware` | Brotli/Zstd/GZip response compression |
| `CorrelationIDMiddleware` | X-Request-ID tracking across requests |
| `AuthContextMiddleware` | Extract JWT user context for security logging |
| `TokenScopingMiddleware` | Email auth token scoping |

### 2.6 Service Layer Architecture

All services follow a consistent pattern:

```python
class ToolService:
    def __init__(self):
        self._event_service = EventService()
        self._plugin_manager = None  # set via set_plugin_manager()

    async def register_tool(self, db, tool_create, team_id=None) -> ToolRead:
        # 1. Validate input
        # 2. Check for name conflicts
        # 3. Create ORM model
        # 4. Persist to database
        # 5. Publish event
        # 6. Invalidate cache
        # 7. Return schema

    async def invoke_tool(self, db, name, arguments, team_id=None) -> ToolResult:
        # 1. Look up tool by name
        # 2. Validate arguments against input_schema
        # 3. Run pre-invoke plugin hooks
        # 4. Route invocation (local handler, remote SSE, remote HTTP)
        # 5. Run post-invoke plugin hooks
        # 6. Record metrics
        # 7. Return result
```

**Core services and interactions:**

```
GatewayService ──→ ToolService ──→ PluginManager
     │               │                  │
     │               ▼                  ▼
     │         ResourceService    Plugin hooks
     │               │           (pre/post invoke)
     │               ▼
     │         PromptService
     │
     ▼
ServerService ──→ A2AAgentService
     │
     ▼
ExportService (aggregates all services for bulk export)
```

**GatewayService** (largest service, ~200KB):

- Manages gateway registration, health monitoring, federation
- `connect_to_sse_server()` / `connect_to_streamablehttp_server()` — establishes MCP protocol connections to remote servers
- `aggregate_capabilities()` — merges tools/resources/prompts from multiple gateways
- `forward_request()` — routes JSON-RPC requests to appropriate gateway
- `check_health_of_gateways()` — periodic health check loop

**ToolService** (~150KB):

- `invoke_tool()` — the core tool execution path with plugin hooks, schema validation, and remote invocation
- `create_tool_from_a2a_agent()` — bridges A2A agents as callable tools
- `register_tools_bulk()` — bulk registration with conflict resolution

**ResourceService** (~137KB):

- `invoke_resource()` — content retrieval with template matching
- URI template matching: `_uri_matches_template()`, `_extract_template_params()`
- Subscription management: `subscribe_resource()`, `unsubscribe_resource()`

**PromptService** (~95KB):

- Jinja2 template rendering: `_render_template()`
- Argument extraction: `_get_required_arguments()`
- Multi-message parsing: `_parse_messages()`

### 2.7 Transport Implementations

All transports implement the abstract `Transport` base class:

```python
class Transport(ABC):
    async def connect(self) -> None: ...
    async def disconnect(self) -> None: ...
    async def send_message(self, message: Dict[str, Any]) -> None: ...
    async def receive_message(self) -> AsyncGenerator[Dict[str, Any], None]: ...
    def is_connected(self) -> bool: ...
```

| Transport | Protocol | Use Case |
|-----------|----------|----------|
| `SSETransport` | Server-Sent Events | Streaming responses to web clients |
| `WebSocketTransport` | WebSocket | Full-duplex bidirectional communication |
| `StdioTransport` | Standard I/O | CLI integration, subprocess communication |
| `StreamableHTTPTransport` | HTTP streaming | Modern MCP protocol transport |

### 2.8 Plugin Framework

**Architecture:** Singleton `PluginManager` with priority-ordered hook execution.

```
Plugin Config (YAML)
    │
    ▼
ConfigLoader ──→ PluginLoader ──→ PluginInstanceRegistry
                     │                     │
                     ▼                     ▼
              Plugin instances      Hook mappings
              (with priority)       (hook_type → [plugins])
```

**Plugin lifecycle:**

1. `ConfigLoader` reads `plugins/config.yaml` (with Jinja2 env var support)
2. `PluginLoader` dynamically imports plugin classes by `kind` attribute
3. Plugins register into `PluginInstanceRegistry` with hook mappings
4. At hook execution, the registry returns plugins sorted by priority
5. `PluginExecutor` runs each plugin with asyncio timeout (30s default)
6. Modified payloads chain through plugins; violations handled per mode

**Plugin modes:**

- `ENFORCE` — block request on failure
- `ENFORCE_IGNORE_ERROR` — enforce logic but don't block on errors
- `PERMISSIVE` — audit/log violations without blocking
- `DISABLED` — skip entirely

**Hook discovery:**

- Convention-based: method name matches hook type (e.g., `tool_pre_invoke`)
- Decorator-based: `@hook("hook_type")` annotation
- Signature validation: async methods with `(payload, context)` parameters

### 2.9 Federation and Discovery

**Discovery mechanisms:**

| Mechanism | How It Works |
|-----------|-------------|
| DNS-SD (mDNS/Bonjour) | `LocalDiscoveryService` advertises and discovers gateways on local network via Zeroconf |
| Static peer lists | Configured in settings, loaded on startup |
| Peer exchange protocol | `_exchange_peers()` enables transitive discovery (mesh networking) |
| Manual registration | `POST /gateways` API for direct peer addition |

**Key components:**

- `DiscoveryService` — main federation service with async start/stop, peer management, health check loops
- `DiscoveredPeer` — dataclass tracking URL, capabilities, discovery source, timestamps
- `ForwardingService` — request routing, response aggregation, retry logic across gateways

**Background loops:**

- Refresh loop (5 min) — updates peer capabilities
- Cleanup loop (10 min) — removes stale/unreachable peers

### 2.10 Caching Layer

**Architecture:** Two-tier caching with Redis (distributed) and in-memory (local fallback).

| Cache | Scope | TTL |
|-------|-------|-----|
| `RegistryCache` | Tools, prompts, resources, agents, servers, gateways | 20–60s |
| `AuthCache` | User data, team membership, token revocation | 30–60s |
| `ResourceCache` | Resource content with lazy loading | Configurable |
| `SessionRegistry` | MCP session storage | Session-scoped |
| `AdminStatsCache` | Dashboard statistics | Short TTL |
| `MetricsCache` | Performance metrics | Short TTL |

**Performance impact:** 95%+ cache hit rate, reducing per-request database queries from 3–4 to 0–1.

---

## 3. Codebase Understanding Guide

### 3.1 Where to Start Reading

Begin with these files in order to build a mental model of the system:

1. **`mcpgateway/config.py`** — understand all configuration options and feature flags
2. **`mcpgateway/models.py`** — see the complete data model (all 55+ tables)
3. **`mcpgateway/schemas.py`** — understand API request/response shapes
4. **`mcpgateway/main.py`** — see how the app boots, what middleware is registered, which routers are mounted
5. **`mcpgateway/db.py`** — understand database session management
6. **`mcpgateway/auth.py`** — understand the authentication flow

### 3.2 Recommended Exploration Order

**Phase 1 — Core Framework:**

```
config.py → models.py → schemas.py → db.py → auth.py → main.py
```

**Phase 2 — Business Logic (pick one entity and trace it end to end):**

```
routers/ (pick tools) → services/tool_service.py → models.py (Tool) → schemas.py (ToolCreate/ToolRead)
```

**Phase 3 — Cross-Cutting Concerns:**

```
middleware/ → plugins/framework/ → cache/ → federation/ → validation/
```

**Phase 4 — UI:**

```
admin.py → templates/admin.html → templates/*_partial.html → static/admin.js
```

**Phase 5 — Deployment and Operations:**

```
cli.py → gunicorn.config.py → docker-compose.yml → Containerfile → charts/
```

### 3.3 How Each Part Connects

```
CLI (cli.py) ──→ main.py (FastAPI app)
                    │
                    ├─ Middleware pipeline (auth, logging, validation)
                    ├─ Routers (REST + JSON-RPC endpoints)
                    │     └─ Services (business logic)
                    │           └─ ORM Models + Database sessions
                    │           └─ Plugin hooks (pre/post processing)
                    │           └─ Cache layer (Redis / in-memory)
                    ├─ Admin UI (Jinja2 templates + HTMX)
                    └─ Transports (SSE, WebSocket, stdio, HTTP)
                          └─ Federation (peer discovery + forwarding)
```

---

## 4. Code Structure Breakdown

### 4.1 Folder Structure Overview

```
mcpgateway/                     # Main application package
├── main.py                     # FastAPI app entry point
├── cli.py                      # CLI (Uvicorn launcher)
├── config.py                   # Pydantic Settings
├── models.py                   # SQLAlchemy ORM models
├── schemas.py                  # Pydantic validation schemas
├── db.py                       # Database engine + session management
├── auth.py                     # JWT/API token authentication
├── admin.py                    # Admin UI routes (100+ endpoints)
├── bootstrap_db.py             # Database initialization
├── wrapper.py                  # MCP client stdio bridge
├── translate.py                # Protocol translation
├── reverse_proxy.py            # Reverse proxy logic
├── validators.py               # Pydantic field validators
├── version.py                  # Version information
│
├── services/                   # Business logic layer (46 files)
│   ├── gateway_service.py      # Federation, gateway management
│   ├── tool_service.py         # Tool CRUD + invocation
│   ├── resource_service.py     # Resource CRUD + content retrieval
│   ├── prompt_service.py       # Prompt CRUD + template rendering
│   ├── server_service.py       # Server registration + lifecycle
│   ├── a2a_service.py          # Agent-to-Agent integration
│   ├── plugin_service.py       # Plugin management interface
│   ├── export_service.py       # Configuration export
│   ├── import_service.py       # Configuration import
│   ├── event_service.py        # Pub/sub event system
│   ├── logging_service.py      # Structured logging
│   ├── metrics*.py             # Metrics collection + rollup
│   ├── auth_service.py         # Authentication logic
│   ├── email_auth_service.py   # Email-based auth
│   ├── sso_service.py          # Single Sign-On
│   ├── oauth_manager.py        # OAuth flow management
│   ├── team_management*.py     # Team/org management
│   ├── role_service.py         # RBAC roles
│   ├── permission_service.py   # Permission checks
│   ├── audit_trail_service.py  # Audit logging
│   ├── encryption_service.py   # Data encryption
│   ├── catalog_service.py      # MCP server catalog
│   ├── root_service.py         # MCP roots
│   ├── completion_service.py   # Auto-completion
│   ├── sampling_service.py     # LLM sampling
│   ├── elicitation_service.py  # User input elicitation
│   ├── system_stats_service.py # System statistics
│   └── ...                     # Additional services
│
├── routers/                    # FastAPI endpoint definitions (17 files)
│   ├── auth.py                 # Authentication endpoints
│   ├── email_auth.py           # Email auth endpoints
│   ├── sso.py                  # SSO endpoints
│   ├── oauth_router.py         # OAuth flow endpoints
│   ├── rbac.py                 # RBAC endpoints
│   ├── teams.py                # Team management endpoints
│   ├── tokens.py               # Token management
│   ├── llmchat_router.py       # LLM chat sessions
│   ├── llm_config_router.py    # LLM provider configuration
│   ├── llm_proxy_router.py     # LLM proxy
│   ├── llm_admin_router.py     # LLM admin operations
│   ├── toolops_router.py       # Tool operations
│   ├── reverse_proxy.py        # Reverse proxy routing
│   ├── well_known.py           # /.well-known/ endpoints
│   ├── observability.py        # Monitoring endpoints
│   ├── log_search.py           # Log search
│   └── metrics_maintenance.py  # Metrics maintenance
│
├── middleware/                  # ASGI middleware (12 files)
│   ├── auth_context.py         # JWT context extraction
│   ├── http_auth.py            # HTTP authentication
│   ├── security_headers.py     # Security response headers
│   ├── validation.py           # Input validation
│   ├── mcp_protocol_version.py # MCP version validation
│   ├── mcp_path_rewrite.py     # Path rewriting
│   ├── request_logging.py      # Request/response logging
│   ├── correlation_id.py       # Request ID tracking
│   ├── observability.py        # Distributed tracing
│   ├── db_query_logging.py     # SQL query logging
│   ├── token_scoping.py        # Token scope enforcement
│   └── rbac.py                 # Role-based access control
│
├── transports/                 # Protocol implementations
│   ├── base.py                 # Abstract Transport class
│   ├── sse_transport.py        # Server-Sent Events
│   ├── websocket_transport.py  # WebSocket
│   ├── stdio_transport.py      # Standard I/O
│   └── streamable_http.py      # HTTP streaming
│
├── plugins/                    # Plugin framework
│   └── framework/
│       ├── base.py             # Plugin base class
│       ├── manager.py          # Plugin lifecycle manager
│       ├── executor.py         # Plugin execution engine
│       ├── registry.py         # Plugin instance registry
│       ├── decorator.py        # @hook decorator
│       ├── loader/             # Config + plugin loading
│       └── hooks/              # Hook type definitions
│
├── federation/                 # Multi-instance federation
│   ├── discovery.py            # Peer discovery (mDNS, static, exchange)
│   └── forwarding.py           # Request forwarding + aggregation
│
├── cache/                      # Caching backends
│   ├── registry_cache.py       # Entity caching
│   ├── auth_cache.py           # Auth data caching
│   └── ...                     # Additional cache types
│
├── validation/                 # Protocol validation
│   ├── jsonrpc.py              # JSON-RPC 2.0 validation
│   └── tags.py                 # Tag validation/normalization
│
├── utils/                      # Utility modules (28 files)
│   ├── create_jwt_token.py     # JWT generation
│   ├── redis_client.py         # Redis connection management
│   ├── ssl_key_manager.py      # TLS certificate handling
│   ├── pagination.py           # Pagination helpers
│   ├── retry_manager.py        # HTTP retry logic
│   └── ...                     # Additional utilities
│
├── handlers/                   # Event handlers
│   └── sampling.py             # LLM sampling handler
│
├── instrumentation/            # Observability instrumentation
│   └── sqlalchemy.py           # SQLAlchemy query tracing
│
├── tools/builder/              # Tool deployment pipeline
│   ├── deploy_factory.py       # Deployment strategy factory
│   └── pipeline.py             # CI/CD pipeline implementation
│
├── alembic/                    # Database migrations
│   ├── env.py                  # Migration environment
│   └── versions/               # Migration scripts
│
├── templates/                  # Jinja2 HTML templates (30 files)
│   ├── admin.html              # Main dashboard
│   ├── login.html              # Login page
│   ├── tools_partial.html      # Tools table partial
│   ├── resources_partial.html  # Resources partial
│   ├── prompts_partial.html    # Prompts partial
│   ├── observability_*.html    # Observability dashboards
│   └── ...                     # Additional partials
│
└── static/                     # CSS, JS, images
    ├── admin.js                # Admin UI JavaScript
    ├── admin.css               # Admin UI styles
    ├── flame-graph.js/css      # Performance flame graphs
    ├── gantt-chart.js/css      # Timeline visualization
    └── contextforge-*.png      # Logo/icon assets
```

### 4.2 Supporting Directories

```
plugins/                        # 50+ production-ready plugins
├── pii_filter/                 # Remove personally identifiable information
├── deny_filter/                # Deny-list filtering
├── regex_filter/               # Regex-based content filtering
├── resource_filter/            # Resource access control
├── circuit_breaker/            # Circuit breaker pattern
├── rate_limiter/               # Rate limiting
├── secrets_detection/          # Secret detection
├── sql_sanitizer/              # SQL injection prevention
├── code_safety_linter/         # Code safety checks
├── cached_tool_result/         # Response caching
├── retry_with_backoff/         # Exponential backoff
└── ...                         # 40+ additional plugins

tests/                          # Test suite
├── unit/                       # Unit tests (fast, isolated)
├── integration/                # Cross-service integration tests
├── e2e/                        # End-to-end workflow tests
├── performance/                # Performance benchmarks
├── security/                   # Security validation
├── fuzz/                       # Fuzzing / property-based testing
├── playwright/                 # Browser automation (UI tests)
└── conftest.py                 # Shared fixtures

docs/                           # MkDocs documentation
├── mkdocs.yml                  # MkDocs configuration
└── docs/                       # Source markdown files
    ├── architecture/           # Architecture & ADRs
    ├── overview/               # Feature overview
    ├── deployment/             # Deployment guides
    └── ...                     # Additional sections

deployment/                     # Infrastructure as Code
├── k8s/                        # Kubernetes manifests
├── terraform/ibm-cloud/        # Terraform for IBM Cloud
├── ansible/ibm-cloud/          # Ansible playbooks
└── knative/                    # Serverless configs

charts/mcp-stack/               # Helm chart
├── Chart.yaml                  # Chart metadata
├── values.yaml                 # Default values
└── templates/                  # Kubernetes templates
```

---

## 5. Complete Execution Flow

### 5.1 Application Boot Sequence

```
1. CLI entry point
   cli.py → mcpgateway command
   └─ Parses --host, --port, --reload flags
   └─ Calls uvicorn.run("mcpgateway.main:app")

2. FastAPI app creation
   main.py → app = FastAPI(lifespan=lifespan)
   └─ Registers exception handlers
   └─ Mounts middleware stack (12 middleware)
   └─ Includes routers (17+ routers, some conditional on feature flags)
   └─ Mounts static files at /static

3. Lifespan startup (async context manager)
   a. Logging service → configure structured logging
   b. Redis client → create connection pool
   c. Observability → Phoenix tracing (if enabled)
   d. Security → validate JWT secret, auth configuration
   e. Plugins → PluginManager.initialize() if PLUGINS_ENABLED
   f. Core services → ToolService(), ResourceService(), PromptService(),
                       GatewayService(), RootService(), CompletionService(),
                       SamplingService(), ExportService()
   g. Caches → ResourceCache, SessionRegistry
   h. Conditional services → MetricsBuffer, LogAggregation, SSO bootstrap
   i. refresh_slugs_on_startup() → ensure all entities have valid slugs

4. Server ready
   └─ Uvicorn/Gunicorn starts accepting connections on configured host:port
```

### 5.2 Request Processing (End-to-End)

**Example: Tool invocation via JSON-RPC**

```
1. Client sends POST /mcp with JSON-RPC body:
   {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "my-tool", "arguments": {...}}, "id": 1}

2. Middleware pipeline (in order):
   a. CompressMiddleware → decompress request if needed
   b. CORSMiddleware → validate origin
   c. SecurityHeadersMiddleware → (pass-through on request)
   d. ValidationMiddleware → validate JSON-RPC structure
   e. MCPProtocolVersionMiddleware → check MCP-Protocol-Version header
   f. HttpAuthMiddleware → run plugin auth hooks
   g. RequestLoggingMiddleware → log request details
   h. CorrelationIDMiddleware → attach X-Request-ID

3. Router dispatch:
   main.py endpoint handler for POST /mcp
   └─ Parses JSON-RPC method
   └─ Dispatches to tool_service.invoke_tool()

4. Service layer (ToolService.invoke_tool):
   a. Look up tool by name from database (with cache)
   b. Validate arguments against tool.input_schema (JSON Schema)
   c. Plugin pre-invoke hooks:
      └─ PluginManager.execute_hook("tool_pre_invoke", payload, context)
      └─ Each plugin processes payload in priority order
      └─ If ENFORCE mode plugin rejects → return error
   d. Invoke tool:
      ├─ Local handler → call registered Python function
      ├─ Remote SSE → connect to gateway, send JSON-RPC, await response
      └─ Remote HTTP → POST to tool endpoint URL
   e. Plugin post-invoke hooks:
      └─ PluginManager.execute_hook("tool_post_invoke", result, context)
   f. Record metrics → ToolMetric(tool_id, latency, success, timestamp)
   g. Return ToolResult schema

5. Response pipeline (middleware in reverse):
   a. SecurityHeadersMiddleware → add security headers
   b. CompressMiddleware → compress response (Brotli/GZip)
   c. RequestLoggingMiddleware → log response status + timing

6. Client receives JSON-RPC response:
   {"jsonrpc": "2.0", "result": {"content": [...]}, "id": 1}
```

### 5.3 Data Flow Across Layers

```
UI (HTMX)  →  Admin API  →  Service  →  ORM Model  →  Database
                                │
                                ├──→ Plugin hooks (pre/post)
                                ├──→ Cache (read-through / write-through)
                                ├──→ Event service (notifications)
                                └──→ Metrics recording
```

**Detailed per-layer transformations:**

| Layer | Input | Output | Operation |
|-------|-------|--------|-----------|
| UI (HTMX) | User action (click, form) | HTTP request | Form data → HTTP POST |
| Router | HTTP request | Pydantic schema | JSON → `ToolCreate` / `ToolInvocation` |
| Service | Pydantic schema | ORM model | `ToolCreate` → `Tool` (SQLAlchemy) |
| ORM | Model instance | SQL | `session.add(tool)` → INSERT |
| Database | SQL | Rows | Persisted to SQLite/PostgreSQL |
| Return: ORM | Rows | Model | SELECT → `Tool` instance |
| Return: Service | Model | Schema | `Tool` → `ToolRead` (Pydantic) |
| Return: Router | Schema | JSON | `ToolRead` → JSON response |

### 5.4 Dry Run: Registering a New MCP Server

```
1. Admin submits "Add Gateway" form in the Admin UI

2. HTMX sends POST /gateways with form data:
   {
     "name": "my-server",
     "url": "http://localhost:9000/sse",
     "transport": "sse",
     "auth_type": "bearer",
     "auth_token": "..."
   }

3. Router: validates → GatewayCreate schema

4. GatewayService.register_gateway():
   a. Check for name conflicts in database
   b. Create Gateway ORM model with generated slug
   c. Persist to database (session.add + commit)
   d. Attempt to connect to the server:
      └─ connect_to_sse_server(url) → MCP initialize handshake
      └─ Discover tools: tools/list → register each as Tool entity
      └─ Discover resources: resources/list → register each as Resource
      └─ Discover prompts: prompts/list → register each as Prompt
   e. Publish "gateway.registered" event
   f. Invalidate gateway cache

5. Admin UI refreshes gateway table via HTMX partial reload

6. Tools/resources/prompts from the new server are now
   available through the gateway's unified API
```

### 5.5 Dry Run: SSE Client Session

```
1. Client connects: GET /sse
   └─ Server creates SSE transport, generates session_id
   └─ Returns event stream with endpoint URL

2. Client sends: POST /mcp (with session_id)
   Body: {"jsonrpc": "2.0", "method": "initialize", "params": {...}, "id": 1}

3. Gateway processes initialize:
   a. Validates protocol version
   b. Returns server capabilities:
      {tools: {listChanged: true}, resources: {subscribe: true}, prompts: {listChanged: true}}
   c. Stores session in SessionRegistry

4. Client sends: {"method": "initialized"}  (notification, no id)

5. Client sends: {"method": "tools/list", "id": 2}
   └─ ToolService.list_tools() → aggregates local + federated tools
   └─ Returns: {"result": {"tools": [...]}}

6. Client sends: {"method": "tools/call", "params": {"name": "...", "arguments": {...}}, "id": 3}
   └─ Full invocation flow (see Section 5.2)

7. Server sends notifications via SSE stream:
   └─ "notifications/tools/list_changed" when tool registry changes
```

---

## 6. Complete UI Breakdown

### 6.1 UI Architecture

The Admin UI follows a **Server-Driven UI** architecture:

- **Server-side rendering** — Jinja2 templates produce complete HTML
- **Partial updates** — HTMX fetches HTML fragments without full page reloads
- **Client state** — Alpine.js manages lightweight UI state (dark mode, sidebar, dropdowns)
- **Styling** — Tailwind CSS utility classes

```
┌─────────────────────────────────────────────────────┐
│                    Browser                           │
│  ┌─────────────────────────────────────────────┐    │
│  │  Jinja2-rendered HTML (admin.html)           │    │
│  │  ┌──────────────┐  ┌────────────────────┐   │    │
│  │  │  Alpine.js   │  │  HTMX Engine       │   │    │
│  │  │  (UI state)  │  │  (partial loads)   │   │    │
│  │  └──────────────┘  └────────┬───────────┘   │    │
│  │                             │                │    │
│  │  Tailwind CSS (styling)     │ hx-get/hx-post│    │
│  └─────────────────────────────┼───────────────┘    │
│                                │                     │
└────────────────────────────────┼─────────────────────┘
                                 │ HTTP (HTML partials)
                                 ▼
┌────────────────────────────────────────────────────────┐
│  FastAPI Backend                                        │
│  admin.py → TemplateResponse("*_partial.html", data)   │
└────────────────────────────────────────────────────────┘
```

### 6.2 Component Hierarchy

```
admin.html (Main Dashboard)
├── Header Bar
│   ├── Logo + Title
│   ├── Dark Mode Toggle (Alpine.js)
│   └── User Menu (logout)
│
├── Sidebar Navigation (collapsible, Alpine.js)
│   ├── Servers
│   ├── Tools
│   ├── Resources
│   ├── Prompts
│   ├── Gateways
│   ├── Observability
│   ├── LLM Config
│   ├── Plugins
│   ├── Settings
│   └── Teams / Users (if auth enabled)
│
└── Main Content Area (tab-based)
    ├── Servers Tab
    │   ├── Server table (Jinja2 loop)
    │   ├── Add/Edit/Delete forms
    │   └── Status toggle buttons
    │
    ├── Tools Tab (HTMX partial: tools_partial.html)
    │   ├── Paginated tool table
    │   ├── Tool details modal
    │   └── Pagination controls (pagination_controls.html)
    │
    ├── Resources Tab (HTMX partial: resources_partial.html)
    │   ├── Resource list with URI display
    │   └── Resource subscription status
    │
    ├── Prompts Tab (HTMX partial: prompts_partial.html)
    │   ├── Prompt list with argument display
    │   └── Prompt template preview
    │
    ├── Gateways Tab
    │   ├── Gateway table with health status
    │   ├── Add/Edit/Delete forms
    │   └── Connectivity indicators
    │
    ├── Observability Tab (HTMX: observability_partial.html)
    │   ├── Metrics dashboard (observability_metrics.html)
    │   ├── Traces list (observability_traces_list.html)
    │   ├── Trace detail (observability_trace_detail.html)
    │   └── Stats overview (observability_stats.html)
    │
    ├── LLM Config Tab (HTMX partials)
    │   ├── Providers (llm_providers_partial.html)
    │   ├── Models (llm_models_partial.html)
    │   └── API Info (llm_api_info_partial.html)
    │
    ├── Plugins Tab (HTMX: plugins_partial.html)
    │   ├── Plugin list with status
    │   └── Plugin configuration
    │
    ├── Performance Tab (HTMX: performance_partial.html)
    │   ├── Flame graphs (flame-graph.js)
    │   └── Gantt charts (gantt-chart.js)
    │
    └── Metrics Tab (HTMX: metrics_partial.html)
        ├── Top performers (metrics_top_performers_partial.html)
        └── Aggregate statistics
```

### 6.3 Purpose of Each UI Component

| Component | Template | Purpose |
|-----------|----------|---------|
| **Login Page** | `login.html` | Email/password form + SSO provider buttons |
| **Main Dashboard** | `admin.html` | Primary layout with sidebar + tabbed content |
| **Tools Table** | `tools_partial.html` | Paginated list of registered tools with actions |
| **Resources Table** | `resources_partial.html` | Resource list with URI and subscription info |
| **Prompts Table** | `prompts_partial.html` | Prompt templates with arguments |
| **Pagination** | `pagination_controls.html` | Reusable page navigation component |
| **Observability** | `observability_partial.html` | Monitoring dashboard entry point |
| **Metrics** | `observability_metrics.html` | Real-time metric charts |
| **Traces** | `observability_traces_list.html` | Distributed trace browser |
| **Trace Detail** | `observability_trace_detail.html` | Single trace waterfall view |
| **Performance** | `performance_partial.html` | Flame graph + Gantt chart visualizations |
| **Plugins** | `plugins_partial.html` | Plugin status and configuration |
| **LLM Providers** | `llm_providers_partial.html` | LLM provider management |
| **MCP Registry** | `mcp_registry_partial.html` | MCP server catalog browser |
| **Version Info** | `version_info_partial.html` | System version display |

### 6.4 How Components Interact with the Backend

**HTMX pattern for partial loading:**

```html
<!-- Lazy-load tools table when tab becomes visible -->
<div hx-get="/admin/tools/partial?page=1&per_page=50"
     hx-trigger="revealed once"
     hx-swap="innerHTML">
  Loading tools...
</div>
```

**JWT authentication injection:**

```javascript
// admin.js - Intercept all HTMX requests to add auth header
document.addEventListener("htmx:configRequest", function(evt) {
    const jwtToken = getCookie("jwt_token");
    if (jwtToken) {
        evt.detail.headers["Authorization"] = "Bearer " + jwtToken;
    }
});
```

**Form handling (server action):**

```html
<!-- Toggle server status -->
<button hx-post="/admin/servers/{id}/toggle"
        hx-swap="outerHTML"
        hx-confirm="Toggle server status?">
  Toggle
</button>
```

### 6.5 State Management and Event Flows

**Client-side state (Alpine.js):**

```javascript
// admin.html
x-data="{
    darkMode: localStorage.getItem('darkMode') === 'true',
    sidebarOpen: true,
    activeTab: 'servers'
}"
```

**State persistence:** `localStorage` for dark mode and sidebar preferences.

**Rendering flow:**

1. User navigates to `/admin/` → FastAPI renders `admin.html` with server-side data
2. Alpine.js initializes reactive components (dark mode, sidebar state)
3. HTMX lazy-loads partials as tabs become visible (`hx-trigger="revealed once"`)
4. User interactions trigger HTMX requests → backend returns HTML fragments
5. HTMX swaps new HTML into target elements, Alpine.js re-initializes any new components

---

## 7. Full Dry Run of All Features

### 7.1 User Login

```
1. GET /admin/login → Renders login.html
   └─ Jinja2 template with email/password form
   └─ SSO provider buttons fetched dynamically

2. POST /admin/login (email, password)
   └─ admin.py: admin_login()
   └─ email_auth_service.authenticate(email, password)
       └─ Fetch EmailUser by email
       └─ argon2.verify(password, user.password_hash)
       └─ Generate JWT token with claims (sub, email, team_id, exp)
   └─ Set jwt_token as HttpOnly cookie
   └─ Redirect to /admin/ (HTTP 303)

3. GET /admin/ → admin_home()
   └─ Verify JWT from cookie
   └─ Query initial data: servers, tools (count), resources (count), gateways
   └─ Render admin.html with context data
```

### 7.2 Registering a Tool

```
1. POST /tools (JSON body: ToolCreate schema)
   └─ Router validates body → ToolCreate Pydantic model
   └─ auth dependency → verify JWT, resolve user/team

2. ToolService.register_tool(db, tool_create, team_id):
   a. Validate name uniqueness (scoped to team)
   b. Validate input_schema (if provided) is valid JSON Schema
   c. Create Tool ORM model:
      Tool(name=..., description=..., input_schema=..., team_id=..., slug=create_slug(name))
   d. db.add(tool) → db.commit()
   e. EventService.publish("tool.registered", {tool_id, name})
   f. RegistryCache.invalidate("tools")
   g. Return ToolRead schema (serialized from ORM model)

3. Response: 201 Created with ToolRead JSON
```

### 7.3 Invoking a Tool

```
1. POST /mcp (JSON-RPC: tools/call)
   Body: {"jsonrpc": "2.0", "method": "tools/call",
          "params": {"name": "search", "arguments": {"query": "hello"}}, "id": 1}

2. Middleware pipeline processes request (auth, validation, logging)

3. ToolService.invoke_tool(db, "search", {"query": "hello"}, team_id):
   a. Lookup: tool = db.query(Tool).filter_by(name="search", is_active=True).first()
   b. Schema validation: jsonschema.validate({"query": "hello"}, tool.input_schema)
   c. Pre-invoke plugins:
      └─ PluginManager.execute_hook("tool_pre_invoke", payload, context)
      └─ pii_filter: scan arguments for PII → redact if found
      └─ deny_filter: check against deny list → block if matched
      └─ rate_limiter: check rate limits → reject if exceeded
   d. Route invocation:
      ├─ tool.gateway_id is None → local invocation (call registered handler)
      └─ tool.gateway_id is set → remote invocation:
          └─ GatewayService.forward_request(gateway_id, "tools/call", params)
          └─ SSE: connect → send JSON-RPC → await response → disconnect
   e. Post-invoke plugins:
      └─ PluginManager.execute_hook("tool_post_invoke", result, context)
      └─ cached_tool_result: cache response for future calls
      └─ output_length_guard: truncate if response exceeds limit
   f. Record metrics:
      └─ ToolMetric(tool_id=..., latency_ms=42, success=True, timestamp=now)
   g. Return ToolResult

4. Response: {"jsonrpc": "2.0", "result": {"content": [{"type": "text", "text": "..."}]}, "id": 1}
```

### 7.4 Gateway Federation (Peer Discovery)

```
1. Startup: GatewayService initializes
   └─ If ENABLE_FEDERATION: start DiscoveryService
       └─ Advertise self via mDNS (Zeroconf)
       └─ Start background loops:
           └─ refresh_loop (5 min): poll peers for capability updates
           └─ cleanup_loop (10 min): remove stale peers

2. Peer discovered (mDNS or manual POST /gateways):
   a. DiscoveryService.add_peer(url):
      └─ GET {url}/mcp → initialize handshake
      └─ Parse server capabilities
      └─ Store DiscoveredPeer(url, capabilities, timestamp)
   b. GatewayService.register_gateway():
      └─ Create Gateway ORM model
      └─ connect_to_sse_server(url):
          └─ tools/list → register discovered tools
          └─ resources/list → register discovered resources
          └─ prompts/list → register discovered prompts
      └─ Mark tools/resources/prompts with gateway_id (remote origin)

3. Client requests tools/list:
   └─ ToolService.list_tools() returns local + federated tools
   └─ Each tool has gateway_id indicating origin

4. Client invokes federated tool:
   └─ ToolService detects tool.gateway_id is set
   └─ Forwards request to remote gateway via SSE/HTTP
   └─ Returns response to client
```

### 7.5 Plugin Execution Flow

```
1. PluginManager.initialize():
   a. ConfigLoader.load("plugins/config.yaml"):
      └─ Parse YAML with Jinja2 env var substitution
      └─ Return list of plugin configurations
   b. For each plugin config:
      └─ PluginLoader.load(kind="pii_filter", config={...})
      └─ Import module: plugins.pii_filter
      └─ Instantiate class: PiiFilter(config)
      └─ Discover hooks: scan methods for convention names or @hook decorators
      └─ Register in PluginInstanceRegistry:
          └─ hooks["tool_pre_invoke"] = [(priority=10, plugin=PiiFilter)]

2. Hook execution (e.g., tool_pre_invoke):
   a. PluginManager.execute_hook("tool_pre_invoke", payload, context):
      └─ Registry returns plugins sorted by priority
      └─ For each plugin:
          └─ Check mode (ENFORCE/PERMISSIVE/DISABLED)
          └─ Check conditions (tool name match, server match, etc.)
          └─ PluginExecutor.execute(plugin, payload, context, timeout=30s):
              └─ asyncio.wait_for(plugin.tool_pre_invoke(payload, context), timeout)
              └─ On success: payload = modified_payload (chain to next plugin)
              └─ On violation (ENFORCE mode): raise PluginViolationError
              └─ On violation (PERMISSIVE mode): log warning, continue
              └─ On error: log error, continue (unless ENFORCE)
   b. Return final payload after all plugins have processed
```

### 7.6 Export/Import Flow

```
Export:
1. GET /export?format=json (or POST /export with filters)
2. ExportService.export_configuration(db, filters):
   a. _export_tools(db) → query local tools (exclude federated)
   b. _export_gateways(db) → query gateways
   c. _export_servers(db) → query servers
   d. _export_prompts(db) → query prompts
   e. _export_resources(db) → query resources
   f. _export_roots(db) → query roots
   g. _extract_dependencies() → resolve inter-entity dependencies
   h. Assemble export document with version, timestamp, entity arrays
   i. Optional: encrypt sensitive fields (auth tokens)
3. Return JSON/YAML export document

Import:
1. POST /import (JSON/YAML body)
2. ImportService.import_configuration(db, document):
   a. Validate document schema
   b. For each entity type (gateways, tools, resources, prompts, servers):
      └─ Check for conflicts (existing name)
      └─ Create or update entity
      └─ Restore dependencies (tool → gateway associations)
   c. Commit all changes in a single transaction
3. Return import summary (created, updated, skipped counts)
```

### 7.7 Admin UI: Adding a Server via the Dashboard

```
1. User clicks "Add Server" button in Servers tab

2. JavaScript (admin.js) shows modal form:
   └─ Fields: Name, URL, Transport (SSE/WebSocket/HTTP), Auth Type, Auth Token

3. User fills form and clicks "Save"

4. HTMX sends POST /admin/servers with form data

5. admin.py: admin_create_server():
   a. Parse form data → ServerCreate schema
   b. ServerService.register_server(db, server_create, team_id)
   c. If transport is SSE/WebSocket:
      └─ GatewayService.connect_to_sse_server(url)
      └─ Discover and register tools/resources/prompts
   d. Return updated server table HTML partial

6. HTMX swaps new HTML into the servers table
   └─ New server appears in the list with status indicator
```

### 7.8 Observability: Viewing Traces

```
1. User clicks "Observability" tab in sidebar

2. HTMX loads: GET /admin/observability/partial
   └─ admin.py: renders observability_partial.html
   └─ Contains sub-tabs: Metrics, Traces, Prompts, Resources, Tools, Stats

3. User clicks "Traces" sub-tab

4. HTMX loads: GET /admin/observability/traces?page=1
   └─ Queries ObservabilityTrace table
   └─ Renders observability_traces_list.html with trace summaries

5. User clicks a trace row

6. HTMX loads: GET /admin/observability/traces/{trace_id}
   └─ Queries ObservabilityTrace + associated ObservabilitySpan records
   └─ Renders observability_trace_detail.html
   └─ Shows waterfall timeline of spans with durations
   └─ flame-graph.js renders interactive visualization
```

---

## Appendix A: Key File Quick Reference

| File | Lines (approx.) | Purpose |
|------|-----------------|---------|
| `main.py` | 1000+ | Application entry point, middleware, routers |
| `config.py` | 800+ | All configuration settings |
| `models.py` | 2000+ | 55+ ORM table definitions |
| `schemas.py` | 1500+ | 50+ Pydantic schemas |
| `db.py` | 300+ | Engine, sessions, connection pooling |
| `auth.py` | 400+ | JWT/token authentication |
| `admin.py` | 2000+ | 100+ admin UI endpoints |
| `services/gateway_service.py` | 4000+ | Gateway federation (largest service) |
| `services/tool_service.py` | 3000+ | Tool registration + invocation |
| `services/resource_service.py` | 2800+ | Resource management |
| `services/prompt_service.py` | 1900+ | Prompt templates |
| `static/admin.js` | 2000+ | Admin UI JavaScript |
| `templates/admin.html` | 1500+ | Main dashboard template |

## Appendix B: Environment Variable Categories

| Category | Example Variables | Count |
|----------|-------------------|-------|
| Core | `HOST`, `PORT`, `DATABASE_URL`, `RELOAD` | ~10 |
| Authentication | `JWT_SECRET_KEY`, `AUTH_REQUIRED`, `BASIC_AUTH_USER` | ~15 |
| SSO Providers | `GITHUB_CLIENT_ID`, `GOOGLE_CLIENT_ID`, `OKTA_DOMAIN` | ~30 |
| Features | `MCPGATEWAY_UI_ENABLED`, `MCPGATEWAY_A2A_ENABLED`, `PLUGINS_ENABLED` | ~20 |
| Caching | `REDIS_URL`, `RESOURCE_CACHE_SIZE`, `RESOURCE_CACHE_TTL` | ~10 |
| Federation | `MCPGATEWAY_ENABLE_FEDERATION`, `MCPGATEWAY_ENABLE_MDNS_DISCOVERY` | ~5 |
| Observability | `LOG_LEVEL`, `STRUCTURED_LOGGING_DATABASE_ENABLED` | ~15 |
| Limits | `TOOL_TIMEOUT`, `MCPGATEWAY_A2A_MAX_AGENTS`, `MAX_PATH_DEPTH` | ~15 |

## Appendix C: Database Relationship Map

```
EmailUser ──< UserRole >── Role
    │
    ├──< EmailApiToken
    ├──< EmailAuthEvent
    ├──< TokenRevocation
    │
    └──< EmailTeamMember >── EmailTeam
                                │
                                ├──< Tool
                                ├──< Resource
                                ├──< Prompt
                                ├──< Server
                                ├──< Gateway
                                └──< A2AAgent

Gateway ──< Tool     (federated tools)
        ──< Resource (federated resources)
        ──< Prompt   (federated prompts)

Server ──< Tool     (server-scoped tools)
       ──< Resource (server-scoped resources)
       ──< Prompt   (server-scoped prompts)

Tool     ──< ToolMetric     ──< ToolMetricsHourly
Resource ──< ResourceMetric ──< ResourceMetricsHourly
Prompt   ──< PromptMetric   ──< PromptMetricsHourly
Server   ──< ServerMetric   ──< ServerMetricsHourly
A2AAgent ──< A2AAgentMetric ──< A2AAgentMetricsHourly
```
