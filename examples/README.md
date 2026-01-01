# Examples Directory

This directory contains example configurations and templates for use with MCP Gateway.

## Files

### remote-tools-template.json

A ready-to-use JSON template for bulk importing remote tools into MCP Gateway. This template includes 7 example tool configurations demonstrating various integration patterns:

1. **OpenWeather API** - Weather data with GET requests and Bearer token auth
2. **GitHub User API** - Public GitHub data with no authentication
3. **JSONPlaceholder API** - Test POST endpoint for creating blog posts
4. **REST Countries API** - Country information lookup
5. **Bearer Auth Example** - Template showing Bearer token authentication
6. **Basic Auth Example** - Template showing basic username/password authentication
7. **Custom Headers Example** - Template showing custom header authentication

### Usage

#### Option 1: Via Admin UI

1. Navigate to `http://localhost:4444/admin`
2. Go to the **Tools** tab
3. Click **Bulk Import** button
4. Choose "Upload File" and select `remote-tools-template.json`
5. Or choose "Paste JSON" and copy the contents
6. Review the preview and click **Import Tools**

#### Option 2: Via API

```bash
# Get JWT token
TOKEN=$(python3 -m mcpgateway.utils.create_jwt_token \
  --username admin@example.com \
  --exp 10080 \
  --secret changeme123 2>/dev/null | head -1)

# Bulk import tools
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:4444/admin/tools/bulk-import \
  --data @examples/remote-tools-template.json
```

### Customization

Before importing, customize the template:

1. **Replace API Keys**: Update `auth_value` fields with your actual API keys
2. **Update URLs**: Replace example URLs with your actual endpoints
3. **Modify Schemas**: Adjust `input_schema` and `output_schema` to match your APIs
4. **Change Names**: Use descriptive names that match your use case
5. **Set Visibility**: Choose appropriate visibility (`public`, `team`, or `private`)

### Validation

To validate your modifications before importing:

```bash
# Run the validation script
python3 scripts/validate_remote_tools_template.py
```

This will check for:
- Required fields presence
- Valid field values
- Proper JSON structure
- Schema validity

### Getting API Keys

- **OpenWeather**: Sign up at https://openweathermap.org/api
- **GitHub**: Optional for public data; get token at https://github.com/settings/tokens
- **Other APIs**: Check respective API documentation for authentication details

## Related Documentation

- [Quick Guide: Adding Remote Tools](../ADDING_REMOTE_TOOLS.md)
- [Detailed Remote Tools Guide](../docs/docs/how-to-add-remote-tool.md)
- [Main README](../README.md)

## Tips

- Start with the template as a base and modify one tool at a time
- Test each tool individually before bulk importing
- Use `visibility: "private"` while testing, then change to `public` when ready
- Keep sensitive credentials in environment variables, not in the JSON file
- Use meaningful tags to organize your tools
- Document your custom tools with clear descriptions

## Support

For issues or questions:
- Check the [main documentation](../README.md)
- Review the [troubleshooting guide](../docs/docs/how-to-add-remote-tool.md#troubleshooting)
- Open an issue on [GitHub](https://github.com/IBM/mcp-context-forge/issues)
