"""
Slack utilities for looking up user information.
"""

import os
import httpx

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")


def get_slack_username(slack_id: str) -> str | None:
    """
    Look up a Slack user's username (display name) by their Slack ID.
    
    Args:
        slack_id: The Slack user ID (e.g., "U01234567")
        
    Returns:
        The user's Slack username (e.g., "johndoe") or None if lookup fails
    """
    if not SLACK_BOT_TOKEN:
        print("⚠️  SLACK_BOT_TOKEN not set, cannot look up Slack username")
        return None
    
    if not slack_id:
        return None
    
    try:
        response = httpx.get(
            "https://slack.com/api/users.info",
            params={"user": slack_id},
            headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"},
            timeout=10.0
        )
        data = response.json()
        
        if data.get("ok"):
            user = data.get("user", {})
            profile = user.get("profile", {})
            # Prefer display_name, fall back to real_name, then username
            return profile.get("display_name") or user.get("real_name") or user.get("name")
        else:
            error = data.get("error", "unknown error")
            print(f"⚠️  Slack API error for user {slack_id}: {error}")
            return None
            
    except Exception as e:
        print(f"⚠️  Error fetching Slack user {slack_id}: {e}")
        return None


async def get_slack_username_async(slack_id: str) -> str | None:
    """
    Async version of get_slack_username.
    """
    if not SLACK_BOT_TOKEN:
        print("⚠️  SLACK_BOT_TOKEN not set, cannot look up Slack username")
        return None
    
    if not slack_id:
        return None
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://slack.com/api/users.info",
                params={"user": slack_id},
                headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"},
                timeout=10.0
            )
            data = response.json()
            
            if data.get("ok"):
                user = data.get("user", {})
                profile = user.get("profile", {})
                # Prefer display_name, fall back to real_name, then username
                return profile.get("display_name") or user.get("real_name") or user.get("name")
            else:
                error = data.get("error", "unknown error")
                print(f"⚠️  Slack API error for user {slack_id}: {error}")
                return None
                
    except Exception as e:
        print(f"⚠️  Error fetching Slack user {slack_id}: {e}")
        return None
