# Campus Helpdesk Plugin

The **Campus Helpdesk** plugin bundles domain skills, an official Python MCP server, and security hooks for university student services.

## Features Included
- **Timetable Skill (`timetable-helper`)**: Natural language querying for classes, lecture timings, faculty, and room locations.
- **Timetable Slash Command (`/timetable`)**: Slash-invokable shortcut to look up daily batch schedules.
- **PreToolUse Security Hook (`hooks/security_hook.py`)**: Sanitizes tool inputs and blocks path traversal attempts or unauthorized system access.
- **Model Context Protocol (`mcp-server`)**: Connects to the local stdio MCP server for typed timetable queries, student fee balances, and hostel policies.

## Installation & Usage
1. Place in your workspace or copy to `~/.gemini/config/plugins/campus-helpdesk`.
2. Toggle on/off via the Antigravity Customizations interface.
3. Access commands using `/timetable <batch> <day>` in the chat.

