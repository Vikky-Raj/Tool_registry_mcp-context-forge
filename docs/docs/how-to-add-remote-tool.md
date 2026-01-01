# How to Add a Remote Tool to MCP Gateway

This guide explains how to add remote tools to the MCP Gateway, allowing you to integrate external REST APIs as MCP tools that can be discovered and used by AI assistants.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Understanding Tool Fields](#understanding-tool-fields)
4. [Method 1: Add Tool via Admin UI](#method-1-add-tool-via-admin-ui)
5. [Method 2: Bulk Import via JSON](#method-2-bulk-import-via-json)
6. [Complete Example: OpenWeather API](#complete-example-openweather-api)
7. [Testing Your Tool](#testing-your-tool)
8. [Troubleshooting](#troubleshooting)

## Overview

The MCP Gateway allows you to register external REST APIs as tools that can be discovered and invoked through the Model Context Protocol. This enables AI assistants to interact with your APIs seamlessly.

## Prerequisites

- MCP Gateway installed and running (see [Quick Start](README.md#quick-start---pypi))
- Access to the Admin UI (default: `http://localhost:4444/admin`)
- Valid authentication credentials (JWT token or basic auth)
- The REST API endpoint you want to add

## Understanding Tool Fields

### Required Fields

| Field | Description | Example |
|-------|-------------|---------|
| **name** | Unique identifier for the tool (alphanumeric, hyphens, underscores) | `weather-api` |
| **url** | The REST API endpoint URL | `https://api.openweathermap.org/data/2.5/weather` |
| **integration_type** | Type of integration (REST, MCP, or A2A) | `REST` |
| **request_type** | HTTP method (GET, POST, PUT, DELETE, PATCH) | `GET` |

### Optional Fields

| Field | Description | Example |
|-------|-------------|---------|
| **displayName** | Human-readable name shown in UI | `Weather API Tool` |
| **description** | Detailed description of what the tool does | `Get current weather data for any location` |
| **headers** | Custom HTTP headers as JSON object | `{"Accept": "application/json"}` |
| **input_schema** | JSON Schema defining input parameters | See example below |
| **output_schema** | JSON Schema defining expected output structure | See example below |
| **jsonpath_filter** | JSONPath expression to extract specific data | `$.main` |
| **tags** | Comma-separated tags for categorization | `weather, api, external` |
| **visibility** | Access level: `public`, `team`, or `private` | `public` |

### Authentication Fields

| Field | Description | Options |
|-------|-------------|---------|
| **auth_type** | Authentication method | `none`, `basic`, `bearer`, `authheaders`, `oauth` |
| **auth_username** | Username (for basic auth) | `your_username` |
| **auth_password** | Password (for basic auth) | `your_password` |
| **auth_token** | Bearer token value | `your-api-key-here` |
| **auth_headers** | Custom auth headers (JSON) | `{"X-API-Key": "key123"}` |

## Method 1: Add Tool via Admin UI

### Step-by-Step Guide

1. **Navigate to Admin UI**
   - Open your browser and go to `http://localhost:4444/admin`
   - Login with your credentials

2. **Go to Tools Section**
   - Click on the "Tools" tab in the navigation
   - Scroll down to "Add New Tool from REST API" section

3. **Fill in Required Fields**
   - **Name**: Enter a unique tool name (e.g., `weather-api`)
   - **Display Name**: Enter a friendly name (e.g., `Weather API Tool`)
   - **URL**: Enter the API endpoint (e.g., `https://api.openweathermap.org/data/2.5/weather`)
   - **Description**: Describe what the tool does

4. **Configure Integration Settings**
   - **Integration Type**: Select `REST`
   - **Request Type**: Select appropriate HTTP method (e.g., `GET`)

5. **Add Input Schema (Optional but Recommended)**
   
   You can use the Schema Builder or JSON Input. Example JSON:
   
   ```json
   {
     "type": "object",
     "properties": {
       "q": {
         "type": "string",
         "description": "City name, state code and country code divided by comma"
       },
       "units": {
         "type": "string",
         "description": "Units of measurement (standard, metric, imperial)",
         "enum": ["standard", "metric", "imperial"]
       }
     },
     "required": ["q"]
   }
   ```

6. **Configure Authentication**
   - Select authentication type (e.g., `Bearer Token`)
   - Enter your API key or credentials

7. **Add Tags and Set Visibility**
   - Tags: `weather, api, external`
   - Visibility: Choose `public`, `team`, or `private`

8. **Submit**
   - Click "Add Tool" button
   - Tool will be registered and available immediately

## Method 2: Bulk Import via JSON

For adding multiple tools at once, use the Bulk Import feature.

### Step-by-Step Guide

1. **Navigate to Tools Section** in Admin UI

2. **Click "Bulk Import" Button** (top right of the form)

3. **Choose Import Method**
   - Upload File: Upload a JSON file
   - Paste JSON: Paste JSON directly

4. **Use This Template**

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
    "auth_value": "your-openweather-api-key-here",
    "headers": {
      "Accept": "application/json",
      "User-Agent": "MCP-Gateway/1.0"
    },
    "input_schema": {
      "type": "object",
      "properties": {
        "q": {
          "type": "string",
          "description": "City name, state code and country code"
        },
        "units": {
          "type": "string",
          "description": "Temperature units (standard, metric, imperial)",
          "enum": ["standard", "metric", "imperial"]
        }
      },
      "required": ["q"]
    },
    "output_schema": {
      "type": "object",
      "properties": {
        "main": {
          "type": "object",
          "properties": {
            "temp": {"type": "number"},
            "feels_like": {"type": "number"},
            "humidity": {"type": "number"}
          }
        },
        "weather": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "description": {"type": "string"},
              "main": {"type": "string"}
            }
          }
        }
      }
    },
    "jsonpath_filter": "$.main",
    "tags": ["weather", "api", "external"],
    "visibility": "public"
  }
]
```

5. **Validate (Optional)**
   
   Before importing, you can validate your JSON file:
   
   ```bash
   python3 scripts/validate_remote_tools_template.py
   ```

6. **Import**
   - Review the preview showing number of tools
   - Click "Import Tools"
   - Check results showing success/failure counts

## Complete Example: OpenWeather API

Here's a complete, working example for adding OpenWeather API as a remote tool:

### Tool Configuration

```json
{
  "name": "openweather-current",
  "displayName": "OpenWeather Current Weather",
  "url": "https://api.openweathermap.org/data/2.5/weather",
  "integration_type": "REST",
  "request_type": "GET",
  "description": "Retrieves current weather data for any location worldwide. Provides temperature, humidity, pressure, wind speed, and weather conditions.",
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
        "description": "City name. Examples: 'London', 'New York,US', 'Tokyo,JP'"
      },
      "units": {
        "type": "string",
        "description": "Units of measurement",
        "enum": ["standard", "metric", "imperial"],
        "default": "metric"
      },
      "lang": {
        "type": "string",
        "description": "Language for weather descriptions",
        "default": "en"
      }
    },
    "required": ["q"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "coord": {
        "type": "object",
        "properties": {
          "lon": {"type": "number"},
          "lat": {"type": "number"}
        }
      },
      "weather": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "id": {"type": "integer"},
            "main": {"type": "string"},
            "description": {"type": "string"},
            "icon": {"type": "string"}
          }
        }
      },
      "main": {
        "type": "object",
        "properties": {
          "temp": {"type": "number", "description": "Temperature"},
          "feels_like": {"type": "number", "description": "Feels like temperature"},
          "temp_min": {"type": "number"},
          "temp_max": {"type": "number"},
          "pressure": {"type": "integer", "description": "Atmospheric pressure in hPa"},
          "humidity": {"type": "integer", "description": "Humidity percentage"}
        }
      },
      "wind": {
        "type": "object",
        "properties": {
          "speed": {"type": "number", "description": "Wind speed"},
          "deg": {"type": "integer", "description": "Wind direction in degrees"}
        }
      },
      "clouds": {
        "type": "object",
        "properties": {
          "all": {"type": "integer", "description": "Cloudiness percentage"}
        }
      },
      "name": {"type": "string", "description": "City name"}
    }
  },
  "tags": ["weather", "api", "openweather", "external", "real-time"],
  "visibility": "public"
}
```

### Getting Your API Key

1. Sign up at [OpenWeather](https://openweathermap.org/api)
2. Get your free API key from the dashboard
3. Replace `YOUR_OPENWEATHER_API_KEY` with your actual key

### Using JSONPath Filter

If you only want to return the main weather data, use:

```
jsonpath_filter: "$.main"
```

This will extract only the temperature, humidity, and pressure data from the response.

## Testing Your Tool

### Via Admin UI

1. Navigate to the Tools section
2. Find your newly added tool in the list
3. Check the status indicator (should show "Online" if reachable)
4. Look for the green checkmark next to the status

### Via API

Use the tool invocation endpoint:

```bash
# Get JWT token
TOKEN=$(python3 -m mcpgateway.utils.create_jwt_token \
  --username admin@example.com \
  --exp 10080 \
  --secret changeme123 2>/dev/null | head -1)

# Invoke the tool
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

Expected response:
```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"coord\":{\"lon\":-0.1257,\"lat\":51.5085},\"weather\":[{\"id\":800,\"main\":\"Clear\",\"description\":\"clear sky\",\"icon\":\"01d\"}],\"main\":{\"temp\":15.2,\"feels_like\":14.8,\"temp_min\":13.5,\"temp_max\":16.8,\"pressure\":1013,\"humidity\":72},...}"
    }
  ],
  "isError": false
}
```

### Via MCP Client (Claude Desktop)

Add the wrapper configuration to your Claude Desktop config:

```json
{
  "mcpServers": {
    "mcp-gateway": {
      "command": "uvx",
      "args": [
        "mcp-contextforge-gateway[wrapper]",
        "--url",
        "http://localhost:4444"
      ],
      "env": {
        "MCP_SERVER_URL": "http://localhost:4444",
        "MCP_AUTH": "Bearer YOUR_JWT_TOKEN"
      }
    }
  }
}
```

Then in Claude, you can ask: "What's the weather in London?"

## Troubleshooting

### Tool Shows as "Offline"

**Possible Causes:**
- The API endpoint is not reachable
- Authentication credentials are invalid
- Network connectivity issues
- CORS or security restrictions

**Solutions:**
1. Test the API endpoint directly with `curl`
2. Verify your API key is valid
3. Check firewall and network settings
4. Review the gateway logs for detailed error messages

### Tool Invocation Fails

**Check:**
1. Input parameters match the `input_schema`
2. Required fields are provided
3. Authentication is properly configured
4. API rate limits haven't been exceeded

**Debug with logs:**
```bash
# Enable detailed logging
export LOG_LEVEL=DEBUG
mcpgateway --log-level DEBUG
```

### Schema Validation Errors

**Common Issues:**
- JSON syntax errors in `input_schema` or `output_schema`
- Type mismatches between schema and actual data
- Missing required fields

**Solutions:**
1. Use a JSON Schema validator like [jsonschemavalidator.net](https://www.jsonschemavalidator.net/) to validate your schemas
2. Use the built-in validation script before importing:
   ```bash
   python3 scripts/validate_remote_tools_template.py
   ```
   This will check:
   - All required fields are present
   - Field values are valid
   - JSON structure is correct
   - Schemas are properly formatted

### Bulk Import Issues

**Validation Errors:**
Before importing a large JSON file, validate it first:
```bash
python3 scripts/validate_remote_tools_template.py
```

**Common Problems:**
- Missing required fields (name, url, integration_type, request_type)
- Invalid enum values (integration_type, request_type, auth_type)
- Malformed JSON structure
- Authentication credentials not properly formatted

### Authentication Not Working

**For Bearer Token:**
```json
{
  "auth_type": "bearer",
  "auth_value": "your-api-key-here"
}
```

**For Basic Auth:**
```json
{
  "auth_type": "basic",
  "auth_username": "username",
  "auth_password": "password"
}
```

**For Custom Headers:**
```json
{
  "auth_type": "authheaders",
  "auth_headers": {
    "X-API-Key": "your-key",
    "X-Custom-Header": "value"
  }
}
```

## Additional Examples

### Example: GitHub API

```json
{
  "name": "github-user-info",
  "displayName": "GitHub User Information",
  "url": "https://api.github.com/users/{username}",
  "integration_type": "REST",
  "request_type": "GET",
  "description": "Retrieve public information about a GitHub user",
  "headers": {
    "Accept": "application/vnd.github+json",
    "User-Agent": "MCP-Gateway"
  },
  "input_schema": {
    "type": "object",
    "properties": {
      "username": {
        "type": "string",
        "description": "GitHub username"
      }
    },
    "required": ["username"]
  },
  "tags": ["github", "api", "developer"],
  "visibility": "public"
}
```

### Example: REST API with POST

```json
{
  "name": "sentiment-analyzer",
  "displayName": "Text Sentiment Analyzer",
  "url": "https://api.example.com/v1/analyze",
  "integration_type": "REST",
  "request_type": "POST",
  "description": "Analyze sentiment of provided text",
  "auth_type": "bearer",
  "auth_value": "YOUR_API_KEY",
  "headers": {
    "Content-Type": "application/json"
  },
  "input_schema": {
    "type": "object",
    "properties": {
      "text": {
        "type": "string",
        "description": "Text to analyze for sentiment"
      },
      "language": {
        "type": "string",
        "description": "Language code (en, es, fr, etc.)",
        "default": "en"
      }
    },
    "required": ["text"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "sentiment": {
        "type": "string",
        "enum": ["positive", "negative", "neutral"]
      },
      "confidence": {
        "type": "number",
        "minimum": 0,
        "maximum": 1
      }
    }
  },
  "tags": ["nlp", "sentiment", "analysis"],
  "visibility": "team"
}
```

## Best Practices

1. **Naming Conventions**
   - Use lowercase with hyphens: `weather-api`, `github-search`
   - Keep names descriptive but concise
   - Avoid spaces and special characters

2. **Security**
   - Never commit API keys to version control
   - Use environment variables for sensitive data
   - Set appropriate visibility (private/team/public)
   - Regularly rotate API keys

3. **Schema Design**
   - Always provide `input_schema` for better validation
   - Include descriptions for all parameters
   - Use `enum` for limited value sets
   - Mark required fields explicitly

4. **Testing**
   - Test tools before making them public
   - Verify authentication works correctly
   - Check rate limits and quotas
   - Monitor tool performance and errors

5. **Documentation**
   - Write clear, detailed descriptions
   - Include usage examples
   - Document any limitations or requirements
   - Tag appropriately for discoverability

## Related Documentation

- [MCP Gateway README](README.md)
- [Authentication Guide](README.md#authentication-examples)
- [API Endpoints](README.md#api-endpoints)
- [Configuration Options](README.md#configuration-env-or-env-vars)
- [Virtual Servers Guide](docs/virtual-servers.md)

## Support

For issues or questions:
- Check the [GitHub Issues](https://github.com/IBM/mcp-context-forge/issues)
- Review existing documentation
- Enable debug logging for detailed error messages
- Check the Admin UI observability metrics

---

**Need Help?** Open an issue on GitHub with:
- Tool configuration (redact sensitive data)
- Error messages or logs
- Steps to reproduce the issue
- Expected vs actual behavior
