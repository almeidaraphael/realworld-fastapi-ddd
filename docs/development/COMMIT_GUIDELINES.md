# Commit Message Guidelines

> 📖 **[← Back to README](../../README.md)** | **[📋 Documentation Index](../README.md)**

This document outlines the commit message conventions for the FastAPI RealWorld Demo project.

> **💡 Note**: This document provides detailed commit guidelines. For a complete development workflow including setup, testing, and deployment, see the [Development Workflow](../../README.md#development-workflow) section in README.md.

## Table of Contents

- [Format](#format)
- [Type](#type)
- [Scope](#scope)
- [Subject](#subject)
- [Body](#body)
- [Footer](#footer)
- [Examples](#examples)
- [Tips for Better Commits](#tips-for-better-commits)
- [Setting up the commit template](#setting-up-the-commit-template)
- [Tools and Automation](#tools-and-automation)
- [Bad vs Good Examples](#bad-vs-good-examples)
- [RealWorld Project Specific Guidelines](#realworld-project-specific-guidelines)

## Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

## Type

The type must be one of the following:

- **feat**: A new feature for the user
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools and libraries
- **ci**: Changes to CI configuration files and scripts
- **build**: Changes that affect the build system or external dependencies
- **revert**: Reverts a previous commit

## Scope

The scope is optional and should indicate the module or component affected:

- **users**: User-related functionality (registration, login, profile updates)
- **articles**: Article-related functionality (CRUD operations, favorites)
- **profiles**: Profile-related functionality (following, user profiles)
- **comments**: Comment-related functionality
- **auth**: Authentication and authorization
- **db**: Database schema changes, migrations
- **api**: API layer changes (endpoints, routing)
- **domain**: Domain layer changes (models, business logic)
- **service**: Service layer changes
- **infra**: Infrastructure changes (Docker, deployment)
- **config**: Configuration changes
- **deps**: Dependency updates

## Subject

The subject contains a succinct description of the change:

- Use the imperative mood: "change" not "changed" nor "changes"
- Don't capitalize the first letter
- No dot (.) at the end
- Maximum 50 characters

## Body

The body should include the motivation for the change and contrast this with previous behavior:

- Use the imperative mood: "change" not "changed" nor "changes"
- Wrap at 72 characters
- Explain **what** and **why** vs. **how**
- Can include multiple paragraphs separated by blank lines

## Footer

The footer should contain any information about **Breaking Changes** and is also the place to reference GitHub issues that this commit **Closes**.

- **Breaking Changes** should start with the word `BREAKING CHANGE:` with a space or two newlines
- **Closing issues** should use keywords like `Closes #123`, `Fixes #456`, `Resolves #789`

## Examples

### Feature with scope and body

```
feat(articles): add article deletion endpoint

Implement DELETE /api/articles/:slug endpoint following RealWorld spec.
Only article authors can delete their own articles.

- Add delete_article method to ArticleRepository
- Add delete_article service method with authorization check
- Add DELETE endpoint with proper error handling
- Include comprehensive integration tests

Closes #42
```

### Bug fix

```
fix(auth): resolve JWT token expiration handling

Fix issue where expired tokens were not properly handled, causing
500 errors instead of 401 Unauthorized responses.

- Add token expiration validation in jwt.decode_token
- Update exception handling in auth dependency
- Add tests for expired token scenarios

Fixes #128
```

### Refactoring

```
refactor(domain): migrate from SQLModel to pure SQLAlchemy

Separate concerns between API schemas (Pydantic) and ORM models
(SQLAlchemy) following Domain-Driven Design principles.

- Split mixed SQLModel classes into separate files
- Create dedicated schemas.py for API models
- Create dedicated orm.py for database models
- Update all imports and dependencies
- Maintain backward compatibility

BREAKING CHANGE: Internal model structure changed, affects direct
model imports
```

### Documentation

```
docs: update API documentation with authentication examples

Add comprehensive examples for JWT authentication flows including
registration, login, and authenticated requests.
```

### Simple feature

```
feat(users): add email validation on registration
```

## Tips for Better Commits

1. **Make atomic commits**: Each commit should represent a single logical change
2. **Write descriptive subjects**: Someone should understand what changed just from the subject
3. **Use the body for context**: Explain why the change was made, not just what changed
4. **Reference issues**: Always link to related issues or tickets
5. **Test your changes**: Ensure tests pass before committing
6. **Review your diff**: Use `git diff --cached` to review staged changes before committing

## Setting up the commit template

Configure Git to use the commit template:

```bash
git config commit.template .commit-template
```

## Tools and Automation

Consider using:
- **Commitizen**: Tool to create standardized commit messages
- **Conventional Changelog**: Automatically generate changelogs
- **Husky + Commitlint**: Enforce commit message format via Git hooks

## Bad vs Good Examples

### ❌ Bad Examples

```
fix stuff
update code
WIP
feat: add new feature
fix: bug
```

### ✅ Good Examples

```
feat(articles): implement article favoriting functionality
fix(auth): resolve token refresh infinite loop
docs(api): add OpenAPI schema validation examples
test(users): add integration tests for registration flow
refactor(db): optimize article query performance
```

## RealWorld Project Specific Guidelines

For this FastAPI RealWorld implementation:

1. **Always reference the RealWorld spec**: When implementing endpoints, mention spec compliance
2. **Include test information**: Mention what types of tests were added/updated
3. **Mention layer changes**: Specify if changes affect API, service, domain, or infrastructure layers
4. **Database changes**: Always mention migration implications
5. **Authentication context**: Specify if changes affect auth flows

### Example for RealWorld endpoints

```
feat(articles): implement GET /api/articles/:slug endpoint

Add individual article retrieval following RealWorld API specification.
Includes proper error handling for non-existent articles and author
information in response.

- Add get_article_by_slug method to ArticleRepository
- Add get_article service method with author lookup
- Add GET /:slug endpoint with 404 handling
- Include integration tests for success and error cases
- Ensure response format matches RealWorld spec

Refs: https://realworld-docs.netlify.app/docs/specs/backend-specs/endpoints/
```

## Related Documentation

- **[README.md](README.md)** - Main project documentation and setup guide
- **[EXCEPTION_HANDLING.md](EXCEPTION_HANDLING.md)** - Exception handling architecture and best practices
- **[Development Workflow](README.md#development-workflow)** - Complete development workflow in README.md

---

> 📖 **[← Back to README](../../README.md)** | **[📋 Documentation Index](../README.md)**
