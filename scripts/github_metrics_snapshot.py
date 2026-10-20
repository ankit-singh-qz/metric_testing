#!/usr/bin/env python3
"""Snapshot GitHub-sourced engineering metrics (2–7) for the metrics demo repo.

AI-authored code % (metric 1) requires Cursor AI Code Tracking or equivalent;
see docs/ai-telemetry-github.md.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SNAPSHOT_VERSION = "0.1.1"

ISSUE_KEYWORDS = re.compile(
    r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)\b", re.I
)


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def gh_api(path: str, token: str) -> Any:
    url = f"https://api.github.com{path}"
    req = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urlopen(req, timeout=60) as resp:
        return json.load(resp)


def gh_api_paginated(path: str, token: str, params: dict[str, str] | None = None) -> list[Any]:
    items: list[Any] = []
    query = ""
    if params:
        query = "?" + "&".join(f"{k}={v}" for k, v in params.items())
    page = 1
    while True:
        separator = "&" if query else "?"
        page_path = f"{path}{query}{separator}page={page}&per_page=100"
        batch = gh_api(page_path, token)
        if not batch:
            break
        items.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return items


def resolve_repo_and_token() -> tuple[str, str, str]:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        try:
            token = (
                subprocess.check_output(["gh", "auth", "token"], text=True).strip()
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
    if not token:
        sys.exit(
            "Set GITHUB_TOKEN or run `gh auth login` so this script can call the GitHub API."
        )

    repo = os.environ.get("GITHUB_REPOSITORY")
    if not repo:
        try:
            repo = subprocess.check_output(
                ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
                text=True,
            ).strip()
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
    if not repo or "/" not in repo:
        sys.exit("Could not detect owner/repo. Set GITHUB_REPOSITORY=owner/repo.")
    owner, name = repo.split("/", 1)
    return owner, name, token


def linked_issue_numbers(pr_body: str | None) -> set[int]:
    if not pr_body:
        return set()
    return {int(n) for n in ISSUE_KEYWORDS.findall(pr_body)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Look back this many days from now (UTC). Default: 30",
    )
    args = parser.parse_args()
    owner, repo, token = resolve_repo_and_token()
    since = datetime.now(timezone.utc) - timedelta(days=args.days)

    pulls = gh_api_paginated(
        f"/repos/{owner}/{repo}/pulls",
        token,
        {"state": "closed", "sort": "updated", "direction": "desc"},
    )

    merged_prs: list[dict[str, Any]] = []
    review_waits_hours: list[float] = []
    rework_numerator = 0
    rework_denominator = 0
    attribution_linked = 0
    lead_times_hours: list[float] = []

    for pr in pulls:
        merged_at = _parse_iso(pr.get("merged_at"))
        if merged_at is None or merged_at < since:
            continue

        number = pr["number"]
        merged_prs.append(pr)
        body = pr.get("body") or ""
        if linked_issue_numbers(body):
            attribution_linked += 1

        created_at = _parse_iso(pr.get("created_at"))
        reviews = gh_api(f"/repos/{owner}/{repo}/pulls/{number}/reviews", token)
        human_reviews = [
            r
            for r in reviews
            if r.get("user", {}).get("type") == "User"
            and r.get("submitted_at")
            and r.get("state") in {"APPROVED", "CHANGES_REQUESTED", "COMMENTED"}
        ]
        if human_reviews:
            rework_denominator += 1
            human_reviews.sort(key=lambda r: r["submitted_at"])
            first_review_at = _parse_iso(human_reviews[0]["submitted_at"])
            if created_at and first_review_at:
                review_waits_hours.append(
                    (first_review_at - created_at).total_seconds() / 3600.0
                )

            commits = gh_api_paginated(
                f"/repos/{owner}/{repo}/pulls/{number}/commits", token
            )
            commit_times = [
                t
                for t in (_parse_iso(c["commit"]["author"]["date"]) for c in commits)
                if t
            ]
            if first_review_at and any(t > first_review_at for t in commit_times):
                rework_numerator += 1

        issue_nums = linked_issue_numbers(body)
        if issue_nums and merged_at:
            for issue_num in issue_nums:
                try:
                    issue = gh_api(f"/repos/{owner}/{repo}/issues/{issue_num}", token)
                except HTTPError:
                    continue
                issue_created = _parse_iso(issue.get("created_at"))
                if issue_created:
                    lead_times_hours.append(
                        (merged_at - issue_created).total_seconds() / 3600.0
                    )
                    break

    deployments = gh_api_paginated(f"/repos/{owner}/{repo}/deployments", token)
    prod_deployments = 0
    for dep in deployments:
        if dep.get("environment") != "production":
            continue
        created = _parse_iso(dep.get("created_at"))
        if created and created >= since:
            statuses = gh_api(
                f"/repos/{owner}/{repo}/deployments/{dep['id']}/statuses", token
            )
            if any(s.get("state") == "success" for s in statuses):
                prod_deployments += 1

    total_merged = len(merged_prs)
    window_days = args.days
    deploy_per_week = (prod_deployments / window_days) * 7.0 if window_days else 0.0

    report = {
        "snapshot_version": SNAPSHOT_VERSION,
        "repository": f"{owner}/{repo}",
        "window_days": window_days,
        "since_utc": since.isoformat(),
        "metrics": {
            "ai_authored_code_percent": {
                "value": None,
                "note": "Use Cursor /analytics/ai-code/commits or your AI-Telemetry backend; not available from GitHub API alone.",
            },
            "pr_throughput": {
                "merged_prs": total_merged,
            },
            "review_wait_time_hours": {
                "median": statistics.median(review_waits_hours)
                if review_waits_hours
                else None,
                "sample_size": len(review_waits_hours),
            },
            "rework_rate": {
                "rate": (rework_numerator / rework_denominator)
                if rework_denominator
                else None,
                "prs_with_post_review_commits": rework_numerator,
                "prs_with_human_review": rework_denominator,
            },
            "lead_time_for_changes_hours": {
                "median_issue_to_merge": statistics.median(lead_times_hours)
                if lead_times_hours
                else None,
                "sample_size": len(lead_times_hours),
                "definition": "Issue created → PR merged (linked via Closes/Fixes/Resolves #n)",
            },
            "deployment_frequency": {
                "successful_production_deployments": prod_deployments,
                "deployments_per_week": round(deploy_per_week, 4),
            },
            "attribution_mapping_rate": {
                "rate": (attribution_linked / total_merged) if total_merged else None,
                "prs_with_linked_issue": attribution_linked,
                "merged_prs": total_merged,
            },
        },
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    try:
        main()
    except HTTPError as exc:
        sys.exit(f"GitHub API error: {exc.code} {exc.reason}")
    except URLError as exc:
        sys.exit(f"Network error: {exc.reason}")
