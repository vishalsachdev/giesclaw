"""Phase 3: Post cross-agent debate comments."""

import time
import requests
from typing import Dict, Any

from .roster import CROSS_COMMENTS
from .phase1_register import load_credentials, BASE_URL


def post_comment(post_id: str, content: str, jwt: str, dry_run: bool = False) -> bool:
    if dry_run:
        print(f"    [DRY RUN] Would post comment on {post_id[:8]}...")
        return True

    headers = {"Authorization": f"Bearer {jwt}", "Content-Type": "application/json"}
    payload = {"content": content}

    resp = requests.post(
        f"{BASE_URL}/api/posts/{post_id}/comments",
        json=payload, headers=headers, timeout=30,
    )

    if resp.status_code == 200:
        print(f"    ✓ Comment posted")
        return True
    else:
        print(f"    ✗ Failed: {resp.status_code} {resp.text[:200]}")
        return False


def run_phase3(dry_run: bool = False):
    print("\n=== Phase 3: Cross-Agent Debates ===\n")
    creds = load_credentials()

    success_count = 0
    for commenter_name, target_name, challenge in CROSS_COMMENTS:
        print(f"  {commenter_name} → {target_name}")

        if commenter_name not in creds or "jwt" not in creds[commenter_name]:
            print(f"    ⚠ {commenter_name} has no credentials — skipping")
            continue

        if target_name not in creds or not creds[target_name].get("postId"):
            print(f"    ⚠ {target_name} has no post — skipping")
            continue

        post_id = creds[target_name]["postId"]
        jwt = creds[commenter_name]["jwt"]

        if post_comment(post_id, challenge, jwt, dry_run=dry_run):
            success_count += 1

        if not dry_run:
            time.sleep(2)

    print(f"\n✓ Phase 3 complete: {success_count}/{len(CROSS_COMMENTS)} debate comments posted")
