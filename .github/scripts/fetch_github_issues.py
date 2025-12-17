#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.error


def fetch_github_issues():
    """Fetch GitHub issues from the repository"""
    repo = "amd/halo_playbooks"
    token = os.environ.get("GITHUB_TOKEN", "")

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Halo-Website-Fetch",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    issues = []

    # Try to fetch by milestone first
    try:
        milestones_url = f"https://api.github.com/repos/{repo}/milestones"
        req = urllib.request.Request(milestones_url, headers=headers)

        with urllib.request.urlopen(req) as response:
            milestones = json.loads(response.read())

        playbooks_milestone = next(
            (m for m in milestones if m["title"].lower() == "playbooks"), None
        )

        if playbooks_milestone:
            issues_url = f"https://api.github.com/repos/{repo}/issues?milestone={playbooks_milestone['number']}&state=all&per_page=100"
            req = urllib.request.Request(issues_url, headers=headers)

            with urllib.request.urlopen(req) as response:
                issues = json.loads(response.read())
    except Exception as e:
        print(f"Milestone fetch failed: {e}", file=sys.stderr)

    # Fallback: fetch issues with "playbooks" label
    if not issues:
        try:
            issues_url = f"https://api.github.com/repos/{repo}/issues?labels=playbooks&state=all&per_page=100"
            req = urllib.request.Request(issues_url, headers=headers)

            with urllib.request.urlopen(req) as response:
                issues = json.loads(response.read())
        except Exception as e:
            print(f"Label fetch failed: {e}", file=sys.stderr)

    # If still no issues, try fetching all issues and filter
    if not issues:
        try:
            all_issues_url = (
                f"https://api.github.com/repos/{repo}/issues?state=all&per_page=100"
            )
            req = urllib.request.Request(all_issues_url, headers=headers)

            with urllib.request.urlopen(req) as response:
                all_issues = json.loads(response.read())

            # Filter for issues that have relevant labels
            issues = [
                issue
                for issue in all_issues
                if any(
                    label["name"].startswith(prefix)
                    for label in issue.get("labels", [])
                    for prefix in ["track::", "os::", "app::", "framework::", "model::"]
                )
            ]
        except Exception as e:
            print(f"All issues fetch failed: {e}", file=sys.stderr)

    return issues


if __name__ == "__main__":
    try:
        issues = fetch_github_issues()
        result = {"issues": issues}

        # Write to file
        output_file = "github_issues_cache.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        print(f"Successfully fetched {len(issues)} issues and saved to {output_file}")
    except Exception as e:
        error_result = {"error": str(e), "issues": []}
        with open("github_issues_cache.json", "w", encoding="utf-8") as f:
            json.dump(error_result, f, indent=2)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
