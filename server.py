"""MCP server for bbw-chat.de (Synology Chat) — read tasks, send files/messages.

Auth via env vars BBW_CHAT_HOST / BBW_CHAT_USER / BBW_CHAT_PASS (see .env).
"""
import os
from functools import lru_cache

from fastmcp import FastMCP
from synology_api import chat

mcp = FastMCP("bbw-chat")


@lru_cache(maxsize=1)
def _client() -> chat.ChatUser:
    return chat.ChatUser(
        ip_address=os.environ["BBW_CHAT_HOST"],
        port="443",
        username=os.environ["BBW_CHAT_USER"],
        password=os.environ["BBW_CHAT_PASS"],
        secure=True,
        cert_verify=True,
        application="Chat",
        debug=False,
    )


@mcp.tool
def list_channels() -> list[dict]:
    """List all joined chat channels/DMs with id, name, type, last_post_at."""
    chans = _client().channel_list()["data"]["channels"]
    return [
        {
            "channel_id": c["channel_id"],
            "name": c.get("name") or "(DM)",
            "type": c["type"],
            "members": c.get("members"),
            "last_post_at": c.get("last_post_at"),
            "unread": c.get("unread", 0),
        }
        for c in chans
    ]


@mcp.tool
def find_user(name_query: str) -> list[dict]:
    """Find users by (partial, case-insensitive) username, e.g. 'wilke'."""
    users = _client().user_list()["data"]["users"]
    q = name_query.lower()
    return [
        {"user_id": u["user_id"], "username": u.get("username", "")}
        for u in users
        if q in u.get("username", "").lower()
    ]


@mcp.tool
def get_recent_posts(channel_id: int, limit: int = 20) -> list[dict]:
    """Read recent messages/tasks in a channel (use to check for new Ausbilder-Aufgaben)."""
    result = _client().post_search([channel_id], limit=limit)
    posts = result.get("data", {}).get("search_results", [])
    out = []
    for p in posts:
        out.append({
            "post_id": p.get("post_id"),
            "creator_id": p.get("creator_id"),
            "message": p.get("message", ""),
            "type": p.get("type"),
            "file_name": (p.get("file_props") or {}).get("name"),
            "create_at": p.get("create_at"),
        })
    return out


@mcp.tool
def dm_channel_for_user(user_id: int) -> int | None:
    """Find (or None if none exists yet) the 1:1 DM channel_id for a given user_id."""
    chans = _client().channel_list()["data"]["channels"]
    for c in chans:
        members = c.get("members") or []
        if c.get("type") == "anonymous" and user_id in members and len(members) == 2:
            return c["channel_id"]
    return None


@mcp.tool
def send_message(channel_id: int, message: str) -> dict:
    """Post a text message to a channel/DM."""
    return _client().post_create(channel_id, message)


@mcp.tool
def send_file(channel_id: int, file_path: str, message: str = "") -> dict:
    """Upload a file to a channel/DM, optionally followed by a text message."""
    upload_result = _client().post_file_upload(channel_id, file_path)
    if message:
        _client().post_create(channel_id, message)
    return upload_result


if __name__ == "__main__":
    mcp.run()
