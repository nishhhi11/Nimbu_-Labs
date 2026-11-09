# Campus Helpdesk Plugin

The **Campus Helpdesk** plugin bundles university domain skills, an official Python MCP server, and PreToolUse security hooks for student services within Antigravity.

## Features Included
- **Timetable Skill (`timetable-helper`)**: Natural language querying for classes, lecture timings, faculty, and room locations using progressive disclosure reference data.
- **Timetable Slash Command (`/timetable`)**: Slash-invokable shortcut to look up daily batch schedules.
- **PreToolUse Security Hook (`hooks/security_hook.py`)**: Sanitizes tool inputs and blocks destructive shell commands and unauthorized system path traversals.
- **Model Context Protocol (`mcp-server`)**: Connects to the local stdio MCP server for typed timetable queries, student fee balances, and hostel policies.

## Prerequisites & Python MCP Setup
The bundled MCP server requires Python 3 with the Model Context Protocol SDK (`mcp`). Because Antigravity plugins do not include a post-install hook, install the server requirements prior to activating the MCP server:

1. Create and activate a virtual environment within the server directory (or install dependencies into your Python environment):
   ```bash
   cd mcp-server
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. The MCP configuration (`mcp_config.json`) is configured to run `python3` with `PYTHONPATH` referencing the plugin's local packages (`${PLUGIN_ROOT}/mcp-server/.venv/lib/python3.14/site-packages` or your local environment):
   ```json
   {
     "mcpServers": {
       "campus-mcp": {
         "command": "python3",
         "args": [
           "${PLUGIN_ROOT}/mcp-server/server.py"
         ],
         "env": {
           "PYTHONPATH": "${PLUGIN_ROOT}/mcp-server/.venv/lib/python3.14/site-packages"
         }
       }
     }
   }
   ```

## Installation & Usage
1. Place this directory in your project workspace or copy to `~/.gemini/config/plugins/campus-helpdesk`.
2. Toggle on/off via the Antigravity Customizations interface or the Antigravity CLI:
   ```bash
   agy plugin enable campus-helpdesk
   ```
3. Access commands using `/timetable <batch> <day>` in the chat.

## Running Tests
Run the security hook unit tests:
```bash
python3 tests/test_security_hook.py
```
Run strict plugin validation:
```bash
agy plugin validate --strict .
```
