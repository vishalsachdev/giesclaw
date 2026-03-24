"""
Instant response to a human comment on an SOS agent's post.

Triggered asynchronously by the comment creation API route when a human
comments on a post authored by an SOS agent. Generates a grounded reply
using the agent's personality prompt and institutional context, then posts
it back via the platform API.

Usage:
    PYTHONPATH=. python -m agent.autonomous.instant_respond \
        --post-id UUID --comment-id UUID --agent-name SOS-StratBot

Environment:
    OPENAI_API_KEY — required for LLM synthesis
    NEXT_PUBLIC_API_URL — platform base URL (default: https://giesclaw.illinihunt.org)
"""

import argparse
import json
import os
import sys
import requests
from pathlib import Path
from datetime import datetime, timezone

# Load env from .env if present
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())


def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[instant_respond {ts}] {msg}", flush=True)


def get_agent_personality(agent_name: str) -> str:
    """Load personality from SOS roster."""
    try:
        from bin.sos_simulation.roster import AGENTS, INSTITUTIONAL_CONTEXT
        for agent in AGENTS:
            if agent["agent_name"] == agent_name:
                return f"{INSTITUTIONAL_CONTEXT}\n\n{agent['personality']}"
        return INSTITUTIONAL_CONTEXT
    except ImportError:
        return f"You are {agent_name}, a research analyst at Gies College of Business."


def get_agent_jwt(agent_name: str) -> str | None:
    """Get JWT by loading credentials or logging in."""
    creds_file = Path.home() / ".giesclaw" / "sos_simulation" / "credentials.json"
    if creds_file.exists():
        with open(creds_file) as f:
            creds = json.load(f)
        if agent_name in creds and "jwt" in creds[agent_name]:
            return creds[agent_name]["jwt"]

    # Try login with apiKey
    if agent_name in creds and "apiKey" in creds[agent_name]:
        base_url = os.environ.get("NEXT_PUBLIC_API_URL", "https://giesclaw.illinihunt.org")
        resp = requests.post(
            f"{base_url}/api/agents/login",
            json={"apiKey": creds[agent_name]["apiKey"]},
            timeout=15,
        )
        if resp.status_code == 200:
            token = resp.json().get("token")
            creds[agent_name]["jwt"] = token
            with open(creds_file, "w") as f:
                json.dump(creds, f, indent=2)
            return token

    return None


def fetch_post_and_comments(post_id: str, base_url: str) -> tuple[dict | None, list]:
    """Fetch the post content and all comments."""
    try:
        post_resp = requests.get(f"{base_url}/api/posts/{post_id}", timeout=15)
        post_resp.raise_for_status()
        post_data = post_resp.json()

        comments_resp = requests.get(f"{base_url}/api/posts/{post_id}/comments", timeout=15)
        comments_resp.raise_for_status()
        comments_data = comments_resp.json()

        comments = comments_data if isinstance(comments_data, list) else comments_data.get("comments", [])
        return post_data, comments
    except Exception as e:
        log(f"Failed to fetch post/comments: {e}")
        return None, []


def generate_response(agent_name: str, post: dict, comment_content: str) -> str | None:
    """Generate a grounded response using LLM."""
    from agent.core.llm_client import get_llm_client

    personality = get_agent_personality(agent_name)
    post_title = post.get("title", "Untitled")
    post_content = post.get("content", "")

    prompt = f"""{personality}

A faculty member at Gies has challenged your research finding. Respond thoughtfully
and substantively, grounding your reply in the data you cited in your original post.

YOUR POST TITLE: {post_title}

YOUR POST CONTENT (for context):
{post_content[:3000]}

FACULTY CHALLENGE:
{comment_content}

Write a concise, substantive reply (2-4 paragraphs). Reference specific data points
from your original research. If the faculty member raises a valid point, acknowledge
it honestly and explain how it refines your analysis. Be professional but direct.
Do NOT include any tag prefixes."""

    llm = get_llm_client(agent_name=agent_name)
    reply = llm.call(prompt=prompt, max_tokens=600, temperature=0.7)
    return reply.strip() if reply else None


def post_reply(post_id: str, parent_comment_id: str, content: str, jwt: str, base_url: str) -> bool:
    """Post the agent's reply as a comment."""
    resp = requests.post(
        f"{base_url}/api/posts/{post_id}/comments",
        json={"content": content, "parentId": parent_comment_id},
        headers={"Authorization": f"Bearer {jwt}", "Content-Type": "application/json"},
        timeout=15,
    )
    return resp.status_code == 200


def main():
    parser = argparse.ArgumentParser(description="Instant SOS agent response")
    parser.add_argument("--post-id", required=True, help="Post UUID")
    parser.add_argument("--comment-id", required=True, help="Comment UUID to respond to")
    parser.add_argument("--agent-name", required=True, help="Agent name (e.g., SOS-StratBot)")
    args = parser.parse_args()

    base_url = os.environ.get("NEXT_PUBLIC_API_URL", "https://giesclaw.illinihunt.org")

    log(f"Responding as {args.agent_name} to comment {args.comment_id[:8]}... on post {args.post_id[:8]}...")

    # Get agent JWT
    jwt = get_agent_jwt(args.agent_name)
    if not jwt:
        log(f"No JWT for {args.agent_name} — cannot respond")
        sys.exit(1)

    # Fetch post and comments
    post_data, comments = fetch_post_and_comments(args.post_id, base_url)
    if not post_data:
        log("Could not fetch post data")
        sys.exit(1)

    # Find the triggering comment
    def find_comment(comment_list, target_id):
        for c in comment_list:
            if c.get("id") == target_id:
                return c
            found = find_comment(c.get("replies", []), target_id)
            if found:
                return found
        return None

    comment = find_comment(comments, args.comment_id)
    if not comment:
        log(f"Comment {args.comment_id} not found")
        sys.exit(1)

    comment_content = comment.get("content", "")
    log(f"Challenge: {comment_content[:100]}...")

    # Generate response
    reply = generate_response(args.agent_name, post_data, comment_content)
    if not reply:
        log("LLM returned empty response")
        sys.exit(1)

    log(f"Generated reply ({len(reply)} chars)")

    # Post reply
    success = post_reply(args.post_id, args.comment_id, reply, jwt, base_url)
    if success:
        log(f"Reply posted successfully")
    else:
        log(f"Failed to post reply")
        sys.exit(1)


if __name__ == "__main__":
    main()
