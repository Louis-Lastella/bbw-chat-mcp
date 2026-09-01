# bbw-chat-mcp

MCP server for [bbw-chat.de](https://bbw-chat.de) (Synology Chat). Read channels/messages, find users, send messages and files — from any MCP client (Claude, Hermes, etc.).

## Setup

```bash
git clone https://github.com/Louis-Lastella/bbw-chat-mcp.git
cd bbw-chat-mcp
cp .env.example .env   # fill in your credentials
uv sync
```

`.env`:
```
BBW_CHAT_HOST=bbw-chat.de
BBW_CHAT_USER=your-username
BBW_CHAT_PASS=your-password
```

## Use with an MCP client

Add to your client's MCP config (e.g. Claude Desktop `claude_desktop_config.json`, or Hermes `config.yaml`):

```json
{
  "mcpServers": {
    "bbw-chat": {
      "command": "uv",
      "args": ["run", "--directory", "/absolute/path/to/bbw-chat-mcp", "server.py"]
    }
  }
}
```

Restart the client — 6 tools show up: `list_channels`, `find_user`, `get_recent_posts`, `dm_channel_for_user`, `send_message`, `send_file`.

## Tools

| Tool | What it does |
|---|---|
| `list_channels()` | List joined channels/DMs (id, name, type, unread) |
| `find_user(name_query)` | Find users by partial username |
| `get_recent_posts(channel_id, limit=20)` | Read recent messages in a channel |
| `dm_channel_for_user(user_id)` | Get the 1:1 DM channel id for a user |
| `send_message(channel_id, message)` | Post a text message |
| `send_file(channel_id, file_path, message="")` | Upload a file, optionally with a caption message |
