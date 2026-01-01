# Quick Guide: Adding Remote Tools

This is a quick reference for adding remote tools to MCP Gateway. For detailed documentation, see [docs/docs/how-to-add-remote-tool.md](docs/docs/how-to-add-remote-tool.md).

## Quick Start

### Via Admin UI (Recommended for Single Tools)

1. Navigate to `http://localhost:4444/admin`
2. Go to **Tools** tab
3. Scroll to **Add New Tool from REST API**
4. Fill in the required fields:
   - **Name**: `weather-api` (unique identifier)
   - **Display Name**: `Weather API Tool` (friendly name)
   - **URL**: `https://api.openweathermap.org/data/2.5/weather`
   - **Integration Type**: `REST`
   - **Request Type**: `GET`
   - **Description**: What your tool does
5. Add authentication (if needed):
   - Select auth type: `bearer`, `basic`, or `authheaders`
   - Enter credentials
6. Click **Add Tool**

### Via Bulk Import (Recommended for Multiple Tools)

1. Go to **Tools** tab in Admin UI
2. Click **Bulk Import** button
3. Choose "Paste JSON" or "Upload File"
4. Use this template:

```json
[
  {
    "name": "weather-api",
    "displayName": "Weather API Tool",
    "url": "https://api.openweathermap.org/data/2.5/weather",
    "integration_type": "REST",
    "request_type": "GET",
    "description": "Get current weather data for any location",
    "auth_type": "bearer",
    "auth_value": "YOUR_API_KEY_HERE",
    "headers": {
      "Accept": "application/json"
    },
    "input_schema": {
      "type": "object",
      "properties": {
        "q": {
          "type": "string",
          "description": "City name"
        },
        "units": {
          "type": "string",
          "enum": ["standard", "metric", "imperial"]
        }
      },
      "required": ["q"]
    },
    "tags": ["weather", "api", "external"],
    "visibility": "public"
  }
]
```

5. Click **Import Tools**

## Required Fields

| Field | Example | Description |
|-------|---------|-------------|
| `name` | `weather-api` | Unique tool identifier |
| `url` | `https://api.example.com/endpoint` | API endpoint URL |
| `integration_type` | `REST` | Type of integration |
| `request_type` | `GET` or `POST` | HTTP method |

## Optional but Recommended Fields

| Field | Example | Purpose |
|-------|---------|---------|
| `displayName` | `Weather API Tool` | Friendly name in UI |
| `description` | `Get weather data...` | What the tool does |
| `input_schema` | `{...}` | Parameter validation |
| `tags` | `["weather", "api"]` | Categorization |
| `visibility` | `public` | Access control |

## Authentication Options

### No Authentication
```json
{
  "auth_type": ""
}
```

### Bearer Token (API Keys)
```json
{
  "auth_type": "bearer",
  "auth_value": "your-api-key-here"
}
```

### Basic Authentication
```json
{
  "auth_type": "basic",
  "auth_username": "username",
  "auth_password": "password"
}
```

### Custom Headers
```json
{
  "auth_type": "authheaders",
  "auth_headers": {
    "X-API-Key": "key123",
    "X-Custom-Header": "value"
  }
}
```

## Complete Working Example: OpenWeather API

```json
{
  "name": "openweather-current",
  "displayName": "OpenWeather Current Weather",
  "url": "https://api.openweathermap.org/data/2.5/weather",
  "integration_type": "REST",
  "request_type": "GET",
  "description": "Get current weather data for any location worldwide",
  "auth_type": "bearer",
  "auth_value": "YOUR_OPENWEATHER_API_KEY",
  "headers": {
    "Accept": "application/json",
    "User-Agent": "MCP-Gateway/1.0"
  },
  "input_schema": {
    "type": "object",
    "properties": {
      "q": {
        "type": "string",
        "description": "City name (e.g., 'London', 'New York,US')"
      },
      "units": {
        "type": "string",
        "description": "Units of measurement",
        "enum": ["standard", "metric", "imperial"],
        "default": "metric"
      }
    },
    "required": ["q"]
  },
  "tags": ["weather", "api", "openweather", "external"],
  "visibility": "public"
}
```

**Get your free API key:** Sign up at [OpenWeather](https://openweathermap.org/api)

## Testing Your Tool

### Via curl

```bash
# Get JWT token
TOKEN=$(python3 -m mcpgateway.utils.create_jwt_token \
  --username admin@example.com \
  --exp 10080 \
  --secret changeme123 2>/dev/null | head -1)

# Test tool invocation
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:4444/tools/invoke \
  -d '{
    "name": "openweather-current",
    "arguments": {
      "q": "London,UK",
      "units": "metric"
    }
  }' | jq
```

### Via Admin UI

1. Go to **Tools** tab
2. Find your tool in the list
3. Check status indicator (should be "Online" with green checkmark)

## Common Issues

### Tool Shows "Offline"
- ✅ Check API endpoint is accessible
- ✅ Verify authentication credentials
- ✅ Check gateway logs for errors

### Invocation Fails
- ✅ Ensure input matches `input_schema`
- ✅ Check required fields are provided
- ✅ Verify API rate limits

### Authentication Errors
- ✅ Double-check API key/credentials
- ✅ Ensure correct auth_type is selected
- ✅ Test API endpoint with curl first

## More Examples

### GitHub User API
```json
{
  "name": "github-user",
  "url": "https://api.github.com/users/{username}",
  "integration_type": "REST",
  "request_type": "GET",
  "description": "Get GitHub user information",
  "headers": {
    "Accept": "application/vnd.github+json"
  },
  "tags": ["github", "api"]
}
```

### POST Request Example
```json
{
  "name": "sentiment-analyzer",
  "url": "https://api.example.com/analyze",
  "integration_type": "REST",
  "request_type": "POST",
  "description": "Analyze text sentiment",
  "auth_type": "bearer",
  "auth_value": "YOUR_KEY",
  "headers": {
    "Content-Type": "application/json"
  },
  "input_schema": {
    "type": "object",
    "properties": {
      "text": {
        "type": "string",
        "description": "Text to analyze"
      }
    },
    "required": ["text"]
  }
}
```

## Need More Help?

📖 **Full Documentation:** [docs/docs/how-to-add-remote-tool.md](docs/docs/how-to-add-remote-tool.md)

🔧 **Troubleshooting:** Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
mcpgateway --log-level DEBUG
```

💬 **Support:** Open an issue on [GitHub](https://github.com/IBM/mcp-context-forge/issues)

---

**Pro Tips:**
- Use the Schema Builder in the Admin UI for easier input schema creation
- Test APIs with curl before adding them as tools
- Use JSONPath filters to extract specific data from responses
- Tag tools appropriately for better organization and discovery
- Set visibility to `private` for testing, then change to `public` when ready
