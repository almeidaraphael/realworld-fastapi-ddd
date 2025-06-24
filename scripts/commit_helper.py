#!/usr/bin/env python3
"""
Interactive commit message helper that guides you through creating
conventional commit messages.
"""

import subprocess
import sys


def get_staged_files() -> list[str]:
    """Get list of staged files."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True
        )
        return [f.strip() for f in result.stdout.split("\n") if f.strip()]
    except subprocess.CalledProcessError:
        return []


def suggest_scope(files: list[str]) -> str:
    """Suggest scope based on changed files."""
    scopes = {
        "users": ["user", "auth", "login", "register"],
        "articles": ["article", "post"],
        "profiles": ["profile", "follow"],
        "comments": ["comment"],
        "api": ["api/", "endpoint"],
        "domain": ["domain/", "models.py", "schemas.py"],
        "service": ["service_layer/", "services.py"],
        "db": ["alembic/", "migration", "models.py"],
        "test": ["test", "spec"],
        "config": ["config", "settings"],
        "infra": ["docker", "deploy", "ci"],
        "deps": ["pyproject.toml", "requirements", "poetry.lock"],
    }

    for scope, patterns in scopes.items():
        if any(pattern in " ".join(files).lower() for pattern in patterns):
            return scope

    return ""


def main():
    """Interactive commit message creation."""
    print("🚀 Interactive Commit Message Helper")
    print("=" * 50)

    # Check if there are staged changes
    staged_files = get_staged_files()
    if not staged_files:
        print("❌ No staged changes found. Stage your changes first with 'git add'.")
        sys.exit(1)

    print(f"📁 Staged files ({len(staged_files)}):")
    for file in staged_files[:5]:  # Show first 5 files
        print(f"   - {file}")
    if len(staged_files) > 5:
        print(f"   ... and {len(staged_files) - 5} more")
    print()

    # Get commit type
    types = {
        "1": ("feat", "A new feature"),
        "2": ("fix", "A bug fix"),
        "3": ("docs", "Documentation only changes"),
        "4": ("style", "Code style changes (formatting, etc.)"),
        "5": ("refactor", "Code change that neither fixes a bug nor adds a feature"),
        "6": ("perf", "Performance improvement"),
        "7": ("test", "Adding or updating tests"),
        "8": ("chore", "Build process or auxiliary tool changes"),
        "9": ("ci", "CI configuration changes"),
        "10": ("build", "Build system or dependency changes"),
    }

    print("📝 Select commit type:")
    for key, (type_name, description) in types.items():
        print(f"   {key}. {type_name}: {description}")

    while True:
        choice = input("\nEnter choice (1-10): ").strip()
        if choice in types:
            commit_type = types[choice][0]
            break
        print("❌ Invalid choice. Please enter a number 1-10.")

    # Get scope
    suggested_scope = suggest_scope(staged_files)
    scope_prompt = (
        f"🔍 Scope (optional, suggested: {suggested_scope}): "
        if suggested_scope
        else "🔍 Scope (optional): "
    )
    scope = input(scope_prompt).strip() or suggested_scope

    # Get subject
    print("\n📋 Subject (describe what the change does):")
    print("   - Use imperative mood (add, fix, update)")
    print("   - Start with lowercase")
    print("   - No period at the end")
    print("   - Max 50 characters")

    while True:
        subject = input("Subject: ").strip()
        if not subject:
            print("❌ Subject cannot be empty.")
            continue
        if len(subject) > 50:
            print(f"❌ Subject too long ({len(subject)} chars). Keep under 50.")
            continue
        if subject[0].isupper():
            print("❌ Subject should start with lowercase letter.")
            continue
        if subject.endswith("."):
            print("❌ Subject should not end with a period.")
            continue
        break

    # Build commit message
    scope_part = f"({scope})" if scope else ""
    commit_msg = f"{commit_type}{scope_part}: {subject}"

    # Get body (optional)
    print("\n📝 Body (optional - explain WHY, not what):")
    print("   Press Enter to skip, or type your explanation:")
    body = input().strip()

    if body:
        commit_msg += f"\n\n{body}"

    # Get footer (optional)
    print("\n🔗 Footer (optional - issues, breaking changes):")
    print("   Examples: 'Closes #123', 'BREAKING CHANGE: ...'")
    print("   Press Enter to skip:")
    footer = input().strip()

    if footer:
        commit_msg += f"\n\n{footer}"

    # Preview
    print("\n" + "=" * 50)
    print("📋 Preview of your commit message:")
    print("-" * 30)
    print(commit_msg)
    print("-" * 30)

    # Confirm
    while True:
        confirm = input("\n✅ Commit with this message? (y/n/e): ").strip().lower()
        if confirm == "y":
            # Create commit
            try:
                subprocess.run(["git", "commit", "-m", commit_msg], check=True)
                print("🎉 Commit created successfully!")
                return
            except subprocess.CalledProcessError as e:
                print(f"❌ Commit failed: {e}")
                return
        elif confirm == "n":
            print("❌ Commit cancelled.")
            return
        elif confirm == "e":
            # Edit message
            print("📝 Edit mode - enter the complete message:")
            commit_msg = input("New message: ").strip()
            if not commit_msg:
                print("❌ Message cannot be empty.")
                continue
        else:
            print("❌ Please enter 'y' (yes), 'n' (no), or 'e' (edit).")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user.")
        sys.exit(1)
