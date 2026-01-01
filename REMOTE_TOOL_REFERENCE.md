# Remote Tool Configuration Reference Card

Quick reference card for all fields when adding remote tools to MCP Gateway.

## Field Categories

```
┌─────────────────────────────────────────────────────────────┐
│                    REMOTE TOOL FIELDS                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  REQUIRED FIELDS                                             │
│  ├─ name              (tool identifier)                      │
│  ├─ url               (API endpoint)                         │
│  ├─ integration_type  (REST, MCP, A2A)                       │
│  └─ request_type      (GET, POST, PUT, DELETE, PATCH)        │
│                                                              │
│  DISPLAY & METADATA                                          │
│  ├─ displayName       (friendly name)                        │
│  ├─ description       (what it does)                         │
│  ├─ tags              (["tag1", "tag2"])                     │
│  └─ visibility        (public, team, private)                │
│                                                              │
│  AUTHENTICATION                                              │
│  ├─ auth_type         (none, basic, bearer, authheaders)    │
│  ├─ auth_username     (for basic auth)                       │
│  ├─ auth_password     (for basic auth)                       │
│  ├─ auth_value        (for bearer token)                     │
│  └─ auth_headers      ({"X-API-Key": "..."})                 │
│                                                              │
│  REQUEST CONFIGURATION                                       │
│  ├─ headers           ({"Accept": "application/json"})       │
│  ├─ input_schema      (JSON Schema for parameters)           │
│  ├─ output_schema     (JSON Schema for response)             │
│  └─ jsonpath_filter   ($.data.results)                       │
│                                                              │
│  TEAM & ACCESS CONTROL                                       │
│  ├─ team_id           (team identifier)                      │
│  └─ owner_email       (owner's email)                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Quick Field Reference

### Required Fields (Must Have)

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `name` | string | `"weather-api"` | Unique identifier, lowercase with hyphens |
| `url` | string | `"https://api.example.com/v1/data"` | Full API endpoint URL |
| `integration_type` | enum | `"REST"` | One of: REST, MCP, A2A |
| `request_type` | enum | `"GET"` | One of: GET, POST, PUT, DELETE, PATCH, SSE, STDIO, STREAMABLEHTTP |

### Display Fields (Highly Recommended)

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `displayName` | string | `"Weather API"` | Human-readable name shown in UI |
| `description` | string | `"Get weather data..."` | Detailed description of functionality |
| `tags` | array | `["weather", "api"]` | Categories for organization |
| `visibility` | enum | `"public"` | One of: public, team, private |

### Authentication Fields (As Needed)

| Field | Type | When to Use | Example |
|-------|------|-------------|---------|
| `auth_type` | enum | Always specify if auth needed | `"bearer"` |
| `auth_value` | string | For bearer token | `"sk-abc123..."` |
| `auth_username` | string | For basic auth | `"myuser"` |
| `auth_password` | string | For basic auth | `"mypass"` |
| `auth_headers` | object | For custom headers | `{"X-API-Key": "key"}` |

### Schema Fields (Optional but Recommended)

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `input_schema` | object | Validate input parameters | See below |
| `output_schema` | object | Validate response structure | See below |
| `jsonpath_filter` | string | Extract specific data | `"$.data"` |
| `headers` | object | Custom HTTP headers | `{"Accept": "application/json"}` |

## Schema Examples

### Basic Input Schema
```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Search query"
    },
    "limit": {
      "type": "integer",
      "description": "Max results",
      "default": 10,
      "minimum": 1,
      "maximum": 100
    }
  },
  "required": ["query"]
}
```

### Advanced Input Schema
```json
{
  "type": "object",
  "properties": {
    "location": {
      "type": "object",
      "properties": {
        "city": {"type": "string"},
        "country": {"type": "string"}
      },
      "required": ["city"]
    },
    "units": {
      "type": "string",
      "enum": ["metric", "imperial"],
      "default": "metric"
    },
    "include_forecast": {
      "type": "boolean",
      "default": false
    }
  },
  "required": ["location"]
}
```

## Authentication Patterns

### Pattern 1: No Authentication
```json
{
  "name": "public-api",
  "url": "https://api.example.com/public",
  "integration_type": "REST",
  "request_type": "GET"
}
```

### Pattern 2: Bearer Token (API Key)
```json
{
  "name": "weather-api",
  "url": "https://api.weather.com/v1/current",
  "integration_type": "REST",
  "request_type": "GET",
  "auth_type": "bearer",
  "auth_value": "YOUR_API_KEY_HERE"
}
```

### Pattern 3: Basic Authentication
```json
{
  "name": "secure-api",
  "url": "https://api.example.com/secure",
  "integration_type": "REST",
  "request_type": "POST",
  "auth_type": "basic",
  "auth_username": "myusername",
  "auth_password": "mypassword"
}
```

### Pattern 4: Custom Headers
```json
{
  "name": "custom-api",
  "url": "https://api.example.com/custom",
  "integration_type": "REST",
  "request_type": "GET",
  "auth_type": "authheaders",
  "auth_headers": {
    "X-API-Key": "your-key",
    "X-Client-ID": "your-client-id",
    "X-Custom-Auth": "custom-value"
  }
}
```

## Common HTTP Methods

| Method | When to Use | Typical Response |
|--------|-------------|------------------|
| **GET** | Retrieve data | Status 200, data in body |
| **POST** | Create/submit data | Status 201, created resource |
| **PUT** | Update entire resource | Status 200, updated resource |
| **DELETE** | Remove resource | Status 204, no content |
| **PATCH** | Partial update | Status 200, updated fields |

## Valid Enum Values

### integration_type
- `REST` - Standard REST API
- `MCP` - MCP server (gateway-discovered)
- `A2A` - Agent-to-Agent integration

### request_type
**For REST integration:**
- `GET` - Retrieve data
- `POST` - Create/submit data
- `PUT` - Update resource
- `DELETE` - Remove resource
- `PATCH` - Partial update

**For MCP integration:**
- `SSE` - Server-Sent Events
- `STDIO` - Standard input/output
- `STREAMABLEHTTP` - Streamable HTTP

### auth_type
- `""` (empty) - No authentication
- `basic` - Basic username/password
- `bearer` - Bearer token (API keys)
- `authheaders` - Custom headers
- `oauth` - OAuth 2.0 (advanced)

### visibility
- `public` - Accessible to all users
- `team` - Accessible to team members only
- `private` - Accessible only to owner

## JSONPath Filter Examples

Extract specific parts of API responses:

| Pattern | Effect | Example |
|---------|--------|---------|
| `$.data` | Extract 'data' field | `{"data": {...}}` → `{...}` |
| `$.results[*]` | All items in 'results' array | `{"results": [1,2,3]}` → `[1,2,3]` |
| `$.main.temp` | Nested field | `{"main": {"temp": 20}}` → `20` |
| `$..name` | All 'name' fields recursively | Finds all `name` fields |

## Validation Checklist

Before submitting your tool configuration:

- [ ] `name` is unique and descriptive
- [ ] `url` is a valid, accessible endpoint
- [ ] `integration_type` is set correctly (usually "REST")
- [ ] `request_type` matches your API's HTTP method
- [ ] `description` clearly explains what the tool does
- [ ] `input_schema` includes all required parameters
- [ ] Authentication is properly configured
- [ ] `tags` help with discovery and organization
- [ ] `visibility` is appropriate for your use case
- [ ] Test the API with curl before adding
- [ ] Run validation script: `python3 scripts/validate_remote_tools_template.py`

## Testing Your Configuration

### 1. Test API Directly
```bash
# For GET with Bearer token
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.example.com/endpoint

# For POST with JSON
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"key": "value"}' \
  https://api.example.com/endpoint
```

### 2. Validate JSON
```bash
python3 scripts/validate_remote_tools_template.py
```

### 3. Test via Gateway
```bash
# Get JWT token
TOKEN=$(python3 -m mcpgateway.utils.create_jwt_token \
  --username admin@example.com \
  --exp 10080 \
  --secret changeme123 2>/dev/null | head -1)

# Invoke tool
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:4444/tools/invoke \
  -d '{"name": "your-tool-name", "arguments": {...}}'
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Tool shows "Offline" | Verify URL is accessible, check auth credentials |
| Invocation fails | Ensure input matches `input_schema` |
| Schema errors | Validate JSON structure, check required fields |
| Auth not working | Double-check `auth_type` and credentials format |
| Missing in list | Check if name conflicts with existing tool |

## Related Resources

- [Quick Guide: Adding Remote Tools](../ADDING_REMOTE_TOOLS.md)
- [Detailed Documentation](../docs/docs/how-to-add-remote-tool.md)
- [JSON Template](../examples/remote-tools-template.json)
- [Examples README](../examples/README.md)
- [Main README](../README.md)

---

**Quick Tips:**
- Use the template as a starting point
- Test APIs with curl first
- Start with `visibility: "private"` for testing
- Add tags for better organization
- Document clearly for team members
- Keep credentials secure (use env vars in production)
