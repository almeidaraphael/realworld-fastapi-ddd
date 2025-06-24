#!/usr/bin/env python3
"""
Script to help improve commit messages by analyzing recent commits
and suggesting improvements based on conventional commit standards.
"""

import re
import subprocess
import sys
from typing import Optional


def run_git_command(command: list[str]) -> str:
    """Run a git command and return the output."""
    try:
        result = subprocess.run(["git"] + command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")
        return ""


def parse_commit_message(message: str) -> dict[str, Optional[str] | bool]:
    """Parse a commit message and extract components."""
    lines = message.split("\n")
    subject = lines[0] if lines else ""

    # Try to parse conventional commit format
    pattern = r"^(\w+)(\([^)]+\))?: (.+)$"
    match = re.match(pattern, subject)

    if match:
        return {
            "type": match.group(1),
            "scope": match.group(2)[1:-1] if match.group(2) else None,
            "subject": match.group(3),
            "body": "\n".join(lines[2:]) if len(lines) > 2 else None,
            "is_conventional": True,
        }
    else:
        return {
            "type": None,
            "scope": None,
            "subject": subject,
            "body": "\n".join(lines[2:]) if len(lines) > 2 else None,
            "is_conventional": False,
        }


def suggest_improvements(commit_data: dict[str, Optional[str] | bool]) -> list[str]:
    """Suggest improvements for a commit message."""
    suggestions = []
    subject = commit_data.get("subject")
    if not isinstance(subject, str):
        subject = ""

    if not commit_data.get("is_conventional"):
        suggestions.append("Use conventional commit format: type(scope): subject")

    if len(subject) > 50:
        suggestions.append(f"Subject too long ({len(subject)} chars). Keep under 50 characters")

    if subject and subject[0].isupper():
        suggestions.append("Subject should start with lowercase letter")

    if subject.endswith("."):
        suggestions.append("Subject should not end with a period")

    # Check for imperative mood (basic heuristics)
    past_tense_words = ["added", "fixed", "updated", "created", "removed", "deleted"]
    if any(word in subject.lower() for word in past_tense_words):
        suggestions.append(
            "Use imperative mood (add, fix, update instead of added, fixed, updated)"
        )

    if not commit_data.get("body") and len(subject) < 30:
        suggestions.append("Consider adding a body to explain the 'why' behind the change")

    return suggestions


def analyze_recent_commits(count: int = 10) -> None:
    """Analyze recent commits and provide improvement suggestions."""
    print(f"Analyzing last {count} commits...\n")

    # Get recent commit hashes and messages
    commit_format = "--format=%H|%s|%b"
    output = run_git_command(["log", f"-{count}", commit_format])

    if not output:
        print("No commits found or git command failed")
        return

    commits = []
    current_commit = {}

    for line in output.split("\n"):
        if "|" in line and len(line.split("|")) >= 2:
            # New commit line
            if current_commit:
                commits.append(current_commit)

            parts = line.split("|", 2)
            current_commit = {
                "hash": parts[0][:8],
                "message": parts[1]
                + ("\n" + parts[2] if len(parts) > 2 and parts[2].strip() else ""),
            }
        elif current_commit:
            # Body continuation
            current_commit["message"] += "\n" + line

    if current_commit:
        commits.append(current_commit)

    # Analyze each commit
    for i, commit in enumerate(commits, 1):
        commit_data = parse_commit_message(commit["message"])
        suggestions = suggest_improvements(commit_data)

        print(f"Commit {i}: {commit['hash']}")
        print(f"Current: {commit_data['subject']}")

        if commit_data["is_conventional"]:
            print("✅ Follows conventional commit format")
        else:
            print("❌ Does not follow conventional commit format")

        if suggestions:
            print("💡 Suggestions:")
            for suggestion in suggestions:
                print(f"   - {suggestion}")
        else:
            print("✅ No improvements suggested")

        # Provide a better example
        if suggestions:
            example = create_better_example(commit_data, commit["hash"])
            if example:
                print(f"📝 Better example: {example}")

        print("-" * 60)


def create_better_example(
    commit_data: dict[str, Optional[str] | bool], commit_hash: str
) -> Optional[str]:
    """Create a better commit message example."""
    subject_raw = commit_data.get("subject")
    if not isinstance(subject_raw, str):
        return None
    subject = subject_raw.lower()

    # Get files changed in this commit
    files_output = run_git_command(["show", "--name-only", "--format=", commit_hash])
    files = files_output.split("\n") if files_output else []

    # Determine scope based on files
    scope = None
    if any("user" in f for f in files):
        scope = "users"
    elif any("article" in f for f in files):
        scope = "articles"
    elif any("profile" in f for f in files):
        scope = "profiles"
    elif any("comment" in f for f in files):
        scope = "comments"
    elif any("test" in f for f in files):
        scope = "test"
    elif any("api" in f for f in files):
        scope = "api"

    # Determine type
    commit_type = "feat"
    if "fix" in subject or "bug" in subject:
        commit_type = "fix"
    elif "test" in subject:
        commit_type = "test"
    elif "refactor" in subject:
        commit_type = "refactor"
    elif "doc" in subject:
        commit_type = "docs"

    # Clean up subject
    clean_subject = subject
    # Remove common prefixes
    prefixes = ["feat:", "fix:", "add:", "update:", "feat", "fix", "add", "update"]
    for prefix in prefixes:
        if clean_subject.startswith(prefix):
            clean_subject = clean_subject[len(prefix) :].strip(":").strip()

    # Make imperative
    replacements = {
        "added": "add",
        "fixed": "fix",
        "updated": "update",
        "created": "create",
        "removed": "remove",
        "deleted": "delete",
    }

    for old, new in replacements.items():
        clean_subject = clean_subject.replace(old, new)

    # Construct better message
    scope_part = f"({scope})" if scope else ""
    return f"{commit_type}{scope_part}: {clean_subject}"


def main():
    """Main function."""
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            print("Usage: python improve_commits.py [number_of_commits]")
            return
    else:
        count = 10

    print("🔍 Commit Message Analyzer")
    print("=" * 50)
    analyze_recent_commits(count)

    print("\n📚 Quick Reference:")
    print("Format: type(scope): subject")
    print("Types: feat, fix, docs, style, refactor, perf, test, chore")
    print("Scopes: users, articles, profiles, comments, auth, db, api, domain, service")
    print("\nFor more details, see COMMIT_GUIDELINES.md")


if __name__ == "__main__":
    main()
