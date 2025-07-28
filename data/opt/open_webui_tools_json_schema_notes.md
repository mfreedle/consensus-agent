## Open WebUI Tool Import: JSON Format & Schema

When importing tools into **Open WebUI**, the expected format is a JSON object that describes all necessary metadata and (usually) the core tool code and configuration. The schema is based on the structure used when exporting tools from the Open WebUI Community site or tool editor.

Below is an overview of the standard fields and structure, followed by a sample schema derived from your attachment and public tooling documentation.

### Required Fields in the JSON Schema

| Key             | Type     | Description                                                                    |
|-----------------|----------|--------------------------------------------------------------------------------|
| id              | string   | Unique identifier for the tool (snake_case recommended)                         |
| name            | string   | Display name of the tool                                                        |
| meta            | object   | Metadata including description and manifest; often includes a `description`     |
| content         | string   | The Python code for the tool, often with YAML-style header as a docstring       |
| info            | object   | Extra info (can be blank or contain tool-specific data)                         |
| downloads       | integer  | Number of times the tool has been downloaded (optional)                         |
| upvotes/downvotes| integer | Popularity metrics (optional, for community tools)                              |
| updatedAt       | integer  | Last updated timestamp (Unix epoch, optional for imports, set automatically)    |
| createdAt       | integer  | Creation timestamp (Unix epoch, optional)                                       |
| user            | object   | Creator's info (may be omitted or included for attribution/community tools)     |

### Example: Open WebUI Tool JSON Schema

Here’s an example structure based on your attached file:

```json
{
  "id": "google_tools",
  "name": "Google Tools",
  "meta": {
    "description": "This tool provides functionalities to interact with Google Calendar and Gmail using the Google API. It allows you to fetch upcoming events from your calendar and retrieve emails from your inbox.",
    "manifest": {}
  },
  "content": "# Python code as a string including the tool header and main implementation",
  "info": {},
  "downloads": 123,
  "upvotes": 0,
  "downvotes": 0,
  "updatedAt": 1740426101,
  "createdAt": 1739303282,
  "user": {
    "id": "564c6d19-2977-4301-8c10-7254528a3c71",
    "username": "shmarkus",
    "name": "",
    "createdAt": 1736925339,
    "role": null,
    "verified": false
  }
}
```

**Key Points:**
- The main Python code should be a string value in the `content` field, usually including any YAML config block in a docstring at the top.
- Most fields ("downloads", "upvotes", etc.) are for the Open WebUI Community site, not strictly required for import—though `id`, `name`, `meta`, and `content` are essential.
- Keep the JSON valid and compliant; avoid additional top-level keys.

### Simplified Minimum Import Example

For a minimal import, this is typically sufficient:

```json
{
  "id": "tool_id",
  "name": "Tool Name",
  "meta": {
    "description": "A short description of what the tool does.",
    "manifest": {}
  },
  "content": "# Python code string here (with YAML docstring header)",
  "info": {}
}
```

### Notes & Best Practices

- **Always export or use examples from the official Open WebUI Tools Library for reference**[1].
- **Timestamps and user attribution fields** are not strictly required for manual import and can be omitted for local or private instances.

This schema enables Open WebUI to recognize and register your tool with accurate metadata and executable code, ready for use after import.

If you need to generate this JSON from a Python module or YAML header, ensure the Python code is formatted as a string, with newline escapes as necessary if entering directly into a JSON file or field.

**References:**  
- Community Tools Import Instructions, Open WebUI[1].
- Example “Google Tools” attachment schema (as provided).

[1] https://open-webui.com/tools/
[2] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/870877/5a06d0b0-15ba-492b-b100-52761013b23e/tool-Google-Tools.json
[3] https://openwebui.com/m/danielrosehill/natural-language-to-json
[4] https://github.com/open-webui/open-webui/discussions/3134
[5] https://openwebui.com/tools
[6] https://documentation.aimms.com/webui/webui-json.html
[7] https://json-schema.org/tools
[8] https://docs.openwebui.com/features/plugin/tools/
[9] https://github.com/open-webui/open-webui/discussions/3522
[10] https://www.reddit.com/r/OpenWebUI/comments/1kf8cyo/how_can_i_efficiently_use_openwebui_with/
[11] https://docs.openwebui.com/features/
[12] https://openwebui.com/m/danielrosehill/json-schema-to-markdown-table
[13] https://github.com/open-webui/open-webui
[14] https://www.reddit.com/r/OpenWebUI/comments/1kvwr4j/how_llm_uses_mcp_tools_setup_in_openwebui/
[15] https://openwebui.com/m/danielrosehill/json-schema-editor-for-ai
[16] https://openwebui.com/t/userx/convert_to_json
[17] https://community.n8n.io/t/extract-data-from-workflow-to-open-webui/57098