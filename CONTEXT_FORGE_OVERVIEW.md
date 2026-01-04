# 🚀 IBM mcp-context-forge Complete Overview

> **Model Context Protocol (MCP) Gateway & Registry** - A production-grade gateway that federates MCP and REST services, offering centralized management, security, observability, and protocol translation.

![ContextForge Banner](docs/docs/images/contextforge-banner.png)

---

## Table of Contents

- [1. Overview & Purpose](#1-overview--purpose)
- [2. Core Functionality](#2-core-functionality)
  - [2.1 Tool Registry](#21-tool-registry)
  - [2.2 Gateway Capabilities](#22-gateway-capabilities)
  - [2.3 Protocol Support](#23-protocol-support)
  - [2.4 Security & Authentication](#24-security--authentication)
  - [2.5 Observability](#25-observability)
  - [2.6 Admin UI](#26-admin-ui)
  - [2.7 Scalability & Federation](#27-scalability--federation)
- [3. Architecture & Workflow](#3-architecture--workflow)
  - [3.1 Interaction Flow](#31-interaction-flow)
  - [3.2 Federation Architecture](#32-federation-architecture)
  - [3.3 Protocol Translation](#33-protocol-translation)
- [4. Installation & Setup](#4-installation--setup)
  - [4.1 PyPI Installation](#41-pypi-installation)
  - [4.2 Docker Usage](#42-docker-usage)
  - [4.3 Optional Components](#43-optional-components)
  - [4.4 Configuration](#44-configuration)
- [5. Registering & Managing Tools](#5-registering--managing-tools)
  - [5.1 REST API Tools](#51-rest-api-tools)
  - [5.2 MCP Server Tools](#52-mcp-server-tools)
  - [5.3 A2A Tools](#53-a2a-tools)
  - [5.4 gRPC Services](#54-grpc-services)
  - [5.5 Tool Discovery & Federation](#55-tool-discovery--federation)
- [6. Using Tools from External Agents](#6-using-tools-from-external-agents)
  - [6.1 Agent Integration](#61-agent-integration)
  - [6.2 Protocol Conversion](#62-protocol-conversion)
  - [6.3 WatsonX Orchestrate Integration](#63-watsonx-orchestrate-integration)
- [7. Advanced Features](#7-advanced-features)
  - [7.1 Virtual Server Composition](#71-virtual-server-composition)
  - [7.2 Authentication Flows](#72-authentication-flows)
  - [7.3 Observability & Tracing](#73-observability--tracing)
  - [7.4 Rate-Limiting & Retries](#74-rate-limiting--retries)
  - [7.5 Plugin Architecture](#75-plugin-architecture)
  - [7.6 Multi-Tenancy & RBAC](#76-multi-tenancy--rbac)
- [8. Examples & Usage Scenarios](#8-examples--usage-scenarios)
  - [8.1 Quick Start Examples](#81-quick-start-examples)
  - [8.2 Tool Registration](#82-tool-registration)
  - [8.3 Federated Tool Discovery](#83-federated-tool-discovery)
- [9. Deployment in Production](#9-deployment-in-production)
  - [9.1 Kubernetes Deployment](#91-kubernetes-deployment)
  - [9.2 Docker Compose](#92-docker-compose)
  - [9.3 PostgreSQL Integration](#93-postgresql-integration)
  - [9.4 Redis Integration](#94-redis-integration)
  - [9.5 Air-Gapped Environments](#95-air-gapped-environments)
  - [9.6 Troubleshooting](#96-troubleshooting)
- [10. Further Reading & References](#10-further-reading--references)

---

## 1. Overview & Purpose

**IBM mcp-context-forge** (also known as **ContextForge MCP Gateway**) is a comprehensive Model Context Protocol (MCP) Gateway and Registry designed to sit in front of MCP servers, REST APIs, A2A (Agent-to-Agent) services, and gRPC services. It provides:

- **Unified Gateway**: Single endpoint for all AI clients to discover and invoke tools from multiple backend services
- **Protocol Translation**: Converts between REST, MCP, A2A, gRPC, WebSocket, SSE, and stdio protocols
- **Federation & Registry**: Distributes tool catalogs across multiple gateway instances with Redis-backed synchronization
- **Security & Auth**: JWT, OAuth, Basic Auth, SSO, and A2A authentication with role-based access control (RBAC)
- **Observability**: OpenTelemetry integration with Phoenix, Jaeger, Zipkin, and other OTLP backends
- **Admin UI**: Built-in web interface for managing servers, tools, prompts, resources, and monitoring logs
- **Production-Ready**: Scales to multi-cluster Kubernetes deployments with PostgreSQL, Redis, and comprehensive security features

The gateway acts as a centralized hub that allows AI agents (OpenAI, Anthropic, Claude, custom LLMs) to discover and use tools without implementing custom network code for each backend service.

### Key Use Cases

- **Tool Consolidation**: Aggregate tools from multiple MCP servers, REST APIs, and gRPC services into a single catalog
- **Legacy API Modernization**: Expose existing REST APIs as MCP-compliant tools without code changes
- **Multi-Agent Orchestration**: Enable different AI frameworks (LangChain, AutoGen, WatsonX Orchestrate) to share tools
- **Enterprise Deployment**: Deploy with authentication, rate-limiting, audit logging, and observability for production use
- **Federated AI Services**: Distribute tool catalogs across regions or clusters with automatic synchronization

---

## 2. Core Functionality

### 2.1 Tool Registry

The Tool Registry is the central catalog that tracks all available tools, their schemas, authentication requirements, and metadata.

**Key Features:**
- **Multi-Protocol Support**: Register tools from REST APIs, MCP servers, A2A services, and gRPC endpoints
- **Automatic Schema Generation**: Extracts JSON Schema from OpenAPI specs, MCP tool definitions, or gRPC reflection
- **Annotations**: Add metadata, descriptions, examples, and tags to tools for better discoverability
- **Versioning**: Track tool versions and maintain compatibility across updates
- **Visibility Control**: Configure tools as private (user-only), team (shared within team), or global (public)

**Registration Methods:**
- Admin UI (web interface)
- REST API endpoints (`POST /api/v1/servers`, `POST /api/v1/tools`)
- CLI commands (`mcpgateway` configuration)
- Bulk import via JSON/YAML files

### 2.2 Gateway Capabilities

The gateway provides intelligent routing, transformation, and management of requests between AI clients and backend services.

**Core Capabilities:**
- **Virtual Servers**: Compose custom tool collections by combining tools from multiple backends
- **Request Routing**: Intelligently route tool invocations to the appropriate backend server
- **Response Transformation**: Convert backend responses to MCP-compliant formats
- **Retry Logic**: Automatic retry with exponential backoff for transient failures
- **Circuit Breakers**: Prevent cascading failures by detecting and isolating unhealthy backends
- **Caching**: Cache tool schemas, responses, and metadata for improved performance
- **Rate Limiting**: Control request rates per user, team, or tool to prevent abuse

### 2.3 Protocol Support

ContextForge supports multiple transport protocols for maximum compatibility:

**Supported Protocols:**
- **HTTP/HTTPS**: Standard REST API endpoints
- **JSON-RPC 2.0**: MCP-compliant RPC over HTTP
- **WebSocket**: Bidirectional streaming for real-time communication
- **Server-Sent Events (SSE)**: Unidirectional streaming for live updates
- **stdio**: Standard input/output for local MCP servers
- **Streamable HTTP**: Custom protocol for efficient request/response streaming
- **gRPC**: Binary protocol with automatic service discovery via reflection

**Protocol Translation:**
- Automatically converts between protocols (e.g., REST → MCP, gRPC → MCP)
- Preserves semantics and error handling across protocol boundaries
- Supports both synchronous and asynchronous operations

### 2.4 Security & Authentication

Comprehensive security features protect the gateway and backend services:

**Authentication Methods:**
- **JWT (JSON Web Tokens)**: Token-based authentication with configurable expiration
- **Basic Auth**: Username/password authentication for simple use cases
- **OAuth 2.0**: Support for Authorization Code, Client Credentials, and Device flows
- **SSO (Single Sign-On)**: Integration with GitHub, Google, Microsoft Entra ID, Okta, Keycloak, IBM Security Verify
- **A2A (Agent-to-Agent)**: Specialized authentication for AI agents and services
- **Dynamic Client Registration (DCR)**: Automatic client registration for OAuth flows

**Authorization:**
- **Role-Based Access Control (RBAC)**: Assign roles (Platform Admin, Team Admin, Member) with granular permissions
- **Multi-Tenancy**: Isolate resources by user and team with configurable visibility
- **Header-Based Auth**: Forward authentication headers to backend services (`X-Upstream-Authorization`)
- **Per-Tool Auth**: Configure authentication requirements per tool or server

**Security Features:**
- TLS/SSL support with custom certificates
- Secrets management (avoid storing in environment variables)
- Input validation and sanitization
- Security headers and CORS configuration
- Audit logging of all authentication attempts

### 2.5 Observability

OpenTelemetry-based observability provides deep insights into gateway and tool performance:

**Tracing & Monitoring:**
- **Distributed Tracing**: Track requests across federated gateways and backend services
- **OpenTelemetry Integration**: Export traces to Phoenix, Jaeger, Zipkin, Tempo, DataDog, New Relic
- **LLM-Specific Metrics**: Token usage, costs, model performance, and latency tracking
- **Automatic Instrumentation**: Tools, prompts, resources, and gateway operations are automatically traced

**Logging:**
- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Log Levels**: Configurable DEBUG, INFO, WARNING, ERROR levels
- **Real-Time Log Viewer**: Built-in UI for filtering, searching, and exporting logs
- **Audit Logs**: Track all tool invocations, authentication attempts, and configuration changes

**Health Checks:**
- `/health` and `/health/ready` endpoints for Kubernetes probes
- Backend health monitoring with automatic failover
- Metrics endpoint for Prometheus integration

### 2.6 Admin UI

The Admin UI is a built-in web interface for managing the gateway:

**Features:**
- **Server Management**: Add, edit, delete, and test MCP servers and REST APIs
- **Tool Catalog**: Browse, search, filter tools by name, tags, server, or visibility
- **Virtual Servers**: Create custom tool collections and manage composition
- **User Management**: Manage users, teams, roles, and permissions
- **Authentication Config**: Configure OAuth providers, SSO, and authentication methods
- **Log Viewer**: Real-time log streaming with filtering and search
- **Dashboard**: Overview of servers, tools, users, and system health

**Technology:**
- Built with HTMX and Alpine.js for reactive, low-JavaScript UI
- Responsive design for desktop and mobile
- Air-gapped deployment support (no external dependencies)

**⚠️ Important**: The Admin UI is designed for development and localhost use. For production deployments, disable the UI (`MCPGATEWAY_UI_ENABLED=false`) and use the REST API with proper authentication.

### 2.7 Scalability & Federation

ContextForge scales from single-node deployments to multi-cluster environments:

**Scalability:**
- **Horizontal Scaling**: Run multiple gateway instances behind a load balancer
- **Database Support**: SQLite (development), PostgreSQL (production), MariaDB/MySQL
- **Connection Pooling**: Configurable pool sizes for database and Redis connections
- **Caching Strategies**: In-memory, database-backed, or Redis-distributed caching

**Federation:**
- **Multi-Gateway Sync**: Synchronize tool catalogs across multiple gateway instances
- **Redis-Backed Federation**: Use Redis pub/sub for real-time catalog updates
- **mDNS/Zeroconf Discovery**: Automatic peer discovery on local networks
- **Health Checks & Failover**: Detect failed peers and route requests to healthy instances
- **Cross-Region Deployment**: Distribute gateways across regions with centralized catalog

---

## 3. Architecture & Workflow

### 3.1 Interaction Flow

The typical workflow for using ContextForge MCP Gateway:

```
┌─────────────────┐
│   AI Client     │  (Claude Desktop, LangChain, AutoGen, etc.)
│  (Agent/LLM)    │
└────────┬────────┘
         │ 1. Discover tools (MCP protocol)
         ▼
┌─────────────────────────────────────────┐
│   ContextForge MCP Gateway              │
│  ┌─────────────────────────────────┐   │
│  │  Tool Registry & Catalog        │   │ 2. Query registry
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  Auth, Rate Limit, Validation   │   │ 3. Apply policies
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  Protocol Translation Layer     │   │ 4. Convert protocols
│  └─────────────────────────────────┘   │
└────────┬────────────────────────────────┘
         │ 5. Route to backend
         ▼
┌─────────────────────────────────────────┐
│   Backend Services                      │
│  ┌──────────┐ ┌──────────┐ ┌─────────┐ │
│  │ MCP      │ │ REST API │ │ gRPC    │ │
│  │ Server   │ │          │ │ Service │ │
│  └──────────┘ └──────────┘ └─────────┘ │
└─────────────────────────────────────────┘
```

**Step-by-Step Flow:**

1. **Tool Discovery**: AI client connects to gateway via MCP protocol and requests available tools
2. **Authentication**: Gateway validates client credentials (JWT, OAuth, Basic Auth)
3. **Catalog Query**: Gateway queries registry for tools matching client's access level
4. **Tool Invocation**: Client invokes a tool by sending MCP tool call request
5. **Authorization**: Gateway checks if client has permission to invoke the tool
6. **Protocol Translation**: Gateway converts MCP request to backend protocol (REST, gRPC, etc.)
7. **Request Routing**: Gateway routes request to appropriate backend server
8. **Backend Execution**: Backend service executes the tool and returns response
9. **Response Translation**: Gateway converts backend response to MCP format
10. **Result Delivery**: Gateway returns MCP-compliant response to client

### 3.2 Federation Architecture

Federation enables multiple gateway instances to share a unified tool catalog:

```
                    ┌──────────────┐
                    │    Redis     │ (Pub/Sub + Cache)
                    └──────┬───────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐       ┌────▼────┐      ┌────▼────┐
    │Gateway 1│       │Gateway 2│      │Gateway 3│
    │ (US)    │       │ (EU)    │      │ (APAC)  │
    └────┬────┘       └────┬────┘      └────┬────┘
         │                 │                 │
    ┌────▼────┐       ┌────▼────┐      ┌────▼────┐
    │Local    │       │Local    │      │Local    │
    │MCP      │       │MCP      │      │MCP      │
    │Servers  │       │Servers  │      │Servers  │
    └─────────┘       └─────────┘      └─────────┘
```

**Federation Features:**
- **Catalog Sync**: Tools registered on one gateway appear on all federated gateways
- **Health Monitoring**: Each gateway monitors peers and routes around failures
- **Regional Routing**: Route requests to geographically closest backend
- **Conflict Resolution**: Handle tool name collisions across federations

### 3.3 Protocol Translation

ContextForge seamlessly translates between different protocols:

**REST → MCP Translation:**
```json
// REST API Endpoint
GET /api/weather?city=London

// Translated to MCP Tool
{
  "name": "get_weather",
  "description": "Get weather for a city",
  "inputSchema": {
    "type": "object",
    "properties": {
      "city": { "type": "string" }
    },
    "required": ["city"]
  }
}
```

**gRPC → MCP Translation:**
- Automatic service discovery via gRPC Server Reflection
- Converts protobuf definitions to JSON Schema
- Maps gRPC methods to MCP tools
- Handles streaming and bidirectional communication

**Protocol Conversion Benefits:**
- AI clients only need to implement MCP protocol
- Backend services don't require MCP-specific code
- Centralized management of protocol-specific quirks
- Consistent error handling across protocols

---

## 4. Installation & Setup

### 4.1 PyPI Installation

Install ContextForge from PyPI for local development or production use:

**Quick Start:**
```bash
# Install using pip
pip install mcp-contextforge-gateway

# Or using uv (recommended)
uvx --from mcp-contextforge-gateway mcpgateway --host 0.0.0.0 --port 4444
```

**Step-by-Step Installation:**
```bash
# 1. Create isolated virtual environment
mkdir mcpgateway && cd mcpgateway
python3 -m venv .venv && source .venv/bin/activate

# 2. Install gateway
pip install --upgrade pip
pip install mcp-contextforge-gateway

# 3. Download configuration template
curl -O https://raw.githubusercontent.com/IBM/mcp-context-forge/main/.env.example
cp .env.example .env

# 4. Edit configuration (set passwords, secrets, etc.)
nano .env

# 5. Run gateway
mcpgateway --host 0.0.0.0 --port 4444
```

**Environment Variables for Quick Start:**
```bash
export MCPGATEWAY_UI_ENABLED=true
export MCPGATEWAY_ADMIN_API_ENABLED=true
export PLATFORM_ADMIN_EMAIL=admin@example.com
export PLATFORM_ADMIN_PASSWORD=changeme
export PLATFORM_ADMIN_FULL_NAME="Platform Administrator"
export JWT_SECRET_KEY=your-secret-key-change-me
export BASIC_AUTH_PASSWORD=pass

mcpgateway --host 0.0.0.0 --port 4444
```

### 4.2 Docker Usage

Run ContextForge in a container for production or testing:

**Minimum Viable Run:**
```bash
docker run -p 4444:4444 \
  -e MCPGATEWAY_UI_ENABLED=true \
  -e MCPGATEWAY_ADMIN_API_ENABLED=true \
  -e PLATFORM_ADMIN_EMAIL=admin@example.com \
  -e PLATFORM_ADMIN_PASSWORD=changeme \
  -e JWT_SECRET_KEY=your-secret-key \
  ghcr.io/ibm/mcp-context-forge:latest
```

**Persist SQLite Database:**
```bash
docker run -p 4444:4444 \
  -v $(pwd)/data:/app/data \
  -e DATABASE_URL=sqlite:///./data/mcp.db \
  -e MCPGATEWAY_UI_ENABLED=true \
  ghcr.io/ibm/mcp-context-forge:latest
```

**Host Network Mode (for local server discovery):**
```bash
docker run --network host \
  -e MCPGATEWAY_UI_ENABLED=true \
  -e HOST=0.0.0.0 \
  -e PORT=4444 \
  ghcr.io/ibm/mcp-context-forge:latest
```

**Using docker-compose:**
```bash
# Download docker-compose.yml
curl -O https://raw.githubusercontent.com/IBM/mcp-context-forge/main/docker-compose.yml

# Start with PostgreSQL and Redis
docker-compose up -d
```

**Key Environment Variables:**
- `MCPGATEWAY_UI_ENABLED`: Enable/disable Admin UI (default: false)
- `MCPGATEWAY_ADMIN_API_ENABLED`: Enable/disable Admin API (default: true)
- `DATABASE_URL`: Database connection string (SQLite, PostgreSQL, MySQL)
- `REDIS_URL`: Redis connection for caching and federation
- `JWT_SECRET_KEY`: Secret key for JWT token generation
- `PLATFORM_ADMIN_EMAIL`: Initial admin user email
- `PLATFORM_ADMIN_PASSWORD`: Initial admin user password

### 4.3 Optional Components

**PostgreSQL (Recommended for Production):**
```bash
# Using Docker
docker run -d \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -e POSTGRES_DB=mcp \
  postgres:15

# Configure gateway
export DATABASE_URL=postgresql+psycopg://postgres:mysecretpassword@localhost:5432/mcp
```

**Redis (For Caching & Federation):**
```bash
# Using Docker
docker run -d \
  -p 6379:6379 \
  redis:7-alpine

# Configure gateway
export CACHE_TYPE=redis
export REDIS_URL=redis://localhost:6379/0
```

**Phoenix (LLM Observability):**
```bash
# Start Phoenix
docker run -p 6006:6006 -p 4317:4317 arizephoenix/phoenix:latest

# Configure gateway
export OTEL_ENABLE_OBSERVABILITY=true
export OTEL_TRACES_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

### 4.4 Configuration

ContextForge can be configured via `.env` file or environment variables:

**Basic Configuration (`.env`):**
```bash
# Application
APP_NAME=MCP_Gateway
HOST=0.0.0.0
PORT=4444
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql+psycopg://postgres:password@db:5432/mcp

# Cache
CACHE_TYPE=redis
REDIS_URL=redis://redis:6379/0

# Auth
JWT_SECRET_KEY=your-very-secret-key-change-me
BASIC_AUTH_USER=admin
BASIC_AUTH_PASSWORD=changeme

# Platform Admin (created on first run)
PLATFORM_ADMIN_EMAIL=admin@example.com
PLATFORM_ADMIN_PASSWORD=secure-password
PLATFORM_ADMIN_FULL_NAME="Platform Administrator"

# Features
MCPGATEWAY_UI_ENABLED=false  # Disable in production
MCPGATEWAY_ADMIN_API_ENABLED=true
MCPGATEWAY_ENABLE_TOOLS=true
MCPGATEWAY_ENABLE_PROMPTS=true
MCPGATEWAY_ENABLE_RESOURCES=true

# Observability
OTEL_ENABLE_OBSERVABILITY=true
OTEL_TRACES_EXPORTER=otlp
OTEL_EXPORTER_OTLP_ENDPOINT=http://phoenix:4317

# Federation
MCPGATEWAY_ENABLE_FEDERATION=true
MCPGATEWAY_PEER_DISCOVERY=redis  # or mdns, manual
```

**Verification:**
```bash
# Check environment configuration
make check-env

# Test API connectivity
curl http://localhost:4444/health
```

---

## 5. Registering & Managing Tools

### 5.1 REST API Tools

Register existing REST APIs as MCP tools without code changes:

**Method 1: Admin UI**
1. Navigate to http://localhost:4444/ui
2. Click "Servers" → "Add Server"
3. Select "REST API" type
4. Enter base URL and authentication
5. Gateway automatically discovers endpoints

**Method 2: REST API**
```bash
curl -X POST http://localhost:4444/api/v1/servers \
  -H "Authorization: Bearer $MCPGATEWAY_BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "weather-api",
    "url": "https://api.weather.com",
    "auth_type": "bearer",
    "auth_token": "your-api-key",
    "tool_annotations": {
      "get_weather": {
        "description": "Get current weather for a city",
        "tags": ["weather", "public"]
      }
    }
  }'
```

**Method 3: Annotations in Code**
For APIs you control, add MCP annotations:
```python
from mcpgateway.annotations import tool

@tool(
    name="get_weather",
    description="Get weather for a city",
    tags=["weather", "api"]
)
def get_weather(city: str) -> dict:
    """Fetch weather data."""
    return {"city": city, "temp": 72, "conditions": "sunny"}
```

### 5.2 MCP Server Tools

Register native MCP servers:

**Stdio MCP Servers:**
```bash
# Using translate wrapper
python -m mcpgateway.translate \
  --stdio "uvx mcp-server-git" \
  --port 9000

# Then register in gateway
curl -X POST http://localhost:4444/api/v1/servers \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "git-server",
    "url": "http://localhost:9000",
    "transport": "sse"
  }'
```

**HTTP/SSE MCP Servers:**
```bash
curl -X POST http://localhost:4444/api/v1/servers \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "filesystem-server",
    "url": "http://localhost:8080/sse",
    "transport": "sse",
    "protocol_version": "2025-03-26"
  }'
```

**WebSocket MCP Servers:**
```bash
curl -X POST http://localhost:4444/api/v1/servers \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "realtime-server",
    "url": "ws://localhost:8080/mcp",
    "transport": "websocket"
  }'
```

### 5.3 A2A Tools

Agent-to-Agent (A2A) tools enable external AI services to register capabilities:

**Register A2A Tool:**
```bash
curl -X POST http://localhost:4444/api/v1/tools \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "analyze_sentiment",
    "description": "Analyze sentiment of text",
    "type": "a2a",
    "endpoint": "https://ai-service.com/sentiment",
    "inputSchema": {
      "type": "object",
      "properties": {
        "text": {"type": "string"}
      },
      "required": ["text"]
    }
  }'
```

**WatsonX Orchestrate Integration:**
See [Tutorial: Deploying MCP Tools on watsonx Orchestrate](https://developer.ibm.com/tutorials/build-mcp-tools-mcp-gateway-watsonx-orchestrate-agents) for detailed steps.

### 5.4 gRPC Services

Automatically discover and register gRPC services:

```bash
curl -X POST http://localhost:4444/api/v1/servers \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "grpc-service",
    "url": "grpc://localhost:50051",
    "transport": "grpc",
    "reflection_enabled": true
  }'
```

Gateway uses gRPC Server Reflection to:
- Discover available services and methods
- Extract protobuf definitions
- Generate JSON Schema for each method
- Create MCP tools automatically

### 5.5 Tool Discovery & Federation

**Discover Tools (MCP Client):**
```python
from mcp import StdioServerParameters, stdio_client

server_params = StdioServerParameters(
    command="uvx",
    args=["mcp-contextforge-gateway-wrapper"],
    env={
        "MCP_SERVER_URL": "http://localhost:4444",
        "MCP_AUTH": f"Bearer {token}"
    }
)

async with stdio_client(server_params) as (read, write):
    result = await session.list_tools()
    print(f"Available tools: {result.tools}")
```

**Federated Discovery:**
When federation is enabled, tools from all peer gateways appear in the catalog:

```bash
# Gateway 1 (US): Has tools A, B, C
# Gateway 2 (EU): Has tools D, E, F
# Gateway 3 (APAC): Has tools G, H, I

# Query any gateway returns all tools A-I
curl http://gateway1:4444/api/v1/tools
# Returns: [A, B, C, D, E, F, G, H, I]
```

---

## 6. Using Tools from External Agents

### 6.1 Agent Integration

ContextForge integrates with popular AI frameworks and agents:

**Claude Desktop:**
Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "contextforge": {
      "command": "uvx",
      "args": [
        "mcp-contextforge-gateway-wrapper",
        "--server-url", "http://localhost:4444",
        "--auth", "Bearer YOUR_TOKEN"
      ]
    }
  }
}
```

**LangChain:**
```python
from langchain.agents import initialize_agent
from langchain.tools import Tool
import requests

# Discover tools from gateway
response = requests.get(
    "http://localhost:4444/api/v1/tools",
    headers={"Authorization": f"Bearer {token}"}
)
tools_data = response.json()

# Create LangChain tools
tools = []
for tool_data in tools_data:
    def call_tool(input_data, tool=tool_data):
        response = requests.post(
            f"http://localhost:4444/api/v1/tools/{tool['name']}/invoke",
            headers={"Authorization": f"Bearer {token}"},
            json={"arguments": input_data}
        )
        return response.json()
    
    tools.append(Tool(
        name=tool_data["name"],
        description=tool_data["description"],
        func=call_tool
    ))

# Create agent
agent = initialize_agent(tools, llm, agent="zero-shot-react-description")
```

**OpenAI Function Calling:**
```python
import openai

# Get tools from gateway
response = requests.get(
    "http://localhost:4444/api/v1/tools",
    headers={"Authorization": f"Bearer {token}"}
)

# Convert to OpenAI function format
functions = []
for tool in response.json():
    functions.append({
        "name": tool["name"],
        "description": tool["description"],
        "parameters": tool["inputSchema"]
    })

# Use with OpenAI
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What's the weather in London?"}],
    functions=functions
)
```

### 6.2 Protocol Conversion

**MCP Tool Call (from AI Client):**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "get_weather",
    "arguments": {
      "city": "London"
    }
  },
  "id": 1
}
```

**Gateway Converts to REST:**
```http
GET https://api.weather.com/v1/current?city=London
Authorization: Bearer backend-api-key
```

**Gateway Returns MCP Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"city\":\"London\",\"temp\":72,\"conditions\":\"sunny\"}"
      }
    ]
  },
  "id": 1
}
```

### 6.3 WatsonX Orchestrate Integration

Deploy MCP tools to WatsonX Orchestrate for enterprise AI workflows:

**Step 1: Register Gateway in Orchestrate**
1. Log into WatsonX Orchestrate
2. Navigate to "Skills" → "Add Skill"
3. Select "MCP Server"
4. Enter gateway URL: `http://your-gateway:4444`
5. Configure authentication (JWT token)

**Step 2: Synchronize Tools**
Tools registered in ContextForge automatically appear in WatsonX Orchestrate catalog

**Step 3: Use in Orchestrate Flows**
- Build workflows using gateway tools
- Combine with other Orchestrate skills
- Add approval gates and business logic

See [IBM Developer Tutorial](https://developer.ibm.com/tutorials/build-mcp-tools-mcp-gateway-watsonx-orchestrate-agents) for complete guide.

---

## 7. Advanced Features

### 7.1 Virtual Server Composition

Virtual servers allow you to create custom tool collections:

**Create Virtual Server:**
```bash
curl -X POST http://localhost:4444/api/v1/virtual-servers \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "data-analytics",
    "description": "Tools for data analysis",
    "servers": ["postgres-server", "pandas-server", "plotly-server"],
    "tools": ["query_database", "analyze_dataframe", "create_chart"],
    "visibility": "team"
  }'
```

**Use Cases:**
- **Role-Based Collections**: Different tool sets for analysts, developers, managers
- **Project-Specific Tools**: Group tools needed for a specific project
- **Isolated Environments**: Separate production and development tools

### 7.2 Authentication Flows

**Email-Based Registration:**
```bash
# User registers
curl -X POST http://localhost:4444/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure-password",
    "full_name": "John Doe"
  }'

# User logs in
curl -X POST http://localhost:4444/auth/login \
  -d '{
    "email": "user@example.com",
    "password": "secure-password"
  }'
# Returns: {"access_token": "jwt-token", "token_type": "bearer"}
```

**OAuth 2.0 Flow:**
```bash
# Configure OAuth provider in .env
SSO_ENABLED=true
SSO_PROVIDER_NAME=github
SSO_CLIENT_ID=your-github-client-id
SSO_CLIENT_SECRET=your-github-client-secret
SSO_AUTHORIZATION_ENDPOINT=https://github.com/login/oauth/authorize
SSO_TOKEN_ENDPOINT=https://github.com/login/oauth/access_token
SSO_USERINFO_ENDPOINT=https://api.github.com/user

# Users click "Login with GitHub" in UI
# Gateway handles OAuth flow automatically
```

**Dynamic Client Registration:**
```bash
# Client requests registration
curl -X POST http://localhost:4444/oauth/register \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "My AI Agent",
    "redirect_uris": ["http://localhost:8080/callback"],
    "grant_types": ["authorization_code"]
  }'

# Returns client_id and client_secret
```

### 7.3 Observability & Tracing

**Enable OpenTelemetry:**
```bash
# Configuration
export OTEL_ENABLE_OBSERVABILITY=true
export OTEL_SERVICE_NAME=mcp-gateway
export OTEL_TRACES_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317

# Start gateway - traces automatically exported
mcpgateway
```

**View Traces in Phoenix:**
1. Access Phoenix UI: http://localhost:6006
2. View LLM traces with token usage and costs
3. Analyze tool invocation patterns
4. Debug performance bottlenecks

**Trace Attributes:**
- Tool name and server
- Input arguments and output
- Execution duration
- Authentication context
- Error details

### 7.4 Rate-Limiting & Retries

**Rate Limiting Configuration:**
```python
# Per-user rate limit
curl -X PATCH http://localhost:4444/api/v1/tools/get_weather \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "rate_limit": {
      "requests_per_minute": 10,
      "requests_per_hour": 100
    }
  }'
```

**Retry Configuration:**
```bash
# Per-server retry policy
curl -X PATCH http://localhost:4444/api/v1/servers/weather-api \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "retry_config": {
      "max_retries": 3,
      "backoff_strategy": "exponential",
      "initial_delay": 1000,
      "max_delay": 10000
    }
  }'
```

### 7.5 Plugin Architecture

ContextForge supports plugins for extending functionality:

**Built-in Plugins:**
- **PII Filter**: Remove personally identifiable information from logs
- **Deny Filter**: Block specific tools or patterns
- **Regex Filter**: Transform requests/responses with regex
- **Resource Filter**: Control access to resources

**Plugin Configuration (`plugins/config.yaml`):**
```yaml
plugins:
  - name: pii_filter
    enabled: true
    config:
      mask_email: true
      mask_phone: true
      mask_ssn: true
  
  - name: deny_filter
    enabled: true
    config:
      blocked_tools: ["dangerous_tool"]
      blocked_patterns: [".*delete.*"]
```

**Custom Plugins:**
Create plugins in `plugins/` directory following the plugin framework interface.

### 7.6 Multi-Tenancy & RBAC

**User Roles:**
- **Platform Admin**: Full system access, manage all resources
- **Team Admin**: Manage team resources, users, and tools
- **Team Member**: Access team tools and resources

**Resource Visibility:**
- **Private**: Only visible to creator
- **Team**: Visible to team members
- **Global**: Visible to all authenticated users

**Create Team:**
```bash
curl -X POST http://localhost:4444/api/v1/teams \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Data Science Team",
    "description": "ML and analytics team"
  }'
```

**Add Team Member:**
```bash
curl -X POST http://localhost:4444/api/v1/teams/team-id/members \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "user_email": "analyst@example.com",
    "role": "member"
  }'
```

---

## 8. Examples & Usage Scenarios

### 8.1 Quick Start Examples

**Example 1: Register and Use a REST API Tool**
```bash
# 1. Start gateway
mcpgateway --host 0.0.0.0 --port 4444

# 2. Get auth token
export TOKEN=$(python -m mcpgateway.utils.create_jwt_token \
  --username admin@example.com --exp 10080 --secret my-key)

# 3. Register REST API
curl -X POST http://localhost:4444/api/v1/servers \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "jsonplaceholder",
    "url": "https://jsonplaceholder.typicode.com"
  }'

# 4. Invoke tool
curl -X POST http://localhost:4444/api/v1/tools/get_users/invoke \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"arguments": {}}'
```

### 8.2 Tool Registration

**Example: Weather API with Authentication**
```bash
curl -X POST http://localhost:4444/api/v1/servers \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "weather-api",
    "url": "https://api.openweathermap.org/data/2.5",
    "auth_type": "query_param",
    "auth_config": {
      "param_name": "appid",
      "param_value": "your-api-key"
    },
    "tool_annotations": {
      "weather": {
        "description": "Get current weather",
        "input_transform": {
          "city": "q",
          "units": "units"
        }
      }
    }
  }'
```

**Example: Stdio MCP Server**
```bash
# 1. Start stdio wrapper
python -m mcpgateway.translate \
  --stdio "uvx mcp-server-filesystem /tmp" \
  --port 9001 &

# 2. Register in gateway
curl -X POST http://localhost:4444/api/v1/servers \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "filesystem",
    "url": "http://localhost:9001/sse",
    "transport": "sse"
  }'
```

### 8.3 Federated Tool Discovery

**Example: Multi-Region Setup**
```yaml
# docker-compose.yml for 3 regions
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
  
  gateway-us:
    image: ghcr.io/ibm/mcp-context-forge:latest
    environment:
      - CACHE_TYPE=redis
      - REDIS_URL=redis://redis:6379/0
      - MCPGATEWAY_ENABLE_FEDERATION=true
      - REGION=us
    ports: ["4444:4444"]
  
  gateway-eu:
    image: ghcr.io/ibm/mcp-context-forge:latest
    environment:
      - CACHE_TYPE=redis
      - REDIS_URL=redis://redis:6379/0
      - MCPGATEWAY_ENABLE_FEDERATION=true
      - REGION=eu
    ports: ["4445:4444"]
  
  gateway-apac:
    image: ghcr.io/ibm/mcp-context-forge:latest
    environment:
      - CACHE_TYPE=redis
      - REDIS_URL=redis://redis:6379/0
      - MCPGATEWAY_ENABLE_FEDERATION=true
      - REGION=apac
    ports: ["4446:4444"]
```

**Query Federated Catalog:**
```bash
# Tools registered on any gateway appear on all gateways
curl http://localhost:4444/api/v1/tools | jq '.[] | {name, server, region}'
```


---

## 9. Deployment in Production

### 9.1 Kubernetes Deployment

**Using Helm Chart:**
```bash
# Add Helm repository
helm repo add contextforge https://ibm.github.io/mcp-context-forge/charts
helm repo update

# Install with custom values
helm install mcp-gateway contextforge/mcp-gateway \
  --set postgresql.enabled=true \
  --set redis.enabled=true \
  --set replicaCount=3 \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=gateway.example.com \
  --set env.JWT_SECRET_KEY=your-secret-key \
  --set env.MCPGATEWAY_UI_ENABLED=false
```

**Manual Kubernetes Manifests:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-gateway
  template:
    metadata:
      labels:
        app: mcp-gateway
    spec:
      containers:
      - name: gateway
        image: ghcr.io/ibm/mcp-context-forge:latest
        ports:
        - containerPort: 4444
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: gateway-secrets
              key: database-url
        - name: REDIS_URL
          value: redis://redis-service:6379/0
        - name: MCPGATEWAY_UI_ENABLED
          value: "false"
        livenessProbe:
          httpGet:
            path: /health
            port: 4444
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 4444
          initialDelaySeconds: 15
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: mcp-gateway
spec:
  selector:
    app: mcp-gateway
  ports:
  - port: 80
    targetPort: 4444
  type: LoadBalancer
```

### 9.2 Docker Compose

**Production docker-compose.yml:**
```yaml
version: '3.8'

services:
  gateway:
    image: ghcr.io/ibm/mcp-context-forge:latest
    ports:
      - "4444:4444"
    environment:
      - DATABASE_URL=postgresql+psycopg://postgres:${POSTGRES_PASSWORD}@postgres:5432/mcp
      - REDIS_URL=redis://redis:6379/0
      - CACHE_TYPE=redis
      - MCPGATEWAY_UI_ENABLED=false
      - MCPGATEWAY_ADMIN_API_ENABLED=true
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - PLATFORM_ADMIN_EMAIL=${ADMIN_EMAIL}
      - PLATFORM_ADMIN_PASSWORD=${ADMIN_PASSWORD}
      - OTEL_ENABLE_OBSERVABILITY=true
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
  
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=mcp
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
    restart: unless-stopped
  
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # Jaeger UI
      - "4317:4317"    # OTLP gRPC
    restart: unless-stopped

volumes:
  postgres-data:
  redis-data:
```

**Start Services:**
```bash
# Create .env file with secrets
cat > .env << EOF
POSTGRES_PASSWORD=your-secure-password
JWT_SECRET_KEY=your-jwt-secret
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin-password
EOF

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f gateway

# Check health
curl http://localhost:4444/health
```

### 9.3 PostgreSQL Integration

**Connection Configuration:**
```bash
# PostgreSQL with psycopg3 (recommended)
DATABASE_URL=postgresql+psycopg://user:password@host:5432/dbname

# With connection pool tuning
DB_POOL_SIZE=50
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

**PgBouncer for Connection Pooling:**
```ini
# pgbouncer.ini
[databases]
mcp = host=postgres port=5432 dbname=mcp

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = md5
auth_file = userlist.txt
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
```

**Gateway Configuration with PgBouncer:**
```bash
DATABASE_URL=postgresql+psycopg://user:password@pgbouncer:6432/mcp
DB_POOL_SIZE=15  # Smaller pool since PgBouncer handles pooling
```

### 9.4 Redis Integration

**Redis Configuration:**
```bash
# Basic Redis
CACHE_TYPE=redis
REDIS_URL=redis://localhost:6379/0

# Redis with authentication
REDIS_URL=redis://username:password@localhost:6379/0

# Redis Cluster
REDIS_URL=redis://node1:6379,node2:6379,node3:6379/0

# Performance tuning
REDIS_MAX_CONNECTIONS=50
REDIS_SOCKET_TIMEOUT=2.0
REDIS_HEALTH_CHECK_INTERVAL=30
```

**Redis for Federation:**
```bash
# Enable federation with Redis pub/sub
MCPGATEWAY_ENABLE_FEDERATION=true
MCPGATEWAY_PEER_DISCOVERY=redis
CACHE_TYPE=redis
REDIS_URL=redis://redis:6379/0
```

### 9.5 Air-Gapped Environments

Deploy ContextForge in environments without internet access:

**Preparation:**
```bash
# 1. Download Docker image
docker pull ghcr.io/ibm/mcp-context-forge:latest
docker save ghcr.io/ibm/mcp-context-forge:latest > mcp-gateway.tar

# 2. Transfer to air-gapped environment
scp mcp-gateway.tar airgap-host:/tmp/

# 3. Load image on air-gapped host
docker load < /tmp/mcp-gateway.tar
```

**Configuration for Air-Gapped:**
```bash
# Disable external dependencies
MCPGATEWAY_UI_ENABLED=true  # UI has no external dependencies
OTEL_ENABLE_OBSERVABILITY=false  # Or use local OTLP collector
CACHE_TYPE=database  # Or local Redis instance

# Start gateway
docker run -p 4444:4444 \
  -e MCPGATEWAY_UI_ENABLED=true \
  -e DATABASE_URL=sqlite:///./data/mcp.db \
  -v $(pwd)/data:/app/data \
  ghcr.io/ibm/mcp-context-forge:latest
```

### 9.6 Troubleshooting

**Common Issues:**

**1. Database Connection Errors**
```bash
# Check database connectivity
psql -h localhost -U postgres -d mcp -c "SELECT 1;"

# Verify DATABASE_URL format
echo $DATABASE_URL
# Should be: postgresql+psycopg://user:pass@host:5432/db

# Check logs
docker logs mcp-gateway | grep -i database
```

**2. Redis Connection Errors**
```bash
# Test Redis connectivity
redis-cli -h localhost -p 6379 ping
# Should return: PONG

# Check gateway Redis config
curl http://localhost:4444/health | jq '.redis'
```

**3. Port Binding Issues**
```bash
# Check if port is already in use
lsof -i :4444

# Use different port
docker run -p 5555:4444 -e PORT=4444 ...
```

**4. Authentication Failures**
```bash
# Verify JWT secret is set
echo $JWT_SECRET_KEY

# Generate valid token
python -m mcpgateway.utils.create_jwt_token \
  --username admin@example.com \
  --exp 10080 \
  --secret $JWT_SECRET_KEY

# Test authentication
curl -H "Authorization: Bearer $TOKEN" http://localhost:4444/api/v1/tools
```

**5. Tool Invocation Errors**
```bash
# Check server health
curl http://localhost:4444/api/v1/servers | jq '.[] | {name, health_status}'

# View tool details
curl http://localhost:4444/api/v1/tools/tool-name | jq .

# Check logs for errors
docker logs mcp-gateway --tail 100 | grep ERROR
```

**Diagnostic Commands:**
```bash
# Health check
curl http://localhost:4444/health

# List all servers
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:4444/api/v1/servers

# Test tool invocation
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"arguments": {}}' \
  http://localhost:4444/api/v1/tools/tool-name/invoke

# View OpenAPI docs
open http://localhost:4444/docs
```

---

## 10. Further Reading & References

### Official Documentation

- **GitHub Repository**: https://github.com/IBM/mcp-context-forge
- **Documentation Site**: https://ibm.github.io/mcp-context-forge/
- **PyPI Package**: https://pypi.org/project/mcp-contextforge-gateway/
- **Docker Images**: https://github.com/ibm/mcp-context-forge/pkgs/container/mcp-context-forge

### MCP Protocol & Specification

- **Model Context Protocol**: https://modelcontextprotocol.io
- **MCP Specification**: https://spec.modelcontextprotocol.io
- **MCP GitHub**: https://github.com/modelcontextprotocol

### Tutorials & Guides

- **Deploying MCP Tools on watsonx Orchestrate**: https://developer.ibm.com/tutorials/build-mcp-tools-mcp-gateway-watsonx-orchestrate-agents
- **CLI and UI Usage Guide**: https://heidloff.net/article/context-forge-client/
- **Complete Guide to MCP Gateway**: https://www.decisioncrafters.com/ibm-mcp-context-forge-the-complete-guide-to-mcp-gateway-registry-for-ai-agent-infrastructure/
- **ArgoCD Helm Deployment Tutorial**: https://ibm.github.io/mcp-context-forge/tutorials/argocd-helm-deployment-ibm-cloud-iks/
- **OpenWebUI Integration**: https://ibm.github.io/mcp-context-forge/tutorials/openwebui-tutorial/
- **Dynamic Client Registration**: https://ibm.github.io/mcp-context-forge/tutorials/dcr-hyprmcp/

### Architecture & Design

- **Architecture Overview**: https://ibm.github.io/mcp-context-forge/architecture/
- **Roadmap**: https://ibm.github.io/mcp-context-forge/architecture/roadmap/
- **Multi-Tenancy Design**: https://ibm.github.io/mcp-context-forge/architecture/multitenancy/
- **Security Features**: https://ibm.github.io/mcp-context-forge/architecture/security-features/
- **Plugin Architecture**: https://ibm.github.io/mcp-context-forge/architecture/plugins/
- **OAuth Design**: https://ibm.github.io/mcp-context-forge/architecture/oauth-design/

### Deployment Guides

- **Kubernetes Deployment**: https://ibm.github.io/mcp-context-forge/deployment/kubernetes/
- **Helm Charts**: https://ibm.github.io/mcp-context-forge/deployment/helm/
- **Docker Compose**: https://ibm.github.io/mcp-context-forge/deployment/compose/
- **IBM Cloud Code Engine**: https://ibm.github.io/mcp-context-forge/deployment/ibm-code-engine/
- **Google Cloud Run**: https://ibm.github.io/mcp-context-forge/deployment/google-cloud-run/
- **AWS Deployment**: https://ibm.github.io/mcp-context-forge/deployment/aws/
- **Azure Deployment**: https://ibm.github.io/mcp-context-forge/deployment/azure/

### Management & Operations

- **Configuration Guide**: https://ibm.github.io/mcp-context-forge/manage/configuration/
- **Observability**: https://ibm.github.io/mcp-context-forge/manage/observability/
- **Securing the Gateway**: https://ibm.github.io/mcp-context-forge/manage/securing/
- **SSO Configuration**: https://ibm.github.io/mcp-context-forge/manage/sso/
- **OAuth Setup**: https://ibm.github.io/mcp-context-forge/manage/oauth/
- **Scaling Guide**: https://ibm.github.io/mcp-context-forge/manage/scale/
- **Backup & Export**: https://ibm.github.io/mcp-context-forge/manage/export-import/

### Using the Gateway

- **REST Passthrough**: https://ibm.github.io/mcp-context-forge/using/rest-passthrough/
- **gRPC Services**: https://ibm.github.io/mcp-context-forge/using/grpc-services/
- **MCP Wrapper**: https://ibm.github.io/mcp-context-forge/using/mcpgateway-wrapper/
- **MCP Translate**: https://ibm.github.io/mcp-context-forge/using/mcpgateway-translate/
- **Tool Annotations**: https://ibm.github.io/mcp-context-forge/using/tool-annotations/
- **Reverse Proxy Setup**: https://ibm.github.io/mcp-context-forge/using/reverse-proxy/

### Video & Media

- **Context Forge Client Demo**: https://www.youtube.com/watch?v=KA0iAeJHe7g (by Niklas Heidloff)
- **Media Kit**: https://ibm.github.io/mcp-context-forge/media/kit/

### Community & Support

- **GitHub Issues**: https://github.com/IBM/mcp-context-forge/issues
- **Contributing Guide**: https://github.com/IBM/mcp-context-forge/blob/main/CONTRIBUTING.md
- **Security Policy**: https://github.com/IBM/mcp-context-forge/blob/main/SECURITY.md
- **Changelog**: https://github.com/IBM/mcp-context-forge/blob/main/CHANGELOG.md
- **Migration Guide (v0.7.0)**: https://github.com/IBM/mcp-context-forge/blob/main/MIGRATION-0.7.0.md

### Related Projects

- **MCP Servers**: https://github.com/modelcontextprotocol/servers
- **MCP Python SDK**: https://github.com/modelcontextprotocol/python-sdk
- **MCP TypeScript SDK**: https://github.com/modelcontextprotocol/typescript-sdk

---

## Appendix: Quick Reference

### Environment Variables Summary

| Variable | Description | Default |
|----------|-------------|---------|
| `MCPGATEWAY_UI_ENABLED` | Enable Admin UI | `false` |
| `MCPGATEWAY_ADMIN_API_ENABLED` | Enable Admin API | `true` |
| `DATABASE_URL` | Database connection string | `sqlite:///./mcp.db` |
| `REDIS_URL` | Redis connection string | - |
| `CACHE_TYPE` | Cache backend (database/memory/redis) | `database` |
| `JWT_SECRET_KEY` | Secret for JWT tokens | - |
| `PLATFORM_ADMIN_EMAIL` | Initial admin email | - |
| `PLATFORM_ADMIN_PASSWORD` | Initial admin password | - |
| `OTEL_ENABLE_OBSERVABILITY` | Enable OpenTelemetry | `false` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP endpoint | - |
| `MCPGATEWAY_ENABLE_FEDERATION` | Enable federation | `false` |

### API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/servers` | GET | List servers |
| `/api/v1/servers` | POST | Register server |
| `/api/v1/tools` | GET | List tools |
| `/api/v1/tools/{name}/invoke` | POST | Invoke tool |
| `/api/v1/virtual-servers` | GET | List virtual servers |
| `/api/v1/teams` | GET | List teams |
| `/auth/login` | POST | User login |
| `/auth/register` | POST | User registration |
| `/docs` | GET | OpenAPI documentation |

### CLI Commands Summary

```bash
# Start gateway
mcpgateway --host 0.0.0.0 --port 4444

# Generate JWT token
python -m mcpgateway.utils.create_jwt_token \
  --username admin@example.com --exp 10080 --secret KEY

# Translate stdio server to HTTP
python -m mcpgateway.translate \
  --stdio "uvx mcp-server-git" --port 9000

# Run with custom config
mcpgateway --config /path/to/config.yaml

# Check version
mcpgateway --version
```

### Docker Commands Summary

```bash
# Run with UI enabled
docker run -p 4444:4444 \
  -e MCPGATEWAY_UI_ENABLED=true \
  ghcr.io/ibm/mcp-context-forge:latest

# Run with PostgreSQL
docker run -p 4444:4444 \
  -e DATABASE_URL=postgresql+psycopg://user:pass@host:5432/db \
  ghcr.io/ibm/mcp-context-forge:latest

# Run with volume persistence
docker run -p 4444:4444 \
  -v $(pwd)/data:/app/data \
  -e DATABASE_URL=sqlite:///./data/mcp.db \
  ghcr.io/ibm/mcp-context-forge:latest

# View logs
docker logs -f container-name

# Execute command in container
docker exec -it container-name bash
```

---

**Version**: 1.0.0-BETA-1  
**Last Updated**: January 2026  
**License**: Apache-2.0  
**Maintainer**: IBM Research

For the latest updates, visit the [GitHub repository](https://github.com/IBM/mcp-context-forge).
