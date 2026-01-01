#!/usr/bin/env python3
"""
Test script to validate the remote tools JSON template.

This script validates that the remote-tools-template.json file is properly
formatted and contains all required fields for tool registration.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Required fields according to ToolCreate schema
REQUIRED_FIELDS = ["name", "url", "integration_type", "request_type"]

# Optional but commonly used fields
RECOMMENDED_FIELDS = ["displayName", "description", "tags", "visibility"]

# Valid values for specific fields
VALID_INTEGRATION_TYPES = ["REST", "MCP", "A2A"]
VALID_REQUEST_TYPES = ["GET", "POST", "PUT", "DELETE", "PATCH", "SSE", "STDIO", "STREAMABLEHTTP"]
VALID_AUTH_TYPES = ["", "basic", "bearer", "authheaders", "oauth"]
VALID_VISIBILITY = ["public", "team", "private"]


def validate_tool(tool: Dict[str, Any], index: int) -> List[str]:
    """
    Validate a single tool configuration.
    
    Args:
        tool: Tool configuration dictionary
        index: Index of tool in array (for error messages)
    
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in tool or not tool[field]:
            errors.append(f"Tool {index}: Missing required field '{field}'")
    
    # Validate integration_type
    if "integration_type" in tool:
        if tool["integration_type"] not in VALID_INTEGRATION_TYPES:
            errors.append(
                f"Tool {index} ({tool.get('name', 'unknown')}): "
                f"Invalid integration_type '{tool['integration_type']}'. "
                f"Must be one of: {', '.join(VALID_INTEGRATION_TYPES)}"
            )
    
    # Validate request_type
    if "request_type" in tool:
        if tool["request_type"] not in VALID_REQUEST_TYPES:
            errors.append(
                f"Tool {index} ({tool.get('name', 'unknown')}): "
                f"Invalid request_type '{tool['request_type']}'. "
                f"Must be one of: {', '.join(VALID_REQUEST_TYPES)}"
            )
    
    # Validate auth_type if present
    if "auth_type" in tool:
        if tool["auth_type"] not in VALID_AUTH_TYPES:
            errors.append(
                f"Tool {index} ({tool.get('name', 'unknown')}): "
                f"Invalid auth_type '{tool['auth_type']}'. "
                f"Must be one of: {', '.join(VALID_AUTH_TYPES)}"
            )
    
    # Validate visibility if present
    if "visibility" in tool:
        if tool["visibility"] not in VALID_VISIBILITY:
            errors.append(
                f"Tool {index} ({tool.get('name', 'unknown')}): "
                f"Invalid visibility '{tool['visibility']}'. "
                f"Must be one of: {', '.join(VALID_VISIBILITY)}"
            )
    
    # Check for recommended fields
    for field in RECOMMENDED_FIELDS:
        if field not in tool:
            print(
                f"  ℹ️  Tool {index} ({tool.get('name', 'unknown')}): "
                f"Recommended field '{field}' is missing"
            )
    
    # Validate input_schema if present
    if "input_schema" in tool and tool["input_schema"]:
        schema = tool["input_schema"]
        if not isinstance(schema, dict):
            errors.append(
                f"Tool {index} ({tool.get('name', 'unknown')}): "
                f"input_schema must be a JSON object"
            )
        elif "type" not in schema:
            errors.append(
                f"Tool {index} ({tool.get('name', 'unknown')}): "
                f"input_schema must have a 'type' field"
            )
    
    # Validate output_schema if present
    if "output_schema" in tool and tool["output_schema"]:
        schema = tool["output_schema"]
        if not isinstance(schema, dict):
            errors.append(
                f"Tool {index} ({tool.get('name', 'unknown')}): "
                f"output_schema must be a JSON object"
            )
    
    # Validate headers if present
    if "headers" in tool and tool["headers"]:
        if not isinstance(tool["headers"], dict):
            errors.append(
                f"Tool {index} ({tool.get('name', 'unknown')}): "
                f"headers must be a JSON object"
            )
    
    # Validate tags if present
    if "tags" in tool and tool["tags"]:
        if not isinstance(tool["tags"], list):
            errors.append(
                f"Tool {index} ({tool.get('name', 'unknown')}): "
                f"tags must be an array"
            )
    
    return errors


def main():
    """Main validation function."""
    print("🔍 Validating remote-tools-template.json...")
    print()
    
    # Find the template file
    template_path = Path(__file__).parent.parent / "examples" / "remote-tools-template.json"
    
    if not template_path.exists():
        print(f"❌ Error: Template file not found at {template_path}")
        return 1
    
    # Load and parse JSON
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            tools = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in template file: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error reading template file: {e}")
        return 1
    
    # Check that it's an array
    if not isinstance(tools, list):
        print("❌ Error: Template must be a JSON array of tool configurations")
        return 1
    
    print(f"📝 Found {len(tools)} tool configurations to validate")
    print()
    
    # Validate each tool
    all_errors = []
    for i, tool in enumerate(tools, 1):
        if not isinstance(tool, dict):
            all_errors.append(f"Tool {i}: Must be a JSON object")
            continue
        
        # Skip comment entries
        if "_comment" in tool and len(tool) == 1:
            continue
        
        errors = validate_tool(tool, i)
        all_errors.extend(errors)
        
        if not errors:
            name = tool.get("name", "unknown")
            print(f"  ✅ Tool {i}: {name}")
    
    print()
    
    # Report results
    if all_errors:
        print(f"❌ Validation failed with {len(all_errors)} error(s):")
        print()
        for error in all_errors:
            print(f"  • {error}")
        return 1
    else:
        print("✨ All tools validated successfully!")
        print()
        print("📊 Summary:")
        print(f"  • Total tools: {len(tools)}")
        print(f"  • Integration types: {len(set(t.get('integration_type', '') for t in tools))}")
        print(f"  • Request types: {len(set(t.get('request_type', '') for t in tools))}")
        print(f"  • With authentication: {sum(1 for t in tools if t.get('auth_type'))}")
        print(f"  • With input schema: {sum(1 for t in tools if t.get('input_schema'))}")
        print(f"  • With output schema: {sum(1 for t in tools if t.get('output_schema'))}")
        print()
        print("✅ The template is ready to use for bulk import!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
